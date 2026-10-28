#!/usr/bin/env python3
"""Seeded permutation null with K4's letter histogram; no plaintext or clue data."""
import random
import sys
from pathlib import Path

src, dst, seed = sys.argv[1:4]
s = list("".join(c for c in Path(src).read_text().upper() if "A" <= c <= "Z"))
if len(s) != 97:
    raise ValueError("expected 97 ciphertext letters")
rng = random.Random(int(seed))
rng.shuffle(s)
Path(dst).write_text("".join(s) + "\n")
print("Null permutation created; preserves original ciphertext letter counts")
