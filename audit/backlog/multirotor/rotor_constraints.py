#!/usr/bin/env python3
"""Synthetic two-rotor reference and bounded feasibility proof kernel.

This module reads no files, contains no target ciphertext or known-letter mask,
does not score language, and never returns wirings or decoded candidates from
the constraint checker. See DESIGN.md for the proof and scope.
"""
from itertools import combinations


def permutation(wiring, q):
    if sorted(wiring) != list(range(q)):
        raise ValueError("wiring must be a permutation")


def encrypt(plain, w1, w2, shifts):
    q = len(w1)
    permutation(w1, q)
    permutation(w2, q)
    if len(plain) != len(shifts) or any(x not in range(q) for x in plain):
        raise ValueError("invalid symbols or schedule length")
    return [((w2[(w1[(p + s1) % q] - s1 + s2) % q] - s2) % q)
            for p, (s1, s2) in zip(plain, shifts)]


def decrypt(cipher, w1, w2, shifts):
    q = len(w1)
    permutation(w1, q)
    permutation(w2, q)
    if len(cipher) != len(shifts) or any(x not in range(q) for x in cipher):
        raise ValueError("invalid symbols or schedule length")
    # Inverse is implemented directly by looking up the output contact twice.
    out = []
    for c, (s1, s2) in zip(cipher, shifts):
        middle = (w2.index((c + s2) % q) - s2) % q
        out.append((w1.index((middle + s1) % q) - s1) % q)
    return out


def odometer(length, n, r, h, d1, d2, q=26):
    if n < 1 or r not in range(n) or h not in range(q) or d1 not in (-1, 1) or d2 not in (-1, 1):
        raise ValueError("invalid odometer setting")
    return [(d1 * ((i + r) // n) % q,
             d2 * ((((i + r) // n) + h) // q) % q) for i in range(length)]


def clocks(length, n1, n2, r1, r2, d1, d2, q=26):
    if min(n1, n2) < 1 or r1 not in range(n1) or r2 not in range(n2) or d1 not in (-1, 1) or d2 not in (-1, 1):
        raise ValueError("invalid clock setting")
    return [(d1 * ((i + r1) // n1) % q, d2 * ((i + r2) // n2) % q) for i in range(length)]


def collapses(shifts, q):
    """Sufficient collapse: a constant relative rotor angle at every position."""
    return len({(s2 - s1) % q for s1, s2 in shifts}) <= 1


def feasible(q, observations, max_nodes=10000):
    """Exact SAT/UNSAT or UNKNOWN on capped branching, without key completion.

    observations consists of (plaintext_contact, ciphertext_contact, s1, s2).
    No primality of q is assumed: only additions/subtractions modulo q occur.
    The returned result is aggregate-only. SAT is compatibility, not a solution.
    """
    if q < 2 or max_nodes < 0:
        raise ValueError("invalid alphabet or node budget")
    obs = list(observations)
    if any(len(row) != 4 or row[0] not in range(q) or row[1] not in range(q) for row in obs):
        raise ValueError("invalid observation")
    equations = [((p + s1) % q, (c + s2) % q, (s2 - s1) % q) for p, c, s1, s2 in obs]
    vertices = sorted({a for a, _, _ in equations})
    graph = {a: [] for a in vertices}
    # x_j - x_i = delta_i - delta_j whenever b_i == b_j.
    by_output = {}
    for a, b, delta in equations:
        if b in by_output:
            other, other_delta = by_output[b]
            step = (other_delta - delta) % q
            graph[other].append((a, step))
            graph[a].append((other, -step % q))
        else:
            by_output[b] = (a, delta)
    component, potential = {}, {}
    count = 0
    for root in vertices:
        if root in component:
            continue
        component[root], potential[root] = count, 0
        stack = [root]
        while stack:
            a = stack.pop()
            for b, step in graph[a]:
                wanted = (potential[a] + step) % q
                if b in component:
                    if component[b] != count or potential[b] != wanted:
                        return {"status": "UNSAT", "nodes": 0, "reason": "inconsistent equalities"}
                else:
                    component[b], potential[b] = count, wanted
                    stack.append(b)
        count += 1
    # A forbidden offset d on (u,v) means offset_v-offset_u != d.
    forbidden = {}

    def unequal(a, ka, b, kb):
        u, v = component[a], component[b]
        d = (potential[a] + ka - potential[b] - kb) % q
        if u == v:
            return d != 0
        if u > v:
            u, v, d = v, u, -d % q
        forbidden.setdefault((u, v), set()).add(d)
        return True

    # W1 is one-to-one on every observed first-rotor input.
    for a, b in combinations(vertices, 2):
        if not unequal(a, 0, b, 0):
            return {"status": "UNSAT", "nodes": 0, "reason": "first wiring collision"}
    # W2 is one-to-one on different observed second-rotor outputs.
    for (a, ba, da), (b, bb, db) in combinations(equations, 2):
        if ba != bb and not unequal(a, da, b, db):
            return {"status": "UNSAT", "nodes": 0, "reason": "second wiring collision"}
    if any(len(values) == q for values in forbidden.values()):
        return {"status": "UNSAT", "nodes": 0, "reason": "all offsets forbidden"}
    if not vertices:
        return {"status": "SAT", "nodes": 0, "components": 0}
    adjacent = {v: [] for v in range(count)}
    for (u, v), values in forbidden.items():
        adjacent[u].append((v, values, 1))
        adjacent[v].append((u, values, -1))
    nodes = 0
    # Global interface rotation is a genuine gauge, even for composite q.
    assigned = {0: 0}

    def domain(v):
        available = set(range(q))
        for other, values, sign in adjacent[v]:
            if other in assigned:
                if sign == 1:
                    available.difference_update((assigned[other] - d) % q for d in values)
                else:
                    available.difference_update((assigned[other] + d) % q for d in values)
        return sorted(available)

    def visit():
        nonlocal nodes
        if len(assigned) == count:
            return "SAT"
        options = [(domain(v), v) for v in range(count) if v not in assigned]
        candidates, v = min(options, key=lambda pair: (len(pair[0]), -len(adjacent[pair[1]]), pair[1]))
        if not candidates:
            return "UNSAT"
        for value in candidates:
            if nodes >= max_nodes:
                return "UNKNOWN"
            nodes += 1
            assigned[v] = value
            result = visit()
            del assigned[v]
            if result != "UNSAT":
                return result
        return "UNSAT"

    return {"status": visit(), "nodes": nodes, "components": count,
            "inequality_edges": len(forbidden)}
