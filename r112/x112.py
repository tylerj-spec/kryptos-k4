"""R112 prototype: exact Slidefair crib check with free alphabets and periodic key, where EVERY crib pair may be
normal or same-column (proper equations for both), optionally one pair dropped. DFS over pair branches with
incremental elimination mod 2 and mod 13; prune on inconsistency or forced collision (both monotone)."""
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def pair_starts(n, a):
    return list(range(a, n - 1, 2))

def crib_pairs(ct, hyp, conv, p):
    t, r, o, a = conv
    out = []
    for j, i in enumerate(pair_starts(len(ct), a)):
        if hyp[i] is None or hyp[i + 1] is None:
            continue
        u, w = (hyp[i], hyp[i + 1]) if r == 0 else (hyp[i + 1], hyp[i])
        cu, cl = (ct[i], ct[i + 1]) if o == 0 else (ct[i + 1], ct[i])
        out.append((j if p is None else j % p, u, w, cu, cl))
    return out

def eqs(pr, t, mode):
    """[(coef dict, rhs)] for one pair; mode 'N' normal, 'S' same-column. Columns: a 0-25, b 26-51, k 52+s."""
    s, u, w, cu, cl = pr
    A = lambda x: AZ.index(x)
    B = lambda x: 26 + AZ.index(x)
    K = 52 + s
    def e(terms, rhs):
        d = {}
        for c, v in terms:
            d[c] = d.get(c, 0) + v
        return (d, rhs)
    if t == "VIG":
        if mode == "N":
            return [e([(A(cu), 1), (B(w), -1), (K, 1)], 0), e([(B(cl), 1), (A(u), -1), (K, -1)], 0)]
        return [e([(A(cu), 1), (A(u), -1)], 1), e([(B(cl), 1), (B(w), -1)], 1), e([(A(u), 1), (B(w), -1), (K, 1)], 0)]
    if mode == "N":
        return [e([(A(cu), 1), (B(w), 1), (K, -1)], 0), e([(B(cl), 1), (A(u), 1), (K, -1)], 0)]
    return [e([(A(cu), 1), (A(u), -1)], 1), e([(B(cl), 1), (B(w), -1)], -1), e([(A(u), 1), (B(w), 1), (K, -1)], 0)]

class Sys:
    """Row-reduced affine system mod p: pivots {col: (row dict, rhs)} with row[col] = 1, pivot cols eliminated elsewhere."""
    def __init__(self, p, piv=None):
        self.p = p
        self.piv = dict(piv) if piv else {}
    def reduce(self, d, rhs):
        p = self.p
        d = {c: v % p for c, v in d.items() if v % p}
        rhs %= p
        changed = True
        while changed:
            changed = False
            for c in [c for c in d if c in self.piv]:
                f = d[c]
                row, r = self.piv[c]
                for cc, vv in row.items():
                    d[cc] = (d.get(cc, 0) - f * vv) % p
                    if d[cc] == 0:
                        del d[cc]
                rhs = (rhs - f * r) % p
                changed = True
        return d, rhs
    def add(self, d, rhs):
        """False if inconsistent."""
        p = self.p
        d, rhs = self.reduce(d, rhs)
        if not d:
            return rhs == 0
        c = min(d)
        inv = pow(d[c], -1, p)
        d = {cc: (vv * inv) % p for cc, vv in d.items()}
        rhs = (rhs * inv) % p
        # eliminate c from existing pivot rows
        newpiv = {}
        for pc, (row, r) in self.piv.items():
            if c in row:
                f = row[c]
                row = dict(row)
                for cc, vv in d.items():
                    row[cc] = (row.get(cc, 0) - f * vv) % p
                    if row[cc] == 0:
                        del row[cc]
                r = (r - f * rhs) % p
            newpiv[pc] = (row, r)
        newpiv[c] = (d, rhs)
        self.piv = newpiv
        return True
    def signature(self, col):
        d, rhs = self.reduce({col: 1}, 0)
        return (tuple(sorted(d.items())), (-rhs) % self.p)   # value = -rhs + free part... sign irrelevant for equality

def collision(s2, s13, groups):
    for g in groups:
        sig13 = {}
        for x in g:
            sig13.setdefault(s13.signature(x), []).append(x)
        for cls in sig13.values():
            if len(cls) >= 3:
                return True
            if len(cls) == 2 and s2.signature(cls[0]) == s2.signature(cls[1]):
                return True
    return False

def check(ct, hyp, conv, p, allow_drop=False):
    """EXCL if no branch assignment (each crib pair normal or same-column; with allow_drop also at most one pair
    set aside) survives; else OPEN."""
    t = conv[0]
    pairs = crib_pairs(ct, hyp, conv, p)
    if any(u == cu for _, u, _, cu, _ in pairs) and not allow_drop:
        return "EXCL"
    ident = [q for q, pr in enumerate(pairs) if pr[1] == pr[3]]
    if len(ident) >= 2:
        return "EXCL"
    groups_all = (sorted({AZ.index(x) for _, u, _, cu, _ in pairs for x in (u, cu)}),
                  sorted({26 + AZ.index(x) for _, _, w, _, cl in pairs for x in (w, cl)}))
    def dfs(q, s2, s13, dropped):
        if q == len(pairs):
            return True
        pr = pairs[q]
        modes = [] if pr[1] == pr[3] else ["N", "S"]
        if allow_drop and not dropped:
            modes = modes + ["D"]
        for m in modes:
            if m == "D":
                if dfs(q + 1, s2, s13, True):
                    return True
                continue
            a2, a13 = Sys(2, s2.piv), Sys(13, s13.piv)
            ok = all(a2.add(d, r) and a13.add(d, r) for d, r in eqs(pr, t, m))
            if ok and not collision(a2, a13, groups_all):
                if dfs(q + 1, a2, a13, dropped):
                    return True
        return False
    return "OPEN" if dfs(0, Sys(2), Sys(13), False) else "EXCL"
