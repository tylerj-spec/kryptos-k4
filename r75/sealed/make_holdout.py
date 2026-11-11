#!/usr/bin/env python3
"""R75 sealed holdout (never read by r75/blind/run.py). Synthetic only; no K4 data.
  Positives: 60 = 5 per sub-family (F1A, F1B, F2A, F2B, F3A, F3B) from each of PT_BOOK_A and PT_BOOK_B, 6 of each book
             with 2 random letters changed; each is 97 consecutive letters from a word start, enciphered by the
             explicit encryptor under a hidden setting drawn uniformly from its sub-family (r75/items.py).
  Negatives: 100 = 12 from each of R71's seven wrong-family generators (NEG_PT_BOOK text, NEG_KEY_BOOK keys) plus 16
             frequency-preserving shuffles of positive ciphertexts.
Ids H_000..H_159 in a seeded random order. The four books are checked against the sha256 values fixed in
r75/PREREGISTRATION.md.
Usage: make_holdout.py PT_BOOK_A PT_BOOK_B NEG_PT_BOOK NEG_KEY_BOOK SEED OUTDIR   (writes blind.tsv, sealed_truth.json)"""
import hashlib
import json
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r75"))
import items as I  # noqa: E402

BOOK_SHA256 = {"pt_a": "f6b39bd6c79270d117e0a4e9a8814628e4185d356a0a6d6bd7116e74c389b7d5",      # The Lost World (139)
               "pt_b": "8947f71d33499484c6d438a02df0146e037eb1052846b33e9822ff8b1536c5fa",      # Three Men in a Boat (308)
               "neg_pt": "f875d0ae7c153741c516d4db2f3c1686f8dd79e341ea27dbc2167178a09cd587",    # The Wind in the Willows (289)
               "neg_key": "85a20ed2f9b6dc6161a2c0757f0bf34a9728f7e7e2962e890837089d16c26617"}


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
    items = I.build((a, b), 5, 6, neg_pt, neg_key, 12, 16, rng, np.random.default_rng(seed + 1))
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
