#!/usr/bin/env python3
"""R61 blind contract: r61/blind/ holds no K4 plaintext words, clue positions or sealed imports, and its Python uses
the standard library only. Run: python3 -I r59/tests/test_contract.py"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BLIND = ROOT / "r61/blind"
FORBIDDEN = ["EASTNORTHEAST", "NORTHEAST", "BERLINCLOCK", "BERLIN", "CLOCK", "sealed", "truth", "CLUES"]
bad = []
for f in sorted(BLIND.iterdir()):
    if f.suffix not in (".py", ".cpp") and f.name != "LM_SHA256":
        continue
    t = f.read_text()
    for w in FORBIDDEN:
        if re.search(w, t, re.IGNORECASE if w.islower() else 0):
            bad.append(f"{f.name}: {w}")
    if f.suffix == ".py":
        for m in re.findall(r"^\s*(?:import|from)\s+([A-Za-z_]+)", t, re.M):
            if m not in {"hashlib", "subprocess", "sys", "pathlib", "json", "random", "re", "concurrent", "routes"}:
                bad.append(f"{f.name}: import {m}")
if bad:
    print("CONTRACT FAIL:", bad)
    sys.exit(1)
print(f"R61 CONTRACT OK: {len(list(BLIND.iterdir()))} blind files, no K4 clue data")
