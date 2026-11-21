#!/usr/bin/env python3
"""R90 family F26C (SYNTHETIC ONLY: no K4 ciphertext and no published letters are read by this file).
The F26 / F26L cipher of R89 (r89/f26l.py, same equations) over the 15 alphabet classes that ChatGPT's original
development kit listed and R89 did NOT test (ChatGPT's result review, r89/audit/REVIEW_20261121.md, correction D;
r89/audit/evidence/ALPHABET_SCOPE.json). Built as the kit built them: keyword first, then the rest of A-Z.
Inner F26: rows/columns of a 2 x 13 layout of alphabet A; blocks of b (5, 7, 9, 11; last block 97 mod b); output j
  takes the row of input (j + u) mod t and the column of input (j + v) mod t, u != v in 1..b-1.
Outer (optional): C_i = KRY[KRY-place(M_i) + sign * KRY-place(U[(i + phase) mod |U|])], U = PALIMPSEST / ABSCISSA.
Settings: 15 alphabets x 188 (b, u, v) x (36 outer + none) = 104,340 fixed decryptions, no free key.
Key equivalence (fixed for R90's gate): two settings are the same key iff their alphabets are in the same F26 class
  (same unordered row partition and the same column pairs; canonical()) and b, u, v and the outer stage are equal."""
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def keyed(w):
    return "".join(dict.fromkeys(w + AZ))


KRY = keyed("KRYPTOS")
WORDS = ("ORCHARD", "MYSTERY", "TRAVEL", "MECHANIC", "RIVER", "PHILOSOPHY", "HORIZON", "GARDEN", "SECRET", "TEMPLE",
         "MARKET", "TUNNEL", "LIBRARY", "MIRROR", "CIPHER")
ALPHABETS = {w: keyed(w) for w in WORDS}
BLOCKS = (5, 7, 9, 11)
KEYS = {"PAL": "PALIMPSEST", "ABS": "ABSCISSA"}


def canonical(A):
    rows = frozenset({frozenset(A[:13]), frozenset(A[13:])})
    cols = frozenset(frozenset((A[h], A[13 + h])) for h in range(13))
    return rows, cols


def pairs(b):
    return [(u, v) for u in range(1, b) for v in range(1, b) if u != v]


def outer_options():
    return [(k, sg, ph) for k in KEYS for sg in (1, -1) for ph in range(len(KEYS[k]))]


def inner_settings():
    return [(a, b, u, v) for a in ALPHABETS for b in BLOCKS for (u, v) in pairs(b)]


def blocks(n, b):
    return [(o, min(b, n - o)) for o in range(0, n, b)]


def f26_enc(pt, A, b, u, v):
    k = [A.index(ch) for ch in pt]
    out = []
    for o, t in blocks(len(pt), b):
        for j in range(t):
            out.append(A[13 * (k[o + (j + u) % t] // 13) + k[o + (j + v) % t] % 13])
    return "".join(out)


def f26_dec(ct, A, b, u, v):
    k = [A.index(ch) for ch in ct]
    out = []
    for o, t in blocks(len(ct), b):
        for j in range(t):
            out.append(A[13 * (k[o + (j - u) % t] // 13) + k[o + (j - v) % t] % 13])
    return "".join(out)


def outer_enc(m, key, sign, phase):
    U = KEYS[key]
    return "".join(KRY[(KRY.index(ch) + sign * KRY.index(U[(i + phase) % len(U)])) % 26] for i, ch in enumerate(m))


def encrypt(pt, st, alphabets=ALPHABETS):
    a, b, u, v, outer = st
    m = f26_enc(pt, alphabets[a], b, u, v)
    return m if outer is None else outer_enc(m, *outer)


def decrypt(ct, st, alphabets=ALPHABETS):
    a, b, u, v, outer = st
    m = ct if outer is None else outer_enc(ct, outer[0], -outer[1], outer[2])
    return f26_dec(m, alphabets[a], b, u, v)


def same_key(s1, s2, alphabets=ALPHABETS):
    """R90's key equivalence (see docstring)."""
    return (canonical(alphabets[s1[0]]) == canonical(alphabets[s2[0]]) and tuple(s1[1:4]) == tuple(s2[1:4]) and
            (s1[4] is None) == (s2[4] is None) and (s1[4] is None or tuple(s1[4]) == tuple(s2[4])))
