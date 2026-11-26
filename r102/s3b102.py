#!/usr/bin/env python3
"""R102 primary solver (PREREGISTRATION T3): consistency of a plaintext hypothesis with a ciphertext under the
two-free-alphabet plaintext autokey  b(C_i) = s1*a(P_i) + s2*f(P_{i-L}) + c  (mod 26), a = A^-1, b = B^-1, f = a, b or
the A-Z rank, with a and b bijective. One equation per known pair (P_{i-L}, P_i), i >= L. Exact for closed hypotheses
(every known i >= L has P_{i-L} known); necessary only otherwise. Method: CRT. The affine solution spaces mod 13 and
mod 2 come from Gaussian elimination. The mod-13 space is enumerated with each value at most twice inside the a-group
and inside the b-group; a GF(2) system then separates each such pair. The result includes a witness (A, B, c)."""
import numpy as np

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DMAX = 7
NV = 53                                   # 0..25 a(letter), 26..51 b(letter), 52 c; column 53 is the constant


def rows(ct, pt, L, s1, s2, F):
    """pt: sequence of letters or None (unknown)."""
    R = []
    for i in range(L, len(ct)):
        if pt[i] is None or pt[i - L] is None:
            continue
        v = [0] * 54
        v[26 + ord(ct[i]) - 65] += 1
        v[ord(pt[i]) - 65] -= s1
        if F == "A":
            v[ord(pt[i - L]) - 65] -= s2
        elif F == "B":
            v[26 + ord(pt[i - L]) - 65] -= s2
        else:
            v[53] -= s2 * (ord(pt[i - L]) - 65)
        v[52] -= 1
        R.append(v)
    return R


def affine_space(R, cols, p):
    """(particular, basis) of {x over cols : R[:, cols] x + R[:, 53] = 0 (mod p)}, or None if no solution."""
    M = [[r[c] % p for c in cols] + [(-r[53]) % p] for r in R]
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
    if any(not any(r[:-1]) and r[-1] for r in M):
        return None
    part = [0] * n
    for r, pc in enumerate(piv):
        part[pc] = M[r][-1]
    basis = []
    for f in (c for c in range(n) if c not in piv):
        x = [0] * n
        x[f] = 1
        for r, pc in enumerate(piv):
            x[pc] = (-M[r][f]) % p
        basis.append(x)
    return np.array(part, dtype=np.int64), np.array(basis, dtype=np.int64).reshape(len(basis), n)


def gf2_solve(A, b):
    """A solution z of A z = b over GF(2), or None."""
    if not A:
        return []
    n = len(A[0])
    R = [list(r) + [bb] for r, bb in zip(A, b)]
    piv, rk = [], 0
    for col in range(n):
        k = next((k for k in range(rk, len(R)) if R[k][col]), None)
        if k is None:
            continue
        R[rk], R[k] = R[k], R[rk]
        for q in range(len(R)):
            if q != rk and R[q][col]:
                R[q] = [x ^ y for x, y in zip(R[q], R[rk])]
        piv.append(col)
        rk += 1
    if any(not any(r[:-1]) and r[-1] for r in R):
        return None
    z = [0] * n
    for r, pc in enumerate(piv):
        z[pc] = R[r][-1]
    return z


def solve(ct, pt, L, s1, s2, F, dmax=DMAX, chunk=200_000):
    """(status, d13, witness). status: CONSISTENT / INCONSISTENT / UNDECIDED / NO_EQUATIONS.
    witness: (A, B, c) alphabets as strings and the constant, when CONSISTENT."""
    R = rows(ct, pt, L, s1, s2, F)
    if not R:
        return "NO_EQUATIONS", None, None
    used = sorted({c for r in R for c in range(NV) if r[c] % 26})
    ga = [k for k, c in enumerate(used) if c < 26]
    gb = [k for k, c in enumerate(used) if 26 <= c < 52]
    s13 = affine_space(R, used, 13)
    s2_ = affine_space(R, used, 2)
    if s13 is None or s2_ is None:
        return "INCONSISTENT", (None if s13 is None else len(s13[1])), None
    p13, B13 = s13
    p2, B2 = s2_
    d = len(B13)
    if d > dmax:
        return "UNDECIDED", d, None
    for start in range(0, 13 ** d, chunk):
        idx = np.arange(start, min(13 ** d, start + chunk), dtype=np.int64)
        coef = np.zeros((len(idx), d), dtype=np.int64)
        x = idx.copy()
        for k in range(d):
            coef[:, k] = x % 13
            x //= 13
        V = (p13[None, :] + (coef @ B13 if d else 0)) % 13
        ok = np.ones(len(V), dtype=bool)
        for g in (ga, gb):
            if len(g) >= 3:
                S = np.sort(V[:, g], axis=1)
                ok &= ~((S[:, 2:] == S[:, :-2]).any(axis=1))
        for row in V[ok]:
            pairs = [(g[p], g[q]) for g in (ga, gb) for p in range(len(g)) for q in range(p + 1, len(g))
                     if row[g[p]] == row[g[q]]]
            A_ = [[int(B2[r, a]) ^ int(B2[r, b]) for r in range(len(B2))] for a, b in pairs]
            rhs = [1 ^ (int(p2[a]) ^ int(p2[b])) for a, b in pairs]
            if len(B2) == 0:
                z = [] if all(v == 0 for v in rhs) else None
            else:
                z = gf2_solve(A_, rhs) if pairs else [0] * len(B2)
            if z is None:
                continue
            v2 = (p2 + (np.array(z, dtype=np.int64) @ B2 if len(B2) else 0)) % 2
            vals = {used[k]: int(row[k] + 13 * ((v2[k] - row[k]) % 2)) for k in range(len(used))}
            return "CONSISTENT", d, witness(vals)
    return "INCONSISTENT", d, None


def witness(vals):
    """Complete the solved ranks to full alphabets (unused letters take the unused ranks in order)."""
    def alphabet(off):
        rank = {l: vals[off + l] for l in range(26) if off + l in vals}
        assert len(set(rank.values())) == len(rank)
        free_r = [r for r in range(26) if r not in rank.values()]
        free_l = [l for l in range(26) if l not in rank]
        rank.update(zip(free_l, free_r))
        out = [""] * 26
        for l, r in rank.items():
            out[r] = AZ[l]
        return "".join(out)
    return alphabet(0), alphabet(26), vals.get(52, 0)
