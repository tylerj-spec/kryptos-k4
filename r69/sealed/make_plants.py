#!/usr/bin/env python3
"""R69 SEALED plant maker (never read by r69/blind/). Each plant: a 97-letter window of held-out English (P) and a
97-letter window of held-out Europarl German (K), enciphered letterwise under a convention drawn uniformly from
AZ/KRY x VIG/BEAU/VARB (X[i] = S(P[i], K[i]), as R64/R67's positives), then read out by one R69 reading:
CT[j] = X[perm[j]].
  32 F plants: each of the 16 F readings twice (set F);
  8 B plants: 8 distinct start columns c != 27 drawn at random, parity q at random (set A).
Windows are non-overlapping within each source. Ids HOLD_00-39 are assigned in a seeded random order.
Usage: make_plants.py PT_LETTERS DE_LETTERS SEED OUTDIR
Writes OUTDIR/blind.tsv (id, ciphertext, set; ids sorted) and OUTDIR/sealed_truth.json."""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r64/sealed"))
from common import enc  # noqa: E402
N = 97


def readings():
    out = {}
    for line in (ROOT / "r69/data/patterns.txt").read_text().splitlines():
        name, _, p = line.split()
        out[name] = [int(x) for x in p.split(",")]
    return out


def window(rng, text, used):
    while True:
        o = rng.randrange(len(text) - N)
        if all(abs(o - u) >= N for u in used):
            used.append(o)
            return o


def main():
    pt_p, de_p, seed, outdir = sys.argv[1:5]
    rng, outdir = random.Random(int(seed)), Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    if any(outdir.iterdir()):
        raise SystemExit("refusing to overwrite")
    pt, de = (Path(x).read_text().strip() for x in (pt_p, de_p))
    rd = readings()
    fnames = sorted(n for n in rd if n.startswith("F_"))
    cols = rng.sample([c for c in range(31) if c != 27], 8)
    specs = [(n, "F") for n in fnames for _ in range(2)] + [(f"B_c{c:02d}_q{rng.randrange(2)}", "A") for c in cols]
    rng.shuffle(specs)
    convs = [f"{x}_{op}" for x in ("AZ", "KRY") for op in ("VIG", "BEAU", "VARB")]
    upt, ude, rows, truth = [], [], [], {}
    for i, (name, sset) in enumerate(specs):
        o, ko = window(rng, pt, upt), window(rng, de, ude)
        p, k = pt[o:o + N], de[ko:ko + N]
        conv = rng.choice(convs)
        x = enc(p, k, conv)
        perm = rd[name]
        ct = "".join(x[perm[j]] for j in range(N))
        rid = f"HOLD_{i:02d}"
        rows.append(f"{rid}\t{ct}\t{sset}")
        truth[rid] = {"reading": name, "set": sset, "convention": conv, "plaintext": p, "key": k,
                      "pt_offset": o, "key_offset": ko}
    (outdir / "blind.tsv").write_text("id\tciphertext\tset\n" + "\n".join(sorted(rows)) + "\n")
    (outdir / "sealed_truth.json").write_text(json.dumps(truth, indent=1, sort_keys=True) + "\n")
    print(f"wrote {len(rows)} plants to {outdir}")


if __name__ == "__main__":
    main()
