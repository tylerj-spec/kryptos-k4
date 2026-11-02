#!/usr/bin/env python3
"""R59 BLIND runner. Reads only an "id<TAB>ciphertext" TSV and the generic models; no K4 clue data exists here.
Runs the frozen solver in parallel shards, merges the results in input order, and writes a freeze manifest.

Usage: python3 -I r59/blind/run.py IN.tsv OUTDIR LM.bin SOLVER_BINARY [PROCS=4]
Writes OUTDIR/RESULTS.jsonl, OUTDIR/logs/, OUTDIR/FROZEN.sha256 (input, results, solver source and binary, models,
protocol). Refuses to overwrite an existing RESULTS.jsonl. Solver parameters are fixed here (R59 pre-registration)."""
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORDS = ROOT / "k4kit/data/word_model_orth.tsv"
PARAMS = ["100000", "2000", "1", "AZ_VIG,AZ_BEAU,KRY_VIG,KRY_BEAU", "3", "20000"]   # BEAM TOPN LAMBDA CONVS POLISH_M WORDS


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    inp, out, lm, solver = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
    procs = int(sys.argv[5]) if len(sys.argv) > 5 else 4
    reg = (ROOT / "r59/blind/LM_SHA256").read_text().split()[0]
    if sha(lm) != reg:
        raise SystemExit("language model sha256 does not match r59/blind/LM_SHA256")
    out.mkdir(parents=True, exist_ok=True)
    if (out / "RESULTS.jsonl").exists():
        raise SystemExit("refusing to overwrite")
    rows = [l for l in inp.read_text().splitlines() if l and not l.startswith("id\t")]
    ids = [r.split("\t")[0] for r in rows]
    if len(set(ids)) != len(ids):
        raise SystemExit("duplicate ids")
    logs = out / "logs"
    logs.mkdir(exist_ok=True)
    shards = [rows[i::procs] for i in range(procs)]
    ps = []
    for i, sh in enumerate(shards):
        if not sh:
            continue
        (logs / f"shard_{i}.tsv").write_text("\n".join(sh) + "\n")
        ps.append(subprocess.Popen([str(solver), str(lm), str(WORDS), str(logs / f"shard_{i}.tsv"),
                                    str(logs / f"shard_{i}.jsonl")] + PARAMS,
                                   stderr=open(logs / f"shard_{i}.log", "w")))
    for p in ps:
        if p.wait() != 0:
            raise SystemExit("solver failed; see logs")
    res = {}
    for i in range(len(shards)):
        f = logs / f"shard_{i}.jsonl"
        if f.exists():
            for line in f.read_text().splitlines():
                if line.strip():
                    rid = line.split('"id":"', 1)[1].split('"', 1)[0]
                    res[rid] = line
    if set(res) != set(ids):
        raise SystemExit("missing results")
    (out / "RESULTS.jsonl").write_text("".join(res[i] + "\n" for i in ids))
    man = [(inp, "input"), (out / "RESULTS.jsonl", "results"), (ROOT / "r59/blind/rk_solve.cpp", "solver_source"),
           (solver, "solver_binary"), (lm, "language_model"), (WORDS, "word_model"), (Path(__file__), "runner"),
           (ROOT / "r59/PREREGISTRATION.md", "protocol")]
    (out / "FROZEN.sha256").write_text("".join(f"{sha(p)}  {lab}  {p.name}\n" for p, lab in man))
    print(f"R59 froze {len(ids)} results in {out}")


if __name__ == "__main__":
    main()
