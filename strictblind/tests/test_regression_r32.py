#!/usr/bin/env python3
"""Regression: the harness scanner must reproduce R32's frozen K4_F1_G5 top 100 byte for byte (about 10 s)."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SB = Path(__file__).resolve().parents[1]
R32 = SB.parent / "k4kit/r32/runs"
with tempfile.TemporaryDirectory() as td:
    exp = Path(td)
    subprocess.run([sys.executable, "-I", str(SB / "blind/routes.py"), "r27", str(exp / "routes.txt")], check=True, capture_output=True)
    shutil.copy(R32 / "k4_ciphertext.txt", exp / "k4.txt")
    (exp / "manifest.json").write_text(json.dumps({"runs": [{"tag": "K4_F1_G5", "ct": "k4.txt", "routes": "routes.txt",
                                                              "key": ["CHAIN", "5"], "label": "G5"}]}))
    subprocess.run([sys.executable, "-I", str(SB / "blind/experiment.py"), str(exp)], check=True, capture_output=True)
    same = (exp / "out/K4_F1_G5.tsv").read_bytes() == (R32 / "K4_F1_G5.tsv").read_bytes()
    print("REGRESSION OK: identical to R32 K4_F1_G5.tsv" if same else "REGRESSION FAILED")
    sys.exit(0 if same else 1)
