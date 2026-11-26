#!/usr/bin/env python3
"""R102 second solver: depth-first search mod 26 over the unknowns (a-letters, b-letters, c) of s3b102.rows(),
with forward checking (every coefficient is a unit, so an equation with one unknown forces it) and injectivity
pruning inside each group. No elimination, CRT or enumeration. UNDECIDED at the node cap."""
import s3b102 as S

INV = {a: pow(a, -1, 26) for a in range(26) if a % 2 and a != 13}


class Cap(Exception):
    pass


def solve(ct, pt, L, s1, s2, F, node_cap=200_000):
    R = S.rows(ct, pt, L, s1, s2, F)
    if not R:
        return "NO_EQUATIONS"
    eqs = [({k: v % 26 for k, v in enumerate(r[:53]) if v % 26}, r[53] % 26) for r in R]
    allv = sorted({k for e, _ in eqs for k in e})
    deg = {k: sum(k in e for e, _ in eqs) for k in allv}
    grp = lambda k: 0 if k < 26 else (1 if k < 52 else 2)  # noqa: E731
    nodes = [0]

    def search(assign, used):
        nodes[0] += 1
        if nodes[0] > node_cap:
            raise Cap
        assign = dict(assign)
        used = [set(used[0]), set(used[1])]
        changed = True
        while changed:
            changed = False
            for e, const in eqs:
                un = [k for k in e if k not in assign]
                s = (sum(e[k] * assign[k] for k in e if k in assign) + const) % 26
                if not un:
                    if s:
                        return False
                    continue
                if len(un) == 1 and e[un[0]] in INV:
                    k = un[0]
                    v = (-s * INV[e[k]]) % 26
                    g = grp(k)
                    if g < 2 and v in used[g]:
                        return False
                    assign[k] = v
                    if g < 2:
                        used[g].add(v)
                    changed = True
        rest = [k for k in allv if k not in assign]
        if not rest:
            return True
        k = max(rest, key=lambda q: deg[q])
        g = grp(k)
        for v in range(26):
            if g < 2 and v in used[g]:
                continue
            a2 = dict(assign)
            a2[k] = v
            u2 = [set(used[0]), set(used[1])]
            if g < 2:
                u2[g].add(v)
            if search(a2, u2):
                return True
        return False

    try:
        return "CONSISTENT" if search({}, [set(), set()]) else "INCONSISTENT"
    except Cap:
        return "UNDECIDED"
