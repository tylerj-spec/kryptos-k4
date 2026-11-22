#!/usr/bin/env python3
"""Same-model internal mathematical challenge of RX2; synthetic inputs only.

This is not an independent-model council vote, an English power gate, or a
target-ciphertext experiment. No K4 file, text, position, or known letter is read.
"""
import itertools
import json
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rotor_constraints as R


def oracle_cipher(p, w1, w2, shifts):
    q = len(w1)
    result = []
    for plain, (s1, s2) in zip(p, shifts):
        a = (plain + s1) % q
        first = (w1[a] - s1) % q
        b = (first + s2) % q
        result.append((w2[b] - s2) % q)
    return tuple(result)


def brute_first_wiring(q, observations):
    # Enumerate each complete W1. Check whether the required W2 outputs can
    # be part of a permutation by direct lookup, without component reduction.
    for wiring in itertools.permutations(range(q)):
        second, used = {}, {}
        for p, c, s1, s2 in observations:
            inp = (wiring[(p + s1) % q] - s1 + s2) % q
            out = (c + s2) % q
            if (inp in second and second[inp] != out) or (out in used and used[out] != inp):
                break
            second[inp], used[out] = out, inp
        else:
            return True
    return False


def run():
    rng = random.Random(902211)
    q, length = 4, 4
    wirings = list(itertools.permutations(range(q)))
    words = list(itertools.product(range(q), repeat=length))
    schedules = ([(0, 0), (1, 0), (2, 1), (3, 2)], [(0, 1), (1, 0), (2, 3), (0, 2)])
    exhaustive = 0
    for shifts in schedules:
        for plain in words:
            attainable = {oracle_cipher(plain, w1, w2, shifts) for w1 in wirings for w2 in wirings}
            for cipher in words:
                obs = [(p, c, *shift) for p, c, shift in zip(plain, cipher, shifts)]
                result = R.feasible(q, obs, max_nodes=100000)
                assert result["status"] == ("SAT" if cipher in attainable else "UNSAT")
                exhaustive += 1
    composite = 0
    outcomes = {"SAT": 0, "UNSAT": 0}
    for _ in range(200):
        obs = [tuple(rng.randrange(6) for _ in range(4)) for _ in range(rng.randrange(1, 13))]
        expected = "SAT" if brute_first_wiring(6, obs) else "UNSAT"
        assert R.feasible(6, obs, 100000)["status"] == expected
        shuffled = list(obs)
        rng.shuffle(shuffled)
        assert R.feasible(6, shuffled + shuffled[:2], 100000)["status"] == expected
        outcomes[expected] += 1
        composite += 1
    # Difference 13 is not invertible modulo 26. The proof does not divide by
    # it: these two equal-output observations are feasible exactly as written.
    assert R.feasible(26, [(0, 0, 0, 0), (1, 13, 0, 13)])["status"] == "SAT"
    assert R.feasible(26, [(0, 0, 0, 0), (1, 13, 0, 13), (1, 0, 0, 0)])["status"] == "UNSAT"
    gauge_checks = initial_angle_checks = 0
    for q in (4, 6, 26):
        for _ in range(10):
            w1, w2 = rng.sample(range(q), q), rng.sample(range(q), q)
            plain = [rng.randrange(q) for _ in range(40)]
            shifts = [(rng.randrange(q), rng.randrange(q)) for _ in plain]
            want = oracle_cipher(plain, w1, w2, shifts)
            for t in range(q):
                changed1 = [(v + t) % q for v in w1]
                changed2 = [w2[(x - t) % q] for x in range(q)]
                assert oracle_cipher(plain, changed1, changed2, shifts) == want
                gauge_checks += 1
            a1, a2 = rng.randrange(q), rng.randrange(q)
            shifted = [(s1 + a1, s2 + a2) for s1, s2 in shifts]
            conjugate1 = [(w1[(x + a1) % q] - a1) % q for x in range(q)]
            conjugate2 = [(w2[(x + a2) % q] - a2) % q for x in range(q)]
            assert oracle_cipher(plain, w1, w2, shifted) == oracle_cipher(plain, conjugate1, conjugate2, shifts)
            initial_angle_checks += 1
    raw, removed, removed_phase0, removed_phase_nonzero = [], [], [], []
    for n1, n2 in itertools.product(range(1, 5), repeat=2):
        for r1, r2 in itertools.product(range(n1), range(n2)):
            for d1, d2 in itertools.product((-1, 1), repeat=2):
                st = (n1, n2, r1, r2, d1, d2)
                sequence = tuple(R.clocks(97, *st))
                raw.append(sequence)
                if R.collapses(sequence, 26):
                    assert n1 == n2 and r1 == r2 and d1 == d2
                    removed.append(st)
                    (removed_phase0 if r1 == 0 else removed_phase_nonzero).append(st)
    assert len(raw) == len(set(raw)) == 400 and len(removed) == 20
    assert len(removed_phase0) == 8 and len(removed_phase_nonzero) == 12
    odo, static = [], 0
    for n in range(1, 5):
        for r in range(n):
            for h, d1, d2 in itertools.product(range(26), (-1, 1), (-1, 1)):
                sequence = tuple(R.odometer(97, n, r, h, d1, d2))
                assert not R.collapses(sequence, 26)
                odo.append(sequence)
                if len({s2 for _, s2 in sequence}) == 1:
                    assert n == 4 and h in (0, 1)
                    static += 1
    assert len(odo) == 1040 and len(set(odo)) == 1016 and static == 32
    # A boundary-phase rotor has time maps F0 != F1 == F2 here. A zero-phase
    # n>=2 rotor has F0==F1; a zero-phase n=1 rotor with F1==F2 is stationary
    # at all times. This pattern therefore cannot be absorbed as orientation.
    q = 26
    w = [1, 0] + list(range(2, q))
    phase_maps = [tuple((w[(p + s) % q] - s) % q for p in range(q)) for s in (0, 1, 1)]
    assert phase_maps[0] != phase_maps[1] and phase_maps[1] == phase_maps[2]
    # W1 identity and fixed W2=A/B swap gives a stationary substitution.
    # In R87 a stationary output map requires W*=a cyclic translation in the
    # selected contact numberings. Enumerate its 16*26 possible static maps.
    az = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    alph = ["".join(dict.fromkeys(word + az)) for word in ("", "KRYPTOS", "PALIMPSEST", "ABSCISSA")]
    static_r87_maps = {tuple(az.index(eout[(ein.index(p) + k) % 26]) for p in az)
                       for ein, eout, k in itertools.product(alph, alph, range(26))}
    assert tuple(w) not in static_r87_maps
    return {"status": "PASS", "review_role": "same-model internal challenge; not independent-model council",
            "q4_length4_exhaustive_plaintext_ciphertext_comparisons": exhaustive,
            "q6_random_oracle_comparisons": composite, "q6_outcomes": outcomes,
            "q6_observation_order_and_duplicate_checks": composite,
            "mod26_nonunit_difference_cases": 2,
            "interface_gauge_checks": gauge_checks, "initial_angle_absorption_checks": initial_angle_checks,
            "D": {"raw_clock_rows": 400, "constant_relative_rows": 20,
                  "retained_labelled_settings": 6080, "removed_r87_phase0_labels": 128,
                  "removed_phase_nonzero_labels_still_open": 192},
            "O": {"labelled_clock_rows": 1040, "distinct_literal_full_schedules": 1016,
                  "labelled_settings": 16640, "distinct_literal_schedules_times_contacts": 16256,
                  "static_second_clock_rows": 32, "static_second_labelled_settings": 512,
                  "constant_relative_rows": 0},
            "boundary_phase_not_absorbed_counterexample": {"q": 26, "n": 2, "r": 1,
                  "wiring": "swap 0 and 1; identity elsewhere", "full_time_map_pattern": "F0 != F1 == F2"},
            "static_second_counterexample_outside_all_r87_static_maps": True,
            "scope": "Synthetic mathematics only. No target text, known-letter positions, English score, or K4 call."}


if __name__ == "__main__":
    result = run()
    if len(sys.argv) == 2:
        Path(sys.argv[1]).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
