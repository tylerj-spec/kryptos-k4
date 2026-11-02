#!/usr/bin/env python3
"""R59 SEALED plant maker (never imported or read by r59/blind/). Running-key encryption of English with an English key
from a DIFFERENT book: c = X[x(p) + x(k)] (VIG), X[x(k) - x(p)] (BEAU) or X[x(p) - x(k)] (VARB), X in {AZ, KRY}.
Plaintext windows and key windows are 97 letters at uniformly random offsets (no two plaintext windows overlap);
the convention is drawn uniformly from the 6.

Usage: make_plants.py PT_LETTERS KEY_LETTERS N SEED PREFIX OUTDIR
Writes OUTDIR/blind.tsv (id<TAB>ciphertext only) and OUTDIR/sealed_truth.json; refuses to overwrite."""
import json
import random
import sys
from pathlib import Path

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
N = 97


def enc(p, k, X, op):
    out = []
    for a, b in zip(p, k):
        x, y = X.index(a), X.index(b)
        out.append(X[(x + y) % 26 if op == "VIG" else (y - x) % 26 if op == "BEAU" else (x - y) % 26])
    return "".join(out)


def main():
    pt_path, key_path, n, seed, prefix, outdir = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5], Path(sys.argv[6])
    outdir.mkdir(parents=True, exist_ok=True)
    if any(outdir.iterdir()):
        raise SystemExit("refusing to overwrite")
    pt = Path(pt_path).read_text().strip()
    ky = Path(key_path).read_text().strip()
    rng = random.Random(seed)
    used, rows, truth = [], ["id\tciphertext"], {}
    convs = [(xn, op) for xn in ("AZ", "KRY") for op in ("VIG", "BEAU", "VARB")]
    for i in range(n):
        while True:
            o = rng.randrange(len(pt) - N)
            if all(abs(o - u) >= N for u in used):
                break
        used.append(o)
        ko = rng.randrange(len(ky) - N)
        xn, op = convs[rng.randrange(6)]
        p, k = pt[o:o + N], ky[ko:ko + N]
        c = enc(p, k, AZ if xn == "AZ" else KRY, op)
        lab = f"{prefix}_{i:02d}"
        rows.append(f"{lab}\t{c}")
        truth[lab] = {"plaintext": p, "key": k, "convention": f"{xn}_{op}", "pt_offset": o, "key_offset": ko}
    rows_shuf = [rows[0]] + sorted(rows[1:])
    (outdir / "blind.tsv").write_text("\n".join(rows_shuf) + "\n")
    (outdir / "sealed_truth.json").write_text(json.dumps(truth, indent=1) + "\n")
    print(f"wrote {n} plants to {outdir}")


if __name__ == "__main__":
    main()
