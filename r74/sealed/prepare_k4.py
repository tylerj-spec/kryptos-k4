#!/usr/bin/env python3
"""R74 K4 target: r73/sealed/prepare_k4.py unchanged except for a fresh seed (740400) and 1,000 shuffles: the
unchanged 97-letter K4 ciphertext (sha256-checked) plus 1,000 frequency-preserving shuffles, none equal to K4.
Usage: prepare_k4.py OUT.tsv"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "r73" / "sealed"))
import prepare_k4 as P  # noqa: E402

P.SEED, P.NNULL = 740400, 1000

if __name__ == "__main__":
    P.main()
