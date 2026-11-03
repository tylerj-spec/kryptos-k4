#!/usr/bin/env python3
"""R61 BLIND pipeline: running key from an unknown English text, SUBSTITUTED THEN TRANSPOSED by one of the 10 routes in
r61/routes.txt (CT[j] = X[perm[j]]). Reads only an "id<TAB>ciphertext" TSV, the routes and the generic models.
For each ciphertext:
  stage 1  undo every route (X[perm[j]] = CT[j]) and run the frozen R59 solver r59/blind/rk_solve.cpp WITHOUT polish
           (beam B1, TOPN 2000, LAMBDA 1, conventions AZ/KRY x VIG/BEAU);
  stage 2  the TOP_ROUTES best routes by stage-1 total are re-solved with the full R59 parameters
           (beam 100000, TOPN 2000, LAMBDA 1, POLISH_M 3, POLISH_WORDS 20000);
  answer   the best stage-2 total (route, convention, plaintext and key in plaintext order).
Usage: python3 -I r61/blind/run.py IN.tsv OUTDIR LM.bin SOLVER [PROCS=4] [B1=30000] [TOP_ROUTES=2]
Writes OUTDIR/RESULTS.jsonl, OUTDIR/work/, OUTDIR/FROZEN.sha256. Refuses to overwrite RESULTS.jsonl. Finished
ciphertexts are cached in work/ (id + ciphertext checked), so an interrupted run resumes where it stopped."""
import hashlib
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORDS = ROOT / "k4kit/data/word_model_orth.tsv"
CONVS = "AZ_VIG,AZ_BEAU,KRY_VIG,KRY_BEAU"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def load_routes():
    out = []
    for line in (ROOT / "r61/routes.txt").read_text().splitlines():
        name, order, p = line.split()
        assert order == "S_then_T"
        out.append((name, [int(x) for x in p.split(",")]))
    return out


def unroute(ct, perm):
    x = [""] * len(ct)
    for j, src in enumerate(perm):
        x[src] = ct[j]
    return "".join(x)


def solve(solver, lm, tsv, out, params, log):
    with open(log, "w") as lg:
        r = subprocess.run([str(solver), str(lm), str(WORDS), str(tsv), str(out)] + params, stderr=lg)
    if r.returncode != 0:
        raise RuntimeError(f"solver failed: {log}")
    return [json.loads(l) for l in Path(out).read_text().splitlines() if l.strip()]


def one(args):
    rid, ct, work, solver, lm, b1, top = args
    routes = load_routes()
    safe = rid.replace("/", "_")
    done = work / f"{safe}.result.json"
    if done.exists():   # resume after an interrupted run (the solver is deterministic, so this changes nothing)
        r = json.loads(done.read_text())
        if r.get("id") == rid and r.get("ct") == ct:
            return rid, r["result"]
    s1 = work / f"{safe}.s1.tsv"
    s1.write_text("".join(f"{rid}__{i}\t{unroute(ct, p)}\n" for i, (_, p) in enumerate(routes)))
    r1 = solve(solver, lm, s1, work / f"{safe}.s1.jsonl", [str(b1), "2000", "1", CONVS, "0", "20000"], work / f"{safe}.s1.log")
    st1 = sorted(({"route": routes[int(r["id"].rsplit("__", 1)[1])][0], "idx": int(r["id"].rsplit("__", 1)[1]),
                   "total": r["best"]["total"], "convention": r["best"]["convention"]} for r in r1), key=lambda d: -d["total"])
    pick = st1[:top]
    s2 = work / f"{safe}.s2.tsv"
    s2.write_text("".join(f"{rid}__{d['idx']}\t{unroute(ct, routes[d['idx']][1])}\n" for d in pick))
    r2 = solve(solver, lm, s2, work / f"{safe}.s2.jsonl", ["100000", "2000", "1", CONVS, "3", "20000"], work / f"{safe}.s2.log")
    st2 = []
    for r in r2:
        i = int(r["id"].rsplit("__", 1)[1])
        st2.append({"route": routes[i][0], **r["best"]})
    st2.sort(key=lambda d: -d["total"])
    result = {"id": rid, "best": st2[0], "stage2": st2, "stage1": [{k: v for k, v in d.items() if k != "idx"} for d in st1]}
    done.write_text(json.dumps({"id": rid, "ct": ct, "result": result}))
    return rid, result


def main():
    inp, out, lm, solver = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
    procs = int(sys.argv[5]) if len(sys.argv) > 5 else 4
    b1 = int(sys.argv[6]) if len(sys.argv) > 6 else 30000
    top = int(sys.argv[7]) if len(sys.argv) > 7 else 2
    reg = (ROOT / "r59/blind/LM_SHA256").read_text().split()[0]
    if sha(lm) != reg:
        raise SystemExit("language model sha256 does not match r59/blind/LM_SHA256")
    out.mkdir(parents=True, exist_ok=True)
    if (out / "RESULTS.jsonl").exists():
        raise SystemExit("refusing to overwrite")
    work = out / "work"
    work.mkdir(exist_ok=True)
    rows = [l.split("\t") for l in inp.read_text().splitlines() if l and not l.startswith("id\t")]
    ids = [r[0] for r in rows]
    if len(set(ids)) != len(ids):
        raise SystemExit("duplicate ids")
    res = {}
    with ThreadPoolExecutor(procs) as ex:
        for rid, r in ex.map(one, [(rid, ct, work, solver, lm, b1, top) for rid, ct in rows]):
            res[rid] = r
            print(f"R61 {rid} best {r['best']['total']:.2f} {r['best']['route']} {r['best']['convention']}", flush=True)
    (out / "RESULTS.jsonl").write_text("".join(json.dumps(res[i], separators=(",", ":")) + "\n" for i in ids))
    man = [(inp, "input"), (out / "RESULTS.jsonl", "results"), (ROOT / "r59/blind/rk_solve.cpp", "solver_source"),
           (solver, "solver_binary"), (lm, "language_model"), (WORDS, "word_model"), (Path(__file__), "runner"),
           (ROOT / "r61/routes.txt", "routes"), (ROOT / "r61/PREREGISTRATION.md", "protocol")]
    (out / "FROZEN.sha256").write_text("".join(f"{sha(p)}  {lab}  {p.name}\n" for p, lab in man))
    print(f"R61 froze {len(ids)} results in {out} (B1={b1}, TOP_ROUTES={top})")


if __name__ == "__main__":
    main()
