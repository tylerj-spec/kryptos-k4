#!/usr/bin/env python3
"""R66 BLIND runner: homophonic substitution (several cipher letters per plaintext letter; a frequency-masking cipher)
combined with one of the 10 frozen R61 routes, CT[j] = X[perm[j]]. Because the homophonic decode f is the same at every
position, "substitute then transpose" and "transpose then substitute" give the same relation, so one search covers both.
Reads only an "id<TAB>ciphertext" TSV, r61/routes.txt and the generic R59 English model; no K4 clue data.
For each ciphertext: undo each of the 10 routes and run r66/blind/hom_solve.cpp (fixed parameters below) on all 10;
answer = the best total (ties: lower route index). Every route's raw output (best + top 8) is kept in work/.
Usage: python3 -I r66/blind/run.py IN.tsv OUTDIR ENGLISH_LM SOLVER [PROCS=4]
Writes OUTDIR/RESULTS.jsonl, FROZEN.sha256, WORK.sha256. A finished ciphertext is reused only if its digest matches."""
import hashlib
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORDS_EN = ROOT / "k4kit/data/word_model_orth.tsv"
ROUTES = ROOT / "r61/routes.txt"
# RESTARTS ITERS LAMBDA SEED CAP AORD T0 T1 (fixed from development; r66/PREREGISTRATION.md)
PARAMS = ["30", "1000000", "1", "66", "4", "6", "5", "0.05"]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def load_routes():
    out = []
    for line in ROUTES.read_text().splitlines():
        name, order, p = line.split()
        perm = [int(x) for x in p.split(",")]
        if order != "S_then_T" or sorted(perm) != list(range(97)):
            raise SystemExit(f"bad route {name}")
        out.append((name, perm))
    if len(out) != 10:
        raise SystemExit("expected the 10 frozen R61 routes")
    return out


def unroute(ct, perm):
    x = [""] * len(ct)
    for j, src in enumerate(perm):
        x[src] = ct[j]
    return "".join(x)


def job(a):
    rid, ct, work, solver, lm, digest, routes = a
    base = work / rid
    done = Path(f"{base}.result.json")
    if done.exists():
        r = json.loads(done.read_text())
        if r.get("digest") == digest:
            return rid, r["result"]
        done.unlink()
    tsv = Path(f"{base}.tsv")
    tsv.write_text("".join(f"{rid}__{i}\t{unroute(ct, p)}\n" for i, (_, p) in enumerate(routes)))
    with open(f"{base}.log", "w") as lg:
        r = subprocess.run([str(solver), str(lm), str(WORDS_EN), str(tsv), f"{base}.jsonl"] + PARAMS, stderr=lg)
    if r.returncode != 0:
        raise RuntimeError(f"solver failed: {base}")
    rows = [json.loads(l) for l in Path(f"{base}.jsonl").read_text().splitlines() if l.strip()]
    st = []
    for x in rows:
        i = int(x["id"].rsplit("__", 1)[1])
        st.append({"route": routes[i][0], "idx": i, **x["best"]})
    if sorted(d["idx"] for d in st) != list(range(10)):
        raise RuntimeError(f"incomplete: {base}")
    st.sort(key=lambda d: (-d["total"], d["idx"]))
    res = {**{k: v for k, v in st[0].items() if k != "idx"},
           "routes": [{k: v for k, v in d.items() if k not in ("idx", "plaintext", "map")} for d in st]}
    done.write_text(json.dumps({"id": rid, "ct": ct, "digest": digest, "result": res}))
    return rid, res


def main():
    inp, out, lm, solver = (Path(a) for a in sys.argv[1:5])
    procs = int(sys.argv[5]) if len(sys.argv) > 5 else 4
    h_lm = sha(lm)
    if h_lm != (ROOT / "r59/blind/LM_SHA256").read_text().split()[0]:
        raise SystemExit("English LM sha256 mismatch")
    hashes = {"lm": h_lm, "routes": sha(ROUTES), "solver": sha(solver), "words": sha(WORDS_EN)}
    routes = load_routes()
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
        jobs.append((rid, ct, work, solver, lm, dig, routes))
    res = {}
    with ThreadPoolExecutor(procs) as ex:
        for rid, r in ex.map(job, jobs):
            res[rid] = r
            print(f"R66 {rid} {r['total']:.2f} {r['route']}", flush=True)
    (out / "RESULTS.jsonl").write_text("".join(json.dumps({"id": i, **res[i]}, separators=(",", ":")) + "\n" for i in ids))
    man = [(inp, "input"), (out / "RESULTS.jsonl", "results"), (ROOT / "r66/blind/hom_solve.cpp", "solver_source"),
           (solver, "solver_binary"), (lm, "english_lm"), (WORDS_EN, "english_words"), (ROUTES, "routes"),
           (Path(__file__), "runner"), (ROOT / "r66/PREREGISTRATION.md", "protocol")]
    (out / "FROZEN.sha256").write_text("".join(f"{sha(p)}  {lab}  {p.name}\n" for p, lab in man))
    (out / "WORK.sha256").write_text("".join(f"{sha(p)}  {p.name}\n" for p in sorted(work.iterdir())))
    print(f"R66 froze {len(ids)} results in {out}")


if __name__ == "__main__":
    main()
