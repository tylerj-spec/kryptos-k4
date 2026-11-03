#!/usr/bin/env python3
"""R61 SEALED plant maker (never read by r61/blind/). Running-key encryption as in R59 (r59/sealed/make_plants.py:
English plaintext window, English key window from a different book, convention drawn from AZ/KRY x VIG/BEAU/VARB), then
the substitution output X is transposed by a route drawn uniformly from r61/routes.txt: CT[j] = X[perm[j]].
Usage: make_plants.py PT_LETTERS KEY_LETTERS N SEED PREFIX OUTDIR    (writes blind.tsv and sealed_truth.json)"""
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
    pt_path, key_path, n, seed, prefix, outdir = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5], Path(sys.argv[6])
    outdir.mkdir(parents=True, exist_ok=True)
    if any(outdir.iterdir()):
        raise SystemExit("refusing to overwrite")
    routes = [(l.split()[0], [int(x) for x in l.split()[2].split(",")]) for l in (ROOT / "r61/routes.txt").read_text().splitlines()]
    pt, ky = Path(pt_path).read_text().strip(), Path(key_path).read_text().strip()
    rng = random.Random(seed)
    convs = [(xn, op) for xn in ("AZ", "KRY") for op in ("VIG", "BEAU", "VARB")]
    used, rows, truth = [], [], {}
    for i in range(n):
        while True:
            o = rng.randrange(len(pt) - N)
            if all(abs(o - u) >= N for u in used):
                break
        used.append(o)
        ko = rng.randrange(len(ky) - N)
        xn, op = convs[rng.randrange(6)]
        rname, perm = routes[rng.randrange(len(routes))]
        p, k = pt[o:o + N], ky[ko:ko + N]
        x = enc(p, k, AZ if xn == "AZ" else KRY, op)
        c = "".join(x[perm[j]] for j in range(N))
        lab = f"{prefix}_{i:02d}"
        rows.append(f"{lab}\t{c}")
        truth[lab] = {"plaintext": p, "key": k, "convention": f"{xn}_{op}", "route": rname, "pt_offset": o, "key_offset": ko}
    (outdir / "blind.tsv").write_text("id\tciphertext\n" + "\n".join(sorted(rows)) + "\n")
    (outdir / "sealed_truth.json").write_text(json.dumps(truth, indent=1) + "\n")
    print(f"wrote {n} plants to {outdir}")


if __name__ == "__main__":
    main()
