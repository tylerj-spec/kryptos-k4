#!/usr/bin/env python3
"""R68 SEALED plant maker (never read by r68/blind/). English 97-letter windows (non-overlapping) encrypted with one of
the four keyed families, a random convention (12), a random path (ID or one of the 10 R61 routes) and, for routes, a
random model (M1 or M2). Families are assigned in a seeded random order, N/4 each.
  PER  period p uniform 2..20, random shift letters      GRO  random 5-digit primer
  CTAK lag L uniform 1..24, random primer                PTAK lag L uniform 1..24, random primer
Usage: make_plants.py PT_LETTERS N SEED PREFIX OUTDIR   (writes blind.tsv and sealed_truth.json)"""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import AZ, CONVS, N, encrypt_path, paths, to_carved, unlayout, witness_ok  # noqa: E402

FAMS = ["PER", "GRO", "CTAK", "PTAK"]


def main():
    pt_p, n, seed, prefix, outdir = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], Path(sys.argv[5])
    outdir.mkdir(parents=True, exist_ok=True)
    if any(outdir.iterdir()):
        raise SystemExit("refusing to overwrite")
    if n % 4:
        raise SystemExit("N must be divisible by 4")
    pt = Path(pt_p).read_text().strip()
    P = paths()
    names = list(P)
    rng = random.Random(seed)
    fams = FAMS * (n // 4)
    rng.shuffle(fams)
    used, rows, truth = [], [], {}
    for i in range(n):
        while True:
            o = rng.randrange(len(pt) - N)
            if all(abs(o - u) >= N for u in used):
                break
        used.append(o)
        p = pt[o:o + N]
        fam = fams[i]
        conv = CONVS[rng.randrange(len(CONVS))]
        path = names[rng.randrange(len(names))]
        model = "M1" if path == "ID" else ("M1", "M2")[rng.randrange(2)]
        if fam == "PER":
            param = str(rng.randint(2, 20))
            key = "".join(rng.choice(AZ) for _ in range(int(param)))
        elif fam == "GRO":
            param = key = f"{rng.randrange(100000):05d}"
        else:
            param = str(rng.randint(1, 24))
            key = "".join(rng.choice(AZ) for _ in range(int(param)))
        perm = P[path]
        Q = unlayout(p, perm, model)
        ct = to_carved(encrypt_path(Q, fam, conv, param, key), perm)
        assert witness_ok(ct, path, model, fam, conv, param, key, p)
        lab = f"{prefix}_{i:02d}"
        rows.append(f"{lab}\t{ct}")
        truth[lab] = {"plaintext": p, "family": fam, "convention": conv, "param": param, "key": key,
                      "path": path, "model": model, "pt_offset": o}
    (outdir / "blind.tsv").write_text("id\tciphertext\n" + "\n".join(sorted(rows)) + "\n")
    (outdir / "sealed_truth.json").write_text(json.dumps(truth, indent=1) + "\n")
    print(f"wrote {n} plants to {outdir}")


if __name__ == "__main__":
    main()
