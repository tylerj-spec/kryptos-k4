#!/usr/bin/env python3
"""R70 SEALED plant maker (never read by r70/blind/). Each plant: a 97-letter window of held-out English plaintext P,
enciphered with a running key read from one of the five pinned R70 sources at a random offset, under a random row
(ID or route x M1/M2) and convention (6), exactly as r70/sealed/common.encrypt.
  CLEAN (20): key = the normalised source window itself.
  NOISY (10): key = the source window with 2 random letters replaced, and (in 5 of them) one letter deleted at a random
              point, so the rest of the key is shifted by one: a model of OCR differing from the printed text.
Then 20 NULLs: frequency-preserving shuffles of 20 plant ciphertexts (seeded). Plants get HOLD_00-29 in seeded random
order; nulls get NULL_00-19.
Usage: make_plants.py PT_LETTERS NORM_DIR SEED OUTDIR
Writes OUTDIR/blind.tsv (id, ciphertext; ids sorted) and OUTDIR/sealed_truth.json (plants only; nulls listed)."""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import AZ, CONVS, N, encrypt, rows  # noqa: E402

SOURCES = ("BERLIN_1912", "EGYPT_1908", "MURRAY_1907", "COOK_1876", "BUDGE_1898")


def main():
    pt_p, norm, seed, outdir = sys.argv[1:5]
    rng, norm, outdir = random.Random(int(seed)), Path(norm), Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    if any(outdir.iterdir()):
        raise SystemExit("refusing to overwrite")
    pt = Path(pt_p).read_text().strip()
    src = {k: (norm / f"{k}.txt").read_text().strip() for k in SOURCES}
    rws = rows()
    kinds = ["CLEAN"] * 20 + ["NOISY_SUB"] * 5 + ["NOISY_DEL"] * 5
    used, plants = [], []
    for kind in kinds:
        while True:
            o = rng.randrange(len(pt) - N)
            if all(abs(o - u) >= N for u in used):
                used.append(o)
                break
        P = pt[o:o + N]
        s = rng.choice(SOURCES)
        ko = rng.randrange(len(src[s]) - N - 1)
        key = list(src[s][ko:ko + N + 1])
        edits = []
        if kind == "NOISY_DEL":
            d = rng.randrange(1, N)
            del key[d]
            edits.append(["delete", d])
        key = key[:N]
        if kind != "CLEAN":
            for q in rng.sample(range(N), 2):
                key[q] = rng.choice([c for c in AZ if c != key[q]])
                edits.append(["substitute", q])
        key = "".join(key)
        path, model = rng.choice(rws)
        conv = rng.choice(CONVS)
        plants.append({"kind": kind, "plaintext": P, "pt_offset": o, "source": s, "offset": ko, "key_used": key,
                       "edits": edits, "path": path, "model": model, "convention": conv,
                       "ciphertext": encrypt(P, key, path, model, conv)})
    nulls = []
    for p in rng.sample(plants, 20):
        c = list(p["ciphertext"])
        rng.shuffle(c)
        nulls.append("".join(c))
    # ids keep their HOLD_/NULL_ role labels (as R68); the assignment of plants to ids is shuffled
    truth, lines = {}, []
    perm_p = list(range(len(plants)))
    rng.shuffle(perm_p)
    for i, j in enumerate(perm_p):
        truth[f"HOLD_{i:02d}"] = plants[j]
        lines.append(f"HOLD_{i:02d}\t{plants[j]['ciphertext']}")
    for i, c in enumerate(nulls):
        truth[f"NULL_{i:02d}"] = {"kind": "NULL", "ciphertext": c}
        lines.append(f"NULL_{i:02d}\t{c}")
    (outdir / "blind.tsv").write_text("id\tciphertext\n" + "\n".join(sorted(lines)) + "\n")
    (outdir / "sealed_truth.json").write_text(json.dumps(truth, indent=1, sort_keys=True) + "\n")
    print(f"wrote {len(plants)} plants and {len(nulls)} nulls to {outdir}")


if __name__ == "__main__":
    main()
