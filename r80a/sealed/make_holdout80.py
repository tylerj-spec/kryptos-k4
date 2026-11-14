#!/usr/bin/env python3
"""R80a sealed holdout (never read by r80a/blind/run.py). Synthetic only; no K4 data.
  Positives: from each of PT_BOOK_A and PT_BOOK_B, 10 per family (3 misspelled, 2 nonstandard spelling, 5 plain; free
             key 1..10 letters; L1/L2 listed key a word of 3..12 letters, X1/X2 a key of 1..3 letters) -> 80; plus
             2 STRETCH plants (free key 11..12) per family per book -> 16, reported only.
  Negatives: 12 from each of R79's seven wrong-family generators (NEG_PT_BOOK text, NEG_KEY_BOOK keys), 8 NEG_TWO_RANDOM
             (two stages, both keys random 4..12 letters, from NEG_PT_BOOK) and 8 frequency-preserving shuffles of
             positive ciphertexts -> 100.
Ids H_000..H_195 in a seeded random order. The books are checked against the sha256 values fixed in
r80a/PREREGISTRATION.md.
Usage: make_holdout80.py PT_BOOK_A PT_BOOK_B NEG_PT_BOOK NEG_KEY_BOOK SEED OUTDIR   (writes blind.tsv, sealed_truth.json)"""
import hashlib
import json
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r80a"))
import items80 as I  # noqa: E402

BOOK_SHA256 = {"pt_a": "4e134e8386b982db9926144bf9f52d3c337041d0b0f058c5f65ae9bbcb5c289d",      # The Age of Innocence (541)
               "pt_b": "47fd003249cf6dd833476d089cccddc7997349751dfe0183809c18a4baa2128f",      # The Moonstone (155)
               "neg_pt": "94aa2a92a06287230c50e1ae9848fe920bf4f0f4a33467424a1890d985933795",    # Kidnapped (421)
               "neg_key": "262d60db1fe905a8678ff65a71c4af77995455af963d9f30b44493dd4f93ccd4"}   # The Prisoner of Zenda (95)


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
    items = pos + I.negatives(neg_pt, neg_key, 12, np.random.default_rng(seed + 1), 8, rng) + \
        I.shuffles([x for x in pos if x["kind"] != "STRETCH"], 8, rng)
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
