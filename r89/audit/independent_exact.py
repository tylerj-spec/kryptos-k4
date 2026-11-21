#!/usr/bin/env python3
"""Independent R89 aggregate-only exclusion replay; no candidate text is emitted.

F26 uses forward coordinate constraints rather than the builder's decryption.
RCT uses a conflict graph and its vertex covers, with exhaustive 4-contact
toy comparison against all possible wirings. This is a post-freeze audit.
"""
import ast
import hashlib
import itertools
import json
import sys
from pathlib import Path
import numpy as np

ROOT = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def keyed(word):
    return "".join(dict.fromkeys(word + AZ))


NAMES = ("KRYPTOS", "PALIMPSEST", "ABSCISSA", "NUANCE", "MAGNETIC", "PASSAGE", "CANDLE",
         "SANBORN", "SCHEIDT", "LANGLEY", "WEBSTER", "SHADING", "IQLUSION", "UNDERGRUUND",
         "DESPARATLY", "LAYERTWO", "INVISIBLE")
ALPHABETS = {"AZ": AZ, "QWERTY": "QWERTYUIOPASDFGHJKLZXCVBNM", "ALT": AZ[::2] + AZ[1::2],
             **{word: keyed(word) for word in NAMES}}
CONTACTS = {name: keyed(word) for name, word in (("AZ", ""), ("KRY", "KRYPTOS"),
                                               ("PAL", "PALIMPSEST"), ("ABS", "ABSCISSA"))}
KEYS = {"PAL": "PALIMPSEST", "ABS": "ABSCISSA"}
KRY = keyed("KRYPTOS")
INNER = [(b, u, v) for b in (5, 7, 9, 11) for u in range(1, b) for v in range(1, b) if u != v]
OUTER = [None] + [(name, sign, phase) for name, word in KEYS.items()
                 for sign in (1, -1) for phase in range(len(word))]
RCT_SETTINGS = list(itertools.product(CONTACTS, CONTACTS, (1, -1), (2, 3, 4, 5)))
RCT_SETTINGS = [(ei, eo, d, m, q) for ei, eo, d, m in RCT_SETTINGS for q in range(m)]


def relation_counts(x, y):
    """Counts all-, drop-one-, and drop-two-compatible partial permutations."""
    conflict = np.triu((x[:, None] == x[None, :]) != (y[:, None] == y[None, :]), 1)
    edges = int(conflict.sum())
    degree = conflict.sum(0) + conflict.sum(1)
    exact = edges == 0
    one = int(np.count_nonzero(degree == edges))
    covered = degree[:, None] + degree[None, :] - conflict - conflict.T
    two = int(np.count_nonzero(np.triu(covered == edges, 1)))
    return exact, one, two


def toy_relation_oracle():
    # All 16^4 ordered sets of 4 contact-pair constraints; all 4! wirings.
    universe = np.asarray(list(itertools.product(range(16), repeat=4)), dtype=np.int16)
    xs, ys = universe // 4, universe % 4
    best = np.zeros(len(xs), dtype=np.int8)
    for perm in itertools.permutations(range(4)):
        match = np.asarray(perm, dtype=np.int8)[xs] == ys
        best = np.maximum(best, match.sum(1))
    conflict = (xs[:, :, None] == xs[:, None, :]) != (ys[:, :, None] == ys[:, None, :])
    conflict &= np.triu(np.ones((4, 4), dtype=bool), 1)
    edges = conflict.sum((1, 2))
    degree = conflict.sum(1) + conflict.sum(2)
    all_ok = edges == 0
    one_ok = (degree == edges[:, None]).any(1)
    two_ok = np.zeros(len(xs), dtype=bool)
    for a in range(4):
        for b in range(a + 1, 4):
            two_ok |= degree[:, a] + degree[:, b] - conflict[:, a, b] == edges
    assert np.array_equal(all_ok, best >= 4)
    assert np.array_equal(one_ok, best >= 3)
    assert np.array_equal(two_ok, best >= 2)
    return {"constraint_sets": len(xs), "wirings_per_set": 24, "comparisons": int(len(xs) * 24),
            "exact_agreement": True, "drop_one_agreement": True, "drop_two_agreement": True}


