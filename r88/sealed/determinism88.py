#!/usr/bin/env python3
"""R88 determinism check (as R87 Amendment 1): re-run the first N ids of an input TSV (input order, fixed before any
output is seen) OUTSIDE the sandbox with the same runner and 1 process, and require each record to equal the sandbox
record byte for byte. Reads no truth and no published letters.
Usage: determinism88.py LM.bin INPUT.tsv RESULTS.jsonl N OUT.json"""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    lm, tsv, results, n, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), int(sys.argv[4]), Path(sys.argv[5])
    lines = tsv.read_text().splitlines()
    ids = [l.split("\t")[0] for l in lines[1:1 + n]]
    sandbox = {json.loads(l)["id"]: l for l in results.read_text().splitlines() if l}
    with tempfile.TemporaryDirectory() as d:
        sub = Path(d) / "in.tsv"
        sub.write_text("\n".join(lines[:1 + n]) + "\n")
        subprocess.run([sys.executable, "-I", str(ROOT / "r88/blind/run88.py"), lm, str(sub), str(Path(d) / "o"), "1"],
                       check=True)
        rerun = {json.loads(l)["id"]: l for l in (Path(d) / "o/RESULTS.jsonl").read_text().splitlines() if l}
    same = {i: rerun[i] == sandbox[i] for i in ids}
    so = sorted((ROOT / "r88/.build").glob("anneal_*.so"))
    rep = {"ids": ids, "byte_identical": same, "passed": all(same.values()),
           "open_kernel_sha256": [hashlib.sha256(p.read_bytes()).hexdigest() for p in so]}
    out.write_text(json.dumps(rep, indent=1) + "\n")
    print("determinism", "PASSED" if rep["passed"] else "FAILED", sum(same.values()), "of", len(ids))
    sys.exit(0 if rep["passed"] else 1)


if __name__ == "__main__":
    main()
