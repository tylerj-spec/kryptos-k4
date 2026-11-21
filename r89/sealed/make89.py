#!/usr/bin/env python3
"""R89 SEALED item maker (synthetic only; no K4 data, no published letters). Used twice with the same code:
development on SPENT books and the sealed holdout on FRESH, genre-balanced books (pinned in the pre-registration).
POSITIVES, per arm (F26L and RCT), 48 each: 4 parameter strata x 3 genres x 4; in every (stratum, genre) cell the
  first item is MASKED (12 per arm): the plaintext gets the fixed, length-preserving "Germanic" spelling C->K, W->V
  before encryption. F26L strata: block b = 5 / 7 / 9 / 11; random alphabet, (u, v) and outer key/sign/phase.
  RCT strata: modulus m = 2 / 3 / 4 / 5; random q, d, wiring and contact pair.
EXTRAS (REPORTED, never gated), per arm: 2 with one plaintext letter changed before encryption (PTERR), 2 with one
  ciphertext letter changed after encryption (CTERR); RCT also 1 with one state update missed (MISSED).
NEGATIVES, 150 shared, 10 generators (genres rotated):
  RX 15       R87's regular rotor (random wiring, contact pair, n 1-32, d)
  RQ 15       R88's stepped progressive Quagmire with one free alphabet
  PERIODIC 15 periodic Vigenere (AZ) or Quagmire III (KRYPTOS), key 5-14 letters
  RUNKEY 15   running key (Vigenere AZ) from the key book
  SUBTRANS 15 random monoalphabetic substitution, then a columnar transposition (width 5-12, random column order)
  PTAK 15     plaintext autokey, lag 1-7, random primer, AZ
  F26X 15     NEAR-FAMILY: F26 with an alphabet outside the list and an outer KRYPTOS tableau with a random 5-14
              letter key (not PALIMPSEST/ABSCISSA)
  RCTX 15     NEAR-FAMILY: the ciphertext-stepped rotor with a modulus outside the list (m 6 or 7)
  ANAGRAM 25  frequency-preserving English anagram (the plaintext window shuffled)
  RANDOM 5    uniform random letters
Writes BLIND.tsv (id <TAB> ciphertext; ids shuffled) and TRUTH.json (sealed).
Usage: make89.py G1.txt,G2.txt,G3.txt KEY.txt SEED OUTDIR [--raw] [--n-per-cell N] [--neg-scale K]"""
import json
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path[:0] = [str(HERE.parents[1]), str(HERE.parents[2] / "r87"), str(HERE.parents[2] / "r88")]
import f26l as F  # noqa: E402
import rct as RC  # noqa: E402
import rotor87 as RX  # noqa: E402
import rq88 as RQ  # noqa: E402

AZ = F.AZ
START = re.compile(r"\*\*\* ?START OF (THE|THIS) PROJECT GUTENBERG")
END = re.compile(r"\*\*\* ?END OF (THE|THIS) PROJECT GUTENBERG")
MASK = str.maketrans("CW", "KV")
GENS = (("RX", 15), ("RQ", 15), ("PERIODIC", 15), ("RUNKEY", 15), ("SUBTRANS", 15), ("PTAK", 15), ("F26X", 15),
        ("RCTX", 15), ("ANAGRAM", 25), ("RANDOM", 5))


def letters(path, raw):
    t = Path(path).read_text(errors="replace")
    if raw:
        lines = t.splitlines()
        s = next(i for i, l in enumerate(lines) if START.search(l))
        e = next(i for i, l in enumerate(lines) if END.search(l))
        t = "\n".join(lines[s + 1:e])
    return "".join(ch for ch in t.upper() if "A" <= ch <= "Z")


def window(rng, text):
    o = rng.randrange(len(text) - 97)
    return text[o:o + 97]


def perm(rng):
    W = list(range(26))
    rng.shuffle(W)
    return W


def f26l_setting(rng, b):
    u, v = rng.choice(F.pairs(b))
    return (rng.choice(list(F.F26_ALPHABETS)), b, u, v, rng.choice(F.outer_options()))


def rct_setting(rng, m):
    return (rng.choice(RC.A4), rng.choice(RC.A4), rng.choice((1, -1)), m, rng.randrange(m))


def enc(arm, src, st, W=None, skip_at=None):
    if arm == "F26L":
        return F.encrypt(src, st)
    return RC.encrypt(src, W, *st, skip_at=skip_at)


def sdict(arm, st, W=None):
    if arm == "F26L":
        a, b, u, v, o = st
        return {"alphabet": a, "b": b, "u": u, "v": v, "outer": {"key": o[0], "sign": o[1], "phase": o[2]}}
    return {"ein": st[0], "eout": st[1], "d": st[2], "m": st[3], "q": st[4], "wiring": W}


