#!/usr/bin/env python3
"""R90 K4 target: r73/sealed/prepare_k4.py unchanged except for a fresh seed (900400) and 200 shuffles: the unchanged 97-letter K4
ciphertext (sha256-checked) plus 200 frequency-preserving shuffles, none equal to K4. Run only after the gate is GO.
Usage: prepare_k4.py OUT.tsv"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "r73" / "sealed"))
import prepare_k4 as P  # noqa: E402

P.SEED, P.NNULL = 900400, 200

if __name__ == "__main__":
    P.main()
