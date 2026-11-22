#!/usr/bin/env python3
"""R92 family RXP (SYNTHETIC ONLY: no K4 ciphertext and no published letters are read by this file).
R87's single stepping rotor (r87/rotor87.py) with a STEP-BOUNDARY PHASE r: the 192 labels the multi-rotor review
(audit/backlog/multirotor/DESIGN.md, INTERNAL_REVIEW.md) found outside R87's zero-phase schedule.
  Offset s_i = d * floor((i + r) / n), i from 0;  n 2..4, r 1..n-1, d +-1;  contact numberings E_in, E_out in
  AZ / KRYPTOS / PALIMPSEST / ABSCISSA (16 pairs);  W any of 26! wirings.
  Encrypt:  E_out-place(c_i) + s_i = W[E_in-place(p_i) + s_i]  (mod 26)   (R87's equation, new offsets).
An initial angular offset is absorbed by W; the boundary phase r is not (it moves WHEN steps happen). r = 0 is R87's
excluded schedule (L176); n = 1 has no phase r > 0. 16 x 2 x (1 + 2 + 3) = 192 settings.
Functions: offsets, encrypt, decrypt, exact_check (partial bijection of (input contact, output contact) pairs)."""
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def keyed(w):
    return "".join(dict.fromkeys(w + AZ))


ALPH = {"AZ": AZ, "KRY": keyed("KRYPTOS"), "PAL": keyed("PALIMPSEST"), "ABS": keyed("ABSCISSA")}
IDX = {a: {ch: i for i, ch in enumerate(s)} for a, s in ALPH.items()}
A4 = tuple(ALPH)
SCHEDS = [(n, r, d) for n in (2, 3, 4) for r in range(1, n) for d in (1, -1)]
SETTINGS = [(ei, eo, n, r, d) for ei in A4 for eo in A4 for (n, r, d) in SCHEDS]


def offsets(N, n, r, d):
    return [d * ((i + r) // n) for i in range(N)]


def inverse(W):
    inv = [0] * 26
    for x, y in enumerate(W):
        inv[y] = x
    return inv


def encrypt(pt, W, ein, eout, n, r, d):
    return "".join(ALPH[eout][(W[(IDX[ein][p] + s) % 26] - s) % 26] for p, s in zip(pt, offsets(len(pt), n, r, d)))


def decrypt(ct, W, ein, eout, n, r, d):
    Winv = inverse(W)
    return "".join(ALPH[ein][(Winv[(IDX[eout][c] + s) % 26] - s) % 26] for c, s in zip(ct, offsets(len(ct), n, r, d)))


def exact_check(ct, positions, letters, ein, eout, n, r, d):
    s = offsets(len(ct), n, r, d)
    fwd, bwd = {}, {}
    for i, p in zip(positions, letters):
        x, y = (IDX[ein][p] + s[i]) % 26, (IDX[eout][ct[i]] + s[i]) % 26
        if fwd.setdefault(x, y) != y or bwd.setdefault(y, x) != x:
            return False, None
    return True, len(positions) - len(fwd)
