#!/usr/bin/env python3
"""R63 SEALED plant maker (never read by r63/blind/). English plaintext window (97 letters, non-overlapping) encrypted
with a NON-English running key, convention uniform over AZ/KRY x VIG/BEAU/VARB:
  CLOCK  : key = a random sequence of names from r63/data/clock_names.txt (uniform, repeats allowed), starting at a
           random letter inside the first name;
  GERMAN : key = a 97-letter window of German prose (GERMAN_LETTERS file).
Half the plants use each key type (alternating, then shuffled by id).
Usage: make_plants.py PT_LETTERS GERMAN_LETTERS N SEED PREFIX OUTDIR"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
N = 97


def enc(p, k, X, op):
    return "".join(X[(X.index(a) + X.index(b)) % 26 if op == "VIG" else (X.index(b) - X.index(a)) % 26 if op == "BEAU"
                     else (X.index(a) - X.index(b)) % 26] for a, b in zip(p, k))


def main():
    pt_path, de_path, n, seed, prefix, outdir = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5], Path(sys.argv[6])
    outdir.mkdir(parents=True, exist_ok=True)
    if any(outdir.iterdir()):
        raise SystemExit("refusing to overwrite")
    pt, de = Path(pt_path).read_text().strip(), Path(de_path).read_text().strip()
    names = (ROOT / "r63/data/clock_names.txt").read_text().split()
    rng = random.Random(seed)
    convs = [(xn, op) for xn in ("AZ", "KRY") for op in ("VIG", "BEAU", "VARB")]
    used, rows, truth = [], [], {}
    for i in range(n):
        while True:
            o = rng.randrange(len(pt) - N)
            if all(abs(o - u) >= N for u in used):
                break
        used.append(o)
        kind = "CLOCK" if i % 2 == 0 else "GERMAN"
        if kind == "CLOCK":
            seq = ""
            while len(seq) < N + 20:
                seq += names[rng.randrange(len(names))]
            st = rng.randrange(12)   # start up to 12 letters into the sequence (often inside the first name)
            k = seq[st:st + N]
        else:
            ko = rng.randrange(len(de) - N)
            k = de[ko:ko + N]
        xn, op = convs[rng.randrange(6)]
        p = pt[o:o + N]
        c = enc(p, k, AZ if xn == "AZ" else KRY, op)
        lab = f"{prefix}_{i:02d}"
        rows.append(f"{lab}\t{c}")
        truth[lab] = {"plaintext": p, "key": k, "key_model": kind, "convention": f"{xn}_{op}", "pt_offset": o}
    (outdir / "blind.tsv").write_text("id\tciphertext\n" + "\n".join(sorted(rows)) + "\n")
    (outdir / "sealed_truth.json").write_text(json.dumps(truth, indent=1) + "\n")
    print(f"wrote {n} plants to {outdir}")


if __name__ == "__main__":
    main()
