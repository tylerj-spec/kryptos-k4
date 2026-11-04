#!/usr/bin/env python3
"""R64 SEALED plant maker (never read by r64/blind/). A 97-letter English plaintext window (non-overlapping) is
encrypted letterwise with a NON-English running key under a convention drawn uniformly from AZ/KRY x VIG/BEAU/VARB,
then transposed by a route drawn uniformly from the 10 frozen R61 routes: CT[j] = X[perm[j]].
Four key kinds, N/4 plants each (N must be divisible by 4), assigned to ids in a seeded random order:
  CLOCK_RAND : random sequence of names from r63/data/clock_names.txt (as R63), start 0-11 letters in;
  CLOCK_RING : a walk around the clock ring (r64/data/clock_ring.txt = faces in UTC-offset order, chart order within a
               face), from a uniformly random start letter, forward or backward around the ring, wrapping;
               out-of-distribution for the CLOCK model (trained on random name orders);
  GERMAN_EP  : a 97-letter window of Europarl German (R63's in-domain source; dev file 9 / holdout file 10);
  GERMAN_LIT : a 97-letter window of pre-1996 literary German (old spelling; Kafka for dev, Thomas Mann for holdout).
Usage: make_plants.py PT_LETTERS DE_EP_LETTERS DE_LIT_LETTERS N SEED PREFIX OUTDIR
Writes OUTDIR/blind.tsv (id, ciphertext; ids sorted) and OUTDIR/sealed_truth.json."""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
N = 97
KINDS = ["CLOCK_RAND", "CLOCK_RING", "GERMAN_EP", "GERMAN_LIT"]


def enc(p, k, X, op):
    return "".join(X[(X.index(a) + X.index(b)) % 26 if op == "VIG" else (X.index(b) - X.index(a)) % 26 if op == "BEAU"
                     else (X.index(a) - X.index(b)) % 26] for a, b in zip(p, k))


def routes():
    out = []
    for line in (ROOT / "r61/routes.txt").read_text().splitlines():
        name, order, p = line.split()
        out.append((name, [int(x) for x in p.split(",")]))
    return out


def main():
    pt_p, ep_p, lit_p, n, seed, prefix, outdir = sys.argv[1:8]
    n, seed, outdir = int(n), int(seed), Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    if any(outdir.iterdir()):
        raise SystemExit("refusing to overwrite")
    pt, ep, lit = (Path(x).read_text().strip() for x in (pt_p, ep_p, lit_p))
    names = (ROOT / "r63/data/clock_names.txt").read_text().split()
    ring_names = (ROOT / "r64/data/clock_ring.txt").read_text().split()
    rts = routes()
    rng = random.Random(seed)
    convs = [(xn, op) for xn in ("AZ", "KRY") for op in ("VIG", "BEAU", "VARB")]
    if n % 4:
        raise SystemExit("N must be divisible by 4")
    kinds = KINDS * (n // 4)
    rng.shuffle(kinds)
    used, rows, truth = [], [], {}
    for i in range(n):
        while True:
            o = rng.randrange(len(pt) - N)
            if all(abs(o - u) >= N for u in used):
                break
        used.append(o)
        kind = kinds[i]
        info = {}
        if kind == "CLOCK_RAND":
            seq = ""
            while len(seq) < N + 20:
                seq += names[rng.randrange(len(names))]
            st = rng.randrange(12)
            k = seq[st:st + N]
        elif kind == "CLOCK_RING":
            fwd = rng.random() < 0.5
            ring = "".join(ring_names if fwd else ring_names[::-1])
            st = rng.randrange(len(ring))
            k = "".join(ring[(st + t) % len(ring)] for t in range(N))
            info = {"ring_direction": "forward" if fwd else "backward", "ring_start": st}
        else:
            src = ep if kind == "GERMAN_EP" else lit
            ko = rng.randrange(len(src) - N)
            k = src[ko:ko + N]
            info = {"key_offset": ko}
        xn, op = convs[rng.randrange(6)]
        ri = rng.randrange(len(rts))
        p = pt[o:o + N]
        x = enc(p, k, AZ if xn == "AZ" else KRY, op)
        perm = rts[ri][1]
        c = "".join(x[perm[j]] for j in range(N))
        lab = f"{prefix}_{i:02d}"
        rows.append(f"{lab}\t{c}")
        truth[lab] = {"plaintext": p, "key": k, "key_kind": kind, "key_model": kind.split("_")[0],
                      "convention": f"{xn}_{op}", "route": rts[ri][0], "route_idx": ri, "pt_offset": o, **info}
    (outdir / "blind.tsv").write_text("id\tciphertext\n" + "\n".join(sorted(rows)) + "\n")
    (outdir / "sealed_truth.json").write_text(json.dumps(truth, indent=1) + "\n")
    print(f"wrote {n} plants to {outdir}")


if __name__ == "__main__":
    main()
