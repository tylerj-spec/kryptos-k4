#!/usr/bin/env python3
"""R39 BLIND runner; reads ONLY manifest tags, ciphertexts, ranker source and output scores."""
import csv
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
exp = Path(sys.argv[1]).resolve()
if (exp / "FROZEN.sha256").exists():
    raise RuntimeError("R39 experiment already frozen")
man = json.loads((exp / "manifest.json").read_text())
assert len(man["runs"]) == 31
assert "TRUTH" not in json.dumps(man).upper() and "PLAINTEXT" not in json.dumps(man).upper()
tags = [r["tag"] for r in man["runs"]]
assert len(tags) == len(set(tags))
out = exp / "out"
if out.exists() and any(out.iterdir()):
    raise RuntimeError("R39 output directory not empty")
out.mkdir(exist_ok=True)
exe = out / "rank_keys"
subprocess.run(["g++", "-std=c++17", "-O3", "-march=native", str(HERE / "rank_keys.cpp"),
                "-o", str(exe)], check=True)
for run in man["runs"]:
    tag, name = run["tag"], run["ct"]
    if not tag.replace("_", "").isalnum():
        raise ValueError("unsafe run tag")
    p = (exp / name).resolve()
    if not p.is_relative_to(exp) or not p.is_file():
        raise ValueError("unsafe ciphertext path")
    scores = out / f"{tag}.scores.f64"
    top = out / f"{tag}_top.tsv"
    result = subprocess.run([str(exe), str(p), str(scores), str(top)],
                            capture_output=True, text=True, check=True)
    print(tag, result.stderr.strip(), flush=True)
files = [exp / "manifest.json", HERE / "run.py", HERE / "rank_keys.cpp", exe]
files += [exp / r["ct"] for r in man["runs"]]
files += sorted(out.glob("*.scores.f64")) + sorted(out.glob("*_top.tsv"))
lines = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {os.path.relpath(p.resolve(), exp)}"
         for p in dict.fromkeys(files)]
(exp / "FROZEN.sha256").write_text("\n".join(lines) + "\n")
print("R39 BLIND FREEZE:", len(lines), "files")
