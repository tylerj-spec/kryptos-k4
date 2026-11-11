#!/usr/bin/env python3
"""R76 sealed holdout (never read by r75/blind/run.py). Synthetic only; no K4 data.
  Positives: 60 = 10 per sub-family (B1, B2, B3) from each of PT_BOOK_A and PT_BOOK_B, 6 of each book
             with 2 random letters changed; each is 97 consecutive letters from a word start, enciphered by the
             explicit encryptor under a hidden setting drawn uniformly from its sub-family (r76/items.py).
  Negatives: 100 = 12 from each of R71's seven wrong-family generators (NEG_PT_BOOK text, NEG_KEY_BOOK keys) plus 16
             frequency-preserving shuffles of positive ciphertexts.
Ids H_000..H_159 in a seeded random order. The four books are checked against the sha256 values fixed in
r76/PREREGISTRATION.md.
Usage: make_holdout.py PT_BOOK_A PT_BOOK_B NEG_PT_BOOK NEG_KEY_BOOK SEED OUTDIR   (writes blind.tsv, sealed_truth.json)"""
import hashlib
import json
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r75"))
sys.path.insert(0, str(ROOT / "r76"))
import items as I  # noqa: E402

BOOK_SHA256 = {"pt_a": "19007f23f185050fb09ec505260cd14fe0ff7286b11f69f2fd49515da8ff84f2",      # The Woman in White (583)
               "pt_b": "940b404710fc5cc8b3e9b4d19f91c12d8b1657f960eda9dea65a049b3ca05220",      # The Sign of the Four (2097)
               "neg_pt": "567a5212f125554be4e0d882a986e5e0bf6bda45e60d51163ff9e1bd2501fbfb",    # The Invisible Man (5230)
               "neg_key": "2f9486eb4776d23baf1064eebb73bb0093b808b13e10516e81e20d1dbe4909c9"}   # The Jungle Book (236)


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
    items = I.build((a, b), 10, 6, neg_pt, neg_key, 12, 16, rng, np.random.default_rng(seed + 1))
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
