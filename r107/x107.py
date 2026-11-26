#!/usr/bin/env python3
"""R107 exact crib check X107 for Slidefair (r98 reference, 16 conventions) with FREE alphabets PA, CA and a key
that is periodic over pairs with period p (p = None: any key, one free key value per pair). Sound for exclusion only.

Per pair (upper input u, lower input w, key k, outputs cu upper and cl lower), with a = PA^-1 and b = CA^-1:
  normal, VIG:  a(cu) - b(w) + k = 0,  b(cl) - a(u) - k = 0;   normal, BEAU: a(cu) + b(w) - k = 0,  b(cl) + a(u) - k = 0
  every pair:   cu != u (letter identity; a same-column pair also has a(cu) = a(u) + 1).
A branch (EXACT: every crib pair normal; DROP_q: pair q set aside, any rule or an error there) is excluded if a kept
pair has cu = u, or if the homogeneous normal-case system forces a collision: two distinct letters of one alphabet
equal mod 2 and mod 13 on every solution, or three equal mod 13. Synthetic use; standard library only."""
import itertools

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def pair_starts(n, a):
    return list(range(a, n - 1, 2))


def crib_pairs(ct, hyp, conv, p):
    """(slot, u, w, cu, cl) for every pair whose two plaintext letters are given."""
    t, r, o, a = conv
    out = []
    for j, i in enumerate(pair_starts(len(ct), a)):
        if hyp[i] is None or hyp[i + 1] is None:
            continue
        u, w = (hyp[i], hyp[i + 1]) if r == 0 else (hyp[i + 1], hyp[i])
        cu, cl = (ct[i], ct[i + 1]) if o == 0 else (ct[i + 1], ct[i])
        out.append((j if p is None else j % p, u, w, cu, cl))
    return out


def rows_for(pairs, t, nslots):
    """Coefficient rows over [a(A..Z), b(A..Z), k(slot 0..nslots-1)]."""
    nv = 52 + nslots
    rows = []
    for s, u, w, cu, cl in pairs:
        r1, r2 = [0] * nv, [0] * nv
        A_cu, A_u, B_w, B_cl, K = AZ.index(cu), AZ.index(u), 26 + AZ.index(w), 26 + AZ.index(cl), 52 + s
        if t == "VIG":
            r1[A_cu] += 1; r1[B_w] -= 1; r1[K] += 1                     # noqa: E702
            r2[B_cl] += 1; r2[A_u] -= 1; r2[K] -= 1                     # noqa: E702
        else:
            r1[A_cu] += 1; r1[B_w] += 1; r1[K] -= 1                     # noqa: E702
            r2[B_cl] += 1; r2[A_u] += 1; r2[K] -= 1                     # noqa: E702
        rows += [r1, r2]
    return rows


def nullspace(rows, nv, p):
    M = [[x % p for x in r] for r in rows]
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
    basis = []
    for f in (c for c in range(nv) if c not in piv):
        x = [0] * nv
        x[f] = 1
        for r, pc in enumerate(piv):
            x[pc] = (-M[r][f]) % p
        basis.append(x)
    return basis


def forced_classes(basis, cols, p):
    """Classes of columns whose values agree on every solution (same coordinates in every basis vector)."""
    cl = {}
    for c in cols:
        cl.setdefault(tuple(v[c] for v in basis), []).append(c)
    return [v for v in cl.values() if len(v) > 1]


def collision_nullspace(rows, nv, cols_a, cols_b):
    N2, N13 = nullspace(rows, nv, 2), nullspace(rows, nv, 13)
    for cols in (cols_a, cols_b):
        c13, c2 = forced_classes(N13, cols, 13), forced_classes(N2, cols, 2)
        if any(len(v) >= 3 for v in c13):
            return True
        p13 = {frozenset(q) for v in c13 for q in itertools.combinations(v, 2)}
        p2 = {frozenset(q) for v in c2 for q in itertools.combinations(v, 2)}
        if p13 & p2:
            return True
    return False


def branch_excluded(pairs, t, nslots, collision=collision_nullspace):
    if any(u == cu for _, u, _, cu, _ in pairs):
        return True
    if not pairs:
        return False
    rows = rows_for(pairs, t, nslots)
    cols_a = sorted({AZ.index(x) for _, u, _, cu, _ in pairs for x in (u, cu)})
    cols_b = sorted({26 + AZ.index(x) for _, _, w, _, cl in pairs for x in (w, cl)})
    return collision(rows, 52 + nslots, cols_a, cols_b)


def check(ct, hyp, conv, p, collision=collision_nullspace):
    """EXCLUDED_DROP, EXCLUDED_EXACT (only the all-normal branch excluded) or OPEN (not excluded; not a proof of
    consistency)."""
    pairs = crib_pairs(ct, hyp, conv, p)
    nslots = len(pair_starts(len(ct), conv[3])) if p is None else p
    t = conv[0]
    if not branch_excluded(pairs, t, nslots, collision):
        return "OPEN"
    if all(branch_excluded(pairs[:q] + pairs[q + 1:], t, nslots, collision) for q in range(len(pairs))):
        return "EXCLUDED_DROP"
    return "EXCLUDED_EXACT"
