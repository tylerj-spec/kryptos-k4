#!/usr/bin/env python3
"""R65 contract: no r65 code holds K4 plaintext words or clue positions (R65 is ciphertext-only end to end), and the
runner uses R64's stage-1 parameters unchanged. Run: python3 -I r65/tests/test_contract.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
bad = []
for f in sorted(ROOT.glob("r65/**/*.py")):
    if f.name == "test_contract.py":
        continue
    t = f.read_text()
    for w in ("EASTNORTHEAST", "NORTHEAST", "BERLINCLOCK", "CLUES"):
        if w in t:
            bad.append(f"{f.relative_to(ROOT)}: {w}")
sys.path.insert(0, str(ROOT / "r64/blind"))
import run as r64  # noqa: E402
if r64.P1 != ["15000", "2000", "1", "all", "0", "20000"] or len(r64.load_routes()) != 10:
    bad.append("R64 stage-1 parameters or routes changed")
if bad:
    print("R65 CONTRACT FAIL:", bad)
    sys.exit(1)
print("R65 CONTRACT OK: ciphertext-only code; R64 stage-1 parameters and routes unchanged")
