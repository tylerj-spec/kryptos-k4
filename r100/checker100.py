#!/usr/bin/env python3
"""R100 exact checker (PREREGISTRATION section 2). Necessary conditions from the direct links (i, i+L), both letters
published: B^-1(C_{i+L}) - s2*F^-1(P_i) - s1*A^-1(P_{i+L}) = c for one c. Per (lag, signs, F), split each link into a
B-side value g and an A-side value h; c is eliminated against the first link, and (A, B) fits iff the B-code of
(g_k - g_0) equals the A-code of (h_k - h_0). Counts by a sort-and-search join over the tier x tier; codes hold at most
13 differences (int64), longer link sets are joined on their first 14 links and the matched pairs verified on all.
DROP (one wrong published letter): candidates from two link groups that no single cut touches together, then each
candidate is verified directly. A simple path (direct residuals over all pairs of a small tier) cross-checks it."""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):   # one thread: the CPU cap is aggregate
    os.environ.setdefault(_v, "1")
import numpy as np  # noqa: E402

SIGNS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
FEEDBACK = ("A", "B", "AZ")


def tier_idxt(alphabets):
    """(26, n) int16: IDXT[letter, row] = rank of letter in alphabet row."""
    idx = np.zeros((26, len(alphabets)), dtype=np.int16)
    for k, a in enumerate(alphabets):
        for pos, ch in enumerate(a):
            idx[ord(ch) - 65, k] = pos
    return idx


def links(obs, L):
    return [(i, i + L) for i in sorted(obs) if i + L in obs]


def components(lk):
    """Connected components of the link graph (positions joined by links), as lists of link indices."""
    par = {}

    def find(x):
        while par.setdefault(x, x) != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    for i, j in lk:
        par[find(i)] = find(j)
    comps = {}
    for k, (i, j) in enumerate(lk):
        comps.setdefault(find(i), []).append(k)
    return sorted(comps.values())


CAP = 10                                   # links per join: 9 differences, exact in float64 (26**9 < 2**53)
POWF = np.array([26.0 ** j for j in range(CAP - 1)])


def variants(ct, obs, IDXT, lk):
    """A-side h and B-side g per link for every (signs, F): g - h = c.
    Returns hv {hkey: [h_k]}, gv {gkey: [g_k]}, combo {(s1, s2, F): (hkey, gkey)}; int16 vectors over the tier."""
    X = lambda ch: IDXT[ord(ch) - 65]  # noqa: E731
    xj = [X(obs[j]) for i, j in lk]
    xi = [X(obs[i]) for i, j in lk]
    yj = [X(ct[j]) for i, j in lk]
    az = [ord(obs[i]) - 65 for i, j in lk]
    hv, gv, combo = {}, {"A": yj}, {}
    for s1 in (1, -1):
        hv[("BZ", s1)] = [s1 * v for v in xj]
        for s2 in (1, -1):
            hv[("A", s1, s2)] = [s1 * a + s2 * b for a, b in zip(xj, xi)]
    for s2 in (1, -1):
        gv[("B", s2)] = [y - s2 * b for y, b in zip(yj, xi)]
        gv[("AZ", s2)] = [y - s2 * z for y, z in zip(yj, az)]
    for s1, s2 in SIGNS:
        combo[(s1, s2, "A")] = (("A", s1, s2), "A")
        combo[(s1, s2, "B")] = (("BZ", s1), ("B", s2))
        combo[(s1, s2, "AZ")] = (("BZ", s1), ("AZ", s2))
    return hv, gv, combo


def fcode(V, ks):
    """int64 code of V[k] - V[ks[0]] (mod 26), k in ks[1:], at most CAP - 1 differences (float64 product, exact)."""
    d = len(ks) - 1
    assert 1 <= d <= CAP - 1
    D = np.empty((d, V[0].shape[0]), dtype=np.float64)
    for r, k in enumerate(ks[1:]):
        D[r] = (V[k] - V[ks[0]]) % 26
    return (POWF[:d] @ D).astype(np.int64)


class Sorted:
    def __init__(self, cb):
        self.order = np.argsort(cb, kind="stable")
        self.s = cb[self.order]

    def count(self, ca):
        return int((np.searchsorted(self.s, ca, "right") - np.searchsorted(self.s, ca, "left")).sum())

    def pair_chunks(self, ca, chunk=1_000_000):
        """All (a, b) with ca[a] == cb[b], yielded in chunks of about `chunk` pairs (bounded memory)."""
        lo = np.searchsorted(self.s, ca, "left")
        n = np.searchsorted(self.s, ca, "right") - lo
        rows = np.nonzero(n)[0]
        if len(rows) == 0:
            return
        cum = np.cumsum(n[rows])
        start = 0
        while start < len(rows):
            stop = int(np.searchsorted(cum, (cum[start - 1] if start else 0) + chunk, "right"))
            stop = max(stop, start + 1)
            r = rows[start:stop]
            nr = n[r]
            a = np.repeat(r, nr)
            offs = np.arange(nr.sum()) - np.repeat(np.cumsum(nr) - nr, nr)
            yield a, self.order[np.repeat(lo[r], nr) + offs]
            start = stop


