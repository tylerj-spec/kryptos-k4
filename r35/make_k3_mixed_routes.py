#!/usr/bin/env python3
"""Clue-free P1 route maker: K3-shaped stage widths (23-25 then 7-9) with opposite directions."""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1] / "strictblind/blind/routes.py"
spec = importlib.util.spec_from_file_location("routes", HERE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
names = []
for w1 in (23, 24, 25):
    for w2 in (7, 8, 9):
        for directions in ("CW-CCW", "CCW-CW"):
            for sense in ("fwd", "inv"):
                name = f"R{w1}x{w2}/{directions}/{sense}"
                names.append((name, mod.mixed_rotation(name)))
if len(names) != 36:
    raise RuntimeError("expected 36 geometric routes")
out = Path(sys.argv[1])
assert mod.write(out, mod.both(names)) == 72
print("P1 routes: 72 distinct named route-orders")
