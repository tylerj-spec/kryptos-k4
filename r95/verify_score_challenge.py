#!/usr/bin/env python3
"""Independent, scalar, saved-evidence review of the R95 development test.

This file imports neither the experiment nor any cipher/score implementation.
Its forward-map formulation changes output contact labels of the true forward
rotors; the experiment labels the equivalent swaps in inverse-rotor entries.
No optimization, training, target search, or independent-model promotion occurs.
Run once through the separately registered aggregate resource wrapper.
"""

import argparse
import array
import csv
import hashlib
import io
import json
import math
import sys
from collections import Counter
from pathlib import Path


EPSILON = 1e-9
SCORE_ABS_TOLERANCE = 1e-8
MODEL5_SHA256 = "e9c0848f5e256814387968c09006a44804e90a72aeb79034d0b12abfcce31abd"
MODEL4_SHA256 = "85b4adf264619a12c9ed646c7d4fc952ef76025db67dd96f2b668ea1e1cf1f41"
TRAINING_SHA256 = "871627e5fd2f84b4afa976516303098f437b5c339b7297db238fcd1ecb0e0434"
PANEL_SHA256 = "9b3ed6b49d437d4289f2a1126dd79b61ed7158b0e35b408bb39b1409aab8786c"
TRUTH_SHA256 = "27aecaf0aa2050e12d0d05e6c2ccc84b0598acd170e3e47f8667718732cf6ebf"
CATEGORIES = ("exact_text", "near_wrong", "below95")
SCORES = ("lm4", "lm5")
SCORE_FIELD = {"lm4": "lm4_sum_log10", "lm5": "lm5_sum_log10"}
CELL_NAMES = ("n1t3", "n1t4", "n2t1", "n2t2", "n3t1", "n3t2", "n4t0", "n4t1")
CASE_IDS = tuple(f"D_{i:03d}" for i in range(48))
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def checked_digest(path, expected):
    actual = digest_file(path)
    require(actual == expected, f"Digest mismatch: {path.name}")
    return actual


def manifest_records(repo, manifest):
    entries = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split(maxsplit=1)
        require(len(parts) == 2, "Malformed SHA256 manifest line")
        digest, relative = parts
        relative = relative.lstrip("*")
        require(len(digest) == 64 and all(c in "0123456789abcdef" for c in digest),
                "Malformed digest")
        path = Path(relative)
        require(not path.is_absolute() and ".." not in path.parts,
                "Manifest path must remain inside the repository")
        require(relative not in entries, "Duplicate manifest path")
        resolved = (repo / path).resolve()
        require(resolved.is_relative_to(repo), "Manifest symlink escapes repository")
        entries[relative] = checked_digest(resolved, digest)
    require(entries, "Empty manifest")
    return entries


def equivalent_numbers(actual, expected, context):
    """Check all fields in an expected structure; numeric scores have a tight tolerance."""
    if isinstance(expected, dict):
        require(isinstance(actual, dict), f"Expected object at {context}")
        for key, value in expected.items():
            require(key in actual, f"Missing field {context}.{key}")
            equivalent_numbers(actual[key], value, f"{context}.{key}")
    elif isinstance(expected, list):
        require(isinstance(actual, list) and len(actual) == len(expected),
                f"List length/type mismatch at {context}")
        for number, (observed, wanted) in enumerate(zip(actual, expected)):
            equivalent_numbers(observed, wanted, f"{context}[{number}]")
    elif isinstance(expected, bool):
        require(type(actual) is bool and actual is expected, f"Boolean mismatch at {context}")
    elif isinstance(expected, int):
        require(type(actual) is int and actual == expected, f"Integer mismatch at {context}")
    elif isinstance(expected, float):
        require(type(actual) in (int, float) and math.isfinite(actual),
                f"Nonfinite/non-numeric score at {context}")
        require(abs(actual - expected) <= SCORE_ABS_TOLERANCE,
                f"Score mismatch at {context}: {actual!r} != {expected!r}")
    else:
        require(actual == expected, f"Value mismatch at {context}")


