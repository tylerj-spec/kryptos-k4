#!/usr/bin/env python3
"""Independent, overflow-safe R75 F1X two-keyword graph feasibility oracle.

POST-FREEZE AUDIT ONLY; never used to construct a real K4 plaintext or
rank/choose keys. The frozen R75 source and protocol remain unchanged.

For each anchor, stage-2 key slot is a bijective function of stage-1
key slot. Each graph component has 0..26 consistent root values.
Multiply component counts as *Python integers*, then multiply by
26 for all unobserved key slots. No solutions are enumerated and no
plaintext is decrypted.

--synthetic: toy ciphertext/known letters only (not K4).
--k4 OUT: independent post-freeze spot-check against archived R75
          feasible sample, without reading any decrypted plaintext.
"""
import itertools
import json
import random
import sys
from collections import defaultdict, deque
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r75"))
from core import AZ, IDX, LET  # noqa: E402


def as_codes(text):
    return np.fromiter((AZ.index(ch) for ch in text), dtype=np.int64, count=len(text))


def exact_graph(ct, pos, pk, cfg, m1, m2):
    """Exact feasibility + arbitrary-precision count for all free key letters."""
    pa1, ca1, pa2, ca2, s1, s2 = cfg
    ct = np.asarray(ct, dtype=np.int64)
    pos = np.asarray(pos, dtype=np.int64)
    pk = np.asarray(pk, dtype=np.int64)
    if not (len(pos) == len(pk) > 0):
        raise ValueError("anchor positions and letters must be nonempty and equal")
    if not (len(set(map(int, pos))) == len(pos) and all(0 <= i < len(ct) for i in pos)):
        raise ValueError("duplicate/invalid positions")
    if m1 < 1 or m2 < 1:
        raise ValueError("keyword periods must be positive")

    graph = defaultdict(list)
    for edge, (i, p) in enumerate(zip(pos, pk)):
        u = (0, int(i) % m1)
        v = (1, int(i) % m2)
        a = int(IDX[pa1][int(p)])
        target = int(IDX[ca2][int(ct[int(i)])])
        table = []
        for k1 in range(26):
            q = int(LET[ca1][(int(s1) * a + k1) % 26])
            k2 = (target - int(s2) * int(IDX[pa2][q])) % 26
            table.append(k2)
        if sorted(table) != list(range(26)):
            raise AssertionError("stage map must be a permutation")
        inv = [0] * 26
        for x, y in enumerate(table):
            inv[y] = x
        graph[u].append((v, table))
        graph[v].append((u, inv))

    seen, component_counts = set(), []
    for root in graph:
        if root in seen:
            continue
        # Build connected components without any assumption about rank.
        queue = deque([root])
        seen.add(root)
        vertices = []
        while queue:
            u = queue.popleft()
            vertices.append(u)
            for v, _ in graph[u]:
                if v not in seen:
                    seen.add(v)
                    queue.append(v)
        valid_roots = 0
        for root_value in range(26):
            state = {root: root_value}
            queue = deque([root])
            consistent = True
            while queue and consistent:
                u = queue.popleft()
                for v, table in graph[u]:
                    desired = table[state[u]]
                    if v in state:
                        if state[v] != desired:
                            consistent = False
                            break
                    else:
                        state[v] = desired
                        queue.append(v)
            if consistent:
                assert len(state) == len(vertices)
                valid_roots += 1
        component_counts.append(valid_roots)

    total = 1
    for count in component_counts:
        total *= int(count)
    unconstrained_slots = m1 + m2 - len(graph)
    total *= 26 ** unconstrained_slots
    # E - V + components is the cycle count, not a universal exact
    # -log26 feasibility probability for nonlinear/degenerate maps.
    checks = len(pos) - len(graph) + len(component_counts)
    return {
        "feasible": total > 0, "solution_count": str(total),
        "component_counts": component_counts,
        "unconstrained_slots": unconstrained_slots,
        "checks": checks,
        "eff_graph_surrogate": len(pos) - len(graph),
    }


def encrypt(pt, cfg, k1, k2):
    pa1, ca1, pa2, ca2, s1, s2 = cfg
    out = []
    for i, ch in enumerate(pt):
        a = int(IDX[pa1][AZ.index(ch)])
        q = int(LET[ca1][(int(s1) * a + int(k1[i % len(k1)])) % 26])
        out.append(AZ[int(LET[ca2][(int(s2) * int(IDX[pa2][q]) +
                                  int(k2[i % len(k2)])) % 26])])
    return "".join(out)


def tiny_bruteforce(ct, pos, pk, cfg, m1, m2):
    n = 0
    for k1 in itertools.product(range(26), repeat=m1):
        for k2 in itertools.product(range(26), repeat=m2):
            if all(encrypt(AZ[int(pk[j])], cfg, (k1[int(pos[j]) % m1],),
                           (k2[int(pos[j]) % m2],)) ==
                   AZ[int(ct[int(pos[j])])] for j in range(len(pos))):
                n += 1
    return n


