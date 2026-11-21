#!/usr/bin/env python3
"""R89 arm F26L (SYNTHETIC ONLY: no K4 ciphertext and no published letters are read by this file).
Written by Claude Code from the equations in ChatGPT's design (PR #98, docs/R89_ADVERSARIAL_METHOD_AUDIT.md C-D),
not from its code (which is not in the repository). The 20 alphabets below are this round's own list.

Inner stage F26 (2 x 13 fractionation in blocks):
  a keyed 26-letter alphabet A gives each letter a row r = k // 13 and column h = k % 13 (k = place in A).
  The text is cut into blocks of b letters (b in 5, 7, 9, 11); the last block has t = 97 mod b letters (t = b if 0).
  Within a block of length t, output position j takes the ROW of input position (j + u) mod t and the COLUMN of
  input position (j + v) mod t:  M_j = A[13 * r_{(j+u) mod t} + h_{(j+v) mod t}],  u, v in 1..b-1, u != v.
  Inverse: P_k has row r(M_{(k-u) mod t}) and column h(M_{(k-v) mod t}).  (In a short last block u and v may
  coincide mod t; the block is then a rotation, still invertible.)
Outer stage (K1/K2-style tableau, optional): E = KRYPTOS keyed alphabet, key word U = PALIMPSEST or ABSCISSA,
  C_i = E[(E-place(M_i) + sign * E-place(U[(i + phase) mod |U|])) mod 26],  sign +-1, phase 0..|U|-1  (36 options).
Settings: 20 alphabets x 188 (b, u, v) = 3,760 inner settings; x 36 outer options = 135,360 "F26L"; plus the 3,760
  with no outer stage ("F26", bare).  139,120 in all.  Every setting is a fixed, fully determined decryption: there is
  NO free key, so the family can be enumerated exhaustively.
Equivalence: two alphabets that differ only by a permutation of the 13 columns (applied to both rows) or by swapping
  the two rows give the same cipher (tests check the list has no such pair; canonical() below)."""
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def keyed(w):
    return "".join(dict.fromkeys(w + AZ))


KRY = keyed("KRYPTOS")
# Twenty alphabets fixed a priori: the plain alphabet, a keyboard order and an alternate-letter order, and keyed
# alphabets (keyword first, then the rest of A-Z) from Kryptos K1-K3 keys, K1-K3 plaintext words and names connected
# with the sculpture. NO word from the published K4 plaintext is used. A reversed alphabet is NOT a new setting: it
# swaps the rows and mirrors the columns, which F26 cannot see (development found this; tests check all 20 differ).
F26_ALPHABETS = {
    "AZ": AZ,
    "QWERTY": "QWERTYUIOPASDFGHJKLZXCVBNM",
    "ALT": AZ[0::2] + AZ[1::2],
    "KRYPTOS": KRY,
    "PALIMPSEST": keyed("PALIMPSEST"),
    "ABSCISSA": keyed("ABSCISSA"),
    "NUANCE": keyed("NUANCE"),
    "MAGNETIC": keyed("MAGNETIC"),
    "PASSAGE": keyed("PASSAGE"),
    "CANDLE": keyed("CANDLE"),
    "SANBORN": keyed("SANBORN"),
    "SCHEIDT": keyed("SCHEIDT"),
    "LANGLEY": keyed("LANGLEY"),
    "WEBSTER": keyed("WEBSTER"),
    "SHADING": keyed("SHADING"),
    "IQLUSION": keyed("IQLUSION"),
    "UNDERGRUUND": keyed("UNDERGRUUND"),
    "DESPARATLY": keyed("DESPARATLY"),
    "LAYERTWO": keyed("LAYERTWO"),
    "INVISIBLE": keyed("INVISIBLE"),
}
BLOCKS = (5, 7, 9, 11)
KEYS = {"PAL": "PALIMPSEST", "ABS": "ABSCISSA"}


def canonical(A):
    """F26-equivalence class of an alphabet: the unordered row partition and the set of column pairs."""
    rows = frozenset({frozenset(A[:13]), frozenset(A[13:])})
    cols = frozenset(frozenset((A[h], A[13 + h])) for h in range(13))
    return rows, cols


def pairs(b):
    return [(u, v) for u in range(1, b) for v in range(1, b) if u != v]


def outer_options():
    return [(k, sg, ph) for k in KEYS for sg in (1, -1) for ph in range(len(KEYS[k]))]


def inner_settings():
    return [(a, b, u, v) for a in F26_ALPHABETS for b in BLOCKS for (u, v) in pairs(b)]


def blocks(n, b):
    return [(o, min(b, n - o)) for o in range(0, n, b)]


def f26_enc(pt, a, b, u, v):
    A = F26_ALPHABETS[a]
    k = [A.index(ch) for ch in pt]
    out = []
    for o, t in blocks(len(pt), b):
        for j in range(t):
            out.append(A[13 * (k[o + (j + u) % t] // 13) + k[o + (j + v) % t] % 13])
    return "".join(out)


def f26_dec(ct, a, b, u, v):
    A = F26_ALPHABETS[a]
    k = [A.index(ch) for ch in ct]
    out = []
    for o, t in blocks(len(ct), b):
        for j in range(t):
            out.append(A[13 * (k[o + (j - u) % t] // 13) + k[o + (j - v) % t] % 13])
    return "".join(out)


def outer_enc(m, key, sign, phase):
    U = KEYS[key]
    return "".join(KRY[(KRY.index(ch) + sign * KRY.index(U[(i + phase) % len(U)])) % 26] for i, ch in enumerate(m))


def outer_dec(c, key, sign, phase):
    return outer_enc(c, key, -sign, phase)


def encrypt(pt, st):
    """st = (alphabet, b, u, v, outer) with outer = (key, sign, phase) or None (bare F26)."""
    a, b, u, v, outer = st
    m = f26_enc(pt, a, b, u, v)
    return m if outer is None else outer_enc(m, *outer)


def decrypt(ct, st):
    a, b, u, v, outer = st
    m = ct if outer is None else outer_dec(ct, *outer)
    return f26_dec(m, a, b, u, v)
