#!/usr/bin/env python3
"""R81a sealed holdout (never read by r81a/blind/run.py). Synthetic only; no K4 data.
  Positives: from each of PT_BOOK_A and PT_BOOK_B, 10 per family (3 misspelled, 2 nonstandard spelling, 5 plain;
             keyword length 2..10) -> 80; plus 2 STRETCH plants (keyword length 11..12) per family per book -> 16,
             reported only.
  Negatives: 12 from each of the seven wrong-family generators (r79/items.py; NEG_PT_BOOK text, NEG_KEY_BOOK keys)
             plus 16 frequency-preserving shuffles of positive ciphertexts -> 100.
Ids H_000..H_195 in a seeded random order. The books are checked against the sha256 values fixed in
r81a/PREREGISTRATION.md.
Usage: make_holdout.py PT_BOOK_A PT_BOOK_B NEG_PT_BOOK NEG_KEY_BOOK SEED OUTDIR   (writes blind.tsv, sealed_truth.json)"""
import hashlib
import json
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r79"))
sys.path.insert(0, str(ROOT / "r81a"))
import items81 as I  # noqa: E402

BOOK_SHA256 = {"pt_a": "46b39559666acdce85bfbea4d98df3b3db0e044bcbacd22f4a55ba86be76a189",      # Silas Marner (550)
               "pt_b": "b68e3483a11b04bc224f3347f15cda4629a5c32f9a9cc8595abcf8909a57f292",      # Main Street (543)
               "neg_pt": "5d5bd30cb79d2f9302d99f822cc342f268dcd327d800e0ba3790596b5ef09648",    # The Secret Garden (113)
               "neg_key": "4fcd53a85c65ffb7ebbac5611d8a2db9dcc5ddeee35712308e8e84c1a6238685"}   # Howards End (2946)


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
    pos = I.positives(a, 10, 3, 2, 2, rng) + I.positives(b, 10, 3, 2, 2, rng)
    items = pos + I.negatives(neg_pt, neg_key, 12, np.random.default_rng(seed + 1)) + \
        I.shuffles([x for x in pos if x["kind"] != "STRETCH"], 16, rng)
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