def synthetic_tests():
    rng = random.Random(751951)
    alpha = ("AZ", "KRY", "PAL", "ABS")
    samples = []
    for m1, m2 in ((1, 1), (1, 2), (2, 1)):
        for _ in range(3):
            cfg = (rng.choice(alpha), rng.choice(alpha), rng.choice(alpha),
                   rng.choice(alpha), rng.choice((1, -1)), rng.choice((1, -1)))
            k1 = [rng.randrange(26) for _ in range(m1)]
            k2 = [rng.randrange(26) for _ in range(m2)]
            pt = "".join(rng.choice(AZ) for _ in range(9))
            ct = encrypt(pt, cfg, k1, k2)
            pos = np.array((0, 1, 2, 4, 7), dtype=np.int64)
            pk = as_codes("".join(pt[i] for i in pos))
            result = exact_graph(as_codes(ct), pos, pk, cfg, m1, m2)
            brute = tiny_bruteforce(as_codes(ct), pos, pk, cfg, m1, m2)
            assert int(result["solution_count"]) == brute, (cfg, m1, m2, result, brute)
            assert result["feasible"]
            samples.append({"m1": m1, "m2": m2, "count": brute})

    # Regression for the original R75 NumPy int64 overflow:
    # a single connected 2-slot component, 32 unused key slots.
    # 26^33 exceeds 2^63. The SAFE checker must not enumerate it.
    cfg = ("AZ", "KRY", "PAL", "ABS", 1, 1)
    pt = "A" * 97
    ct = encrypt(pt, cfg, [0] * 17, [0] * 17)
    pos = np.array((0, 17, 34), dtype=np.int64)
    pk = as_codes("AAA")
    giant = exact_graph(as_codes(ct), pos, pk, cfg, 17, 17)
    assert giant["feasible"]
    assert int(giant["solution_count"]) == 26 ** 33, giant
    assert int(giant["solution_count"]) > 2 ** 63

    # Contradictory observed ciphertext at the SAME key slots
    # cannot be produced from the SAME plaintext letter.
    changed = list(ct)
    changed[17] = "Q" if changed[17] != "Q" else "P"
    bad = exact_graph(as_codes("".join(changed)), pos, pk, cfg, 17, 17)
    assert not bad["feasible"], bad
    return {"tiny_exhaustive_cases": len(samples),
            "tiny_cases": samples,
            "big_integer_solution_count": giant["solution_count"],
            "big_integer_digits": len(giant["solution_count"]),
            "large_case_mutation_excluded": True}


def k4_audit(out_path):
    """Selected archived positive results, not a full re-enumeration."""
    q = ROOT / "r75/k4/EXACT.json"
    recorded = json.loads(q.read_text())["K4"]["F1X"]["feasible_list"]
    target = dict(x.split("\t") for x in
                  (ROOT / "r75/k4/TARGET.tsv").read_text().splitlines()[1:] if x)
    # The known letters are only accessible in this post-freeze subcommand.
    sys.path.insert(0, str(ROOT / "r73/sealed"))
    from reveal_k4 import CLUES  # noqa: E402
    positions = np.array([off + j for off, text in CLUES
                          for j in range(len(text))], dtype=np.int64)
    known = as_codes("".join(text for _, text in CLUES))
    ct = as_codes(target["K4"])
    assert len(positions) == len(known) == 24 and len(ct) == 97
    outcomes = []
    for record in recorded[:100]:
        st = record["setting"]
        result = exact_graph(ct, positions, known,
                             st["cfg"], st["m1"], st["m2"])
        assert result["feasible"], ("historical positive fails independent oracle", st)
        assert result["checks"] == record["checks"], ("check mismatch", st)
        outcomes.append({"m1": st["m1"], "m2": st["m2"],
                         "checks": result["checks"],
                         "feasible": result["feasible"]})
    report = {
        "label": "POST-FREEZE selected R75 F1X equivalence audit, NOT full family coverage",
        "cases": len(outcomes), "all_passed": len(outcomes) == 100,
        "results": outcomes,
        "hard_limit": "Historical feasible_list is capped to 300 items and is not necessarily a representative or complete sample.",
    }
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(report, indent=2) + "\n")
    print("R75 F1X independently matched", len(outcomes), "archived positive configurations")


if __name__ == "__main__":
    if sys.argv[1] == "--synthetic":
        print(json.dumps(synthetic_tests(), indent=2))
    elif sys.argv[1] == "--k4":
        k4_audit(sys.argv[2])
    else:
        raise SystemExit(__doc__)
