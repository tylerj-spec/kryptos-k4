#!/usr/bin/env python3
"""R90 SEALED item maker (synthetic only; no K4 data, no published letters). Used twice with the same code:
development on SPENT books and the sealed holdout on FRESH, genre-balanced books (pinned in the pre-registration).
POSITIVES (48, family F26C, r90/f26c.py): 4 block strata (b 5 / 7 / 9 / 11) x 3 genres x 4; in every cell the first
  item is MASKED (C->K, W->V before encryption; 12 masked). Random alphabet of the 15, (u, v), and outer key/sign/phase
  (every positive has the outer stage).
EXTRAS (REPORTED, never gated): 2 with one plaintext letter changed before encryption (PTERR), 2 with one ciphertext
  letter changed after encryption (CTERR).
NEGATIVES (150), genres rotated:
  RX 13, RQ 13, PERIODIC 13, RUNKEY 13, SUBTRANS 13, PTAK 13   as R89 (r89/sealed/make89.py)
  F26X 13     near-family: F26 with a random alphabet outside both catalogs + KRYPTOS tableau with a random 5-14 key
  F26R89 13   near-family: R89's F26L with one of R89's 20 alphabets (a catalog already excluded, not searched here)
  RCT 13      R89's ciphertext-stepped rotor (r89/rct.py)
  ANAGRAM 25  frequency-preserving English anagram;  RANDOM 8  uniform letters
Writes BLIND.tsv (id <TAB> ciphertext; ids shuffled) and TRUTH.json (sealed).
Usage: make90.py G1.txt,G2.txt,G3.txt KEY.txt SEED OUTDIR [--raw] [--n-per-cell N] [--neg-scale K]"""
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
R = HERE.parents[2]
sys.path[:0] = [str(HERE.parents[1]), str(R / "r89"), str(R / "r89" / "sealed"), str(R / "r87"), str(R / "r88")]
import f26c as F  # noqa: E402
import f26l as L89  # noqa: E402
import rct as RC  # noqa: E402
import make89 as M89  # noqa: E402

AZ = F.AZ
MASK = str.maketrans("CW", "KV")
GENS = (("RX", 13), ("RQ", 13), ("PERIODIC", 13), ("RUNKEY", 13), ("SUBTRANS", 13), ("PTAK", 13), ("F26X", 13),
        ("F26R89", 13), ("RCT", 13), ("ANAGRAM", 25), ("RANDOM", 8))
ALL_CLASSES = {F.canonical(a) for a in F.ALPHABETS.values()} | {L89.canonical(a) for a in L89.F26_ALPHABETS.values()}


def f26c_setting(rng, b):
    u, v = rng.choice(F.pairs(b))
    return (rng.choice(F.WORDS), b, u, v, rng.choice(F.outer_options()))


def sdict(st):
    a, b, u, v, o = st
    return {"alphabet": a, "b": b, "u": u, "v": v, "outer": {"key": o[0], "sign": o[1], "phase": o[2]}}


def neg(rng, gen, pt, ktext):
    if gen in ("RX", "RQ", "PERIODIC", "RUNKEY", "SUBTRANS", "PTAK", "ANAGRAM", "RANDOM"):
        return M89.neg(rng, gen, pt, ktext)
    if gen == "F26X":
        while True:
            A = list(AZ)
            rng.shuffle(A)
            A = "".join(A)
            if F.canonical(A) not in ALL_CLASSES:
                break
        b = rng.choice(F.BLOCKS)
        u, v = rng.choice(F.pairs(b))
        m = F.f26_enc(pt, A, b, u, v)
        k = [rng.randrange(26) for _ in range(rng.randint(5, 14))]
        return "".join(F.KRY[(F.KRY.index(ch) + k[i % len(k)]) % 26] for i, ch in enumerate(m))
    if gen == "F26R89":
        a, b, u, v = rng.choice(L89.inner_settings())
        return L89.encrypt(pt, (a, b, u, v, rng.choice(L89.outer_options())))
    if gen == "RCT":
        W = list(range(26))
        rng.shuffle(W)
        return RC.encrypt(pt, W, rng.choice(RC.A4), rng.choice(RC.A4), *rng.choice(RC.SCHEDULES))
    raise ValueError(gen)


def main():
    a = sys.argv[1:]
    books, key_book, seed, outdir = a[0].split(","), a[1], int(a[2]), Path(a[3])
    raw = "--raw" in a
    npc = int(a[a.index("--n-per-cell") + 1]) if "--n-per-cell" in a else 4
    nscale = float(a[a.index("--neg-scale") + 1]) if "--neg-scale" in a else 1.0
    assert len(books) == 3, "three genre books"
    rng = random.Random(seed)
    G = [M89.letters(b, raw) for b in books]
    ktext = M89.letters(key_book, raw)
    items = []
    for si, b in enumerate(F.BLOCKS):
        for gi in range(3):
            for k in range(npc):
                pt = M89.window(rng, G[gi])
                src = pt.translate(MASK) if k == 0 else pt
                st = f26c_setting(rng, b)
                items.append({"class": "POS", "arm": "F26C", "stratum": f"S{si + 1}", "param": b, "genre": f"G{gi + 1}",
                              "masked": k == 0, "pt": pt, "enciphered": src, "setting": sdict(st),
                              "ct": F.encrypt(src, st)})
    for n, kind in enumerate(("PTERR", "PTERR", "CTERR", "CTERR")):
        pt = M89.window(rng, G[n % 3])
        st = f26c_setting(rng, rng.choice(F.BLOCKS))
        src, it = pt, {}
        if kind == "PTERR":
            j = rng.randrange(97)
            src = pt[:j] + rng.choice([x for x in AZ if x != pt[j]]) + pt[j + 1:]
            ct = F.encrypt(src, st)
        else:
            ct0 = F.encrypt(pt, st)
            j = rng.randrange(97)
            ct = ct0[:j] + rng.choice([x for x in AZ if x != ct0[j]]) + ct0[j + 1:]
            it = {"error_at": j, "ct_clean": ct0}
        items.append({"class": "EXTRA", "arm": "F26C", "kind": kind, "genre": f"G{n % 3 + 1}", "pt": pt,
                      "enciphered": src, "setting": sdict(st), "ct": ct, **it})
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
