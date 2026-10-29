#!/usr/bin/env python3
"""Create twelve histogram-preserving shuffled ciphertext nulls and manifest, no plaintext."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "r35/p1_carter_k3_mixed"
exp = ROOT / "r35/p1_null_calibration"
if exp.exists():
    raise RuntimeError("existing P1N study; cannot overwrite")
exp.mkdir(parents=True)
for name in ("k4_ciphertext.txt", "routes.txt", "key.txt"):
    (exp / name).write_bytes((src / name).read_bytes())
runs = []
for i, seed in enumerate(range(35021, 35033)):
    tag = f"NULL_{i:02d}"
    ct = f"{tag}_ct.txt"
    subprocess.run([sys.executable, "-I", str(ROOT / "r35/sealed/make_null.py"),
                    str(exp / "k4_ciphertext.txt"), str(exp / ct), str(seed)], check=True)
    runs.append({"tag": tag, "ct": ct, "routes": "routes.txt",
                 "key": ["TEXT", "key.txt"], "label": "CARTER"})
(exp / "manifest.json").write_text(json.dumps({"workers": 4, "runs": runs}, indent=1) + "\n")
assert len(runs) == 12
print("Prepared 12 independent, fixed-seed histogram-preserving nulls")