def f26_forward(pt, alphabet, b, u, v):
    result = []
    for offset in range(0, len(pt), b):
        block = [alphabet.index(ch) for ch in pt[offset:offset + b]]
        length = len(block)
        result.extend(alphabet[13 * (block[(j + u) % length] // 13) + block[(j + v) % length] % 13]
                      for j in range(length))
    return "".join(result)


def f26_constraint_count(ct, known_positions, known_letters, alphabet, b, u, v):
    # Each known input coordinate must land at its corresponding output slot.
    hits = 0
    for position, letter in zip(known_positions, known_letters):
        start = position // b * b
        length = min(b, len(ct) - start)
        local = position - start
        row_source = alphabet.index(ct[start + (local - u) % length]) // 13
        col_source = alphabet.index(ct[start + (local - v) % length]) % 13
        target = alphabet.index(letter)
        hits += (row_source == target // 13 and col_source == target % 13)
    return hits


def f26_toy():
    # Explicit counterexample to the published general >=23 cutoff.
    pt = "A" * 97
    ct = f26_forward(pt, AZ, 5, 1, 2)
    altered = "O" + ct[1:]
    before = f26_constraint_count(ct, range(24), pt[:24], AZ, 5, 1, 2)
    after = f26_constraint_count(altered, range(24), pt[:24], AZ, 5, 1, 2)
    assert before == 24 and after == 22
    # Every one-letter change at every position of a 97-symbol toy input,
    # across all 188 block/offset settings: exact bound of <=2 changed outputs.
    tested = 0
    for b, u, v in INNER:
        for position in range(97):
            start = position // b * b
            length = min(b, 97 - start)
            affected = {start + (position - start + u) % length,
                        start + (position - start + v) % length}
            assert len(affected) <= 2
            tested += 1
    return {"synthetic_counterexample": {"plaintext": "A repeated 97 times", "alphabet": "AZ", "b": 5,
                                         "u": 1, "v": 2, "changed_ciphertext_position": 0,
                                         "change": "A to O", "known_positions": "0..23",
                                         "before_matches": before, "after_matches": after},
            "coordinate_support_positions_checked": tested,
            "single_symbol_substitutions_covered_by_support_bound": tested * 25,
            "general_one_ciphertext_substitution_threshold": 22,
            "maximum_changed_plaintext_symbols": 2}


def read_clues():
    tree = ast.parse((ROOT / "r73/sealed/reveal_k4.py").read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "CLUES" for t in node.targets):
            clues = ast.literal_eval(node.value)
            positions = [offset + i for offset, word in clues for i in range(len(word))]
            letters = "".join(word for _, word in clues)
            return np.asarray(positions, dtype=np.int16), letters
    raise RuntimeError("No literal CLUES definition")


def independent_f26(ct, pos, letters):
    # Undo only the pointwise outer substitution; never reconstruct a full candidate.
    raw = np.asarray([AZ.index(c) for c in ct], dtype=np.int16)
    kry_i = np.asarray([KRY.index(c) for c in AZ], dtype=np.int16)
    kry_letters = np.asarray([AZ.index(c) for c in KRY], dtype=np.int16)
    inner_ct = [raw]
    for name, sign, phase in OUTER[1:]:
        shifts = np.asarray([KRY.index(KEYS[name][(i + phase) % len(KEYS[name])]) for i in range(len(ct))])
        inner_ct.append(kry_letters[(kry_i[raw] - sign * shifts) % 26])
    inner_ct = np.asarray(inner_ct)
    row_at, col_at = [], []
    for b, u, v in INNER:
        start = pos // b * b
        length = np.minimum(b, len(ct) - start)
        row_at.append(start + (pos - start - u) % length)
        col_at.append(start + (pos - start - v) % length)
    row_at, col_at = np.asarray(row_at), np.asarray(col_at)
    counts = []
    for alphabet in ALPHABETS.values():
        index = np.asarray([alphabet.index(c) for c in AZ], dtype=np.int16)
        known = np.asarray([alphabet.index(c) for c in letters], dtype=np.int16)
        middle = index[inner_ct]
        matches = ((middle[:, row_at] // 13 == known[None, None, :] // 13) &
                   (middle[:, col_at] % 13 == known[None, None, :] % 13))
        counts.append(matches.sum(2).ravel())
    counts = np.concatenate(counts)
    assert len(counts) == 139120
    return {"max_hits": int(counts.max()), "n_at_max": int(np.count_nonzero(counts == counts.max())),
            "n_ge_22": int(np.count_nonzero(counts >= 22)), "n_ge_23": int(np.count_nonzero(counts >= 23)),
            "n_24": int(np.count_nonzero(counts == 24))}


def independent_rct(ct, pos, letters, also_two=False):
    raw = np.asarray([AZ.index(c) for c in ct], dtype=np.int16)
    exact, drop, two = 0, 0, 0
    for ei, eo, direction, modulus, residue in RCT_SETTINGS:
        step = direction * (1 + ((raw + residue) % modulus == 0))
        offset = np.r_[0, step.cumsum()[:-1]][pos]
        x = (np.asarray([CONTACTS[ei].index(c) for c in letters]) + offset) % 26
        y = (np.asarray([CONTACTS[eo].index(ct[i]) for i in pos]) + offset) % 26
        ex, one, pair = relation_counts(x, y)
        exact += int(ex)
        drop += one
        if also_two:
            two += pair
    return {"exact_feasible": exact, "drop_feasible": drop,
            **({"drop_two_feasible": two} if also_two else {})}


def main():
    report = {"review_kind": "independent aggregate-only post-freeze exact audit",
              "source_commit": "9e04e4e32eeb7c947e32979dc6663433e358192d",
              "toy_partial_permutation_oracle": toy_relation_oracle(), "f26_error_bound": f26_toy()}
    pos, letters = read_clues()
    rows = dict(line.split("\t") for line in (ROOT / "r89/k4/TARGET.tsv").read_text().splitlines()[1:] if line)
    expected = json.loads((ROOT / "r89/k4/EXACT.json").read_text())
    f26, rct, mismatch = {}, {}, []
    for i, (rid, ct) in enumerate(rows.items()):
        f26[rid] = independent_f26(ct, pos, letters)
        rct[rid] = independent_rct(ct, pos, letters, also_two=rid == "K4")
        ref = expected["F26"]["k4"] if rid == "K4" else expected["F26"]["shuffles"][rid]
        for key in ("max_hits", "n_ge_23", "n_24"):
            if ref[key] != f26[rid][key]:
                mismatch.append([rid, key, ref[key], f26[rid][key]])
        if i % 50 == 0:
            print("audited", i + 1, "of", len(rows), flush=True)
    for key in ("exact_feasible", "drop_feasible"):
        if expected["RCT"]["k4"][key] != rct["K4"][key]:
            mismatch.append(["K4", "RCT", key])
    rct_null_exact = sum(v["exact_feasible"] > 0 for k, v in rct.items() if k != "K4")
    rct_null_drop = sum(v["drop_feasible"] > 0 for k, v in rct.items() if k != "K4")
    assert rct_null_exact == expected["RCT"]["shuffles_with_feasible_exact"]
    assert rct_null_drop == expected["RCT"]["shuffles_with_feasible_drop"]
    assert not mismatch, mismatch
    null_max = [v["max_hits"] for k, v in f26.items() if k != "K4"]
    report.update({"items": len(rows), "f26_settings_per_item": 139120, "rct_settings_per_item": len(RCT_SETTINGS),
                   "f26_k4": f26["K4"], "rct_k4": rct["K4"],
                   "f26_null_max": max(null_max),
                   "f26_nulls_at_least_k4": sum(v >= f26["K4"]["max_hits"] for v in null_max),
                   "rct_nulls_exact_feasible": rct_null_exact, "rct_nulls_drop_feasible": rct_null_drop,
                   "reported_aggregate_mismatches": mismatch,
                   "one_ciphertext_substitution_f26_k4_max_bound": f26["K4"]["max_hits"] + 2,
                   "input_sha256": hashlib.sha256((ROOT / "r89/k4/TARGET.tsv").read_bytes()).hexdigest(),
                   "per_input": {rid: {"F26": f26[rid], "RCT": rct[rid]} for rid in rows}})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "per_input"}, indent=2))


if __name__ == "__main__":
    main()
