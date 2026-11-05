#!/usr/bin/env python3
"""R68 BLIND runner: classic keyed ciphers whose key advances along a path through the carved text.
Reads only an "id<TAB>ciphertext" TSV, r61/routes.txt and the generic R59 English model; no K4 clue data.
Paths: carved order (ID) and the 10 frozen R61 routes; for a path perm, the path-order text is Y with CT[j] = Y[perm[j]].
Two models per route (ID needs only one):
  M1  substitute then transpose (R61/R64): plaintext order = path order;
  M2  position-aligned: carved letter j is enciphered in place at path step perm[j] (plaintext stays in carved order).
For each ciphertext, all 21 (path, model) rows go to r68/blind/keyed_solve.cpp (families PER p<=20, GRO all primers,
CTAK/PTAK lags <= 24; 12 conventions; fixed parameters below). Per family the answer is the best total over rows,
conventions and parameters; every (row, family, convention) best is kept raw in work/.
Usage: python3 -I r68/blind/run.py IN.tsv OUTDIR ENGLISH_LM SOLVER [PROCS=4]"""
import hashlib
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORDS = ROOT / "k4kit/data/word_model_orth.tsv"
ROUTES = ROOT / "r61/routes.txt"
PARAMS = ["20", "24", "20", "68"]   # PMAX LMAX RESTARTS SEED (fixed from development; r68/PREREGISTRATION.md)
FAMILIES = ("PER", "GRO", "CTAK", "PTAK")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def load_paths():
    out = [("ID", list(range(97)))]
    for line in ROUTES.read_text().splitlines():
        name, order, p = line.split()
        perm = [int(x) for x in p.split(",")]
        if order != "S_then_T" or sorted(perm) != list(range(97)):
            raise SystemExit(f"bad route {name}")
        out.append((name, perm))
    if len(out) != 11:
        raise SystemExit("expected ID + the 10 frozen R61 routes")
    return out


def rows_for(rid, ct, paths):
    out = []
    for i, (name, perm) in enumerate(paths):
        y = [""] * 97
        for j, t in enumerate(perm):
            y[t] = ct[j]
        y = "".join(y)
        for model in (("M1",) if name == "ID" else ("M1", "M2")):
            r = "I" if model == "M1" else ",".join(map(str, perm))
            out.append((f"{rid}__{i}__{model}", y, r))
    return out


def job(a):
    rid, ct, work, solver, lm, digest, paths = a
    base = work / rid
    done = Path(f"{base}.result.json")
    if done.exists():
        r = json.loads(done.read_text())
        if r.get("digest") == digest:
            return rid, r["result"]
        done.unlink()
    tsv = Path(f"{base}.tsv")
    tsv.write_text("".join(f"{a}\t{b}\t{c}\n" for a, b, c in rows_for(rid, ct, paths)))
    with open(f"{base}.log", "w") as lg:
        p = subprocess.run([str(solver), str(lm), str(WORDS), str(tsv), f"{base}.jsonl"] + PARAMS, stderr=lg)
    if p.returncode != 0:
        raise RuntimeError(f"solver failed: {base}")
    raw = [json.loads(l) for l in Path(f"{base}.jsonl").read_text().splitlines() if l.strip()]
    if len(raw) != 21:
        raise RuntimeError(f"incomplete rows: {base}")
    fam_best = {}
    for r in raw:
        _, pi, model = r["id"].rsplit("__", 2)
        for b in r["by_family_convention"]:
            rec = {"path": paths[int(pi)][0], "model": model, **b}
            if b["family"] not in fam_best or b["total"] > fam_best[b["family"]]["total"]:
                fam_best[b["family"]] = rec
    if set(fam_best) != set(FAMILIES):
        raise RuntimeError(f"missing families: {base}")
    best = max(fam_best.values(), key=lambda d: d["total"])
    res = {"best": best, "families": fam_best}
    done.write_text(json.dumps({"id": rid, "ct": ct, "digest": digest, "result": res}))
    return rid, res


def main():
    inp, out, lm, solver = (Path(a) for a in sys.argv[1:5])
    procs = int(sys.argv[5]) if len(sys.argv) > 5 else 4
    h_lm = sha(lm)
    if h_lm != (ROOT / "r59/blind/LM_SHA256").read_text().split()[0]:
        raise SystemExit("English LM sha256 mismatch")
    paths = load_paths()
    hashes = {"lm": h_lm, "routes": sha(ROUTES), "solver": sha(solver), "words": sha(WORDS)}
    out.mkdir(parents=True, exist_ok=True)
    if (out / "RESULTS.jsonl").exists():
        raise SystemExit("refusing to overwrite")
    work = out / "work"
    work.mkdir(exist_ok=True)
    rows = [l.split("\t") for l in inp.read_text().splitlines() if l and not l.startswith("id\t")]
    ids = [r[0] for r in rows]
    if len(set(ids)) != len(ids):
        raise SystemExit("duplicate ids")
    jobs = []
    for rid, ct in rows:
        if len(ct) != 97 or not ct.isalpha() or not ct.isupper():
            raise SystemExit(f"bad ciphertext {rid}")
        dig = hashlib.sha256(json.dumps({"ct": ct, "hashes": hashes, "params": PARAMS}, sort_keys=True).encode()).hexdigest()
        jobs.append((rid, ct, work, solver, lm, dig, paths))
    res = {}
    with ThreadPoolExecutor(procs) as ex:
        for rid, r in ex.map(job, jobs):
            res[rid] = r
            b = r["best"]
            print(f"R68 {rid} {b['total']:.2f} {b['family']} {b['path']} {b['model']} {b['convention']} {b['param']}", flush=True)
    (out / "RESULTS.jsonl").write_text("".join(json.dumps({"id": i, **res[i]}, separators=(",", ":")) + "\n" for i in ids))
    man = [(inp, "input"), (out / "RESULTS.jsonl", "results"), (ROOT / "r68/blind/keyed_solve.cpp", "solver_source"),
           (solver, "solver_binary"), (lm, "english_lm"), (WORDS, "english_words"), (ROUTES, "routes"),
           (Path(__file__), "runner"), (ROOT / "r68/PREREGISTRATION.md", "protocol")]
    (out / "FROZEN.sha256").write_text("".join(f"{sha(p)}  {lab}  {p.name}\n" for p, lab in man))
    (out / "WORK.sha256").write_text("".join(f"{sha(p)}  {p.name}\n" for p in sorted(work.iterdir())))
    print(f"R68 froze {len(ids)} results in {out}")


if __name__ == "__main__":
    main()