def neg(rng, gen, pt, ktext):
    if gen == "RX":
        return RX.encrypt(pt, perm(rng), rng.choice(RX.A4), rng.choice(RX.A4), rng.randint(1, 32), rng.choice((1, -1)))
    if gen == "RQ":
        return RQ.encrypt(pt, perm(rng), rng.choice(RQ.SIDES), rng.choice(RQ.A4), rng.randint(1, 32),
                          rng.choice((1, -1)))
    if gen == "PERIODIC":
        k = [rng.randrange(26) for _ in range(rng.randint(5, 14))]
        A = AZ if rng.random() < 0.5 else F.KRY
        return "".join(A[(A.index(p) + k[i % len(k)]) % 26] for i, p in enumerate(pt))
    if gen == "RUNKEY":
        o = rng.randrange(len(ktext) - 97)
        return "".join(AZ[(AZ.index(p) + AZ.index(k)) % 26] for p, k in zip(pt, ktext[o:o + 97]))
    if gen == "SUBTRANS":
        S = perm(rng)
        s = [AZ[S[AZ.index(p)]] for p in pt]
        w = rng.randint(5, 12)
        order = list(range(w))
        rng.shuffle(order)
        return "".join(s[i] for col in order for i in range(col, 97, w))
    if gen == "PTAK":
        L = rng.randint(1, 7)
        prim = [rng.randrange(26) for _ in range(L)]
        return "".join(AZ[(AZ.index(p) + (prim[i] if i < L else AZ.index(pt[i - L]))) % 26] for i, p in enumerate(pt))
    if gen == "F26X":
        A = list(AZ)
        rng.shuffle(A)
        A = "".join(A)
        assert F.canonical(A) not in {F.canonical(x) for x in F.F26_ALPHABETS.values()}
        F.F26_ALPHABETS["_X"] = A
        b = rng.choice(F.BLOCKS)
        u, v = rng.choice(F.pairs(b))
        m = F.f26_enc(pt, "_X", b, u, v)
        del F.F26_ALPHABETS["_X"]
        k = [rng.randrange(26) for _ in range(rng.randint(5, 14))]
        return "".join(F.KRY[(F.KRY.index(ch) + k[i % len(k)]) % 26] for i, ch in enumerate(m))
    if gen == "RCTX":
        m = rng.choice((6, 7))
        return RC.encrypt(pt, perm(rng), rng.choice(RC.A4), rng.choice(RC.A4), rng.choice((1, -1)), m, rng.randrange(m))
    if gen == "ANAGRAM":
        c = list(pt)
        rng.shuffle(c)
        return "".join(c)
    if gen == "RANDOM":
        return "".join(rng.choice(AZ) for _ in range(97))
    raise ValueError(gen)


def main():
    a = sys.argv[1:]
    books, key_book, seed, outdir = a[0].split(","), a[1], int(a[2]), Path(a[3])
    raw = "--raw" in a
    npc = int(a[a.index("--n-per-cell") + 1]) if "--n-per-cell" in a else 4
    nscale = float(a[a.index("--neg-scale") + 1]) if "--neg-scale" in a else 1.0
    assert len(books) == 3, "three genre books"
    rng = random.Random(seed)
    G = [letters(b, raw) for b in books]
    ktext = letters(key_book, raw)
    items = []
    for arm in ("F26L", "RCT"):
        strata = F.BLOCKS if arm == "F26L" else (2, 3, 4, 5)
        for si, sv in enumerate(strata):
            for gi in range(3):
                for k in range(npc):
                    pt = window(rng, G[gi])
                    masked = k == 0
                    src = pt.translate(MASK) if masked else pt
                    st = f26l_setting(rng, sv) if arm == "F26L" else rct_setting(rng, sv)
                    W = None if arm == "F26L" else perm(rng)
                    ct = enc(arm, src, st, W)
                    items.append({"class": "POS", "arm": arm, "stratum": f"S{si + 1}", "param": sv, "genre": f"G{gi + 1}",
                                  "masked": masked, "pt": pt, "enciphered": src, "setting": sdict(arm, st, W), "ct": ct})
        kinds = ["PTERR", "PTERR", "CTERR", "CTERR"] + (["MISSED"] if arm == "RCT" else [])
        for n, kind in enumerate(kinds):
            pt = window(rng, G[n % 3])
            sv = rng.choice(strata)
            st = f26l_setting(rng, sv) if arm == "F26L" else rct_setting(rng, sv)
            W = None if arm == "F26L" else perm(rng)
            src, it = pt, {}
            if kind == "PTERR":
                j = rng.randrange(97)
                src = pt[:j] + rng.choice([x for x in AZ if x != pt[j]]) + pt[j + 1:]
                ct = enc(arm, src, st, W)
            elif kind == "CTERR":
                ct0 = enc(arm, pt, st, W)
                j = rng.randrange(97)
                ct = ct0[:j] + rng.choice([x for x in AZ if x != ct0[j]]) + ct0[j + 1:]
                it = {"error_at": j, "ct_clean": ct0}
            else:
                j = rng.randrange(10, 87)
                ct = enc(arm, pt, st, W, skip_at=j)
                it = {"missed_after": j}
            items.append({"class": "EXTRA", "arm": arm, "kind": kind, "genre": f"G{n % 3 + 1}", "pt": pt,
                          "enciphered": src, "setting": sdict(arm, st, W), "ct": ct, **it})
    gi = 0
    for gen, count in GENS:
        for _ in range(max(1, round(count * nscale))):
            pt = window(rng, G[gi % 3])
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
