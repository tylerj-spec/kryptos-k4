#!/usr/bin/env python3
"""Keystream oracle (Claude R26). Model: c_i = CA[(PA^-1(p_i) + s*k_i) mod 26] with BOTH alphabets arbitrary, for a
GIVEN key sequence k (s = +1 or -1). This covers Vigenère, Beaufort, variant Beaufort and Quagmire I-IV with any
alphabets, for any keystream. Exact test: the 24 clue letters must give a consistent, injective, jointly placeable
assignment (same crib-graph logic as gromark.full_feasible). Returns True when the key sequence is possible."""

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
ANCH = {21 + i: c for i, c in enumerate("EASTNORTHEAST")} | {63 + i: c for i, c in enumerate("BERLINCLOCK")}


def possible(k, ct=K4, anch=ANCH, sign=1):
    adj = {}
    for i, p in anch.items():
        d = (sign * k[i]) % 26
        u, v = ("P", p), ("C", ct[i])
        adj.setdefault(u, []).append((v, d))
        adj.setdefault(v, []).append((u, -d))
    pot, comps = {}, []
    for root in adj:
        if root in pot:
            continue
        pot[root] = 0
        comp, stack = [root], [root]
        while stack:
            u = stack.pop()
            for v, d in adj[u]:
                pv = (pot[u] + d) % 26
                if v in pot:
                    if pot[v] != pv:
                        return False
                else:
                    pot[v] = pv
                    comp.append(v)
                    stack.append(v)
        P = [pot[x] for x in comp if x[0] == "P"]
        C = [pot[x] for x in comp if x[0] == "C"]
        if len(P) != len(set(P)) or len(C) != len(set(C)):
            return False
        comps.append((P, C))
    comps.sort(key=lambda c: -(len(c[0]) + len(c[1])))

    def place(j, mp, mc):
        if j == len(comps):
            return True
        P, C = comps[j]
        for off in range(26 if j else 1):
            bp = sum(1 << ((x + off) % 26) for x in P)
            bc = sum(1 << ((x + off) % 26) for x in C)
            if not (bp & mp or bc & mc) and place(j + 1, mp | bp, mc | bc):
                return True
        return False
    return place(0, 0, 0)


def checks(k, ct=K4, anch=ANCH, sign=1):
    """Number of independent consistency checks the clues impose (edges minus spanning-tree edges)."""
    nodes = {("P", p) for p in anch.values()} | {("C", ct[i]) for i in anch}
    parent = {x: x for x in nodes}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    comps = len(nodes)
    for i, p in anch.items():
        a, b = find(("P", p)), find(("C", ct[i]))
        if a != b:
            parent[a] = b
            comps -= 1
    return len(anch) - (len(nodes) - comps)


if __name__ == "__main__":
    import random
    import time

    def gromark(pr):
        k = [int(x) for x in f"{pr:05d}"]
        while len(k) < 97:
            k.append((k[-5] + k[-4]) % 10)
        return k
    t = time.time()
    n = sum(possible(gromark(p)) for p in range(100000))
    print(f"validation: Gromark primers possible = {n} (expected 39), {time.time() - t:.1f} s")
    print("independent checks imposed by the clues (any keystream):", checks([0] * 97))
    rng = random.Random(260)
    N = 200000
    hits = sum(possible([rng.randrange(26) for _ in range(97)]) for _ in range(N))
    print(f"null: random 0-25 keystreams possible = {hits}/{N} = {hits / N:.2e}")
