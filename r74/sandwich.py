"""R74 reference cipher (PR #65): substitution -> transposition -> substitution on the KRYPTOS tableau. No K4 data.
A = KRYPTOSABCDEFGHIJLMNQUVWXZ; letters are 0-based ranks in A. A stage E(x, k; op) is
  VIG  y = x + k     BEAU  y = k - x     VARB  y = x - k      (mod 26), i.e. y = s*x + t*k with (s, t) = (1, 1),
  (-1, 1), (1, -1).
For a 97-letter plaintext P, keywords (Ka, Kb) = (PALIMPSEST, ABSCISSA) or (ABSCISSA, PALIMPSEST), phases a < |Ka|,
b < |Kb|, operations op_a, op_b and a route r (one of the 14 distinct directed routes formed by r61/routes.txt and
their inverses; convention Y[j] = X[r[j]]):
  X[i] = E(P[i], Ka[(i + a) mod |Ka|]; op_a);   Y[j] = X[r[j]];   C[j] = E(Y[j], Kb[(j + b) mod |Kb|]; op_b).
Composite, for output position j:  C[j] = sigma * P[r[j]] + v[j]  with  sigma = s_a * s_b  and
  v[j] = s_b * t_a * Ka[(r[j] + a) mod |Ka|] + t_b * Kb[(j + b) mod |Kb|]   (mod 26).
A transform is identified by (r, sigma, v); different labels with the same triple are the same cipher."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
IDX = {c: i for i, c in enumerate(A)}
OPS = {"VIG": (1, 1), "BEAU": (-1, 1), "VARB": (1, -1)}
KEYWORDS = ("PALIMPSEST", "ABSCISSA")
N = 97


def load_routes(path=ROOT / "r61/routes.txt"):
    """The 14 distinct directed routes: each frozen R61 route and its inverse, duplicates merged (first name kept)."""
    out = {}
    for line in Path(path).read_text().splitlines():
        name, _, perm = line.split()
        p = tuple(int(x) for x in perm.split(","))
        q = [0] * N
        for j, v in enumerate(p):
            q[v] = j
        for nm, perm_ in ((name, p), (name + "^-1", tuple(q))):
            if perm_ not in out.values():
                out[nm] = perm_
    return out


def stage(x, k, op):
    s, t = OPS[op]
    return (s * x + t * k) % 26


def encrypt(pt, ka, kb, a, b, op_a, op_b, route):
    """Explicit three-stage encryption (no shortcut through the composite)."""
    x = [stage(IDX[c], IDX[ka[(i + a) % len(ka)]], op_a) for i, c in enumerate(pt)]
    y = [x[route[j]] for j in range(N)]
    return "".join(A[stage(y[j], IDX[kb[(j + b) % len(kb)]], op_b)] for j in range(N))


def transform(ka, kb, a, b, op_a, op_b, route):
    sa, ta = OPS[op_a]
    sb, tb = OPS[op_b]
    v = tuple((sb * ta * IDX[ka[(route[j] + a) % len(ka)]] + tb * IDX[kb[(j + b) % len(kb)]]) % 26 for j in range(N))
    return route, sa * sb, v


def configs(routes):
    """All raw settings: 2 keyword orders x |Ka||Kb| phases x 3 x 3 operations x 14 routes = 20,160."""
    for ka, kb in (KEYWORDS, KEYWORDS[::-1]):
        for a in range(len(ka)):
            for b in range(len(kb)):
                for op_a in OPS:
                    for op_b in OPS:
                        for rn, r in routes.items():
                            yield {"ka": ka, "kb": kb, "a": a, "b": b, "op_a": op_a, "op_b": op_b, "route": rn}, r


def classes(routes):
    """Canonical transforms -> list of raw settings that realise them (insertion order is deterministic)."""
    out = {}
    for cfg, r in configs(routes):
        key = transform(cfg["ka"], cfg["kb"], cfg["a"], cfg["b"], cfg["op_a"], cfg["op_b"], r)
        out.setdefault(key, []).append(cfg)
    return out


def decrypt(ct, route, sigma, v):
    """Inverse of C[j] = sigma * P[r[j]] + v[j]: P[r[j]] = sigma * (C[j] - v[j]) (sigma = +-1 is its own inverse)."""
    p = [0] * N
    for j in range(N):
        p[route[j]] = (sigma * (IDX[ct[j]] - v[j])) % 26
    return "".join(A[x] for x in p)
