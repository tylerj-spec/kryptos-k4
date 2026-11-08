"""R71 ciphertext-only fingerprint features (vectorised; rows are 97-letter ciphertexts as int arrays 0-25).
  D       number of doubled-letter starts i (C[i] == C[i+1], i = 0..95).
  A_w     max over residues a of the number of doubled-letter starts with i mod w == a.
  P1_w    exact probability that D distinct start positions drawn uniformly from 0..95 give a max residue count >= A_w
          (product-of-binomials polynomial over the residue classes; no simulation).
  T1      -log10( min over w = 2..48 of P1_w );  0 if D < 2.  [doubled letters concentrated in one column, any width]
  R_w     sum over ordered letter pairs xy of max(0, count_w(xy) - 1), where count_w(xy) counts i in 0..96-w with
          (C[i], C[i+w]) = xy  [repeated vertical pairs when written at width w].
  Z_w     (R_w - m_w) / s_w, with m_w, s_w the mean and sd of R_w over a fixed reference set of K4 letter shuffles.
  T2      max over w = 2..48 of Z_w.  [repeated vertical pairs, any width]
  IC      index of coincidence; NDIST number of distinct letters.
The widths 2..48 are scanned identically for every ciphertext, so K4's choice of width 7 / 21 is paid for."""
from functools import lru_cache
from math import comb, log10

import numpy as np

N = 97
WIDTHS = range(2, 49)


@lru_cache(maxsize=None)
def p_max_residue_ge(w, d, a):
    """P(max residue count >= a) for d distinct positions chosen uniformly from 0..95, residues mod w."""
    if a <= 0:
        return 1.0
    sizes = [len(range(r, 96, w)) for r in range(w)]
    poly = [1]
    for s in sizes:
        term = [comb(s, j) for j in range(min(a - 1, s) + 1)]
        out = [0] * (len(poly) + len(term) - 1)
        for i, x in enumerate(poly):
            if x:
                for j, y in enumerate(term):
                    out[i + j] += x * y
        poly = out[:d + 1]
    below = poly[d] if d < len(poly) else 0
    return 1.0 - below / comb(96, d)


def doubles(C):
    return (C[:, :-1] == C[:, 1:])


def t1(C):
    dm = doubles(C)
    D = dm.sum(axis=1)
    best = np.ones(len(C))
    A = {}
    for w in WIDTHS:
        onehot = np.zeros((96, w), dtype=np.int32)
        onehot[np.arange(96), np.arange(96) % w] = 1
        aw = (dm.astype(np.int32) @ onehot).max(axis=1)
        A[w] = aw
        key = D.astype(np.int64) * 1000 + aw
        uk, inv = np.unique(key, return_inverse=True)
        pu = np.array([p_max_residue_ge(w, int(k // 1000), int(k % 1000)) if k // 1000 >= 2 else 1.0 for k in uk])
        best = np.minimum(best, pu[inv.ravel()])
    T1 = np.where(D >= 2, -np.log10(np.maximum(best, 1e-300)), 0.0)
    return T1, D, A


def repeats(C, w):
    codes = C[:, :-w].astype(np.int32) * 26 + C[:, w:].astype(np.int32)
    s = np.sort(codes, axis=1)
    distinct = 1 + (np.diff(s, axis=1) != 0).sum(axis=1)
    return (N - w) - distinct


def reference(ref_C):
    m, s = {}, {}
    for w in WIDTHS:
        r = repeats(ref_C, w).astype(float)
        m[w], s[w] = r.mean(), r.std()
    return m, s


def t2(C, ref):
    m, s = ref
    best = np.full(len(C), -np.inf)
    R = {}
    for w in WIDTHS:
        r = repeats(C, w)
        R[w] = r
        best = np.maximum(best, (r - m[w]) / s[w])
    return best, R


def ic(C):
    cnt = np.stack([(C == k).sum(axis=1) for k in range(26)], axis=1)
    return (cnt * (cnt - 1)).sum(axis=1) / (N * (N - 1)), (cnt > 0).sum(axis=1)


def all_features(C, ref):
    T1, D, A = t1(C)
    T2, R = t2(C, ref)
    I, nd = ic(C)
    return {"T1": T1, "T2": T2, "D": D, "A7": A[7], "R21": R[21], "IC": I, "NDIST": nd}


def to_int(s):
    return np.frombuffer(s.encode(), dtype=np.uint8).astype(np.int16) - 65


def log10p(p):
    return -log10(p)
