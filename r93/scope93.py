#!/usr/bin/env python3
"""Synthetic schedule accounting only. No ciphertext, clues, or solver imports."""
from collections import Counter
import json
from pathlib import Path
import sys

LENGTH = 97
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALPHABETS = tuple("".join(dict.fromkeys(word + AZ))
                  for word in ("", "KRYPTOS", "PALIMPSEST", "ABSCISSA"))


def schedule(n, phase, direction):
    return tuple((direction * ((i + phase) // n)) % 26 for i in range(LENGTH))


def account():
    labels = [(n, phase, direction) for n in range(5, 97)
              for phase in range(1, n) for direction in (-1, 1)]
    buckets = Counter(schedule(*label) for label in labels)
    old_zero = {schedule(n, 0, direction) for n in range(1, 97)
                for direction in (-1, 1)}
    old_phase = {schedule(n, phase, direction) for n in (2, 3, 4)
                 for phase in range(1, n) for direction in (-1, 1)}
    shared = set(buckets) & old_zero
    affine = []
    for a, aa in enumerate(ALPHABETS):
        for b, bb in enumerate(ALPHABETS):
            index = [bb.index(letter) for letter in aa]
            for sign in (-1, 1):
                for shift in range(26):
                    if all(index[x] == (sign*x + shift) % 26 for x in range(26)):
                        affine.append([a, b, sign, shift])
    assert affine == [[i, i, 1, 0] for i in range(4)]
    assert not (set(buckets) & old_phase)
    answer = {
        "scope": {"n_min": 5, "n_max": 96, "phase": "1..n-1",
                  "directions": [-1, 1], "contact_pairs": 16, "length": LENGTH},
        "all_n2_n96_nonzero_phase_labels": 16*2*sum(range(1, 96)),
        "r92_n2_n4_labels": 16*2*sum(range(1, 4)),
        "registered_labels": 16*len(labels),
        "clock_labels": len(labels),
        "distinct_clock_sequences": len(buckets),
        "distinct_clock_contact_labels": 16*len(buckets),
        "r87_zero_phase_shared_clocks": len(shared),
        "r87_zero_phase_shared_clock_contact_labels": 16*len(shared),
        "raw_labels_equivalent_to_r87_clocks": 16*sum(buckets[c] for c in shared),
        "remaining_distinct_clock_contact_labels": 16*(len(buckets)-len(shared)),
        "r92_shared_clocks": 0,
        "largest_clock_multiplicity": max(buckets.values()),
        "clock_multiplicity_histogram": dict(sorted(Counter(buckets.values()).items())),
        "affine_contact_relations": affine,
        "primary_base_calls_201_inputs": 16*len(labels)*201,
        "logical_exact_and_delete_tests_201_inputs": 16*len(labels)*201*25,
        "claim": "Labeled parameter counts, not independent cipher families or statistical trials."
    }
    assert answer["registered_labels"] == 145728
    assert answer["distinct_clock_sequences"] == 4690
    assert answer["raw_labels_equivalent_to_r87_clocks"] == 36096
    assert answer["remaining_distinct_clock_contact_labels"] == 73536
    return answer


if __name__ == "__main__":
    result = account()
    if len(sys.argv) == 2:
        Path(sys.argv[1]).write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps(result, sort_keys=True))
