#!/usr/bin/env python3
"""R88 SEALED item maker (synthetic only; no K4 data, no published letters). Used twice with the same code:
development on SPENT books (r59 dev_pt / dev_key) and the sealed holdout on FRESH books (pinned in the
pre-registration). R87's maker with RQ positives and one more negative generator.
Positives (family RQ, r88/rq88.py): random free alphabet W, side PA/CA, fixed alphabet, d; step period n in four strata
  S1 1-4, S2 5-8, S3 9-16, S4 17-32; kind "plain" or "2 letters changed" (two random plaintext letters replaced
  before encryption).
CTERR (REPORTED, not gated): 1-in-4 extra positives per stratum with ONE ciphertext letter changed after encryption
  (a carving or transcription error); recovered = >= 95/97 of the enciphered text.
Negatives: English plaintext through a WRONG family (9 generators), plus random letters:
  VIG       periodic Vigenere, AZ tableau, key 5-14 letters
  QUAG3     Quagmire III on the KRYPTOS alphabet, key 5-14 letters
  RUNKEY    running key (Vigenere AZ) from the key book
  GROMARK   base-10 chain addition from a 5-digit primer, KRYPTOS cipher alphabet
  CTAK      ciphertext autokey, lag 1-7, AZ, random primer letters
  TWOSTAGE  two periodic keyword stages on different tableaux (AZ then KRY), keys 3-10 letters
  RX        ONE stepping rotor with a random wiring (R87's family, r87/rotor87.py): the near-family confounder
  RX2       TWO stepping rotors (odometer: rotor 2 advances every 26n letters)
  SHUFRQ    a frequency-preserving shuffle of an RQ ciphertext
  RANDOM    uniform random letters
Writes BLIND.tsv (id <TAB> ciphertext; ids shuffled) and TRUTH.json (sealed).
Usage: make88.py PT_BOOK[,PT_BOOK...] KEY_BOOK SEED N_POS_PER_STRATUM N_CTERR_PER_STRATUM N_NEG_PER_GEN OUTDIR [--raw]
  (--raw: Gutenberg books; header and licence stripped)"""
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "r87"))
import rq88 as R  # noqa: E402
import rotor87 as RX  # noqa: E402

AZ = R.AZ
STRATA = {"S1": (1, 4), "S2": (5, 8), "S3": (9, 16), "S4": (17, 32)}
START = re.compile(r"\*\*\* ?START OF (THE|THIS) PROJECT GUTENBERG")
END = re.compile(r"\*\*\* ?END OF (THE|THIS) PROJECT GUTENBERG")


def letters(path, raw):
    t = Path(path).read_text(errors="replace")
    if raw:
        lines = t.splitlines()
        s = next(i for i, l in enumerate(lines) if START.search(l))
        e = next(i for i, l in enumerate(lines) if END.search(l))
        t = "\n".join(lines[s + 1:e])
    return "".join(ch for ch in t.upper() if "A" <= ch <= "Z")


def window(rng, texts):
    """97 consecutive letters from one of the plaintext books (chosen uniformly when there are several)."""
    text = texts[0] if len(texts) == 1 else rng.choice(texts)
    o = rng.randrange(len(text) - 97)
    return text[o:o + 97]


def change2(rng, pt):
    p = list(pt)
    for i in rng.sample(range(97), 2):
        p[i] = rng.choice([x for x in AZ if x != p[i]])
    return "".join(p)


def tab(pt, keyvals, ca="AZ"):
    return "".join(R.ALPH[ca][(AZ.index(p) + k) % 26] for p, k in zip(pt, keyvals))


