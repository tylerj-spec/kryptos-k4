#!/usr/bin/env python3
"""Independent F1X graph checker: correct unlimited integer counts, NO decryption.

This is a NEW prospective implementation. Do not overwrite the archived
r75/sealed/exact.py (its hash is part of frozen experiments). Inputs are
literal ciphertext, selected known positions, and the corresponding known
plaintext letters. For real K4, this is permitted ONLY as a post-freeze
crib-assisted necessary/sufficient consistency check, never a generator.

Requires only Python stdlib; 26 possible root values per graph component.
No combinations of component roots are enumerated. No K4 plaintext or
candidate key is ever constructed, completed, scored, or emitted.
"""
from collections import deque

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def keyed(word):
    return "".join(dict.fromkeys(word + AZ))


ALPH = {
    "AZ": AZ,
    "KRY": keyed("KRYPTOS"),
    "PAL": keyed("PALIMPSEST"),
    "ABS": keyed("ABSCISSA"),
}


def valid_inputs(ciphertext, positions, known, cfg, m1, m2):
    if not isinstance(ciphertext, str) or not ciphertext:
        raise ValueError("ciphertext must be a nonempty uppercase A-Z string")
    if set(ciphertext) - set(AZ):
        raise ValueError("invalid ciphertext letters")
    if len(positions) != len(known) or not positions:
        raise ValueError("positions and known plaintext must be paired and nonempty")
    if len(set(positions)) != len(positions) or any(
        not isinstance(i, int) or not 0 <= i < len(ciphertext) for i in positions
    ):
        raise ValueError("positions must be unique and inside ciphertext")
    if set(known) - set(AZ):
        raise ValueError("invalid known plaintext letters")
    if (not isinstance(cfg, (tuple, list)) or len(cfg) != 6 or
            any(x not in ALPH for x in cfg[:4]) or
            cfg[4] not in (-1, 1) or cfg[5] not in (-1, 1)):
        raise ValueError("cfg must contain 4 alphabets and two signs")
    if not 1 <= m1 <= len(ciphertext) or not 1 <= m2 <= len(ciphertext):
        raise ValueError("keyword periods out of bounds")


def edge_map(c, p, cfg):
    """For this observed pair, required second-stage shift as a function
    of first-stage shift. Map is a permutation; no guesses or scoring.
    """
    pa1, ca1, pa2, ca2, s1, s2 = cfg
    a, b, d, e = (ALPH[pa1], ALPH[ca1], ALPH[pa2], ALPH[ca2])
    src = a.index(p)
    target = e.index(c)
    values = tuple(
        (target - s2 * d.index(b[(s1 * src + k) % 26])) % 26
        for k in range(26)
    )
    if len(set(values)) != 26:
        raise AssertionError("two-stage key relationship is not bijective")
    inverse = [None] * 26
    for x, y in enumerate(values):
        inverse[y] = x
    return values, tuple(inverse)


def check_setting(ciphertext, positions, known, cfg, m1, m2):
    """Exact count of all feasible key assignments for ONE convention/period.

    Counts are pure Python arbitrary-precision integers. The routine only
    propagates constraints; it cannot accidentally invoke a decode path.
    Result includes:
      active_solution_count: number of assignments on observed slot nodes
      total_solution_count: also assign each unobserved keyword slot 26 ways
      unused_key_slots: first+second stage indices never constrained
      checks: |edges| - |observed nodes| + |connected components|
    """
    valid_inputs(ciphertext, positions, known, cfg, m1, m2)
    adjacency = {}
    for i, p in zip(positions, known):
        u = (0, i % m1)
        v = (1, i % m2)
        gm, gi = edge_map(ciphertext[i], p, cfg)
        adjacency.setdefault(u, []).append((v, gm))
        adjacency.setdefault(v, []).append((u, gi))

    components = 0
    seen = set()
    active_count = 1
    component_root_counts = []
    for root in adjacency:
        if root in seen:
            continue
        # Find vertices of this undirected component. Required for the
        # total graph-count identity and to avoid double-counting roots.
        components += 1
        queue = deque([root])
        vertices = {root}
        while queue:
            u = queue.popleft()
            for v, _ in adjacency[u]:
                if v not in vertices:
                    vertices.add(v)
                    queue.append(v)
        seen.update(vertices)

        valid_roots = 0
        for x0 in range(26):
            assignments = {root: x0}
            work = deque([root])
            consistent = True
            while work and consistent:
                u = work.popleft()
                for v, mapping in adjacency[u]:
                    value = mapping[assignments[u]]
                    if v in assignments:
                        if assignments[v] != value:
                            consistent = False
                            break
                    else:
                        assignments[v] = value
                        work.append(v)
            if consistent:
                valid_roots += 1
        component_root_counts.append(valid_roots)
        active_count *= valid_roots
        # A zero in one component proves infeasible. Exit without
        # constructing a key or exploring other components.
        if not active_count:
            break

    n_used = len(adjacency)
    unused = m1 + m2 - n_used
    checks = len(positions) - n_used + components
    if unused < 0:
        raise AssertionError("negative number of unobserved slots")
    return {
        "feasible": bool(active_count),
        "active_solution_count": int(active_count),
        "unused_key_slots": int(unused),
        "total_solution_count": int(active_count * 26 ** unused),
        "checks": int(checks),
        "components": int(components),
        "observed_slot_nodes": int(n_used),
        "count_type": "arbitrary_precision_integer",
        "creates_plaintext": False,
        "creates_completed_keys": False,
    }


def enumerated_periods(ciphertext, positions, known, cfg, periods=None):
    """Only loop over EXPLICIT predeclared finite period pairs.

    No unbounded search or candidate ranking. The default is intentionally
    absent: callers must declare their resource budget and period list.
    """
    if periods is None:
        raise ValueError("provide explicit finite period list")
    for m1, m2 in periods:
        yield m1, m2, check_setting(ciphertext, positions, known, cfg, m1, m2)
