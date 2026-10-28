#!/usr/bin/env python3
"""Prepare P3 original K4 + independently planted/no-clue controls and histogram-matched null."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
exp = ROOT / "r37/p3_keyword_gromark"
if exp.exists():
    raise RuntimeError("P3 experiment directory already exists; use new preregistration")
exp.mkdir(parents=True)
(exp / "k4_ciphertext.txt").write_bytes((ROOT / "k4kit/r32/runs/k4_ciphertext.txt").read_bytes())
(exp / "routes.txt").write_text("ID ID " + ",".join(map(str, range(97))) + "\n")
PY = [sys.executable, "-I"]
subprocess.run(PY + [str(ROOT / "r35/sealed/make_null.py"),
                     str(exp / "k4_ciphertext.txt"), str(exp / "NULL_ct.txt"), "37200"], check=True)
runs = []
bases = (5, 10, 12, 26)
for base in bases:
    spec = f"{base},5"
    key = ["CHAINALPH", spec]
    for tag, ct in [(f"K4_B{base}", "k4_ciphertext.txt"),
                    (f"PLANTA_B{base}", f"PLANTA_B{base}_ct.txt"),
                    (f"PLANTB_B{base}", f"PLANTB_B{base}_ct.txt"),
                    (f"NULL_B{base}", "NULL_ct.txt")]:
        runs.append({"tag": tag, "ct": ct, "routes": "routes.txt", "key": key, "label": f"B{base}KEYED"})
    for tag, template, seed in [(f"PLANTA_B{base}", 2, 37000 + base),
                                (f"PLANTB_B{base}", 3, 37100 + base)]:
        subprocess.run(PY + [str(ROOT / "r35/sealed/make_controls.py"), str(exp),
                             tag, "routes.txt", "CHAINALPH", spec, str(template), str(seed)], check=True)
(exp / "manifest.json").write_text(json.dumps({"workers": 2, "runs": runs}, indent=1) + "\n")
assert len(runs) == 16
print("P3 prepared 4 K4 scans, 8 non-crib plants, 4 null scans")
