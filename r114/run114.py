#!/usr/bin/env python3
"""R114 registered run (PREREGISTRATION sections 1-3): S105 validation. Both jobs regenerate the same plant list from
seed 1140901 and use solver seed 1140902; job 1 solves A1-A3, job 2 solves A4-A5. Synthetic only (no K4 input).
Usage: python3 -I r114/run114.py --job 1|2 OUT.json"""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"
import argparse  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from math import comb  # noqa: E402,F401
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(ROOT / "r111"), str(ROOT / "r105"), str(ROOT / "r100"), str(ROOT / "r113")]
import cells111 as C  # noqa: E402
import solve105 as S  # noqa: E402
import autokey100 as AK  # noqa: E402
from run113 import cp_bounds  # noqa: E402

SEED_PLANTS, SEED_SOLVER = 1140901, 1140902
AZ = AK.AZ
CLUE_WORDS = ("EASTNORTHEAST", "NORTHEAST", "BERLIN", "CLOCK")
TEXT = ROOT / "r33/data/source_carter_mace_1923_google_ocr.txt"
K1K3 = ROOT / "k4kit/data/k1k3_plaintext.txt"
SIGN_PAIRS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]


def letters_only(s):
    return "".join(ch for ch in s.upper() if "A" <= ch <= "Z")


def texts():
    carter = letters_only(TEXT.read_text(errors="ignore"))
    mid = len(carter) // 2
    return carter[:mid], carter[mid + 2000:], letters_only(K1K3.read_text())


def window(rng, txt, n=97):
    while True:
        s = rng.randrange(0, len(txt) - n + 1)
        w = txt[s:s + n]
        if not any(c in w for c in CLUE_WORDS):
            return w


def make_plant(rng, pt, b, L, sig):
    s1, s2 = rng.choice([sp for sp in SIGN_PAIRS if -sp[0] * sp[1] == sig])
    A = "".join(rng.sample(AZ, 26))
    c = rng.randrange(26)
    ct = AK.encrypt(pt, A, C.B_LIST[b], "A", L, s1, s2, c, [rng.randrange(26) for _ in range(L)])
    return {"B": b, "L": L, "sigma": sig, "signs": [s1, s2], "A": A, "c": c, "pt": pt, "ct": ct}


def plants(rng):
    dev_half, test_c, test_k = texts()
    a1 = [make_plant(rng, window(rng, test_c), b, L, sig) for (b, L, sig) in C.CELLS for _ in range(10)]
    a2 = [make_plant(rng, window(rng, test_k), b, L, sig) for (b, L, sig) in C.CELLS for _ in range(2)]
    a4 = [make_plant(rng, window(rng, test_c), *C.CELLS[(7 * k) % 20]) for k in range(12)]
    a5 = [{"kind": "random", "ct": "".join(rng.choice(AZ) for _ in range(97))} for _ in range(4)]
    for k in range(4):
        lst = list(a4[k]["ct"])
        rng.shuffle(lst)
        a5.append({"kind": "shuffle_of_A4", "ct": "".join(lst)})
    for _ in range(4):
        A, B = "".join(rng.sample(AZ, 26)), "".join(rng.sample(AZ, 26))
        L = rng.randrange(1, 6)
        s1, s2 = rng.choice(SIGN_PAIRS)
        ct = AK.encrypt(window(rng, test_c), A, B, "A", L, s1, s2, rng.randrange(26), [rng.randrange(26) for _ in range(L)])
        a5.append({"kind": "two_free_alphabet_autokey", "ct": ct})
    return dev_half, a1, a2, a4, a5


def witness(ct, P, A, B, L, s1, s2, c):
    """Emit the primer for i < L and forward-encrypt all 97 letters; True if the ciphertext is reproduced."""
    primer = [(B.index(ct[i]) - s1 * A.index(P[i])) % 26 for i in range(L)]
    return AK.encrypt(P, A, B, "A", L, s1, s2, c, primer) == ct, primer


def quad_table(text):
    x = np.array([ord(ch) - 65 for ch in text], dtype=np.int64)
    idx = ((x[:-3] * 26 + x[1:-2]) * 26 + x[2:-1]) * 26 + x[3:]
    cnt = np.bincount(idx, minlength=26 ** 4).astype(np.float64)
    lp = np.log10((cnt + 0.01) / (cnt.sum() + 0.01 * 26 ** 4))
    return np.round(lp * 10000).astype(np.int64)


def solve_plant(p, srng):
    B = C.B_LIST[p["B"]]
    s1, s2 = p["signs"]
    tr = {"z0": S.gauge_truth(p["A"], p["c"], s1, s2, p["L"], p["pt"])}
    o = S.solve(p["ct"], B, p["L"], s1, s2, srng, trace=tr)
    ok, primer = witness(p["ct"], o["plaintext"], o["A"], B, p["L"], s1, s2, o["c"])
    n = sum(a == b for a, b in zip(o["plaintext"], p["pt"]))
    true_score = S.qs([AZ.index(ch) for ch in p["pt"]])
    if ok and n >= 90:
        lost = None
    elif tr["stage1_rank"] is None:
        lost = "stage1"
    elif tr["stage2_rank"] >= S.K_STAGE2:
        lost = "stage2"
    elif tr["stage3_rank"] >= S.K_STAGE3:
        lost = "stage3"
    else:
        lost = "scorer" if true_score <= o["score"] else "annealer"
    return {"B": p["B"], "L": p["L"], "sigma": p["sigma"], "letters": n, "witness_ok": ok, "primer": primer,
            "score": o["score"], "true_score": true_score, "recovered90": ok and n >= 90, "lost_at": lost}


