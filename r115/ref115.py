"""R115 reference for X115 (shares no code with it): an explicit unknown key value at EVERY position from the first to
the last crib position, the recurrence written out as one equation per position, the full coefficient vector a used
directly (no mod-2 / mod-13 decomposition of a), dense Gauss-Jordan elimination with numpy, and the collision rule
applied to particular-solution plus null-space signatures."""
import numpy as np

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def build(ct, hyp, a, drop=None):
    Q = sorted(hyp)
    L = len(a)
    t0, t1 = Q[0], Q[-1]
    kept = [n for n in Q if n != drop]
    xl = sorted({hyp[n] for n in kept})
    yl = sorted({ct[n] for n in kept})
    col = {("x", c): i for i, c in enumerate(xl)}
    col.update({("y", c): len(xl) + i for i, c in enumerate(yl)})
    base = len(xl) + len(yl)
    for n in range(t0, t1 + 1):
        col[("k", n)] = base + n - t0
    col[("d",)] = base + t1 - t0 + 1
    nv = len(col)
    eqs = []
    for n in range(t0 + L, t1 + 1):
        r = np.zeros(nv + 1, dtype=np.int64)
        r[col[("k", n)]] += 1
        for j in range(1, L + 1):
            r[col[("k", n - j)]] -= a[j - 1]
        r[col[("d",)]] -= 1
        eqs.append(r)
    for n in kept:
        r = np.zeros(nv + 1, dtype=np.int64)
        r[col[("y", ct[n])]] += 1
        r[col[("x", hyp[n])]] -= 1
        r[col[("k", n)]] -= 1
        eqs.append(r)
    return np.array(eqs), col, xl, yl


def solve(M, p):
    """Gauss-Jordan mod p on the augmented matrix; None if inconsistent, else (reduced rows, pivot columns)."""
    M = M % p
    nr, nc = M.shape
    nv = nc - 1
    piv = []
    r = 0
    for c in range(nv):
        nz = np.nonzero(M[r:, c])[0]
        if len(nz) == 0:
            continue
        k = r + nz[0]
        if k != r:
            M[[r, k]] = M[[k, r]]
        M[r] = (M[r] * pow(int(M[r, c]), -1, p)) % p
        f = M[:, c].copy()
        f[r] = 0
        M = (M - np.outer(f, M[r])) % p
        piv.append(c)
        r += 1
        if r == nr:
            break
    if np.any((M[:, :nv] == 0).all(axis=1) & (M[:, nv] != 0)):
        return None
    return M[:len(piv)], piv


def signatures(R, piv, nv, p):
    """Per variable: (constant, coefficients on the free variables), from x_pc = rhs - sum_f R[r, f] x_f."""
    free = [c for c in range(nv) if c not in set(piv)]
    sig = {}
    for f in free:
        sig[f] = (0,) + tuple(int(f == g) for g in free)
    for r, pc in enumerate(piv):
        sig[pc] = (int(R[r, nv]),) + tuple(int((-R[r, g]) % p) for g in free)
    return sig


def excluded(ct, hyp, a, drop=None):
    M, col, xl, yl = build(ct, hyp, a, drop)
    nv = M.shape[1] - 1
    sigs = {}
    for p in (2, 13):
        S = solve(M.copy(), p)
        if S is None:
            return True
        sigs[p] = signatures(S[0], S[1], nv, p)
    for group in ([col[("x", c)] for c in xl], [col[("y", c)] for c in yl]):
        by13 = {}
        for v in group:
            by13.setdefault(sigs[13][v], []).append(v)
        for cls in by13.values():
            if len(cls) >= 3:
                return True
            if len(cls) == 2 and sigs[2][cls[0]] == sigs[2][cls[1]]:
                return True
    return False


def verdict(ct, hyp, a, allow_drop=False):
    if not excluded(ct, hyp, a):
        return "OPEN"
    if allow_drop and all(excluded(ct, hyp, a, q) for q in sorted(hyp)):
        return "EXCL_DROP"
    return "EXCL"
