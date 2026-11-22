#!/usr/bin/env python3
"""R92 SEALED item maker (synthetic only; no K4 data, no published letters). Used twice with the same code:
development on SPENT books and the sealed holdout on FRESH, genre-balanced books (pinned in the pre-registration).
POSITIVES (48, family RXP, r92/rotor92.py): 6 clock cells (n, r) = (2,1) (3,1) (3,2) (4,1) (4,2) (4,3) x 8; genre
  (cell + k) mod 3 (16 per genre); items k = 0, 1 of every cell MASKED (C->K, W->V before encryption; 12 masked).
  Random contact pair, direction and wiring.
EXTRAS (REPORTED, never gated): 2 with one plaintext letter changed before encryption, 2 with one ciphertext letter
  changed after encryption.
NEGATIVES (150), 10 generators x 15, genres rotated:
  RX0       NEAR-FAMILY: R87's zero-phase rotor (r = 0), n 2-4      RXN   R87's rotor, n 5-32
  RX2O      NEAR-FAMILY: ChatGPT's two-rotor odometer (audit/backlog/multirotor/DESIGN.md, RX2-O; random r, h, d1, d2,
            contact pair and both wirings)
  RQ, PERIODIC, RUNKEY, SUBTRANS, PTAK  as R89 (r89/sealed/make89.py);   RCT  R89's ciphertext-stepped rotor
  ANAGRAM   frequency-preserving English anagram
Writes BLIND.tsv (id <TAB> ciphertext; ids shuffled) and TRUTH.json (sealed).
Usage: make92.py G1.txt,G2.txt,G3.txt KEY.txt SEED OUTDIR [--raw] [--n-per-cell N] [--neg-scale K]"""
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
R = HERE.parents[2]
sys.path[:0] = [str(HERE.parents[1]), str(R / "r89"), str(R / "r89" / "sealed"), str(R / "r87"), str(R / "r88"),
                str(R / "audit" / "backlog" / "multirotor")]
import rotor92 as RP  # noqa: E402
import rotor87 as RX  # noqa: E402
import rct as RC  # noqa: E402
import make89 as M89  # noqa: E402
import rotor_constraints as RX2  # noqa: E402

AZ = RP.AZ
MASK = str.maketrans("CW", "KV")
CELLS = [(2, 1), (3, 1), (3, 2), (4, 1), (4, 2), (4, 3)]
GENS = (("RX0", 15), ("RXN", 15), ("RX2O", 15), ("RQ", 15), ("PERIODIC", 15), ("RUNKEY", 15), ("SUBTRANS", 15),
        ("PTAK", 15), ("RCT", 15), ("ANAGRAM", 15))


def perm(rng):
    W = list(range(26))
    rng.shuffle(W)
    return W


def rxp_setting(rng, n, r):
    return (rng.choice(RP.A4), rng.choice(RP.A4), n, r, rng.choice((1, -1)))


def sdict(st, W):
    return {"ein": st[0], "eout": st[1], "n": st[2], "r": st[3], "d": st[4], "wiring": W}


def neg(rng, gen, pt, ktext):
    if gen in ("RQ", "PERIODIC", "RUNKEY", "SUBTRANS", "PTAK", "ANAGRAM"):
        return M89.neg(rng, gen, pt, ktext)
    if gen == "RX0":
        return RX.encrypt(pt, perm(rng), rng.choice(RX.A4), rng.choice(RX.A4), rng.randint(2, 4), rng.choice((1, -1)))
    if gen == "RXN":
        return RX.encrypt(pt, perm(rng), rng.choice(RX.A4), rng.choice(RX.A4), rng.randint(5, 32), rng.choice((1, -1)))
    if gen == "RCT":
        return RC.encrypt(pt, perm(rng), rng.choice(RC.A4), rng.choice(RC.A4), *rng.choice(RC.SCHEDULES))
    if gen == "RX2O":
        n = rng.randint(1, 4)
        sh = RX2.odometer(97, n, rng.randrange(n), rng.randrange(26), rng.choice((1, -1)), rng.choice((1, -1)))
        ei, eo = rng.choice(RP.A4), rng.choice(RP.A4)
        c = RX2.encrypt([RP.IDX[ei][p] for p in pt], perm(rng), perm(rng), sh)
        return "".join(RP.ALPH[eo][x] for x in c)
    raise ValueError(gen)


def main():
    a = sys.argv[1:]
    books, key_book, seed, outdir = a[0].split(","), a[1], int(a[2]), Path(a[3])
    raw = "--raw" in a
    npc = int(a[a.index("--n-per-cell") + 1]) if "--n-per-cell" in a else 8
    nscale = float(a[a.index("--neg-scale") + 1]) if "--neg-scale" in a else 1.0
    assert len(books) == 3, "three genre books"
    rng = random.Random(seed)
    G = [M89.letters(b, raw) for b in books]
    ktext = M89.letters(key_book, raw)
    items = []
    for ci, (n, r) in enumerate(CELLS):
        for k in range(npc):
            gi = (ci + k) % 3
            pt = M89.window(rng, G[gi])
            masked = k < 2
            src = pt.translate(MASK) if masked else pt
            st, W = rxp_setting(rng, n, r), perm(rng)
            items.append({"class": "POS", "cell": f"n{n}r{r}", "genre": f"G{gi + 1}", "masked": masked, "pt": pt,
                          "enciphered": src, "setting": sdict(st, W), "ct": RP.encrypt(src, W, *st)})
    for m, kind in enumerate(("PTERR", "PTERR", "CTERR", "CTERR")):
        pt = M89.window(rng, G[m % 3])
        st, W = rxp_setting(rng, *rng.choice(CELLS)), perm(rng)
        src, it = pt, {}
        if kind == "PTERR":
            j = rng.randrange(97)
            src = pt[:j] + rng.choice([x for x in AZ if x != pt[j]]) + pt[j + 1:]
            ct = RP.encrypt(src, W, *st)
        else:
            ct0 = RP.encrypt(pt, W, *st)
            j = rng.randrange(97)
            ct = ct0[:j] + rng.choice([x for x in AZ if x != ct0[j]]) + ct0[j + 1:]
            it = {"error_at": j, "ct_clean": ct0}
        items.append({"class": "EXTRA", "kind": kind, "genre": f"G{m % 3 + 1}", "pt": pt, "enciphered": src,
                      "setting": sdict(st, W), "ct": ct, **it})
    gi = 0
    for gen, count in GENS:
        for _ in range(max(1, round(count * nscale))):
            pt = M89.window(rng, G[gi % 3])
            items.append({"class": "NEG", "generator": gen, "genre": f"G{gi % 3 + 1}", "pt": pt,
                          "ct": neg(rng, gen, pt, ktext)})
            gi += 1
    rng.shuffle(items)
    outdir.mkdir(parents=True, exist_ok=False)
    truth, rows = {}, ["id\tciphertext"]
    for k, it in enumerate(items):
        rid = f"H_{k:03d}"
        assert len(it["ct"]) == 97 and set(it["ct"]) <= set(AZ)
        rows.append(f"{rid}\t{it['ct']}")
        truth[rid] = it
    (outdir / "BLIND.tsv").write_text("\n".join(rows) + "\n")
    (outdir / "TRUTH.json").write_text(json.dumps(truth, indent=1) + "\n")
    print(len(items), "items:", {c: sum(i["class"] == c for i in items) for c in ("POS", "EXTRA", "NEG")})


if __name__ == "__main__":
    main()
