#!/usr/bin/env python3
"""R36 P2 setup before blind scanning: creates only K4/plant/null ciphertext and sealed plant truth."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
exp = ROOT / "r36/p2_direct_multibase"
if exp.exists():
    raise RuntimeError("R36 P2 experiment already exists; refusing overwrite")
exp.mkdir(parents=True)
orig = ROOT / "k4kit/r32/runs/k4_ciphertext.txt"
(exp / "k4_ciphertext.txt").write_bytes(orig.read_bytes())
(exp / "routes.txt").write_text("ID ID " + ",".join(map(str, range(97))) + "\n")
py = [sys.executable, "-I"]
subprocess.run(py + [str(ROOT / "r35/sealed/make_null.py"), str(exp / "k4_ciphertext.txt"),
                     str(exp / "NULL_ct.txt"), "36404"], check=True)
bases = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 16, 20, 26]
runs = []
for base in bases:
    key = ["CHAINBASE", f"{base},5"]
    label = f"B{base}L5"
    run_specs = [(f"K4_B{base}", "k4_ciphertext.txt"),
                 (f"PLANTA_B{base}", f"PLANTA_B{base}_ct.txt"),
                 (f"PLANTB_B{base}", f"PLANTB_B{base}_ct.txt"),
                 (f"NULL_B{base}", "NULL_ct.txt")]
    for tag, ct in run_specs:
        runs.append({"tag": tag, "ct": ct, "routes": "routes.txt", "key": key, "label": label})
    for tag, template, seed in [(f"PLANTA_B{base}", 2, 36200 + base),
                                (f"PLANTB_B{base}", 3, 36300 + base)]:
        subprocess.run(py + [str(ROOT / "r35/sealed/make_controls.py"), str(exp), tag,
                             "routes.txt", "CHAINBASE", key[1], str(template), str(seed)], check=True)
(exp / "manifest.json").write_text(json.dumps({"workers": 2, "runs": runs}, indent=1) + "\n")
assert len(runs) == 52
print("Prepared", len(runs), "blind runs across", len(bases), "declared bases")
