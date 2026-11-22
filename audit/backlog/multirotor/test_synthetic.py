#!/usr/bin/env python3
"""Toy exhaustive two-rotor proof checks; no K4, language model or clue data."""
import itertools
import json
import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rotor_constraints as R


def independent_cipher(plain, w1, w2, shifts):
    q = len(w1)
    answer = []
    for p, (u, v) in zip(plain, shifts):
        first_contact = (p + u) % q
        stationary_wire = (w1[first_contact] - u) % q
        second_contact = (stationary_wire + v) % q
        answer.append((w2[second_contact] - v) % q)
    return tuple(answer)


def run():
    rng = random.Random(911000)
    comparisons = round_trips = collapse_checks = 0
    for q, length, schedule_count in ((2, 4, 6), (3, 3, 8), (4, 2, 8)):
        perms = list(itertools.permutations(range(q)))
        words = list(itertools.product(range(q), repeat=length))
        schedules = [[(rng.randrange(q), rng.randrange(q)) for _ in range(length)] for _ in range(schedule_count)]
        for shifts in schedules:
            for plain in words:
                possible = {independent_cipher(plain, a, b, shifts) for a in perms for b in perms}
                for cipher in words:
                    observations = [(p, c, *s) for p, c, s in zip(plain, cipher, shifts)]
                    status = R.feasible(q, observations, max_nodes=100000)["status"]
                    assert status == ("SAT" if cipher in possible else "UNSAT"), (q, observations, status)
                    comparisons += 1
        for w1, w2 in itertools.product(perms, repeat=2):
            for delta in range(q):
                combined = tuple((w2[(w1[x] + delta) % q] - delta) % q for x in range(q))
                plain = list(range(q)) * 2
                shifts = [(i % q, (i + delta) % q) for i in range(len(plain))]
                predicted = [(combined[(p + s1) % q] - s1) % q for p, (s1, _) in zip(plain, shifts)]
                assert R.encrypt(plain, w1, w2, shifts) == predicted
                collapse_checks += 1
    for q in (4, 6, 26):
        for _ in range(50):
            w1, w2 = rng.sample(range(q), q), rng.sample(range(q), q)
            plain = [rng.randrange(q) for _ in range(97)]
            shifts = [(rng.randrange(q), rng.randrange(q)) for _ in plain]
            cipher = R.encrypt(plain, w1, w2, shifts)
            assert R.decrypt(cipher, w1, w2, shifts) == plain
            assert tuple(cipher) == independent_cipher(plain, w1, w2, shifts)
            selected = sorted(rng.sample(range(97), min(24, 97)))
            obs = [(plain[i], cipher[i], *shifts[i]) for i in selected]
            assert R.feasible(q, obs, 100000)["status"] == "SAT"
            round_trips += 1
    # Cap exhaustion must never masquerade as an exact negative.
    assert R.feasible(26, [(0, 0, 0, 0), (1, 1, 0, 0)], 0)["status"] == "UNKNOWN"
    assert R.feasible(26, [(0, 0, 0, 0), (0, 1, 0, 0)])["status"] == "UNSAT"
    assert R.feasible(26, [])["status"] == "SAT"
    sizes = Counter()
    differential_schedules = []
    for n1, n2, d1, d2 in itertools.product(range(1, 5), range(1, 5), (-1, 1), (-1, 1)):
        for r1, r2 in itertools.product(range(n1), range(n2)):
            shifts = R.clocks(97, n1, n2, r1, r2, d1, d2)
            sizes["differential_raw_schedules"] += 1
            if R.collapses(shifts, 26):
                sizes["differential_constant_relative_schedules"] += 1
            else:
                differential_schedules.append(shifts)
                sizes["differential_retained_schedules"] += 1
    sizes["differential_labelled_settings"] = 16 * sizes["differential_retained_schedules"]
    sizes["odometer_labelled_settings"] = 16 * 4 * 26 * sum(range(1, 5))
    # Declared exploratory synthetic stress test; uniform random symbol pairs,
    # not the K4 known-letter positions and not a prospective English power gate.
    stress = {"plants": Counter(), "random_pairs": Counter()}
    max_nodes = 0
    for family in ("odometer", "differential"):
        for j in range(32):
            n = 1 + j % 4
            shifts = (R.odometer(97, n, j % n, j % 26, 1 if j % 2 else -1, 1)
                      if family == "odometer" else differential_schedules[j])
            w1, w2 = rng.sample(range(26), 26), rng.sample(range(26), 26)
            plain = [rng.randrange(26) for _ in range(97)]
            cipher = R.encrypt(plain, w1, w2, shifts)
            chosen = sorted(rng.sample(range(97), 24))
            for kind in ("plants", "random_pairs"):
                obs = [(plain[i], cipher[i] if kind == "plants" else rng.randrange(26), *shifts[i]) for i in chosen]
                result = R.feasible(26, obs, 10000)
                stress[kind][result["status"]] += 1
                max_nodes = max(max_nodes, result["nodes"])
                if kind == "plants":
                    assert result["status"] != "UNSAT"
    example_plain = [0, 1, 2, 3, 4, 0, 3]
    example_w1, example_w2 = [2, 4, 1, 0, 3], [1, 3, 4, 2, 0]
    example_shifts = R.odometer(7, 1, 0, 0, 1, 1, q=5)
    return {"status": "PASS", "toy_exhaustive_comparisons": comparisons,
            "constant_relative_collapse_checks": collapse_checks, "round_trips": round_trips,
            "composite_alphabets_tested": [4, 6, 26], "structural_counts": dict(sizes),
            "synthetic_stress": {k: dict(v) for k, v in stress.items()}, "stress_max_nodes": max_nodes,
            "worked_example": {"q": 5, "plaintext": example_plain, "w1": example_w1, "w2": example_w2,
                               "shifts": example_shifts, "ciphertext": R.encrypt(example_plain, example_w1, example_w2, example_shifts)},
            "scope": "Synthetic mathematical validation only; no K4 or English recovery gate."}


if __name__ == "__main__":
    result = run()
    if len(sys.argv) == 2:
        Path(sys.argv[1]).write_text(json.dumps(result, indent=2) + "\n")
    else:
        print(json.dumps(result, indent=2))
