"""R115 exact crib check X115: a keystream from an affine linear recurrence of order L over Z26 with BOTH alphabets
free (Quagmire IV type). Model: y(c_n) = x(p_n) + k_n (mod 26), with x = PA^-1 and y = CA^-1 arbitrary bijections;
Beaufort and Variant Beaufort reduce to this form under free alphabets (L92). The key obeys
k_n = a_1 k_{n-1} + ... + a_L k_{n-L} + d (mod 26) from the first crib position t0 onward, a superset of keys generated
from position 0, so an exclusion here also excludes those.

For a coefficient vector a, every crib equation is linear in x, y, the state (k_t0, ..., k_t0+L-1) and d. The system
mod 2 depends only on a mod 2, and the system mod 13 only on a mod 13. Each is row-reduced once (R112's Sys) and the
verdicts are combined:
- EXCL if either system is inconsistent or the two force a collision: two letters of one alphabet equal mod 2 and
  mod 13, or three equal mod 13;
- EXCL_DROP if that holds with every single crib equation set aside in turn;
- otherwise OPEN, which is not a consistency proof.
Columns: x 0-25, y 26-51, state 52..52+L-1, d 52+L."""
import itertools
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent.parent / "r112")]
import x112  # noqa: E402  (Sys: incremental row reduction mod p, as validated in R112)

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def forms(a, Q, m):
    """{n: F_n} with k_n = F_n . (k_t0, ..., k_t0+L-1, d) mod m, for n in Q (sorted crib positions)."""
    L = len(a)
    t0 = Q[0]
    rows = [[1 if j == i else 0 for j in range(L + 1)] for i in range(L)]
    for n in range(t0 + L, Q[-1] + 1):
        r = [0] * (L + 1)
        for j in range(1, L + 1):
            pr = rows[n - t0 - j]
            for c in range(L + 1):
                r[c] = (r[c] + a[j - 1] * pr[c]) % m
        r[L] = (r[L] + 1) % m
        rows.append(r)
    return {n: rows[n - t0] for n in Q}


def rows(ct, hyp, Q, a, m, drop=None):
    """The crib equations mod m as (coef dict, rhs): y(c_n) - x(p_n) - F_n . state = 0."""
    L = len(a)
    F = forms(a, Q, m)
    out = []
    for n in Q:
        if n == drop:
            continue
        d = {26 + AZ.index(ct[n]): 1}
        d[AZ.index(hyp[n])] = d.get(AZ.index(hyp[n]), 0) - 1
        for c in range(L + 1):
            if F[n][c]:
                d[52 + c] = d.get(52 + c, 0) - F[n][c]
        out.append((d, 0))
    return out


class Checker:
    def __init__(self, ct, hyp):
        self.ct, self.hyp = ct, hyp
        self.Q = sorted(hyp)
        self.memo = {}

    def flag(self, m, am, drop):
        """(inconsistent or forced triple mod 13, frozenset of letter pairs forced equal mod m)."""
        key = (m, am, drop)
        if key in self.memo:
            return self.memo[key]
        S = x112.Sys(m)
        bad, pairs = False, set()
        for d, r in rows(self.ct, self.hyp, self.Q, am, m, drop):
            if not S.add(d, r):
                bad = True
                break
        if not bad:
            kept = [n for n in self.Q if n != drop]
            for g in (sorted({AZ.index(self.hyp[n]) for n in kept}), sorted({26 + AZ.index(self.ct[n]) for n in kept})):
                cls = {}
                for c in g:
                    cls.setdefault(S.signature(c), []).append(c)
                for v in cls.values():
                    if m == 13 and len(v) >= 3:
                        bad = True
                    pairs.update(itertools.combinations(v, 2))
        out = (bad, frozenset(pairs))
        self.memo[key] = out
        return out

    def excluded(self, a, drop=None):
        b2, p2 = self.flag(2, tuple(v % 2 for v in a), drop)
        if b2:
            return True
        b13, p13 = self.flag(13, tuple(v % 13 for v in a), drop)
        return b13 or not p2.isdisjoint(p13)

    def verdict(self, a, allow_drop=False):
        if not self.excluded(a):
            return "OPEN"
        if allow_drop and all(self.excluded(a, q) for q in self.Q):
            return "EXCL_DROP"
        return "EXCL"


def scan(ct, hyp, L, allow_drop=False):
    """Counts of verdicts over every a in Z26^L, plus the OPEN vectors."""
    C = Checker(ct, hyp)
    counts = {"EXCL": 0, "EXCL_DROP": 0, "OPEN": 0}
    opens = []
    for a in itertools.product(range(26), repeat=L):
        v = C.verdict(a, allow_drop)
        counts[v] += 1
        if v == "OPEN":
            opens.append(a)
    return counts, opens
