#!/usr/bin/env python3
"""R73b K4 target: r73/sealed/prepare_k4.py unchanged except for a fresh shuffle seed (731300): the unchanged
97-letter K4 ciphertext (sha256-checked) plus 100 frequency-preserving shuffles, none equal to K4.
Usage: prepare_k4_r73b.py OUT.tsv"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prepare_k4 as P  # noqa: E402

P.SEED = 731300

if __name__ == "__main__":
    P.main()
