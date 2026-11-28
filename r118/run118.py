#!/usr/bin/env python3
"""R118 registered run (PREREGISTRATION sections 2-4). Synthetic only (no K4 input).
  --arm S: S105 conditional recovery (as R114 arm A1) on 40 windows x 3 forms.
  --arm R: R59's running-key solver on 12 windows x 3 forms, on each plant's own convention; needs --lm (R59's pinned
           letter model, sha256 checked) and --solver (rk_solve built from r59/blind/rk_solve.cpp, g++ -O2 -std=c++17).
Usage: python3 -I r118/run118.py --arm S OUT.json
       python3 -I r118/run118.py --arm R --lm LM.bin --solver rk_solve --work DIR OUT.json"""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"
import argparse  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "r114"), str(ROOT / "r111"), str(ROOT / "r100")]
import masks118 as M  # noqa: E402
import run114 as R114  # noqa: E402
import cells111 as C  # noqa: E402
import autokey100 as AK  # noqa: E402

SEED_S_PLANTS, SEED_S_SOLVER, SEED_R_PLANTS = 1180901, 1180902, 1180903
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
CLUE_WORDS = ("EASTNORTHEAST", "NORTHEAST", "BERLIN", "CLOCK")
TEXT = ROOT / "r33/data/source_carter_mace_1923_google_ocr.txt"
FORMS = ("U", "G", "T")
R_CONVS = ("AZ_VIG", "AZ_BEAU", "KRY_VIG", "KRY_BEAU")
R_PARAMS = ["100000", "2000", "1"]          # BEAM TOPN LAMBDA (R59); then CONVENTIONS; then POLISH_M WORDS
R_PARAMS_TAIL = ["3", "20000"]
WORDS = ROOT / "k4kit/data/word_model_orth.tsv"
SOURCES = ("masks118.py", "run118.py")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def token_regions():
    """Second-half token start index (>= 2,000 letters after the midpoint) and the first-half letters (keys)."""
    toks = M.tokens(TEXT.read_text(errors="ignore"))
    total = sum(len(t) for t in toks if t != ".")
    mid, acc, start = total // 2, 0, None
    for i, t in enumerate(toks):
        if t != ".":
            acc += len(t)
        if start is None and acc >= mid + 2000:
            start = i + 1
    first_half = "".join(t for t in toks if t != ".")[:mid]
    return toks, start, first_half


def window_forms(rng, toks, start):
    """Three forms of one word run, each cut to 97 letters; skips runs where any form holds a published K4 word."""
    while True:
        s = rng.randrange(start, len(toks) - 200)
        e = s
        while e < len(toks) and min(len(M.form(toks[s:e], k)) for k in FORMS) < 97:
            e += 1
        forms = {k: M.form(toks[s:e], k)[:97] for k in FORMS}
        if all(len(v) == 97 for v in forms.values()) and not any(w in v for v in forms.values() for w in CLUE_WORDS):
            return forms


