#!/usr/bin/env python3
"""Keystream oracle (Claude R26; toolkit copy). Model: c_i = CA[(PA^-1(p_i) + k_i) mod 26] with BOTH alphabets
arbitrary and a GIVEN key sequence k. Covers Vigenère, Beaufort, variant Beaufort and Quagmire I-IV in any alphabets.
Exact test: the clue letters must give a consistent, injective, jointly placeable assignment.

Facts (K4, identity order):
- validation: 39 of 100,000 five-digit Gromark primers are possible (= ledger L22);
- random 0-25 keys pass at 4.70e-4 (94/200,000); judge any family's passes against trials x 4.7e-4;
- +k and -k are the same setting when both alphabets are free (reflect both alphabets; ledger L92): test one sign.
Run `python3 key_oracle.py` to re-validate."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from k4common import ANCH, K4, gromark_key  # noqa: E402


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


def checks(k=None, ct=K4, anch=ANCH, sign=1):
    """Independent crib cycles (edges minus spanning-forest edges). Depends only on ct letters at anchor positions,
    not on the key: identity order gives 2 for K4. 0 cycles = the clues only test alphabet injectivity."""
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
    n = sum(possible(gromark_key(p)) for p in range(100000))
    print(f"Gromark primers possible: {n} (expected 39)")
    rng = random.Random(260)
    N = 200000
    hits = sum(possible([rng.randrange(26) for _ in range(97)]) for _ in range(N))
    print(f"random keys possible: {hits}/{N} (expected 94 with this seed)")
