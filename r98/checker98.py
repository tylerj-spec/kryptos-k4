#!/usr/bin/env python3
"""R98 exact checker (PREREGISTRATION section 2): for every convention and every (PA, CA) in a tier, decide whether
some per-pair key fits every published pair (EXACT) or every pair but one (DROP). Per pair, with
F = IDX_PA[c_up] - IDX_PA[u], H = IDX_CA[c_low] - IDX_CA[w] and G = -H (VIG) or H (BEAU): fit iff (F = G != 0) or
(F = 1 and G = 25). Counts only; no setting is returned. Vectorized with numpy."""
import numpy as np

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
POW = np.array([26 ** j for j in range(13)], dtype=np.int64)   # codes < 26**13 < 2**63: at most 13 pairs


def tier_idx(alphabets):
    idx = np.zeros((len(alphabets), 26), dtype=np.int16)
    for k, a in enumerate(alphabets):
        for pos, ch in enumerate(a):
            idx[k, ord(ch) - 65] = pos
    return idx


def published_pairs(obs, parity):
    """obs: dict position -> plaintext letter. Pairs (i, i+1) with both observed and i = parity (mod 2)."""
    return [i for i in sorted(obs) if i % 2 == parity and i + 1 in obs]


def _count(F, G):
    """Simple reference count: (PA row, CA row) pairs with every column fitting, (F == G != 0) or (F == 1 and G == 25)."""
    m = F.shape[1]
    assert m <= len(POW), "more than 13 pairs"
    if m == 0:
        return F.shape[0] * G.shape[0]
    p = POW[:m]
    gcode = (G.astype(np.int64) * p).sum(axis=1)
    uniq, cnt = np.unique(gcode, return_counts=True)
    ok = ~(F == 0).any(axis=1)
    Fr = F[ok].astype(np.int64)
    codes = (Fr * p).sum(axis=1)
    rows = np.arange(len(codes))
    for j in range(m):                       # alternative digit 25 wherever F_j == 1 (same-column case)
        sel = Fr[rows, j] == 1
        if sel.any():
            codes = np.concatenate([codes, codes[sel] + 24 * p[j]])
            rows = np.concatenate([rows, rows[sel]])
    pos = np.searchsorted(uniq, codes)
    pos = np.minimum(pos, len(uniq) - 1)
    hit = uniq[pos] == codes
    return int(cnt[pos][hit].sum())


def conv_matrices(ct, obs, IDX, conv):
    t, r, o, a = conv
    starts = published_pairs(obs, a)
    L = lambda ch: ord(ch) - 65  # noqa: E731
    u, w, cu, cl = [], [], [], []
    for i in starts:
        first, second = obs[i], obs[i + 1]
        uu, ww = (first, second) if r == 0 else (second, first)
        cc_up, cc_low = (ct[i], ct[i + 1]) if o == 0 else (ct[i + 1], ct[i])
        u.append(L(uu)); w.append(L(ww)); cu.append(L(cc_up)); cl.append(L(cc_low))
    F = (IDX[:, cu] - IDX[:, u]) % 26
    H = (IDX[:, cl] - IDX[:, w]) % 26
    G = (-H) % 26 if t == "VIG" else H
    return F, G, len(starts)


def scan_conv(F, G):
    """EXACT count and DROP count (sum over the dropped pair j) for one convention, sharing codes across j.
    Equal to _count(F, G) and sum_j _count(F without column j, G without column j); checked in the gate."""
    n, m = F.shape
    assert m <= len(POW), "more than 13 pairs"
    if m == 0:
        return F.shape[0] * G.shape[0], 0
    p = POW[:m]
    Fi = F.astype(np.int64)
    Gi = G.astype(np.int64)
    gcode = Gi @ p
    z = (F == 0).sum(axis=1)
    keep = np.nonzero(z <= 1)[0]                       # rows with two zero columns never fit even with one drop
    Fk = Fi[keep]
    codes = Fk @ p
    rows = np.arange(len(keep))
    alt = np.zeros(len(keep), dtype=np.int64)           # bit j set: digit j carries the same-column alternative 25
    for j in range(m):
        sel = np.nonzero(Fk[rows, j] == 1)[0]
        if len(sel):
            codes = np.concatenate([codes, codes[sel] + 24 * p[j]])
            rows = np.concatenate([rows, rows[sel]])
            alt = np.concatenate([alt, alt[sel] | (1 << j)])
    zr = z[keep][rows]

    def hits(gc, q):
        uniq, cnt = np.unique(gc, return_counts=True)
        pos = np.minimum(np.searchsorted(uniq, q), len(uniq) - 1)
        return int(cnt[pos][uniq[pos] == q].sum())

    exact = hits(gcode, codes[zr == 0])
    drop = 0
    for j in range(m):
        fj = Fk[rows, j]
        sel = ((alt >> j) & 1 == 0) & ((zr == 0) | (fj == 0))    # one code per row at digit j; zero only at j allowed
        q = codes[sel] - fj[sel] * p[j]
        drop += hits(gcode - Gi[:, j] * p[j], q)
    return exact, drop


def scan(ct, obs, IDX, conventions, fast=True):
    exact = drop = 0
    any_conv = 0
    per = {}
    for conv in conventions:
        F, G, m = conv_matrices(ct, obs, IDX, conv)
        e, d = scan_conv(F, G) if fast else (_count(F, G), sum(
            _count(np.delete(F, j, axis=1), np.delete(G, j, axis=1)) for j in range(m)))
        per[conv] = (e, d, m)
        exact += e
        drop += d
        any_conv += (e > 0 or d > 0)
    return {"exact_feasible_settings": exact, "drop_feasible_setting_pair_omissions": drop,
            "conventions_with_any_feasible": any_conv}, per


def label_feasible(ct, obs, IDX, conv, pa, ca, allow_drop=False):
    """The same criterion for one (PA row, CA row): fitting pairs count."""
    F, G, m = conv_matrices(ct, obs, IDX, conv)
    f, g = F[pa], G[ca]
    fit = [(f[j] == g[j] and f[j] != 0) or (f[j] == 1 and g[j] == 25) for j in range(m)]
    return sum(fit) >= (m - 1 if allow_drop else m)
