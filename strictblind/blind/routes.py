#!/usr/bin/env python3
"""strictblind BLIND route maker (no clue information; imports nothing from the toolkit).

  routes.py r27 OUT                   identity + the 20 R27 K3-style routes x 2 orders      (= R32 routes_f1.txt)
  routes.py rot LO HI OUT             double rotations R{w1}x{w2}/{CW,CCW}/{fwd,inv}, w1,w2 in LO..HI, 2 orders
                                                                                          (4 28 = R32 routes_f2.txt)
  routes.py columnar WORDS OUT [--canonical]
                                      keyword irregular columnar, 32 read variants per word (or the 4 canonical
                                      ones), 2 orders (KRYPTOS,PALIMPSEST,ABSCISSA = R33 routes_g5.txt; with
                                      --canonical = R33 routes_carter.txt)
Line format: NAME ORDER p0,...,p96 with CT[j] = X[perm[j]] (ORDER = ID | S_then_T | T_then_S)."""
import sys

N = 97


def inv(p):
    q = [0] * len(p)
    for j, i in enumerate(p):
        q[i] = j
    return q


def rot(n, w, cw):
    rows = [list(range(i, min(i + w, n))) for i in range(0, n, w)]
    out = []
    for c in range(w):
        cc = c if cw else w - 1 - c
        for r in (range(len(rows) - 1, -1, -1) if cw else range(len(rows))):
            if cc < len(rows[r]):
                out.append(rows[r][cc])
    return out


def rotation(name, n=N):
    """K3's double quarter-turn, R27 naming (verified on K3 in earlier rounds)."""
    dims, cwn, kind = name[1:].split("/")
    w1, w2 = map(int, dims.split("x"))
    p1, p2 = rot(n, w1, cwn == "CW"), rot(n, w2, cwn == "CW")
    p = [p1[i] for i in p2]
    return p if kind == "fwd" else inv(p)


R27 = [f"R{a}x{b}/{d}/{k}" for a, b in ((24, 8), (23, 8), (25, 8), (24, 7), (24, 9))
       for d in ("CW", "CCW") for k in ("fwd", "inv")]


def columnar(key, revfill=False, snake=False, revsort=False, revread=False):
    """Irregular columnar (R33): fill rows of len(key), read columns in keyword order (ties left to right)."""
    w = len(key)
    grid = {}
    for j in range(N):
        row, col = divmod(j, w)
        if snake and row % 2:
            col = w - 1 - col
        if revfill:
            col = w - 1 - col
        grid[row, col] = j
    cols = sorted(range(w), key=lambda c: (key[c], c))
    if revsort:
        cols.reverse()
    rows = (N + w - 1) // w
    p = [grid[r, c] for c in cols for r in (range(rows - 1, -1, -1) if revread else range(rows)) if (r, c) in grid]
    assert sorted(p) == list(range(N))
    return p


CANONICAL = ("F0S0O0V0", "F0S0O1V0", "F0S0O0V1", "F0S0O1V1")


def columnar_routes(words, canonical):
    for key in words:
        for revfill in (0, 1):
            for snake in (0, 1):
                for revsort in (0, 1):
                    for revread in (0, 1):
                        attrs = f"F{revfill}S{snake}O{revsort}V{revread}"
                        p = columnar(key, revfill, snake, revsort, revread)
                        for invf in (0, 1):
                            if canonical and (attrs not in CANONICAL or invf):
                                continue
                            yield f"{key}/{attrs}/{'INV' if invf else 'FWD'}", inv(p) if invf else p


def write(path, entries):
    with open(path, "w") as f:
        for name, order, p in entries:
            f.write(f"{name} {order} {','.join(map(str, p))}\n")
    return len(entries)


def both(named):
    return [(n, o, p) for n, p in named for o in ("S_then_T", "T_then_S")]


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "r27":
        n = write(a[1], [("ID", "ID", list(range(N)))] + both((r, rotation(r)) for r in R27))
    elif a[0] == "rot":
        lo, hi = int(a[1]), int(a[2])
        named = [(f"R{w1}x{w2}/{d}/{k}", rotation(f"R{w1}x{w2}/{d}/{k}")) for w1 in range(lo, hi + 1)
                 for w2 in range(lo, hi + 1) for d in ("CW", "CCW") for k in ("fwd", "inv")]
        n = write(a[3], both(named))
    elif a[0] == "columnar":
        n = write(a[2], both(columnar_routes(a[1].split(","), "--canonical" in a)))
    else:
        sys.exit(__doc__)
    print(a[0], n, "route-orders")
