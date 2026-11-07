"""R71 synthetic cipher families (vectorised numpy; rows are 97-letter ciphertexts as ints 0-25).
Every family enciphers a fresh 97-letter English window P (random offset in the plaintext source) with a hidden random
key. Conventions: plaintext alphabet Ap; x = Ap^-1(p); y = x + k (VIG), k - x (BEAU) or x - k (VARB) mod 26; the
ciphertext is Ac[y]. All R71 features are invariant under a fixed relabelling of ciphertext letters, so Ac = AZ is used
without loss of generality (this also covers any keyed or free ciphertext alphabet, including in the feedback of CTAK,
where k_t = Ac^-1(C[t-L]) = y[t-L]).
  OTP          k uniform and independent.                                              [negative baseline]
  RUNKEY       running key: k = A^-1(97-letter window of an English key text), one tableau A in {AZ, KRY} for
               plaintext, ciphertext and key letter; op uniform.                       [negative baseline]
  PERIODIC     k_t = s[t mod p], p uniform 2..30, shifts uniform; Ap in {AZ, KRY, random permutation}; op uniform.
  HOMOPHONIC   R66 homophonic table (r66/sealed/homophonic.py: homophones in proportion to English frequency, a
               random homophone per letter), then one of the 10 R61 routes: CT[j] = X[perm[j]].
  GROMARK      5-digit primer uniform, d_t = (d_{t-5} + d_{t-4}) mod 10, k_t = d_t; Ap in {AZ, KRY, random}; op uniform.
  CTAK         ciphertext autokey, lag L uniform 1..30: k_t = y[t-L] for t >= L, uniform primer shifts for t < L;
               Ap in {AZ, KRY, random}; op uniform.
  PTAK         plaintext autokey, lag L uniform 1..30: k_t = x[t-L] for t >= L, uniform primer shifts for t < L;
               Ap in {AZ, KRY, random}; op uniform.
Each sampler returns (C, params) where params holds the per-row parameter used for descriptive breakdowns."""
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "r66/sealed"))
import homophonic as H  # noqa: E402

N = 97
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
KRY_INV = np.array([KRY.index(c) for c in AZ], dtype=np.int16)   # AZ letter index -> position in KRY
ARMS = ("OTP", "RUNKEY", "PERIODIC", "HOMOPHONIC", "GROMARK", "CTAK", "PTAK")


def windows(rng, text, n):
    off = rng.integers(0, len(text) - N, size=n)
    return text[off[:, None] + np.arange(N)[None, :]]


def ap_map(rng, P):
    """x = Ap^-1(P) with Ap chosen per row from {AZ, KRY, random permutation}; returns x and the choice (0, 1, 2)."""
    n = len(P)
    choice = rng.integers(0, 3, size=n)
    inv = np.tile(np.arange(26, dtype=np.int16), (n, 1))
    inv[choice == 1] = KRY_INV
    r = choice == 2
    inv[r] = np.argsort(rng.random((r.sum(), 26)), axis=1).astype(np.int16)
    return np.take_along_axis(inv, P.astype(np.int64), axis=1).astype(np.int16), choice


def combine(x, k, op):
    """op per row: 0 VIG, 1 BEAU, 2 VARB."""
    o = op[:, None]
    return np.where(o == 0, x + k, np.where(o == 1, k - x, x - k)) % 26


def gen(arm, rng, n, pt, keytext, routes, debug=False):
    """Returns (C, params); with debug=True also a dict holding P (and x, k, op where defined) for invertibility tests."""
    P = windows(rng, pt, n)
    dbg = {"P": P}

    def ret(C, par, **kw):
        dbg.update(kw)
        return (C, par, dbg) if debug else (C, par)
    if arm == "OTP":
        k = rng.integers(0, 26, size=(n, N))
        return ret(((P + k) % 26).astype(np.int16), np.zeros(n, dtype=np.int16), x=P, k=k, op=np.zeros(n, dtype=int))
    op = rng.integers(0, 3, size=n)
    if arm == "RUNKEY":
        K = windows(rng, keytext, n)
        tab = rng.integers(0, 2, size=n)
        x = np.where(tab[:, None] == 1, KRY_INV[P], P)
        k = np.where(tab[:, None] == 1, KRY_INV[K], K)
        return ret(combine(x, k, op).astype(np.int16), tab, x=x, k=k, op=op)
    if arm == "HOMOPHONIC":
        prng = random.Random(int(rng.integers(0, 2**63)))
        out = np.zeros((n, N), dtype=np.int16)
        ridx = rng.integers(0, len(routes), size=n)
        for i in range(n):
            p = "".join(AZ[v] for v in P[i])
            X = H.encrypt(p, H.table(p, prng), prng)
            perm = routes[ridx[i]]
            out[i] = [ord(X[perm[j]]) - 65 for j in range(N)]
        return ret(out, ridx.astype(np.int16), routes=ridx)
    x, _ = ap_map(rng, P)
    if arm == "PERIODIC":
        p = rng.integers(2, 31, size=n)
        s = rng.integers(0, 26, size=(n, 30))
        k = np.take_along_axis(s, np.arange(N)[None, :] % p[:, None], axis=1)
        return ret(combine(x, k, op).astype(np.int16), p.astype(np.int16), x=x, k=k, op=op)
    if arm == "GROMARK":
        d = np.zeros((n, N), dtype=np.int16)
        primer = rng.integers(0, 100000, size=n)
        for i in range(5):
            d[:, i] = (primer // 10 ** (4 - i)) % 10
        for t in range(5, N):
            d[:, t] = (d[:, t - 5] + d[:, t - 4]) % 10
        return ret(combine(x, d, op).astype(np.int16), np.zeros(n, dtype=np.int16), x=x, k=d, op=op)
    if arm in ("CTAK", "PTAK"):
        L = rng.integers(1, 31, size=n)
        primer = rng.integers(0, 26, size=(n, 30))
        y = np.zeros((n, N), dtype=np.int16)
        rows = np.arange(n)
        K = np.zeros((n, N), dtype=np.int16)
        for t in range(N):
            early = t < L
            src = np.where(early, primer[rows, np.minimum(t, 29)], 0)
            lagged = np.maximum(t - L, 0)
            fb = y[rows, lagged] if arm == "CTAK" else x[rows, lagged]
            k = np.where(early, src, fb)
            K[:, t] = k
            o = op
            y[:, t] = np.where(o == 0, x[:, t] + k, np.where(o == 1, k - x[:, t], x[:, t] - k)) % 26
        return ret(y, L.astype(np.int16), x=x, k=K, op=op, L=L)
    raise ValueError(arm)