def arm_s():
    toks, start, _ = token_regions()
    rng = random.Random(SEED_S_PLANTS)
    plants = []
    for (b, L, sig) in C.CELLS:
        for _ in range(2):
            forms = window_forms(rng, toks, start)
            s1, s2 = rng.choice([sp for sp in R114.SIGN_PAIRS if -sp[0] * sp[1] == sig])
            A = "".join(rng.sample(AZ, 26))
            c = rng.randrange(26)
            primer = [rng.randrange(26) for _ in range(L)]
            for k in FORMS:
                ct = AK.encrypt(forms[k], A, C.B_LIST[b], "A", L, s1, s2, c, primer)
                plants.append({"form": k, "B": b, "L": L, "sigma": sig, "signs": [s1, s2], "A": A, "c": c,
                               "pt": forms[k], "ct": ct})
    srng = random.Random(SEED_S_SOLVER)
    rows = []
    for i, p in enumerate(plants):
        r = R114.solve_plant(p, srng)
        r.update({"window": i // 3, "form": p["form"], "exact": r["witness_ok"] and r["letters"] == 97})
        rows.append(r)
    summ = {}
    for k in FORMS:
        rk = [r for r in rows if r["form"] == k]
        summ[k] = {"plants": len(rk), "ge90": sum(r["recovered90"] for r in rk), "exact": sum(r["exact"] for r in rk),
                   "witness_failures": sum(not r["witness_ok"] for r in rk),
                   "share_ge90": round(sum(r["recovered90"] for r in rk) / len(rk), 4)}
    return rows, summ, "recovered90"


def enc_r(p, k, conv):
    xn, op = conv.split("_")
    X = AZ if xn == "AZ" else KRY
    return "".join(X[(X.index(a) + X.index(b)) % 26 if op == "VIG" else (X.index(b) - X.index(a)) % 26]
                   for a, b in zip(p, k))


def key_window(rng, first_half):
    while True:
        s = rng.randrange(0, len(first_half) - 97)
        w = first_half[s:s + 97]
        if not any(c in w for c in CLUE_WORDS):
            return w


def arm_r(lm, solver, work):
    reg = (ROOT / "r59/blind/LM_SHA256").read_text().split()[0]
    if sha(lm) != reg:
        raise SystemExit("REFUSED: language model sha256 does not match r59/blind/LM_SHA256")
    toks, start, first_half = token_regions()
    rng = random.Random(SEED_R_PLANTS)
    plants = []
    for i in range(12):
        conv = R_CONVS[i % 4]
        forms = window_forms(rng, toks, start)
        key = key_window(rng, first_half)
        for k in FORMS:
            plants.append({"id": f"W{i:02d}_{k}", "window": i, "form": k, "conv": conv, "pt": forms[k], "key": key,
                           "ct": enc_r(forms[k], key, conv)})
    work.mkdir(parents=True, exist_ok=True)
    out = {}
    for conv in R_CONVS:
        grp = [p for p in plants if p["conv"] == conv]
        tsv, res = work / f"in_{conv}.tsv", work / f"out_{conv}.jsonl"
        if res.exists():
            raise SystemExit("REFUSED: solver output already exists; no overwrite or retry")
        tsv.write_text("id\tciphertext\n" + "".join(f"{p['id']}\t{p['ct']}\n" for p in grp))
        with open(work / f"log_{conv}.txt", "w") as log:
            subprocess.run([str(solver), str(lm), str(WORDS), str(tsv), str(res)] + R_PARAMS + [conv] + R_PARAMS_TAIL,
                           stderr=log, check=True)
        for line in res.read_text().splitlines():
            d = json.loads(line)
            out[d["id"]] = d["best"]
    rows = []
    for p in plants:
        b = out[p["id"]]
        pair = sum(sorted((a, c)) == sorted((x, y)) for a, c, x, y in zip(b["plaintext"], b["key"], p["pt"], p["key"]))
        stream = max(sum(a == x for a, x in zip(b["plaintext"], p["pt"])),
                     sum(c == x for c, x in zip(b["key"], p["pt"])))
        wit = enc_r(b["plaintext"], b["key"], b["convention"]) == p["ct"] and b["convention"] == p["conv"]
        rows.append({"window": p["window"], "form": p["form"], "conv": p["conv"], "pair_correct": pair,
                     "plaintext_stream_correct": stream, "witness_ok": wit, "total": b["total"],
                     "pc60": wit and pair >= 60, "exact": wit and stream == 97})
    summ = {}
    for k in FORMS:
        rk = [r for r in rows if r["form"] == k]
        pcs = sorted(r["pair_correct"] for r in rk)
        summ[k] = {"plants": len(rk), "pc60": sum(r["pc60"] for r in rk), "exact": sum(r["exact"] for r in rk),
                   "witness_failures": sum(not r["witness_ok"] for r in rk), "median_pair_correct": pcs[len(pcs) // 2],
                   "share_pc60": round(sum(r["pc60"] for r in rk) / len(rk), 4)}
    return rows, summ, "pc60"


def drops(rows, summ, key):
    out = {}
    share = "share_ge90" if key == "recovered90" else "share_pc60"
    for m in ("G", "T"):
        by = {}
        for r in rows:
            by.setdefault(r["window"], {})[r["form"]] = r[key]
        lost = sum(v["U"] and not v[m] for v in by.values())
        gained = sum(v[m] and not v["U"] for v in by.values())
        d = round(100 * (summ["U"][share] - summ[m][share]), 1)
        out[m] = {"drop_points": d, "recovered_U_not_M": lost, "recovered_M_not_U": gained,
                  "label": "SENSITIVE" if d > 15 else "ROBUST"}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=("S", "R"), required=True)
    ap.add_argument("--lm", type=Path)
    ap.add_argument("--solver", type=Path)
    ap.add_argument("--work", type=Path)
    ap.add_argument("out", type=Path)
    a = ap.parse_args()
    if a.out.exists():
        raise SystemExit("REFUSED: output exists; no overwrite or retry")
    t0w, t0c = time.time(), time.process_time()
    rep = {"round": "R118", "arm": a.arm}
    if a.arm == "S":
        rows, summ, key = arm_s()
        rep["seeds"] = {"plants": SEED_S_PLANTS, "solver": SEED_S_SOLVER}
    else:
        rows, summ, key = arm_r(a.lm, a.solver, a.work)
        rep["seeds"] = {"plants": SEED_R_PLANTS}
        rep["solver_binary_sha256"] = sha(a.solver)
        rep["solver_build"] = "g++ -O2 -std=c++17 r59/blind/rk_solve.cpp"
        rep["lm_sha256"] = sha(a.lm)
    rep.update({"summary": summ, "drops": drops(rows, summ, key), "rows": rows})
    rep["wall_s"], rep["cpu_s"] = round(time.time() - t0w, 2), round(time.process_time() - t0c, 2)
    rep["source_sha256"] = {s: sha(HERE / s) for s in SOURCES}
    a.out.write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps({"summary": summ, "drops": rep["drops"]}))


if __name__ == "__main__":
    main()
