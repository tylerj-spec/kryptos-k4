#!/usr/bin/env python3
"""R101 second exact solver (PREREGISTRATION section 2): depth-first search over the ranks mod 26, with c enumerated
outside; forward checking forces a letter when an equation has one unassigned letter with a unit coefficient, and
repeated ranks are pruned. No field decomposition, kernels or enumeration. UNDECIDED when the node cap is reached."""
import freealpha101 as FA

INV = {a: pow(a, -1, 26) for a in range(26) if a % 2 and a != 13}


class Cap(Exception):
    pass


def solve(ct, obs, L, s1, s2, node_cap=1_000_000):
    rows = FA.system(ct, obs, L, s1, s2)
    if not rows:
        return "NO_LINKS"
    eqs = [{k: v % 26 for k, v in enumerate(r) if v % 26} for r in rows]          # variable 26 is c
    letters = sorted({k for e in eqs for k in e if k < 26})
    deg = {k: sum(k in e for e in eqs) for k in letters}
    nodes = [0]

    def search(assign, used):
        nodes[0] += 1
        if nodes[0] > node_cap:
            raise Cap
        assign, used = dict(assign), set(used)
        changed = True
        while changed:
            changed = False
            for e in eqs:
                un = [k for k in e if k not in assign]
                s = sum(e[k] * assign[k] for k in e if k in assign) % 26
                if not un:
                    if s:
                        return False
                    continue
                if len(un) == 1 and e[un[0]] in INV:
                    k = un[0]
                    v = (-s * INV[e[k]]) % 26
                    if k < 26 and v in used:
                        return False
                    assign[k] = v
                    if k < 26:
                        used.add(v)
                    changed = True
        rest = [k for k in letters if k not in assign]
        if not rest:
            return all(sum(e[k] * assign[k] for k in e) % 26 == 0 for e in eqs)
        k = max(rest, key=lambda q: deg[q])
        for v in range(26):
            if v not in used:
                a2 = dict(assign)
                a2[k] = v
                if search(a2, used | {v}):
                    return True
        return False

    try:
        for c in range(26):
            if search({26: c}, set()):
                return "FEASIBLE"
        return "INFEASIBLE"
    except Cap:
        return "UNDECIDED"
