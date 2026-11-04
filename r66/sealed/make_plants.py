#!/usr/bin/env python3
"""R66 SEALED plant maker (never read by r66/blind/). A 97-letter English plaintext window (non-overlapping) is
encrypted with a classic HOMOPHONIC table (r66/sealed/homophonic.py: every letter of the message gets one cipher
letter, the spare cipher letters go to frequent letters in proportion to English frequency; the cipher letter for each
occurrence is chosen at random among its homophones), then transposed by a route drawn uniformly from the 10 frozen
R61 routes: CT[j] = X[perm[j]].
Usage: make_plants.py PT_LETTERS N SEED PREFIX OUTDIR   (writes blind.tsv and sealed_truth.json)"""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import homophonic as H  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
N = 97


def routes():
    out = []
    for line in (ROOT / "r61/routes.txt").read_text().splitlines():
        name, _, p = line.split()
        out.append((name, [int(x) for x in p.split(",")]))
    return out


def main():
    pt_p, n, seed, prefix, outdir = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], Path(sys.argv[5])
    outdir.mkdir(parents=True, exist_ok=True)
    if any(outdir.iterdir()):
        raise SystemExit("refusing to overwrite")
    pt = Path(pt_p).read_text().strip()
    rts = routes()
    rng = random.Random(seed)
    used, rows, truth = [], [], {}
    for i in range(n):
        while True:
            o = rng.randrange(len(pt) - N)
            if all(abs(o - u) >= N for u in used):
                break
        used.append(o)
        p = pt[o:o + N]
        f = H.table(p, rng)
        x = H.encrypt(p, f, rng)
        ri = rng.randrange(len(rts))
        perm = rts[ri][1]
        c = "".join(x[perm[j]] for j in range(N))
        lab = f"{prefix}_{i:02d}"
        rows.append(f"{lab}\t{c}")
        truth[lab] = {"plaintext": p, "map": "".join(f[a] for a in H.AZ), "route": rts[ri][0], "route_idx": ri,
                      "pt_offset": o, "ic": round(H.ic(c), 5),
                      "max_homophones": max(list(f.values()).count(v) for v in set(f.values()))}
    (outdir / "blind.tsv").write_text("id\tciphertext\n" + "\n".join(sorted(rows)) + "\n")
    (outdir / "sealed_truth.json").write_text(json.dumps(truth, indent=1) + "\n")
    print(f"wrote {n} plants to {outdir}")


if __name__ == "__main__":
    main()
