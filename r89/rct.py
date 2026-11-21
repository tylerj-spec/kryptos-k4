#!/usr/bin/env python3
"""R89 arm RCT (SYNTHETIC ONLY: no K4 ciphertext and no published letters are read by this file).
A rotor with an unknown wiring whose stepping depends on the ciphertext letter just produced (ChatGPT's M1, PR #98,
docs/R89_ADVERSARIAL_METHOD_AUDIT.md A; a restricted case of r77 H8, which was proposed but never run). Written by
Claude Code from the equation, with R87's contact numberings added.
  Contacts are numbered by E_in and E_out (AZ, KRYPTOS, PALIMPSEST, ABSCISSA), W any of 26! wirings.
  Offset s_0 = 0;  E_out-place(c_i) + s_i = W[E_in-place(p_i) + s_i]  (mod 26)   (R87's rotor equation);
  s_{i+1} = s_i + d * (1 + [ (AZ-index(c_i) + q) mod m == 0 ])  : one step per letter, two when the ciphertext
  letter just produced falls in the trigger class.  d +-1, m 2..5, q 0..m-1: 28 schedules; x 16 contact pairs = 448.
  The offsets depend only on the ciphertext, so the decrypter computes them before each letter. With AZ/AZ this is
  exactly the design's c_i = W[(p_i + s_i) mod 26] - s_i.
A ciphertext error changes every later offset once its trigger status changes (error propagation, by design).
Functions: offsets, encrypt, decrypt, exact_check (partial bijection of (input contact, output contact) pairs)."""
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def keyed(w):
    return "".join(dict.fromkeys(w + AZ))


ALPH = {"AZ": AZ, "KRY": keyed("KRYPTOS"), "PAL": keyed("PALIMPSEST"), "ABS": keyed("ABSCISSA")}
IDX = {a: {ch: i for i, ch in enumerate(s)} for a, s in ALPH.items()}
A4 = tuple(ALPH)
SCHEDULES = [(d, m, q) for d in (1, -1) for m in (2, 3, 4, 5) for q in range(m)]


def step(c, d, m, q):
    return d * (1 + (1 if (AZ.index(c) + q) % m == 0 else 0))


def offsets(ct, d, m, q):
    s, out = 0, []
    for c in ct:
        out.append(s % 26)
        s += step(c, d, m, q)
    return out


def inverse(W):
    inv = [0] * 26
    for x, y in enumerate(W):
        inv[y] = x
    return inv


def encrypt(pt, W, ein, eout, d, m, q, skip_at=None):
    """skip_at: for robustness controls only, the state update after that position is missed (not part of RCT)."""
    s, out = 0, []
    for i, p in enumerate(pt):
        c = ALPH[eout][(W[(IDX[ein][p] + s) % 26] - s) % 26]
        out.append(c)
        if i != skip_at:
            s += step(c, d, m, q)
    return "".join(out)


def decrypt(ct, W, ein, eout, d, m, q):
    Winv = inverse(W)
    return "".join(ALPH[ein][(Winv[(IDX[eout][c] + s) % 26] - s) % 26]
                   for c, s in zip(ct, offsets(ct, d, m, q)))


def exact_check(ct, positions, letters, ein, eout, d, m, q):
    s = offsets(ct, d, m, q)
    fwd, bwd = {}, {}
    for i, p in zip(positions, letters):
        x, y = (IDX[ein][p] + s[i]) % 26, (IDX[eout][ct[i]] + s[i]) % 26
        if fwd.setdefault(x, y) != y or bwd.setdefault(y, x) != x:
            return False, None
    return True, len(positions) - len(fwd)
