#!/usr/bin/env python3
"""Trifid with an ARBITRARY 27-symbol cube (26 letters + one extra symbol '#'), every period 1-97 (Claude R26).
Delastelle: split the plaintext into groups of p letters (last group shorter); write each letter's (layer, row,
column); read all layers, then rows, then columns; regroup in threes; each triple is a ciphertext symbol.
With an arbitrary cube the 6 axis reading orders are equivalent (relabel the axes), so one order suffices.
Known plaintext (the 24 clue letters) plus the full ciphertext give equalities between coordinate variables.
Exact test: is there a bijective cube satisfying them? Unknown plaintext letters are left unconstrained
(a relaxation), so an "impossible" verdict is a valid exclusion."""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from k4common import ANCH, K4  # noqa: E402
SYM = "ABCDEFGHIJKLMNOPQRSTUVWXYZ#"
sys.setrecursionlimit(10000)


def groups(n, p):
    return [(s, min(p, n - s)) for s in range(0, n, p)]


def encrypt(pt, cube, p):
    pos = {cube[i]: (i // 9, (i // 3) % 3, i % 3) for i in range(27)}
    out = []
    for s, L in groups(len(pt), p):
        d = [pos[pt[s + t % L]][t // L] for t in range(3 * L)]
        out += [cube[d[3 * j] * 9 + d[3 * j + 1] * 3 + d[3 * j + 2]] for j in range(L)]
    return "".join(out)


def constraints(ct, anch, p):
    eq = []
    for s, L in groups(len(ct), p):
        for j in range(L):
            for q in range(3):
                t = 3 * j + q
                src = s + t % L
                if src in anch:
                    eq.append(((ct[s + j], q), (anch[src], t // L)))
    return eq


def solve(eq, limit=2_000_000):
    """Return 'possible', 'impossible' or 'undecided' (node limit)."""
    var = [(x, a) for x in SYM for a in range(3)]
    parent = {v: v for v in var}

    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v
    for a, b in eq:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    cls = {}
    for v in var:
        cls.setdefault(find(v), len(cls))
    trip = {x: tuple(cls[find((x, a))] for a in range(3)) for x in SYM}
    if len(set(trip.values())) < 27:
        return "impossible"
    # order classes by how many symbol-coordinates they touch
    use = {}
    for x in SYM:
        for c in trip[x]:
            use[c] = use.get(c, 0) + 1
    order = sorted(use, key=lambda c: -use[c])
    val = {}
    nodes = [0]

    def ok():
        cnt = [[0] * 3 for _ in range(3)]
        seen = set()
        for x in SYM:
            t = trip[x]
            for a in range(3):
                if t[a] in val:
                    cnt[a][val[t[a]]] += 1
                    if cnt[a][val[t[a]]] > 9:
                        return False
            if all(c in val for c in t):
                tv = tuple(val[c] for c in t)
                if tv in seen:
                    return False
                seen.add(tv)
        return True

    def bt(i):
        nodes[0] += 1
        if nodes[0] > limit:
            raise TimeoutError
        if i == len(order):
            return True
        c = order[i]
        for v in range(3):
            val[c] = v
            if ok() and bt(i + 1):
                return True
            del val[c]
        return False
    try:
        return "possible" if bt(0) else "impossible"
    except TimeoutError:
        return "undecided"


if __name__ == "__main__":
    rng = random.Random(2626)
    # planted controls: random cube, random plaintext with the clues, every 8th period
    for p in range(2, 98, 8):
        cube = list(SYM)
        rng.shuffle(cube)
        pt = [rng.choice(SYM[:26]) for _ in range(97)]
        for i, c in ANCH.items():
            pt[i] = c
        pt = "".join(pt)
        ct = encrypt(pt, "".join(cube), p)
        assert solve(constraints(ct, ANCH, p)) == "possible", p
    print("planted controls: true period always possible (12/12)")
    res = {}
    for p in range(1, 98):
        eq = constraints(K4, ANCH, p)
        res[p] = (len(eq), solve(eq))
    imp = [p for p, (n, r) in res.items() if r == "impossible"]
    pos = [p for p, (n, r) in res.items() if r == "possible"]
    und = [p for p, (n, r) in res.items() if r == "undecided"]
    print(f"K4: impossible at {len(imp)} periods, possible at {len(pos)}, undecided {len(und)}")
    print("   possible periods:", pos)
    print("   undecided:", und)
    print("   constraints per period (min/median/max):", min(n for n, r in res.values()),
          sorted(n for n, r in res.values())[48], max(n for n, r in res.values()))


def groups_phase(n, p, s0):
    """Groups of p with the first group of length s0 (1..p): boundaries at s0, s0+p, ..."""
    out, s = [], 0
    first = s0 if s0 else p
    out.append((0, min(first, n)))
    s = first
    while s < n:
        out.append((s, min(p, n - s)))
        s += p
    return out


def constraints_phase(ct, anch, p, s0):
    eq = []
    for s, L in groups_phase(len(ct), p, s0):
        for j in range(L):
            for q in range(3):
                t = 3 * j + q
                src = s + t % L
                if src in anch:
                    eq.append(((ct[s + j], q), (anch[src], t // L)))
    return eq
