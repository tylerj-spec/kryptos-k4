#!/usr/bin/env python3
"""R101 primary exact solver (PREREGISTRATION section 2): is there a BIJECTIVE rank function r (any of 26! alphabets)
and a constant c satisfying every chain link of R99's criterion? The links are homogeneous linear congruences mod 26.
Mod 26 = mod 2 x mod 13 (CRT): r is injective mod 26 iff every value mod 13 occurs at most twice among the involved
letters and the mod-2 bit separates each such pair. The mod-13 solutions are enumerated projectively (the system is
homogeneous); each survivor leaves a GF(2) separation system, solved by elimination. Cells whose mod-13 solution space
has dimension > DMAX are UNDECIDED."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "r99"))
import checker99 as CK99  # noqa: E402  (links: R99's chain links)

DMAX = 7


def system(ct, obs, L, s1, s2):
    """Rows over 27 unknowns (ranks of the 26 letters, then c): one homogeneous congruence per chain link."""
    sig = -s1 * s2
    rows = []
    for i, j, t in CK99.links(obs, L):
        v = [0] * 27
        v[ord(obs[j]) - 65] += 1
        v[ord(obs[i]) - 65] -= sig ** t
        for u in range(1, t + 1):
            v[ord(ct[i + u * L]) - 65] -= s1 * sig ** (t - u)
        v[26] += s1 * sum(sig ** w for w in range(t))
        rows.append(v)
    return rows


def kernel(rows, cols, p):
    """Basis (as rows) of {x over cols : rows . x = 0 mod p}, p prime."""
    M = [[r[c] % p for c in cols] for r in rows]
    n = len(cols)
    piv, rk = [], 0
    for col in range(n):
        k = next((k for k in range(rk, len(M)) if M[k][col]), None)
        if k is None:
            continue
        M[rk], M[k] = M[k], M[rk]
        inv = pow(M[rk][col], -1, p)
        M[rk] = [(x * inv) % p for x in M[rk]]
        for q in range(len(M)):
            if q != rk and M[q][col]:
                f = M[q][col]
                M[q] = [(a - f * b) % p for a, b in zip(M[q], M[rk])]
        piv.append(col)
        rk += 1
    basis = []
    for f in (c for c in range(n) if c not in piv):
        x = [0] * n
        x[f] = 1
        for r, pc in enumerate(piv):
            x[pc] = (-M[r][f]) % p
        basis.append(x)
    return np.array(basis, dtype=np.int64).reshape(len(basis), n)


def gf2_solvable(A, b):
    """Is A z = b solvable over GF(2)? (rows of A as lists of bits)"""
    R = [list(r) + [bb] for r, bb in zip(A, b)]
    if not R:
        return True
    n = len(R[0]) - 1
    rk = 0
    for col in range(n):
        k = next((k for k in range(rk, len(R)) if R[k][col]), None)
        if k is None:
            continue
        R[rk], R[k] = R[k], R[rk]
        for q in range(len(R)):
            if q != rk and R[q][col]:
                R[q] = [a ^ c for a, c in zip(R[q], R[rk])]
        rk += 1
    return all(any(r[:-1]) or not r[-1] for r in R)


def solve(ct, obs, L, s1, s2, dmax=DMAX, chunk=400_000):
    """(status, links, d13): status FEASIBLE / INFEASIBLE / UNDECIDED (d13 > dmax) / NO_LINKS."""
    rows = system(ct, obs, L, s1, s2)
    if not rows:
        return "NO_LINKS", 0, None
    letters = sorted({c for r in rows for c in range(26) if r[c] % 26})
    cols = letters + [26]
    K13 = kernel(rows, cols, 13)
    K2 = kernel(rows, cols, 2)
    d13 = len(K13)
    if d13 > dmax:
        return "UNDECIDED", len(rows), d13
    nl = len(letters)
    K13L = K13[:, :nl]
    K2L = K2[:, :nl]
    for lead in range(d13):                                   # projective: first nonzero coefficient is 1
        total = 13 ** (d13 - lead - 1)
        for start in range(0, total, chunk):
            idx = np.arange(start, min(total, start + chunk), dtype=np.int64)
            coef = np.zeros((len(idx), d13), dtype=np.int64)
            coef[:, lead] = 1
            x = idx.copy()
            for k in range(d13 - 1, lead, -1):
                coef[:, k] = x % 13
                x //= 13
            R = (coef @ K13L) % 13
            S = np.sort(R, axis=1)
            ok = ~((S[:, 2:] == S[:, :-2]).any(axis=1)) if nl >= 3 else np.ones(len(R), dtype=bool)
            for row in R[ok]:
                pairs = [(a, b) for a in range(nl) for b in range(a + 1, nl) if row[a] == row[b]]
                if not pairs:
                    return "FEASIBLE", len(rows), d13
                if len(K2L) == 0:
                    continue
                A = [[int(K2L[q, a]) ^ int(K2L[q, b]) for q in range(len(K2L))] for a, b in pairs]
                if gf2_solvable(A, [1] * len(pairs)):
                    return "FEASIBLE", len(rows), d13
    return "INFEASIBLE", len(rows), d13
