#!/usr/bin/env python3
"""R59 SEALED: frequency-preserving shuffles of planted ciphertexts (null controls for the holdout gate).
Usage: make_nulls.py BLIND.tsv SEED OUT.tsv   (one shuffle per input row; ids NULL_xx)"""
import random
import sys
from pathlib import Path


def main():
    rows = [l.split("\t") for l in Path(sys.argv[1]).read_text().splitlines()[1:] if l]
    rng = random.Random(int(sys.argv[2]))
    out = ["id\tciphertext"]
    for i, (_, ct) in enumerate(rows):
        c = list(ct)
        rng.shuffle(c)
        out.append(f"NULL_{i:02d}\t{''.join(c)}")
    p = Path(sys.argv[3])
    if p.exists():
        raise SystemExit("refusing to overwrite")
    p.write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