def keyed_alphabet(keyword):
    result = ""
    for letter in keyword + ALPHABET:
        if letter not in result:
            result += letter
    return result


CONTACTS = {
    "AZ": ALPHABET,
    "KRY": keyed_alphabet("KRYPTOS"),
    "PAL": keyed_alphabet("PALIMPSEST"),
    "ABS": keyed_alphabet("ABSCISSA"),
}


def validate_text(text):
    require(isinstance(text, str) and len(text) == 97
            and all(letter in ALPHABET for letter in text), "Invalid 97-letter text")


def validate_wiring(wiring):
    require(isinstance(wiring, list) and len(wiring) == 26
            and all(type(value) is int for value in wiring)
            and sorted(wiring) == list(range(26)), "Wiring is not a 26-contact permutation")


def schedule(label):
    require(isinstance(label, list) and len(label) == 7, "Invalid structural label")
    input_name, output_name, period, phase, slow_phase, first_direction, second_direction = label
    require(input_name in CONTACTS and output_name in CONTACTS, "Unknown contact alphabet")
    require(all(type(value) is int for value in label[2:]), "Noninteger structural label")
    require(period in (1, 2, 3, 4) and 0 <= phase < period and 0 <= slow_phase < 26,
            "Structural label outside registered period/phase domain")
    require(first_direction in (-1, 1) and second_direction in (-1, 1), "Invalid direction")
    positions = []
    slow_indices = []
    for position in range(97):
        fast_index = (position + phase) // period
        slow_index = (fast_index + slow_phase) // 26
        positions.append((first_direction * fast_index, second_direction * slow_index))
        slow_indices.append(slow_index)
    turns = sum(slow_indices[i] != slow_indices[i - 1] for i in range(1, 97))
    return CONTACTS[input_name], CONTACTS[output_name], positions, turns


def forward(text, first, second, label):
    """Independent forward contact traversal, without an imported cipher reference."""
    input_letters, output_letters, positions, _ = schedule(label)
    emitted = []
    for character, (fast, slow) in zip(text, positions):
        fast_entry = (input_letters.index(character) + fast) % 26
        stationary_middle = (first[fast_entry] - fast) % 26
        slow_entry = (stationary_middle + slow) % 26
        emitted.append(output_letters[(second[slow_entry] - slow) % 26])
    return "".join(emitted)


def backward(ciphertext, first, second, label):
    """Invert each forward contact by its unique preimage, not an inverse-map formula."""
    input_letters, output_letters, positions, _ = schedule(label)
    recovered = []
    for character, (fast, slow) in zip(ciphertext, positions):
        slow_exit = (output_letters.index(character) + slow) % 26
        slow_entry = second.index(slow_exit)
        fast_exit = (slow_entry - slow + fast) % 26
        fast_entry = first.index(fast_exit)
        recovered.append(input_letters[(fast_entry - fast) % 26])
    return "".join(recovered)


def swap_forward_outputs(wiring, left, right):
    """An inverse-entry swap equals exchanging these forward output contact values."""
    return [right if value == left else left if value == right else value for value in wiring]


