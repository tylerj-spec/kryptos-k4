#!/usr/bin/env python3
"""R65b SEALED check (r65/FOLLOWUP_PREREGISTRATION.md). Holds the published letters. For a route R and a key language
L: implied key fragments at the published positions under each of the 6 conventions, scored by L's order-6 letter model
(each fragment from an empty context); statistic T = best convention's summed log10 probability; null = the same for
10,000 uniformly random permutations of K4 (seed 650071).
Usage: implied_key_check.py ENGLISH_LM GERMAN_LM REPORT.json"""
import hashlib
import json
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
CLUES = ((21, "EASTNORTHEAST"), (63, "BERLINCLOCK"))
SHA = {"EN": "b1a2a3c777dafd6eadc277ee50eb988858253a7843fedfc6903700c61a92a85a",
       "DE": "5451a6ceb24e89293d1935e171cd9d16ca9162720834915ead77d019a096dcc3"}


class LM:
    def __init__(self, path):
        raw = np.memmap(path, dtype=np.uint8, mode="r")
        assert bytes(raw[:5]) == b"R59LM"
        self.K = int(raw[5])
        off, sz, self.T = 8, 26, {}
        for k in range(1, self.K + 1):
            self.T[k] = np.memmap(path, dtype=np.float32, mode="r", offset=off, shape=(sz,))
            off += sz * 4
            sz *= 26

    def score(self, s):
        z = 0.0
        for i in range(len(s)):
            L = min(i, self.K - 1)
            c = 0
            for j in range(i - L, i):
                c = c * 26 + ord(s[j]) - 65
            z += float(self.T[L + 1][c * 26 + ord(s[i]) - 65])
        return z


def key_letter(cl, pl, X, op):
    cx, px = X.index(cl), X.index(pl)
    # VIG c = p + k -> k = c - p ; BEAU c = k - p -> k = c + p ; VARB c = p - k -> k = p - c
    kx = (cx - px) if op == "VIG" else (cx + px) if op == "BEAU" else (px - cx)
    return X[kx % 26]


def fragments(x):
    out = {}
    for xn, X in (("AZ", AZ), ("KRY", KRY)):
        for op in ("VIG", "BEAU", "VARB"):
            out[f"{xn}_{op}"] = ["".join(key_letter(x[o + i], ch, X, op) for i, ch in enumerate(t)) for o, t in CLUES]
    return out


def unroute(ct, perm):
    x = [""] * len(ct)
    for j, src in enumerate(perm):
        x[src] = ct[j]
    return "".join(x)


def T(lm, x):
    fr = fragments(x)
    sc = {c: lm.score(a) + lm.score(b) for c, (a, b) in fr.items()}
    best = max(sc, key=sc.get)
    return sc[best], best, fr, sc


def main():
    en_p, de_p, rep = sys.argv[1:4]
    for p, k in ((en_p, "EN"), (de_p, "DE")):
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for b in iter(lambda: f.read(1 << 20), b""):
                h.update(b)
        assert h.hexdigest() == SHA[k], f"model hash mismatch {k}"
    lms = {"EN": LM(en_p), "DE": LM(de_p)}
    ct = (ROOT / "r39/ic_gate/k4_ciphertext.txt").read_text().strip()
    routes = {l.split()[0]: [int(v) for v in l.split()[2].split(",")] for l in (ROOT / "r61/routes.txt").read_text().splitlines()}
    rng = random.Random(650071)
    perms = []
    for _ in range(10000):
        p = list(range(97))
        rng.shuffle(p)
        perms.append(p)
    out = {}
    for name, route, lang in (("H1", "SNAKE_L", "DE"), ("H2", "COL_LT", "EN")):
        lm = lms[lang]
        t, conv, fr, sc = T(lm, unroute(ct, routes[route]))
        null = [T(lm, unroute(ct, p))[0] for p in perms]
        ge = sum(v >= t for v in null)
        ns = sorted(null)
        out[name] = {"route": route, "language": lang, "T": t, "best_convention": conv,
                     "fragments": fr, "scores": sc, "null_n": len(null), "null_ge": ge, "p": (1 + ge) / (len(null) + 1),
                     "null_median": ns[len(ns) // 2], "null_q99": ns[int(0.99 * (len(ns) - 1))], "null_max": ns[-1],
                     "outcome": "LANGUAGE_LIKE" if (1 + ge) / (len(null) + 1) <= 0.01 else "NOT_LANGUAGE_LIKE"}
        print(name, route, lang, "T %.2f" % t, conv, "null median %.2f q99 %.2f max %.2f" % (ns[len(ns) // 2], out[name]["null_q99"], ns[-1]),
              "ge", ge, "p %.4f" % out[name]["p"], out[name]["outcome"])
        for c, (a, b) in fr.items():
            print("   ", c, a, b, "%.2f" % sc[c])
    Path(rep).write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