def residuals(H, G, a, b):
    """(pairs, links) residuals g - h (mod 26, int16) for the given (A row, B row) pairs."""
    return np.stack([(G[k][b] - H[k][a]) % 26 for k in range(len(H))], axis=1)


def drop_ok(R, cuts):
    """For each pair: some cut (a list of link indices to remove) leaves all remaining residuals equal."""
    ok = np.zeros(R.shape[0], dtype=bool)
    for cut in cuts:
        keep = [k for k in range(R.shape[1]) if k not in cut]
        if not keep:
            ok[:] = True
            continue
        Rk = R[:, keep]
        ok |= (Rk == Rk[:, :1]).all(axis=1)
    return ok


def cut_sets(obs, lk):
    return [[k for k, (i, j) in enumerate(lk) if p in (i, j)] for p in sorted(obs)
            if any(p in e for e in lk)]


def groups(lk):
    """Two groups of link-graph components, balanced by link count; no single cut touches both."""
    g1, g2, n1, n2 = [], [], 0, 0
    for comp in sorted(components(lk), key=len, reverse=True):
        if n1 <= n2:
            g1 += comp
            n1 += len(comp)
        else:
            g2 += comp
            n2 += len(comp)
    return sorted(g1), sorted(g2)


def scan(ct, obs, IDXT, lags, drop_lags=()):
    """{(L, s1, s2, F): (links, exact, drop or None)} for the given lags (fast path)."""
    out = {}
    nB = IDXT.shape[1]
    for L in lags:
        lk = links(obs, L)
        m = len(lk)
        if m < 2:
            continue
        hv, gv, combo = variants(ct, obs, IDXT, lk)
        cuts = cut_sets(obs, lk)
        subsets = [list(range(min(m, CAP)))]
        all_pairs = False
        if L in drop_lags:
            g1, g2 = groups(lk)
            if len(g1) >= 2 and len(g2) >= 2:
                subsets += [g1[:CAP], g2[:CAP]]
            else:                                          # small synthetic tiers only: candidates = every pair
                assert nB * nB <= 4_000_000, "DROP lag without two usable link groups on a large tier"
                all_pairs = True
        res = {key: [] for key in combo}
        for si, ks in enumerate(subsets):
            hc = {k: fcode(v, ks) for k, v in hv.items()}
            gs = {k: Sorted(fcode(v, ks)) for k, v in gv.items()}
            for key, (hk, gk) in combo.items():
                if si == 0 and m <= CAP:
                    res[key].append(gs[gk].count(hc[hk]))
                else:
                    res[key].append((gs[gk], hc[hk]))
        for key, (hk, gk) in combo.items():
            H, G = hv[hk], gv[gk]
            first = res[key][0]
            if isinstance(first, int):
                e = first
            else:                                          # joined on the first CAP links; verify all m links
                e = 0
                for a, b in first[0].pair_chunks(first[1]):
                    R = residuals(H, G, a, b)
                    e += int((R == R[:, :1]).all(axis=1).sum())
            d = None
            if L in drop_lags:
                keys = []
                if all_pairs:
                    sources = [[np.divmod(np.arange(nB * nB), nB)]]
                else:
                    sources = [res[key][1][0].pair_chunks(res[key][1][1]), res[key][2][0].pair_chunks(res[key][2][1])]
                for src in sources:
                    for a, b in src:
                        ok = drop_ok(residuals(H, G, a, b), cuts)
                        keys.append(a[ok].astype(np.int64) * nB + b[ok])
                d = int(len(np.unique(np.concatenate(keys)))) if keys else 0
            out[(L,) + key] = (m, e, d)
    return out


def side_values(ct, obs, IDXT, lk, s1, s2, F):
    """(H, G) for one (signs, F), written out directly (used by the simple path)."""
    H, G = [], []
    for i, j in lk:
        xj = IDXT[ord(obs[j]) - 65]
        yj = IDXT[ord(ct[j]) - 65]
        if F == "A":
            H.append(s1 * xj + s2 * IDXT[ord(obs[i]) - 65])
            G.append(yj)
        elif F == "B":
            H.append(s1 * xj)
            G.append(yj - s2 * IDXT[ord(obs[i]) - 65])
        else:
            H.append(s1 * xj)
            G.append(yj - s2 * (ord(obs[i]) - 65))
    return H, G


def scan_simple(ct, obs, IDXT, lags, drop_lags=()):
    """Second path: direct residuals for every (A, B) pair of a SMALL tier (no codes, joins or candidates)."""
    out = {}
    n = IDXT.shape[1]
    a, b = np.divmod(np.arange(n * n), n)
    for L in lags:
        lk = links(obs, L)
        if len(lk) < 2:
            continue
        cuts = cut_sets(obs, lk)
        for s1, s2 in SIGNS:
            for F in FEEDBACK:
                H, G = side_values(ct, obs, IDXT, lk, s1, s2, F)
                R = residuals(H, G, a, b)
                e = int((R == R[:, :1]).all(axis=1).sum())
                d = int(drop_ok(R, cuts).sum()) if L in drop_lags else None
                out[(L, s1, s2, F)] = (len(lk), e, d)
    return out
