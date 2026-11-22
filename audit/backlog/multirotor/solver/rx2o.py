#!/usr/bin/env python3
"""RX2-O reference (SYNTHETIC / DEVELOPMENT ONLY: reads no file, no K4 ciphertext, no published letters).
ChatGPT's two-rotor odometer (audit/backlog/multirotor/DESIGN.md section 2, RX2-O), with R87's contact numberings:
  tau_i = floor((i + r) / n);  s1_i = d1 * tau_i;  s2_i = d2 * floor((tau_i + h) / 26)   (mod 26), i from 0;
  P_i = E_in-place(p_i), C_i = E_out-place(c_i);   M_i = W1(P_i + s1_i) - s1_i;   C_i = W2(M_i + s2_i) - s2_i.
Domain: n 1..4, r 0..n-1, h 0..25, d1, d2 = +-1, 16 contact pairs = 16,640 labels, each with two free wirings.
The eight turnover cells of the prospective gate (DESIGN.md section 5): (n, h-range) with the slow rotor turning
3/4 (n=1), 1/2 (n=2), 1/2 (n=3), 0/1 (n=4) times in 97 positions.
Cross-checked against audit/backlog/multirotor/rotor_constraints.py (encrypt, odometer) by the tests."""
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def keyed(w):
    return "".join(dict.fromkeys(w + AZ))


ALPH = {"AZ": AZ, "KRY": keyed("KRYPTOS"), "PAL": keyed("PALIMPSEST"), "ABS": keyed("ABSCISSA")}
IDX = {a: {ch: i for i, ch in enumerate(s)} for a, s in ALPH.items()}
A4 = tuple(ALPH)
CELLS = {"n1t3": (1, range(0, 8)), "n1t4": (1, range(8, 26)), "n2t1": (2, range(0, 4)), "n2t2": (2, range(4, 26)),
         "n3t1": (3, range(0, 20)), "n3t2": (3, range(20, 26)), "n4t0": (4, range(0, 2)), "n4t1": (4, range(2, 26))}
LABELS = [(ei, eo, n, r, h, d1, d2) for ei in A4 for eo in A4 for n in (1, 2, 3, 4) for r in range(n)
          for h in range(26) for d1 in (1, -1) for d2 in (1, -1)]


def shifts(N, n, r, h, d1, d2):
    tau = [(i + r) // n for i in range(N)]
    return [(d1 * t) % 26 for t in tau], [(d2 * ((t + h) // 26)) % 26 for t in tau]


def turnovers(N, n, r, h):
    s2 = shifts(N, n, r, h, 1, 1)[1]
    return sum(a != b for a, b in zip(s2, s2[1:]))


def inverse(W):
    inv = [0] * 26
    for x, y in enumerate(W):
        inv[y] = x
    return inv


def encrypt(pt, W1, W2, ein, eout, n, r, h, d1, d2):
    s1, s2 = shifts(len(pt), n, r, h, d1, d2)
    out = []
    for p, a, b in zip(pt, s1, s2):
        m = (W1[(IDX[ein][p] + a) % 26] - a) % 26
        out.append(ALPH[eout][(W2[(m + b) % 26] - b) % 26])
    return "".join(out)


def decrypt(ct, W1, W2, ein, eout, n, r, h, d1, d2):
    s1, s2 = shifts(len(ct), n, r, h, d1, d2)
    V1, V2 = inverse(W1), inverse(W2)
    out = []
    for c, a, b in zip(ct, s1, s2):
        m = (V2[(IDX[eout][c] + b) % 26] - b) % 26
        out.append(ALPH[ein][(V1[(m + a) % 26] - a) % 26])
    return "".join(out)


def cell_of(n, r, h):
    for name, (cn, hr) in CELLS.items():
        if cn == n and h in hr:
            return name
    raise ValueError
