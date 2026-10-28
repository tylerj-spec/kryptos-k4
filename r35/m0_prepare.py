#!/usr/bin/env python3
"""Prepare pre-registered R35 M0 inputs, no K4 clue access."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

repo = Path(__file__).resolve().parents[1]
exp = repo / "r35" / "m0"
if exp.exists():
    raise RuntimeError("M0 experiment already exists: refuse overwrite")
exp.mkdir(parents=True)
shutil.copyfile(repo / "r34/k4_ciphertext.txt", exp / "k4_ciphertext.txt")
shutil.copyfile(repo / "k4kit/data/k1k3_plaintext.txt", exp / "k1k3_plaintext.txt")
subprocess.run([sys.executable, "-I", str(repo / "strictblind/blind/routes.py"),
                "rot-mixed", "4", "28", str(exp / "routes.txt")], check=True)
runs = [{"tag":"K4_M0", "ct":"k4_ciphertext.txt", "routes":"routes.txt",
         "key":["TEXT", "k1k3_plaintext.txt"], "label":"K1K3"}]
for i, seed in enumerate((35001, 35002)):
    tag = f"PLANT_{i}"
    subprocess.run([sys.executable, "-I", str(repo / "strictblind/sealed/make_plants.py"),
                    str(exp), tag, "routes.txt", "TEXT", "k1k3_plaintext.txt",
                    str(i), str(seed)], check=True)
    runs.append({"tag":tag, "ct": f"{tag}_ct.txt", "routes":"routes.txt",
                 "key":["TEXT", "k1k3_plaintext.txt"], "label":"K1K3"})
(exp / "manifest.json").write_text(json.dumps({"workers":4, "runs":runs}, indent=2)+"\n")
print("M0 prepared: 5000 mixed rotation route-orders, 3 ciphertexts")
