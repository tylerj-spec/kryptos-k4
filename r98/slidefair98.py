#!/usr/bin/env python3
"""R98 reference Slidefair (PREREGISTRATION section 1; synthetic use only; standard library).
Convention conv = (t, r, o, a): t 'VIG' or 'BEAU' (Variant = VIG with the key negated, identical constraints),
r role (0: first letter in the upper/PA row), o output (0: upper-row cipher letter written first), a pair parity.
keys: one key value per pair index (any sequence). Unpaired letters: c = lower(IDX_PA[p]) with the next key value."""
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def lower_letter(CA, t, k, x):
    return CA[(x + k) % 26] if t == "VIG" else CA[(k - x) % 26]


def lower_col(CA, t, k, w):
    i = CA.index(w)
    return (i - k) % 26 if t == "VIG" else (k - i) % 26


def enc_pair(u, w, PA, CA, t, k):
    xu, xw = PA.index(u), lower_col(CA, t, k, w)
    if xu != xw:
        return PA[xw], lower_letter(CA, t, k, xu)
    return PA[(xu + 1) % 26], lower_letter(CA, t, k, xu + 1)


def dec_pair(cu, cl, PA, CA, t, k):
    """Inverse of enc_pair: the normal case is reciprocal; a same-column pair came from the letters to the left."""
    xu, xw = PA.index(cu), lower_col(CA, t, k, cl)
    if xu != xw:
        return PA[xw], lower_letter(CA, t, k, xu)
    return PA[(xu - 1) % 26], lower_letter(CA, t, k, xu - 1)


def pair_starts(n, a):
    return list(range(a, n - 1, 2))


def encrypt(pt, PA, CA, conv, keys):
    t, r, o, a = conv
    out = list(pt)
    starts = pair_starts(len(pt), a)
    covered = set()
    for j, i in enumerate(starts):
        first, second = pt[i], pt[i + 1]
        u, w = (first, second) if r == 0 else (second, first)
        cu, cl = enc_pair(u, w, PA, CA, t, keys[j])
        out[i], out[i + 1] = (cu, cl) if o == 0 else (cl, cu)
        covered |= {i, i + 1}
    extra = len(starts)
    for i in range(len(pt)):
        if i not in covered:
            out[i] = lower_letter(CA, t, keys[extra], PA.index(pt[i]))
            extra += 1
    return "".join(out)


def decrypt(ct, PA, CA, conv, keys):
    t, r, o, a = conv
    out = list(ct)
    starts = pair_starts(len(ct), a)
    covered = set()
    for j, i in enumerate(starts):
        cu, cl = (ct[i], ct[i + 1]) if o == 0 else (ct[i + 1], ct[i])
        u, w = dec_pair(cu, cl, PA, CA, t, keys[j])
        out[i], out[i + 1] = (u, w) if r == 0 else (w, u)
        covered |= {i, i + 1}
    extra = len(starts)
    for i in range(len(ct)):
        if i not in covered:
            out[i] = PA[lower_col(CA, t, keys[extra], ct[i])]
            extra += 1
    return "".join(out)


CONVENTIONS = [(t, r, o, a) for t in ("VIG", "BEAU") for r in (0, 1) for o in (0, 1) for a in (0, 1)]