class ScalarLanguageModel:
    def __init__(self, model5, model4):
        checked_digest(model5, MODEL5_SHA256)
        checked_digest(model4, MODEL4_SHA256)
        lower_bytes = model4.read_bytes()
        require(lower_bytes[:8] == b"R59LM\x04\x00\x00", "Incorrect lower-four header")
        require(len(lower_bytes) == 8 + 4 * sum(26 ** order for order in range(1, 5)),
                "Incorrect lower-four byte count")
        self.tables = [None]
        with model5.open("rb") as stream:
            require(stream.read(8) == b"R59LM\x05\x00\x00", "Incorrect order-five header")
            lower_cursor = 8
            for order in range(1, 6):
                byte_count = 4 * 26 ** order
                raw_table = stream.read(byte_count)
                require(len(raw_table) == byte_count, "Truncated language model")
                if order < 5:
                    require(raw_table == lower_bytes[lower_cursor:lower_cursor + byte_count],
                            "Order-five prefix differs from frozen lower-four model")
                    lower_cursor += byte_count
                values = array.array("f")
                require(values.itemsize == 4, "Unsupported native float width")
                values.frombytes(raw_table)
                if sys.byteorder != "little":
                    values.byteswap()
                self.tables.append(values)
            require(not stream.read(1), "Trailing bytes in language model")

    def score_pair(self, text):
        """Scalar float64 sums of the stored float32 log10 conditional probabilities."""
        lower_score = 0.0
        higher_score = 0.0
        suffix = 0
        for position, character in enumerate(text):
            suffix = (26 * suffix + ord(character) - ord("A")) % (26 ** 5)
            low_order = min(position + 1, 4)
            high_order = min(position + 1, 5)
            low_term = self.tables[low_order][suffix % (26 ** low_order)]
            high_term = self.tables[high_order][suffix % (26 ** high_order)]
            require(math.isfinite(low_term) and math.isfinite(high_term), "Nonfinite model term")
            lower_score += low_term
            higher_score += high_term
        return {"lm4": lower_score, "lm5": higher_score}


def category_for(matches):
    return "exact_text" if matches == 97 else "near_wrong" if matches >= 95 else "below95"


def comparison(score, truth_score):
    difference = score - truth_score
    return "wins" if difference > EPSILON else "losses" if difference < -EPSILON else "ties"


def case_metrics(records, truth_scores, score_name):
    metrics = {"categories": {}, "any_wrong_win": False, "any_below95_win": False,
               "any_wrong_tie": False, "any_below95_tie": False}
    score_field = SCORE_FIELD[score_name]
    for category in CATEGORIES:
        selected = [row for row in records if category_for(row["matches"]) == category]
        outcomes = Counter(comparison(row[score_field], truth_scores[score_name]) for row in selected)
        metrics["categories"][category] = {
            "labels": len(selected), "distinct_plaintexts": len({row["text"] for row in selected}),
            "wins": outcomes["wins"], "ties": outcomes["ties"], "losses": outcomes["losses"],
        }
    for row in records:
        outcome = comparison(row[score_field], truth_scores[score_name])
        if row["matches"] < 97:
            metrics["any_wrong_win"] |= outcome == "wins"
            metrics["any_wrong_tie"] |= outcome == "ties"
        if row["matches"] < 95:
            metrics["any_below95_win"] |= outcome == "wins"
            metrics["any_below95_tie"] |= outcome == "ties"
    return metrics


def aggregate_metrics(cases, score_name):
    mapping = {"wrong_win_cases": "any_wrong_win", "below95_win_cases": "any_below95_win",
               "wrong_tie_cases": "any_wrong_tie", "below95_tie_cases": "any_below95_tie"}
    result = {key: sum(case["metrics"][score_name][field] for case in cases)
              for key, field in mapping.items()}
    result["categories"] = {
        category: {field: sum(case["metrics"][score_name]["categories"][category][field] for case in cases)
                   for field in ("labels", "distinct_plaintexts", "wins", "ties", "losses")}
        for category in CATEGORIES
    }
    return result


def best_witness(records, first, second, score_name, threshold):
    eligible = [row for row in records if row["matches"] < threshold]
    if not eligible:
        return None
    # Python max returns the first entry on an exactly equal raw score.
    best = dict(max(eligible, key=lambda row: row[SCORE_FIELD[score_name]]))
    left, right = best["swap"]
    best["W1"] = swap_forward_outputs(first, left, right) if best["inverse_wiring"] == "U" else first[:]
    best["W2"] = swap_forward_outputs(second, left, right) if best["inverse_wiring"] == "V" else second[:]
    return best


def read_jsonl(stream, context):
    line = stream.readline()
    require(bool(line), f"Unexpected end of {context}")
    return json.loads(line)


