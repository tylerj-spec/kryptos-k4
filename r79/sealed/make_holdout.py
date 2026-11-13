#!/usr/bin/env python3
"""R79 sealed holdout (never read by r79/blind/run.py). Synthetic only; no K4 data.
  Positives: from each of PT_BOOK_A and PT_BOOK_B, 10 per family (3 misspelled, 2 nonstandard spelling, 5 plain;
             keyword length 2..10) -> 100; plus 2 STRETCH plants (keyword length 11..12) per keyword family per book
             -> 16, reported only.
  Negatives: 12 from each of the seven wrong-family generators (r79/items.py; NEG_PT_BOOK text, NEG_KEY_BOOK keys)
             plus 16 frequency-preserving shuffles of positive ciphertexts -> 100.
Ids H_000..H_215 in a seeded random order. The books are checked against the sha256 values fixed in
r79/PREREGISTRATION.md.
Usage: make_holdout.py PT_BOOK_A PT_BOOK_B NEG_PT_BOOK NEG_KEY_BOOK SEED OUTDIR   (writes blind.tsv, sealed_truth.json)"""
import hashlib
import json
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r79"))
import items as I  # noqa: E402

BOOK_SHA256 = {"pt_a": "10a716c317b48b808226ef511f606156b2ed5f9c182186227d36bf106dee50f2",      # Lord Jim (5658)
               "pt_b": "d9a8268733f96f30a32a39ea625e7c3aa4ded3177eca6bf4f655f06342375904",      # A Room with a View (2641)
               "neg_pt": "84bac88c0735079245db20963e868c14dc70ed1ea29a1ab72f1bfac4408da82a",    # My Antonia (242)
               "neg_key": "d992ab24f47207498659f6cfc80a086ef307ce912c70b73b75e2b6de70ca7ca7"}   # Ethan Frome (4517)


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
