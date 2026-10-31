#!/usr/bin/env python3
"""Commit-ready manifest of the BLIND raw bytes, before evaluator is run."""
import hashlib
import json
import sys
from pathlib import Path


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    if len(sys.argv) != 5:
        raise SystemExit("usage: make_manifest.py INPUT.ndjson CANDIDATES.ndjson SOLVER.py MANIFEST.json")
    incoming, candidates, solver, manifest = map(Path, sys.argv[1:])
    if not incoming.is_file() or not candidates.is_file() or not solver.is_file():
        raise ValueError("missing blinded input, outputs, or source")
    if manifest.exists():
        raise FileExistsError("cannot overwrite a frozen record")
    payload = {
        "contract": "r53-owner-hard-blind-before-validation",
        "input_sha256": sha(incoming),
        "solver_sha256": sha(solver),
        "candidates_sha256": sha(candidates),
        "candidate_file": candidates.name,
        "status": "BLIND_FROZEN_NO_VALIDATION_YET",
        "warning": "Caesar baseline is only an input-isolation smoke test; it is not a K4 solution",
    }
    manifest.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print("R53 output frozen SHA256", payload["candidates_sha256"])


if __name__ == "__main__":
    main()