def summary(rows):
    k = len(rows)
    out = {"plants": k}
    for name, thr in (("exact", 97), ("ge95", 95), ("ge90", 90)):
        hits = sum(r["witness_ok"] and r["letters"] >= thr for r in rows)
        lo, hi = cp_bounds(hits, k, alpha=0.05)
        out[name] = {"hits": hits, "share": round(hits / k, 4), "cp95": [round(lo, 4), round(hi, 4)]}
    out["witness_failures"] = sum(not r["witness_ok"] for r in rows)
    lost = {}
    for r in rows:
        if r["lost_at"]:
            lost[r["lost_at"]] = lost.get(r["lost_at"], 0) + 1
    out["lost_at"] = lost
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", type=int, choices=(1, 2), required=True)
    ap.add_argument("out", type=Path)
    a = ap.parse_args()
    t0w, t0c = time.time(), time.process_time()
    dev_half, a1, a2, a4, a5 = plants(random.Random(SEED_PLANTS))
    srng = random.Random(SEED_SOLVER)
    rep = {"round": "R114", "job": a.job, "seed_plants": SEED_PLANTS, "seed_solver": SEED_SOLVER}
    if a.job == 1:
        r1 = [solve_plant(p, srng) for p in a1]
        r2 = [solve_plant(p, srng) for p in a2]
        inherited = S.QI
        S.QI = quad_table(dev_half)
        try:
            r3 = [solve_plant(p, srng) for p in a1[:60] + a2]
        finally:
            S.QI = inherited
        per_cell = {}
        for r in r1:
            key = f"{r['B']}_L{r['L']}_sig{r['sigma']:+d}"
            per_cell[key] = per_cell.get(key, 0) + r["recovered90"]
        base3 = sum(r["recovered90"] for r in r1[:60] + r2) / 100
        dev3 = sum(r["recovered90"] for r in r3) / 100
        rep.update({"A1": {**summary(r1), "per_cell_ge90": per_cell, "rows": r1},
                    "A2": {**summary(r2), "rows": r2},
                    "A3": {**summary(r3), "ge90_share_inherited_same_plants": base3, "ge90_share_devhalf_table": dev3,
                           "rows": r3}})
        rep["bars"] = {"bar1_A1": summary(r1)["ge90"]["share"] >= 0.70 and min(per_cell.values()) >= 5,
                       "bar2_A2": summary(r2)["ge90"]["share"] >= 0.50,
                       "bar3_A3": abs(base3 - dev3) <= 0.15}
    else:
        rows4 = []
        for p in a4:
            T, cells = C.search(p["ct"], srng, keep_text=True)
            top = max(cells, key=lambda r: r["score"])
            B = C.B_LIST[top["B"]]
            s1, s2 = C.SIGMA_CELLS[top["sigma"]]
            ok, _ = witness(p["ct"], top["plaintext"], top["A"], B, top["L"], s1, s2, top["c"])
            n = sum(x == y for x, y in zip(top["plaintext"], p["pt"]))
            rows4.append({"B": p["B"], "L": p["L"], "sigma": p["sigma"], "T": T,
                          "top_cell": [top["B"], top["L"], top["sigma"]],
                          "right_cell": (top["B"], top["L"], top["sigma"]) == (p["B"], p["L"], p["sigma"]),
                          "letters": n, "witness_ok": ok, "recovered90": ok and n >= 90})
        rows5 = []
        for d in a5:
            T, _ = C.search(d["ct"], srng)
            rows5.append({"kind": d["kind"], "T": T})
        rec = [r for r in rows4 if r["recovered90"]]
        dmax = max(r["T"] for r in rows5)
        rep.update({"A4": {"plants": 12, "right_cell": sum(r["right_cell"] for r in rows4),
                           "recovered90": len(rec), "rows": rows4},
                    "A5": {"decoys": 12, "max_T": dmax,
                           "max_by_kind": {k: max(r["T"] for r in rows5 if r["kind"] == k)
                                           for k in ("random", "shuffle_of_A4", "two_free_alphabet_autokey")},
                           "rows": rows5}})
        rep["bars"] = {"bar4_A4": sum(r["right_cell"] for r in rows4) >= 9,
                       "bar5_A5": all(r["T"] > dmax for r in rec)}
    rep["wall_s"], rep["cpu_s"] = round(time.time() - t0w, 2), round(time.process_time() - t0c, 2)
    rep["source_sha256"] = {"run114.py": hashlib.sha256((HERE / "run114.py").read_bytes()).hexdigest()}
    a.out.write_text(json.dumps(rep, indent=1) + "\n")
    print("job", a.job, json.dumps(rep["bars"]), json.dumps({k: {x: y for x, y in v.items() if x not in ("rows",)}
                                                           for k, v in rep.items() if k[:1] == "A"})[:900])


if __name__ == "__main__":
    main()
