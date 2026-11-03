#!/usr/bin/env python3
"""R63 blind contract: r63/blind/ code holds no K4 plaintext words, clue positions or sealed imports.
(The key-model vocabulary r63/data/clock_names.txt legitimately contains BERLIN, a city on the World Clock; it is a
KEY-side model only and is not checked here.) Run: python3 -I r63/tests/test_contract.py"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
bad = []
for f in sorted((ROOT / "r63/blind").iterdir()):
    if f.suffix not in (".py", ".cpp"):
        continue
    t = f.read_text()
    for w in ("EASTNORTHEAST", "NORTHEAST", "BERLINCLOCK", "BERLIN"):
        if w in t:
            bad.append(f"{f.name}: {w}")
    for w in ("sealed", "truth"):
        if re.search(w, t, re.I):
            bad.append(f"{f.name}: {w}")
if bad:
    print("CONTRACT FAIL:", bad)
    sys.exit(1)
print("R63 CONTRACT OK: blind code holds no K4 clue data")
