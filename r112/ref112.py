"""R112 reference: brute force over EVERY branch assignment (each crib pair normal or same-column, optionally one pair
set aside), no pruning; per leaf, the affine solution set mod 2 and mod 13 from an explicit particular solution plus
null-space basis (no incremental pivots), then the forced-collision rule on letter values. Standard library."""
import itertools
import x112 as X

def solve_affine(rows, nv, p):
    M = [[r.get(c, 0) % p for c in range(nv)] + [rhs % p] for r, rhs in rows]
    piv, rk = [], 0
    for col in range(nv):
        k = next((k for k in range(rk, len(M)) if M[k][col]), None)
        if k is None:
            continue
        M[rk], M[k] = M[k], M[rk]
        inv = pow(M[rk][col], -1, p)
        M[rk] = [(x * inv) % p for x in M[rk]]
        for q in range(len(M)):
            if q != rk and M[q][col]:
                f = M[q][col]
                M[q] = [(x - f * y) % p for x, y in zip(M[q], M[rk])]
        piv.append(col)
        rk += 1
    if any(not any(r[:-1]) and r[-1] for r in M):
        return None
    part = [0] * nv
    for r, pc in enumerate(piv):
        part[pc] = M[r][-1]
    basis = []
    for f in (c for c in range(nv) if c not in piv):
        x = [0] * nv
        x[f] = 1
        for r, pc in enumerate(piv):
            x[pc] = (-M[r][f]) % p
        basis.append(x)
    return part, basis

def leaf_excluded(rows, nv, groups):
    S2, S13 = solve_affine(rows, nv, 2), solve_affine(rows, nv, 13)
    if S2 is None or S13 is None:
        return True
    def sig(S, c):
        part, basis = S
        return (part[c],) + tuple(b[c] for b in basis)
    for g in groups:
        cls = {}
        for x in g:
            cls.setdefault(sig(S13, x), []).append(x)
        for v in cls.values():
            if len(v) >= 3:
                return True
            if len(v) == 2 and sig(S2, v[0]) == sig(S2, v[1]):
                return True
    return False

def check(ct, hyp, conv, p, allow_drop=False):
    t = conv[0]
    pairs = X.crib_pairs(ct, hyp, conv, p)
    nslots = len(X.pair_starts(len(ct), conv[3])) if p is None else p
    nv = 52 + nslots
    groups = (sorted({X.AZ.index(x) for _, u, _, cu, _ in pairs for x in (u, cu)}),
              sorted({26 + X.AZ.index(x) for _, _, w, _, cl in pairs for x in (w, cl)}))
    drops = [None] + (list(range(len(pairs))) if allow_drop else [])
    for dq in drops:
        kept = [pr for q, pr in enumerate(pairs) if q != dq]
        if any(pr[1] == pr[3] for pr in kept):
            continue
        for modes in itertools.product("NS", repeat=len(kept)):
            rows = [e for pr, m in zip(kept, modes) for e in X.eqs(pr, t, m)]
            if not leaf_excluded(rows, nv, groups):
                return "OPEN"
    return "EXCL"