def neg(rng, gen, pt, keytext):
    if gen == "VIG":
        k = [rng.randrange(26) for _ in range(rng.randint(5, 14))]
        return tab(pt, [k[i % len(k)] for i in range(97)])
    if gen == "QUAG3":
        k = [rng.randrange(26) for _ in range(rng.randint(5, 14))]
        return "".join(R.ALPH["KRY"][(R.IDX["KRY"][p] + k[i % len(k)]) % 26] for i, p in enumerate(pt))
    if gen == "RUNKEY":
        o = rng.randrange(len(keytext) - 97)
        return tab(pt, [AZ.index(ch) for ch in keytext[o:o + 97]])
    if gen == "GROMARK":
        k = [rng.randrange(10) for _ in range(5)]
        while len(k) < 97:
            k.append((k[-5] + k[-4]) % 10)
        return tab(pt, k, "KRY")
    if gen == "CTAK":
        L = rng.randint(1, 7)
        prim = [rng.randrange(26) for _ in range(L)]
        out = []
        for i, p in enumerate(pt):
            k = prim[i] if i < L else AZ.index(out[i - L])
            out.append(AZ[(AZ.index(p) + k) % 26])
        return "".join(out)
    if gen == "TWOSTAGE":
        k1 = [rng.randrange(26) for _ in range(rng.randint(3, 10))]
        k2 = [rng.randrange(26) for _ in range(rng.randint(3, 10))]
        q = tab(pt, [k1[i % len(k1)] for i in range(97)])
        return "".join(R.ALPH["KRY"][(R.IDX["KRY"][c] + k2[i % len(k2)]) % 26] for i, c in enumerate(q))
    if gen == "RX2":
        W1, W2 = list(range(26)), list(range(26))
        rng.shuffle(W1)
        rng.shuffle(W2)
        n = rng.randint(1, 4)
        out = []
        for i, p in enumerate(pt):
            s1, s2 = i // n, i // (26 * n)
            y = (W1[(AZ.index(p) + s1) % 26] - s1) % 26
            out.append(AZ[(W2[(y + s2) % 26] - s2) % 26])
        return "".join(out)
    if gen == "RX":
        W = list(range(26))
        rng.shuffle(W)
        return RX.encrypt(pt, W, rng.choice(RX.A4), rng.choice(RX.A4), rng.randint(1, 32), rng.choice((1, -1)))
    if gen == "SHUFRQ":
        W = list(range(26))
        rng.shuffle(W)
        c = list(R.encrypt(pt, W, rng.choice(R.SIDES), rng.choice(R.A4), rng.randint(1, 32), rng.choice((1, -1))))
        rng.shuffle(c)
        return "".join(c)
    if gen == "RANDOM":
        return "".join(rng.choice(AZ) for _ in range(97))
    raise ValueError(gen)


GENS = ("VIG", "QUAG3", "RUNKEY", "GROMARK", "CTAK", "TWOSTAGE", "RX", "RX2", "SHUFRQ", "RANDOM")


def main():
    pt_book, key_book, seed, npos, ncterr, nneg, outdir = sys.argv[1:8]
    raw = "--raw" in sys.argv
    rng = random.Random(int(seed))
    ptext, ktext = [letters(b, raw) for b in pt_book.split(",")], letters(key_book, raw)
    items = []
    for stratum, (lo, hi) in STRATA.items():
        for k in range(int(npos)):
            pt = window(rng, ptext)
            kind = "plain" if k % 2 == 0 else "changed2"
            src = pt if kind == "plain" else change2(rng, pt)
            W = list(range(26))
            rng.shuffle(W)
            st = (rng.choice(R.SIDES), rng.choice(R.A4), rng.randint(lo, hi), rng.choice((1, -1)))
            ct = R.encrypt(src, W, *st)
            assert R.decrypt(ct, W, *st) == src
            items.append({"class": "POS", "stratum": stratum, "kind": kind, "pt": pt, "enciphered": src,
                          "setting": {"side": st[0], "alph": st[1], "n": st[2], "d": st[3], "wiring": W}, "ct": ct})
        for _ in range(int(ncterr)):
            pt = window(rng, ptext)
            W = list(range(26))
            rng.shuffle(W)
            st = (rng.choice(R.SIDES), rng.choice(R.A4), rng.randint(lo, hi), rng.choice((1, -1)))
            ct0 = R.encrypt(pt, W, *st)
            j = rng.randrange(97)
            ct = ct0[:j] + rng.choice([x for x in AZ if x != ct0[j]]) + ct0[j + 1:]
            items.append({"class": "CTERR", "stratum": stratum, "kind": "ct1err", "pt": pt, "enciphered": pt,
                          "error_at": j, "ct_clean": ct0,
                          "setting": {"side": st[0], "alph": st[1], "n": st[2], "d": st[3], "wiring": W}, "ct": ct})
    for gen in GENS:
        for _ in range(int(nneg)):
            pt = window(rng, ptext)
            items.append({"class": "NEG", "generator": gen, "pt": pt, "ct": neg(rng, gen, pt, ktext)})
    rng.shuffle(items)
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=False)
    truth = {}
    rows = ["id\tciphertext"]
    for k, it in enumerate(items):
        rid = f"H_{k:03d}"
        assert len(it["ct"]) == 97 and set(it["ct"]) <= set(AZ)
        rows.append(f"{rid}\t{it['ct']}")
        truth[rid] = it
    (out / "BLIND.tsv").write_text("\n".join(rows) + "\n")
    (out / "TRUTH.json").write_text(json.dumps(truth, indent=1) + "\n")
    print(len(items), "items:", {c: sum(i["class"] == c for i in items) for c in ("POS", "CTERR", "NEG")})


if __name__ == "__main__":
    main()
