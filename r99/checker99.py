#!/usr/bin/env python3
"""R99 exact checker (PREREGISTRATION section 2). For every lag, signs and alphabet of a tier: is there a constant c
satisfying every chain link (EXACT), or every link once the chain is cut at one published position (DROP)?
Fast path: per link a 26-bit mask of the c values solving a*c = b (mod 26), AND-ed over links, prefix/suffix ANDs for
the cuts. Simple path (cross-check): brute force over c with step-by-step propagation. Counts only."""
import numpy as np

SIGNS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
FULL = (1 << 26) - 1
# MASK[a][b] = bitmask of c in Z26 with a*c = b (mod 26)
MASK = np.zeros((26, 26), dtype=np.int64)
for _a in range(26):
    for _c in range(26):
        MASK[_a, (_a * _c) % 26] |= 1 << _c
MASK32 = MASK.astype(np.int32)                          # 26 bits fit in int32


def tier_idx(alphabets):
    idx = np.zeros((len(alphabets), 26), dtype=np.int16)
    for k, a in enumerate(alphabets):
        for pos, ch in enumerate(a):
            idx[k, ord(ch) - 65] = pos
    return idx


def links(positions, L):
    """Consecutive published positions in each residue chain mod L, as (i, j, t), sorted by chain then position."""
    chains = {}
    for p in sorted(positions):
        chains.setdefault(p % L, []).append(p)
    out = []
    for r in sorted(chains):
        ch = chains[r]
        out += [(a, b, (b - a) // L) for a, b in zip(ch, ch[1:])]
    return out


def _letters(s):
    return [ord(ch) - 65 for ch in s]


def scan_L(ct, obs, IDXT, L):
    """{(s1, s2): (links, EXACT rows, DROP rows)} for one lag, all four signs. IDXT: (26, n) int16, contiguous.
    The ciphertext sums depend only on sigma = -s1*s2, so they are computed once per sigma."""
    lk = links(obs, L)
    n = IDXT.shape[1]
    if not lk:
        return {sg: (0, n, n) for sg in SIGNS}
    cl = _letters(ct)
    m = len(lk)
    adj = {}
    for p in obs:
        a = [k for k, (i, j, _) in enumerate(lk) if p in (i, j)]
        if a:
            assert max(a) + 1 - min(a) == len(a)     # adjacent links are consecutive in the sorted list
            adj[p] = (min(a), max(a) + 1)
    cuts = sorted(set(adj.values()))
    acc = {}
    for sigma in (1, -1):
        rows = []
        for i, j, t in lk:
            a_ = np.zeros(n, dtype=np.int16)
            for u in range(1, t + 1):                  # sum_u sigma^(t-u) y_{i+uL}
                if sigma ** (t - u) == 1:
                    a_ += IDXT[cl[i + u * L]]
                else:
                    a_ -= IDXT[cl[i + u * L]]
            rows.append(a_)
        acc[sigma] = rows
    out = {}
    for s1, s2 in SIGNS:
        sigma = -s1 * s2
        M = np.empty((m, n), dtype=np.int32)
        for k, (i, j, t) in enumerate(lk):
            b = IDXT[ord(obs[j]) - 65] - (sigma ** t) * IDXT[ord(obs[i]) - 65] - s1 * acc[sigma][k]
            b %= 26
            a = (-s1 * sum(sigma ** v for v in range(t))) % 26
            M[k] = MASK32[a][b]
        pre = np.empty((m + 1, n), dtype=np.int32)
        pre[0] = FULL
        for k in range(m):
            np.bitwise_and(pre[k], M[k], out=pre[k + 1])
        exact = pre[m] != 0
        suf = np.empty((m + 1, n), dtype=np.int32)
        suf[m] = FULL
        for k in range(m - 1, -1, -1):
            np.bitwise_and(suf[k + 1], M[k], out=suf[k])
        drop = exact.copy()
        for lo, hi in cuts:
            drop |= (pre[lo] & suf[hi]) != 0
        out[(s1, s2)] = (m, int(exact.sum()), int(drop.sum()))
    return out


def scan_lag(ct, obs, IDX, L, s1, s2):
    """(links, EXACT rows, DROP rows) for one lag and signs (fast path)."""
    return scan_L(ct, obs, np.ascontiguousarray(IDX.T.astype(np.int16)), L)[(s1, s2)]


def scan_lag_simple(ct, obs, IDX, L, s1, s2):
    """Second path: for each c, propagate x along every link step by step and compare."""
    lk = links(obs, L)
    n = IDX.shape[0]
    if not lk:
        return 0, n, n
    cl = _letters(ct)
    ok = np.zeros((26, len(lk), n), dtype=bool)
    for c in range(26):
        for k, (i, j, t) in enumerate(lk):
            x = IDX[:, ord(obs[i]) - 65].astype(np.int64)
            for u in range(1, t + 1):
                q = i + u * L
                x = (s1 * (IDX[:, cl[q]] - s2 * x - c)) % 26
            ok[c, k] = x == IDX[:, ord(obs[j]) - 65]
    exact = ok.all(axis=1).any(axis=0)
    drop = exact.copy()
    for p in obs:
        keep = [k for k, (i, j, _) in enumerate(lk) if p not in (i, j)]
        if len(keep) == len(lk):
            continue
        drop |= ok[:, keep, :].all(axis=1).any(axis=0) if keep else True
    return len(lk), int(exact.sum()), int(drop.sum())


def scan(ct, obs, IDX, lags=range(1, 97), fast=True):
    """Per (L, signs): (links, exact, drop), for lags with at least one link."""
    IDXT = np.ascontiguousarray(IDX.T.astype(np.int16))
    out = {}
    for L in lags:
        if not links(obs, L):
            continue
        if fast:
            for sg, v in scan_L(ct, obs, IDXT, L).items():
                out[(L,) + sg] = v
        else:
            for s1, s2 in SIGNS:
                out[(L, s1, s2)] = scan_lag_simple(ct, obs, IDX, L, s1, s2)
    return out


def label_feasible(ct, obs, A, L, s1, s2, cut=None):
    """The criterion for one alphabet (string), straight from the definition: some c fits every link (with
    cut = a published position, the links adjacent to it are skipped)."""
    lk = [(i, j, t) for i, j, t in links(obs, L) if cut not in (i, j)]
    for c in range(26):
        good = True
        for i, j, t in lk:
            x = A.index(obs[i])
            for u in range(1, t + 1):
                x = (s1 * (A.index(ct[i + u * L]) - s2 * x - c)) % 26
            if x != A.index(obs[j]):
                good = False
                break
        if good:
            return True
    return False
