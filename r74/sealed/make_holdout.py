#!/usr/bin/env python3
"""R74 sealed holdout (never read by r74/blind/run.py). Synthetic only; no K4 data.
  Positives: 120 = 60 from each of PT_BOOK_A, PT_BOOK_B (10 of each with 2 random letters changed), each 97
             consecutive letters from a word start, enciphered under a hidden raw setting drawn uniformly from the
             20,160 (r74/items.py, r74/sandwich.py).
  Negatives: 300 = 40 from each of R71's seven generators on NEG_PT_BOOK with running keys from NEG_KEY_BOOK, plus 20
             frequency-preserving shuffles of positive ciphertexts.
Ids H_000..H_419 in a seeded random order. The four books are checked against the sha256 values fixed in
r74/PREREGISTRATION.md.
Usage: make_holdout.py PT_BOOK_A PT_BOOK_B NEG_PT_BOOK NEG_KEY_BOOK SEED OUTDIR   (writes blind.tsv, sealed_truth.json)"""
import hashlib
import json
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r74"))
import items as I  # noqa: E402

BOOK_SHA256 = {
    "pt_a": "102acac6f05227baf336b9e8f3e61587e4550e21903bde39ac12c3c36a9147d7",      # The Scarlet Pimpernel (60)
    "pt_b": "dfdb09f42cc108aafa9546b051961a0f2b25cecc0cedf3ba29bffb712e9e5e1a",      # King Solomon's Mines (2166)
    "neg_pt": "01822d9242d2d232a61c22ac73bbe36f0282ca7c207e0b3f9a1a9abe37590b28",    # Mysterious Affair at Styles (863)
    "neg_key": "b5bd33ca78ea5edb314d0f543180229819e4617851c00246adf7ef27b4c6ec4d",   # Around the World in 80 Days (103)
}


def main():
    a, b, neg_pt, neg_key, seed, outdir = sys.argv[1:7]
    for role, p in (("pt_a", a), ("pt_b", b), ("neg_pt", neg_pt), ("neg_key", neg_key)):
        if hashlib.sha256(Path(p).read_bytes()).hexdigest() != BOOK_SHA256[role]:
            raise SystemExit(f"{role} book sha256 mismatch")
    seed, outdir = int(seed), Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    if any(outdir.iterdir()):
        raise SystemExit("refusing to overwrite")
    rng = random.Random(seed)
    items = I.build((a, b), 60, 10, neg_pt, neg_key, 40, 20, rng, np.random.default_rng(seed + 1))
    rng.shuffle(items)
    truth, lines = {}, []
    for k, it in enumerate(items):
        rid = f"H_{k:03d}"
        truth[rid] = it
        lines.append(f"{rid}\t{it['ct']}")
    (outdir / "blind.tsv").write_text("id\tciphertext\n" + "\n".join(lines) + "\n")
    (outdir / "sealed_truth.json").write_text(json.dumps(truth, indent=1, sort_keys=True) + "\n")
    print(f"wrote {len(items)} ciphertexts to {outdir}")


if __name__ == "__main__":
    main()
