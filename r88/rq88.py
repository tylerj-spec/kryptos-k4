#!/usr/bin/env python3
"""R88 code (SYNTHETIC ONLY: no K4 ciphertext and no published letters are read by this file).
Family RQ (r85/DESIGN.md section 5, item 2): a stepped progressive Quagmire with ONE FREE alphabet.
  Offset s_i = d * (i // n) (i from 0): the key advances d places every n letters.
  side PA (plaintext alphabet free, cipher alphabet fixed = A):   A-place(c_i) = W[p_i] + s_i        (mod 26)
          W: plaintext letter (A-Z index) -> place, any of 26! permutations.
  side CA (cipher alphabet free, plaintext alphabet fixed = A):   c_i = W[ A-place(p_i) + s_i ]
          W: place -> ciphertext letter (A-Z index), any of 26! permutations.
  A is one of AZ, KRYPTOS, PALIMPSEST, ABSCISSA (keyword first, then the rest of A-Z).
This is R40's (PA free) and R42's (CA free) one-free-alphabet construction with a stepped progressive key instead of
chain-addition or running keys; n = 1 overlaps L16 (free-alphabet affine progressive; no code in the repository,
audit/historical/SOURCE_MAP.md). n >= 97 is one alphabet
(L02). Functions: encrypt / decrypt (reference), exact_check (partial-bijection test on given positions)."""
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def keyed(w):
    return "".join(dict.fromkeys(w + AZ))


ALPH = {"AZ": AZ, "KRY": keyed("KRYPTOS"), "PAL": keyed("PALIMPSEST"), "ABS": keyed("ABSCISSA")}
IDX = {a: {ch: i for i, ch in enumerate(s)} for a, s in ALPH.items()}
A4 = tuple(ALPH)
SIDES = ("PA", "CA")


def inverse(W):
    inv = [0] * 26
    for x, y in enumerate(W):
        inv[y] = x
    return inv


def encrypt(pt, W, side, alph, n, d):
    out = []
    for i, p in enumerate(pt):
        s = d * (i // n)
        if side == "PA":
            out.append(ALPH[alph][(W[AZ.index(p)] + s) % 26])
        else:
            out.append(AZ[W[(IDX[alph][p] + s) % 26]])
    return "".join(out)


def decrypt(ct, W, side, alph, n, d):
    Winv = inverse(W)
    out = []
    for i, c in enumerate(ct):
        s = d * (i // n)
        if side == "PA":
            out.append(AZ[Winv[(IDX[alph][c] - s) % 26]])
        else:
            out.append(ALPH[alph][(Winv[AZ.index(c)] - s) % 26])
    return "".join(out)


def exact_check(ct, positions, letters, side, alph, n, d):
    """(feasible, checks): does some W satisfy every given position? checks = positions - distinct keys."""
    fwd, bwd = {}, {}
    for i, p in zip(positions, letters):
        s = d * (i // n)
        if side == "PA":
            a, b = AZ.index(p), (IDX[alph][ct[i]] - s) % 26
        else:
            a, b = (IDX[alph][p] + s) % 26, AZ.index(ct[i])
        if fwd.setdefault(a, b) != b or bwd.setdefault(b, a) != a:
            return False, None
    return True, len(positions) - len(fwd)