def verify(args):
    repo = args.repo.resolve()
    run = args.run.resolve()
    require(run.is_relative_to(repo / "r95"), "Run directory must be inside r95")
    protocol = args.protocol.resolve()
    require(protocol == repo / "r95/PROTOCOL.sha256", "Unexpected protocol-manifest path")
    require(Path(__file__).resolve() == repo / "r95/verify_score_challenge.py",
            "Reviewer must run from its registered repository path")
    protocol_hashes = manifest_records(repo, protocol)
    required_protocol_entries = {
        "r95/PREREGISTRATION.md", "r95/score_challenge.py", "r95/verify_score_challenge.py",
        "r94/inputs/PANEL_TRUTH.json", "r94/inputs/PANEL.tsv",
        "r91/R59_LOWER4_FROM_K5.bin", "r59/blind/lm_build.cpp",
    }
    require(required_protocol_entries <= set(protocol_hashes), "Protocol lacks required source/input pins")
    output_hashes = manifest_records(repo, run / "OUTPUTS.sha256")
    truth_path = repo / "r94/inputs/PANEL_TRUTH.json"
    panel_path = repo / "r94/inputs/PANEL.tsv"
    checked_digest(truth_path, TRUTH_SHA256)
    checked_digest(panel_path, PANEL_SHA256)
    truth = json.loads(truth_path.read_text(encoding="utf-8"))
    require(sorted(truth) == list(CASE_IDS), "Unexpected truth-panel case IDs")
    with panel_path.open(encoding="utf-8", newline="") as stream:
        panel_rows = list(csv.DictReader(stream, delimiter="\t"))
    require([row["id"] for row in panel_rows] == list(CASE_IDS), "Unexpected ciphertext-panel order")
    panel = {row["id"]: row for row in panel_rows}
    checked_digest(args.training_text, TRAINING_SHA256)
    # Match the public builder's A-Z letter stream, retaining a raw-file hash above.
    training = bytes(value for value in args.training_text.read_bytes() if 65 <= value <= 90)
    model = ScalarLanguageModel(args.model5, repo / "r91/R59_LOWER4_FROM_K5.bin")
    verified_cases = []
    overlap_cases = []
    max_score_error = 0.0
    with (run / "CASES.jsonl").open(encoding="utf-8") as cases_stream:
        for case_id in CASE_IDS:
            neighbor_path = run / "neighbors" / f"{case_id}.jsonl"
            require(neighbor_path.stat().st_size <= 512 * 1024, "Neighbor shard exceeds retention cap")
            neighbors_stream = io.StringIO(neighbor_path.read_text(encoding="utf-8"))
            actual_case = read_jsonl(cases_stream, "CASES.jsonl")
            item = truth[case_id]
            label, first, second = item["label"], item["W1"], item["W2"]
            plaintext, ciphertext = item["pt"], item["ct"]
            validate_text(plaintext)
            validate_text(ciphertext)
            validate_wiring(first)
            validate_wiring(second)
            require(panel[case_id]["ciphertext"] == ciphertext, "Panel/truth ciphertext mismatch")
            require(panel[case_id]["label"] == ",".join(map(str, label)), "Panel/truth label mismatch")
            _, _, _, turns = schedule(label)
            cell = f"n{label[2]}t{turns}"
            require(cell == item["cell"] and turns == item["turnovers"] and cell in CELL_NAMES,
                    "Turnover/cell mismatch")
            require(forward(plaintext, first, second, label) == ciphertext, "Truth forward mismatch")
            require(backward(ciphertext, first, second, label) == plaintext, "Truth inverse mismatch")
            truth_scores = model.score_pair(plaintext)
            offset = training.find(plaintext.encode("ascii"))
            overlap = {"present": offset >= 0, "first_normalized_offset": offset if offset >= 0 else None}
            if offset >= 0:
                overlap_cases.append(case_id)
            records = []
            for inverse_name in ("U", "V"):
                for left in range(26):
                    for right in range(left + 1, 26):
                        changed_first = swap_forward_outputs(first, left, right) if inverse_name == "U" else first
                        changed_second = swap_forward_outputs(second, left, right) if inverse_name == "V" else second
                        text = backward(ciphertext, changed_first, changed_second, label)
                        require(forward(text, changed_first, changed_second, label) == ciphertext,
                                "Neighbor forward/inverse inconsistency")
                        matches = sum(a == b for a, b in zip(text, plaintext))
                        scores = model.score_pair(text)
                        expected = {"id": case_id, "inverse_wiring": inverse_name, "swap": [left, right],
                                    "text": text, "matches": matches,
                                    "lm4_sum_log10": scores["lm4"], "lm5_sum_log10": scores["lm5"],
                                    "lm4_delta": scores["lm4"] - truth_scores["lm4"],
                                    "lm5_delta": scores["lm5"] - truth_scores["lm5"],
                                    "forward_witness": True, "same_plaintext_on97": matches == 97}
                        actual = read_jsonl(neighbors_stream, f"neighbors/{case_id}.jsonl")
                        equivalent_numbers(actual, expected, f"neighbor {case_id}/{inverse_name}/{left}/{right}")
                        for score_name in SCORES:
                            field = SCORE_FIELD[score_name]
                            max_score_error = max(max_score_error, abs(actual[field] - expected[field]))
                            require(comparison(actual[field], truth_scores[score_name])
                                    == comparison(expected[field], truth_scores[score_name]),
                                    "Recorded score tolerance changes an epsilon-threshold classification")
                            require(comparison(actual[field], actual_case["truth"][field])
                                    == comparison(expected[field], truth_scores[score_name]),
                                    "Recorded score/truth disposition disagrees with scalar review")
                            delta_field = f"{score_name}_delta"
                            require(comparison(actual[delta_field], 0.0)
                                    == comparison(expected[delta_field], 0.0),
                                    "Recorded delta disposition disagrees with scalar review")
                            require(abs(actual[delta_field] - (actual[field] - actual_case["truth"][field]))
                                    <= SCORE_ABS_TOLERANCE, "Recorded delta disagrees with recorded score/truth")
                        records.append(expected)
            require(len(records) == 650, "Incomplete neighbor catalog")
            metrics = {name: case_metrics(records, truth_scores, name) for name in SCORES}
            witnesses = {name: {"best_wrong": best_witness(records, first, second, name, 97),
                                "best_below95": best_witness(records, first, second, name, 95)}
                         for name in SCORES}
            margins = {
                name: {"best_wrong_delta": (witnesses[name]["best_wrong"][SCORE_FIELD[name]] - truth_scores[name])
                       if witnesses[name]["best_wrong"] is not None else None,
                       "best_below95_delta": (witnesses[name]["best_below95"][SCORE_FIELD[name]] - truth_scores[name])
                       if witnesses[name]["best_below95"] is not None else None}
                for name in SCORES
            }
            expected_case = {
                "id": case_id, "cell": cell, "label": label, "ciphertext": ciphertext,
                "truth": {"text": plaintext, "W1": first, "W2": second,
                          "lm4_sum_log10": truth_scores["lm4"], "lm5_sum_log10": truth_scores["lm5"]},
                "neighbors_evaluated": 650, "distinct_plaintexts": len({row["text"] for row in records}),
                "metrics": metrics, "witnesses": witnesses, "margins": margins, "training_overlap": overlap,
            }
            equivalent_numbers(actual_case, expected_case, f"case {case_id}")
            verified_cases.append(expected_case)
            require(not neighbors_stream.read().strip(), "Unexpected trailing neighbor records")
            neighbors_stream.close()
        require(not cases_stream.read().strip(), "Unexpected trailing case records")
    aggregate = {name: aggregate_metrics(verified_cases, name) for name in SCORES}
    require(Counter(case["cell"] for case in verified_cases) == Counter({cell: 6 for cell in CELL_NAMES}),
            "Expected six cases per turnover cell")
    by_cell = {
        cell: {"cases": 6, "metrics": {name: aggregate_metrics(
            [case for case in verified_cases if case["cell"] == cell], name) for name in SCORES}}
        for cell in CELL_NAMES
    }
    verdict = "GO_FOR_CONDITIONAL_DEVELOPMENT" if aggregate["lm5"]["below95_win_cases"] <= 2 else "SCORE_NO_GO"
    expected_summary = {
        "status": "COMPLETE", "mode": "SPENT_SYNTHETIC_DEVELOPMENT",
        "cases": 48, "neighbors_evaluated": 31200, "metrics": aggregate, "by_cell": by_cell,
        "score_evaluations_per_score": 31248, "score_order": ["lm4", "lm5"],
        "epsilon": EPSILON,
        "primary_endpoint": "cases with any below95 neighbor above truth + epsilon",
        "go_max_cases": 2, "decision_pending_separate_verification": True,
        "candidate_verdict": verdict,
        "training_overlap": {"cases_present": len(overlap_cases),
                             "normalized_training_letters": len(training), "rows_discarded": 0},
    }
    summary = json.loads((run / "SUMMARY.json").read_text(encoding="utf-8"))
    equivalent_numbers(summary, expected_summary, "SUMMARY")
    require(summary["epsilon"] == EPSILON, "Summary decision epsilon differs from preregistration")
    receipt = json.loads((run / "RECEIPT.json").read_text(encoding="utf-8"))
    expected_input_hashes = {"r94/inputs/PANEL.tsv": PANEL_SHA256,
                             "r94/inputs/PANEL_TRUTH.json": TRUTH_SHA256}
    expected_receipt = {
        "status": "COMPLETE", "protocol_sha256": digest_file(protocol),
        "protocol_files_sha256": protocol_hashes,
        "source_sha256": protocol_hashes["r95/score_challenge.py"],
        "input_sha256": expected_input_hashes,
        "models": {
            "lm4": {"sha256": MODEL4_SHA256,
                    "bytes": (repo / "r91/R59_LOWER4_FROM_K5.bin").stat().st_size, "order": 4},
            "lm5": {"sha256": MODEL5_SHA256, "bytes": args.model5.stat().st_size, "order": 5,
                    "definition": "K=5 builder top order uses raw counts; not the old K=6 order5 table"},
            "lower_tables_byte_equal": True,
        },
        "training": {"sha256": TRAINING_SHA256, "bytes": args.training_text.stat().st_size,
                     "normalized_letters": len(training), "filter": "retain ASCII A-Z only",
                     "overlap_is_diagnostic_only": True},
        "runtime": {"threads_requested": 1},
        "output_manifest_relative_to": "repository root",
        "retention_byte_caps": {"neighbor_shard": 524288, "json_or_cases_file": 2097152,
                                "event_file": 1048576, "all_controlled_outputs": 33554432},
        "truth_available_from_start": True, "random_restarts": 0, "optimization_calls": 0, "retries": 0,
    }
    equivalent_numbers(receipt, expected_receipt, "RECEIPT")
    require(receipt["protocol_files_sha256"] == protocol_hashes, "Receipt protocol inventory differs")
    require(receipt["input_sha256"] == expected_input_hashes, "Receipt input inventory differs")
    runtime = receipt["runtime"]
    require(all(isinstance(runtime.get(key), str) and bool(runtime[key]) for key in ("python", "numpy")),
            "Missing/invalid runtime version metadata")
    require(isinstance(runtime.get("argv"), list) and bool(runtime["argv"])
            and all(isinstance(value, str) for value in runtime["argv"]), "Invalid runtime argv metadata")
    for filename in ("CASES.jsonl", "SUMMARY.json", "RECEIPT.json"):
        require((run / filename).stat().st_size <= 2 * 1024 * 1024, "JSON/cases file exceeds retention cap")
    require((run / "EVENTS.jsonl").stat().st_size <= 1024 * 1024, "Event file exceeds retention cap")
    expected_outputs = tuple(f"neighbors/{case_id}.jsonl" for case_id in CASE_IDS) + (
        "CASES.jsonl", "SUMMARY.json", "EVENTS.jsonl")
    require(set(receipt["output_sha256"]) == set(expected_outputs), "Receipt output inventory differs")
    for filename in expected_outputs:
        checked_digest(run / filename, receipt["output_sha256"][filename])
    expected_manifest_paths = {str((run / filename).relative_to(repo))
                               for filename in expected_outputs + ("RECEIPT.json",)}
    require(set(output_hashes) == expected_manifest_paths, "Frozen manifest output inventory differs")
    retained_bytes = sum(path.stat().st_size for path in run.rglob("*") if path.is_file())
    require(retained_bytes <= 32 * 1024 * 1024, "Run output exceeds aggregate retention cap")
    # Recheck all protocol and frozen output bytes after the complete review.
    require(manifest_records(repo, protocol) == protocol_hashes, "Protocol changed during review")
    require(manifest_records(repo, run / "OUTPUTS.sha256") == output_hashes, "Output freeze changed during review")
    checked_digest(args.model5, MODEL5_SHA256)
    checked_digest(args.training_text, TRAINING_SHA256)
    return {
        "schema": "r95-independent-scalar-review-v1", "status": "PASS",
        "independent_model_review": "NONE", "review_type": "INTERNAL_SEPARATE_IMPLEMENTATION",
        "scope": "Spent synthetic score-neighborhood development; no target computation or recovery search",
        "cases_verified": 48, "neighbor_labels_verified": 31200,
        "truth_forward_and_inverse_witnesses_verified": 48,
        "neighbor_forward_and_inverse_witnesses_verified": 31200,
        "plaintext_score_pairs_verified": 31248,
        "score_tolerance": SCORE_ABS_TOLERANCE, "decision_epsilon": EPSILON,
        "maximum_observed_score_error": max_score_error,
        "lower4_prefix_byte_equality": True,
        "primary_catalog": "True inverse U then V, lexicographic contact-pair swaps",
        "review_catalog": "Equivalent forward-output-value transpositions, independent scalar preimage inverse",
        "model5_sha256": MODEL5_SHA256, "model4_sha256": MODEL4_SHA256,
        "training_sha256": TRAINING_SHA256,
        "training_overlap_case_ids": overlap_cases,
        "training_overlap_is_not_clean_holdout_certification": True,
        "count_semantics": "Wins/ties/losses count labels; distinct_plaintexts counts all texts in each category and sums per case",
        "receipt_scientific_source_and_artifact_metadata_verified": True,
        "runtime_metadata_types_verified": True,
        "runtime_versions_not_required_to_equal_verifier_environment": True,
        "summary": expected_summary,
        "protocol_manifest_sha256": digest_file(protocol), "protocol_hash_entries_verified": len(protocol_hashes),
        "frozen_output_hash_entries_verified": len(output_hashes),
        "retained_output_bytes": retained_bytes,
        "frozen_output_sha256": output_hashes,
        "reviewer_source_sha256": digest_file(Path(__file__).resolve()),
        "limitations": [
            "The data are spent development material with public answers.",
            "All 650 local labels are checked; wider key neighborhoods and global score optima are not.",
            "No key-recovery optimizer, new hidden gate, full method classifier, or target was run.",
            "Pass permits conditional-solver development only; neither outcome identifies or excludes a cipher family.",
            "Resource enforcement and publication ancestry are reviewed separately.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--model5", type=Path, required=True)
    parser.add_argument("--training-text", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    # Refusal of a reused directory must not overwrite any previous failure record.
    args.out.mkdir(parents=True, exist_ok=False)
    try:
        result = verify(args)
        with (args.out / "REVIEW_RESULTS.json").open("x", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
        print(json.dumps({"status": "PASS", "cases": 48, "neighbor_labels": 31200,
                          "candidate_verdict": result["summary"]["candidate_verdict"]}, sort_keys=True))
    except Exception as exc:
        with (args.out / "REVIEW_FAILURE.json").open("x", encoding="utf-8") as stream:
            json.dump({"status": "FAIL", "error_type": type(exc).__name__, "error": str(exc)},
                      stream, indent=2, sort_keys=True)
            stream.write("\n")
        raise


if __name__ == "__main__":
    main()
