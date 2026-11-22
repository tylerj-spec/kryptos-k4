#!/usr/bin/env python3
"""R95: fixed-score development challenge on an already public synthetic panel.

There is no optimizer, key search, training, fresh holdout, or target input.
Both true wirings and the complete plaintext are deliberately available.
All nontrivial entry swaps in the true inverse wirings are retained as labels.
Identical recovered plaintexts are observation aliases, not equivalent ciphers.
"""
import os

for _variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
                  "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_variable] = "1"

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import sys
import time

import numpy as np


HERE = Path(__file__).resolve().parent
MODEL5_SHA256 = "e9c0848f5e256814387968c09006a44804e90a72aeb79034d0b12abfcce31abd"
MODEL4_SHA256 = "85b4adf264619a12c9ed646c7d4fc952ef76025db67dd96f2b668ea1e1cf1f41"
TRAINING_SHA256 = "871627e5fd2f84b4afa976516303098f437b5c339b7297db238fcd1ecb0e0434"
EPSILON = 1e-9
GO_MAX_CASES = 2
MAX_SHARD_BYTES = 512 * 1024
MAX_JSON_BYTES = 2 * 1024 * 1024
MAX_EVENT_BYTES = 1024 * 1024
MAX_OUTPUT_BYTES = 32 * 1024 * 1024
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALPHABETS = {
    name: "".join(dict.fromkeys(keyword + AZ))
    for name, keyword in (("AZ", ""), ("KRY", "KRYPTOS"),
                          ("PAL", "PALIMPSEST"), ("ABS", "ABSCISSA"))
}
CELLS = ("n1t3", "n1t4", "n2t1", "n2t2", "n3t1", "n3t2", "n4t0", "n4t1")
CATEGORIES = ("exact_text", "near_wrong", "below95")
SCORES = ("lm4", "lm5")
METRIC_FIELDS = ("labels", "distinct_plaintexts", "wins", "ties", "losses")
REQUIRED_PROTOCOL_PATHS = {
    "r95/PREREGISTRATION.md", "r95/score_challenge.py",
    "r94/inputs/PANEL.tsv", "r94/inputs/PANEL_TRUTH.json",
    "r91/R59_LOWER4_FROM_K5.bin",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest_bytes(value):
    return hashlib.sha256(value).hexdigest()


def digest_file(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def save_json(path, value):
    encoded = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    require(len(encoded.encode("utf-8")) <= MAX_JSON_BYTES, "JSON artifact exceeds byte cap")
    with path.open("x", encoding="utf-8") as stream:
        stream.write(encoded)


def line_json(stream, value, max_bytes=MAX_JSON_BYTES):
    encoded = json.dumps(value, separators=(",", ":"), allow_nan=False) + "\n"
    require(stream.tell() + len(encoded.encode("utf-8")) <= max_bytes,
            "NDJSON artifact exceeds byte cap")
    stream.write(encoded)


def check_retention(out):
    size = sum(path.stat().st_size for path in out.rglob("*") if path.is_file())
    require(size <= MAX_OUTPUT_BYTES, "retained output exceeds aggregate byte cap")
    return size


class Events:
    def __init__(self, path):
        self.path = path
        self.started_wall = time.monotonic()
        self.started_cpu = time.process_time()
        self.stream = path.open("x", encoding="utf-8")

    def add(self, name, **extra):
        line_json(self.stream, {
            "event": name,
            "wall_seconds": time.monotonic() - self.started_wall,
            "process_cpu_seconds": time.process_time() - self.started_cpu,
            **extra,
        }, MAX_EVENT_BYTES)
        self.stream.flush()

    def close(self):
        self.stream.close()


def verify_protocol(root, protocol):
    require(protocol == root / "r95/PROTOCOL.sha256", "unexpected protocol path")
    entries = {}
    for line in protocol.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        fields = line.split(maxsplit=1)
        require(len(fields) == 2, "malformed protocol line")
        expected, relative = fields
        require(re.fullmatch(r"[0-9a-f]{64}", expected) is not None,
                "malformed protocol digest")
        rel = Path(relative)
        require(not rel.is_absolute() and ".." not in rel.parts,
                "protocol paths must stay inside repository")
        require(relative not in entries, "duplicate protocol entry")
        path = (root / rel).resolve()
        require(path.is_relative_to(root) and path.is_file(),
                "protocol file missing or outside repository: " + relative)
        actual = digest_file(path)
        require(actual == expected, "protocol hash mismatch: " + relative)
        entries[relative] = actual
    require(REQUIRED_PROTOCOL_PATHS <= entries.keys(),
            "protocol omits a required source or input")
    return entries


def read_model(path, order, expected_sha256):
    raw = path.read_bytes()
    require(digest_bytes(raw) == expected_sha256, "language model hash mismatch")
    require(raw[:8] == b"R59LM" + bytes((order, 0, 0)), "bad model header")
    expected_values = sum(26 ** k for k in range(1, order + 1))
    require(len(raw) == 8 + 4 * expected_values, "bad model length")
    values = np.frombuffer(raw, dtype="<f4", offset=8)
    require(bool(np.isfinite(values).all()), "nonfinite language model value")
    tables, offset = [], 0
    for k in range(1, order + 1):
        size = 26 ** k
        tables.append(values[offset:offset + size])
        offset += size
    return raw, tables


def score_batch(texts, tables):
    """Sum float32 log10 entries using float64 addition, with short prefixes.

    At position i, use order min(i+1,K), oldest letter most significant in
    the base-26 index. There is no end symbol, word score, or length penalty.
    """
    x = np.asarray(texts, dtype=np.int64)
    require(x.ndim == 2 and x.shape[1] > 0, "score expects nonempty text matrix")
    require(bool(((x >= 0) & (x < 26)).all()), "non-letter in score input")
    kmax = len(tables)
    out = np.zeros(x.shape[0], dtype=np.float64)
    prefix = np.zeros(x.shape[0], dtype=np.int64)
    for i in range(min(kmax - 1, x.shape[1])):
        prefix = prefix * 26 + x[:, i]
        out += tables[i][prefix]
    if x.shape[1] >= kmax:
        count = x.shape[1] - kmax + 1
        codes = np.zeros((x.shape[0], count), dtype=np.int64)
        for j in range(kmax):
            codes = codes * 26 + x[:, j:j + count]
        out += tables[kmax - 1][codes].sum(axis=1, dtype=np.float64)
    require(bool(np.isfinite(out).all()), "nonfinite score")
    return out


def letter_array(text):
    require(isinstance(text, str) and len(text) == 97 and set(text) <= set(AZ),
            "expected a 97-letter uppercase synthetic message")
    return np.array([ord(c) - 65 for c in text], dtype=np.int64)


def inverse(permutation):
    values = np.asarray(permutation, dtype=np.int64)
    require(values.shape == (26,) and sorted(values.tolist()) == list(range(26)),
            "invalid wiring")
    return np.argsort(values)


def schedule(label):
    ein, eout, period, phase, turnover, d1, d2 = label
    require(ein in ALPHABETS and eout in ALPHABETS, "invalid contact alphabet")
    require(all(type(v) is int for v in label[2:]), "noninteger structural label")
    require(1 <= period <= 4 and 0 <= phase < period and 0 <= turnover < 26
            and d1 in (-1, 1) and d2 in (-1, 1), "out-of-domain structural label")
    tick = (np.arange(97, dtype=np.int64) + phase) // period
    fast = d1 * tick
    slow = d2 * ((tick + turnover) // 26)
    turn_count = int(np.count_nonzero(np.diff(slow)))
    cell = f"n{period}t{turn_count}"
    require(cell in CELLS, "unexpected turnover cell")
    return fast, slow, cell, turn_count


def load_panel(root):
    with (root / "r94/inputs/PANEL.tsv").open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        require(reader.fieldnames == ["id", "label", "ciphertext"],
                "unexpected input columns")
        rows = list(reader)
    truth = json.loads((root / "r94/inputs/PANEL_TRUTH.json").read_text(encoding="utf-8"))
    ids = [f"D_{i:03d}" for i in range(48)]
    require(len(rows) == 48 and [r["id"] for r in rows] == ids, "panel IDs differ")
    require(isinstance(truth, dict) and set(truth) == set(ids), "truth IDs differ")
    cells = {cell: 0 for cell in CELLS}
    for row in rows:
        parts = row["label"].split(",")
        require(len(parts) == 7, "invalid label width")
        label = parts[:2] + [int(v) for v in parts[2:]]
        t = truth[row["id"]]
        require(set(t) == {"cell", "label", "W1", "W2", "pt", "ct", "turnovers"},
                "unexpected truth fields")
        require(t["label"] == label and t["ct"] == row["ciphertext"],
                "truth and input disagree")
        letter_array(t["pt"])
        letter_array(t["ct"])
        inverse(t["W1"])
        inverse(t["W2"])
        fast, slow, cell, turns = schedule(label)
        require(cell == t["cell"] and turns == t["turnovers"], "turnover metadata differs")
        row.update(label=label, cell=cell, fast=fast, slow=slow, truth=t)
        cells[cell] += 1
    require(all(v == 6 for v in cells.values()), "expected six cases per turnover cell")
    return rows


def decode_batch(row, inverse1, inverse2):
    """Vectorized inverse applied to complete, legal permutation pairs."""
    alphabet_in = np.array([ord(c) - 65 for c in ALPHABETS[row["label"][0]]])
    alphabet_out = ALPHABETS[row["label"][1]]
    cipher = np.array([alphabet_out.index(c) for c in row["ciphertext"]])
    fast, slow = row["fast"], row["slow"]
    n = len(inverse1)
    selected = np.arange(n)[:, None]
    middle = (inverse2[:, (cipher + slow) % 26] - slow) % 26
    contacts = (inverse1[selected, (middle + fast) % 26] - fast) % 26
    return alphabet_in[contacts]


def forward_check_batch(row, plaintexts, inverse1, inverse2):
    """Check complete forward encryption for every generated plaintext/key."""
    alphabet_in = ALPHABETS[row["label"][0]]
    alphabet_out = np.array([ord(c) - 65 for c in ALPHABETS[row["label"][1]]])
    input_index = np.empty(26, dtype=np.int64)
    for i, ch in enumerate(alphabet_in):
        input_index[ord(ch) - 65] = i
    w1 = np.argsort(inverse1, axis=1)
    w2 = np.argsort(inverse2, axis=1)
    selected = np.arange(len(plaintexts))[:, None]
    fast, slow = row["fast"], row["slow"]
    middle = (w1[selected, (input_index[plaintexts] + fast) % 26] - fast) % 26
    encoded = alphabet_out[(w2[selected, (middle + slow) % 26] - slow) % 26]
    require(bool((encoded == letter_array(row["ciphertext"])).all()),
            "generated neighbor failed forward encryption")


def neighbors(row):
    """U, then V; lexicographic x<y, exactly the R94 neighborhood labels."""
    u, v = inverse(row["truth"]["W1"]), inverse(row["truth"]["W2"])
    metadata, us, vs = [], [], []
    for block, name in enumerate(("U", "V")):
        for x in range(26):
            for y in range(x + 1, 26):
                a, b = u.copy(), v.copy()
                changed = a if block == 0 else b
                changed[x], changed[y] = changed[y], changed[x]
                metadata.append((name, x, y))
                us.append(a)
                vs.append(b)
    require(len(metadata) == 650 and len(set(metadata)) == 650,
            "wrong neighborhood size")
    inverse1, inverse2 = np.asarray(us), np.asarray(vs)
    decoded = decode_batch(row, inverse1, inverse2)
    forward_check_batch(row, decoded, inverse1, inverse2)
    actual_truth = decode_batch(row, u[None, :], v[None, :])[0]
    require(bool((actual_truth == letter_array(row["truth"]["pt"])).all()),
            "true key does not recover synthetic truth")
    forward_check_batch(row, actual_truth[None, :], u[None, :], v[None, :])
    return metadata, inverse1, inverse2, decoded


def case_metric(records, score, truth_score):
    result = {"categories": {}}
    for category in CATEGORIES:
        selected = [r for r in records if (
            "exact_text" if r["matches"] == 97 else
            "near_wrong" if r["matches"] >= 95 else "below95") == category]
        deltas = [r[score + "_sum_log10"] - truth_score for r in selected]
        wins = sum(d > EPSILON for d in deltas)
        ties = sum(abs(d) <= EPSILON for d in deltas)
        losses = sum(d < -EPSILON for d in deltas)
        require(wins + ties + losses == len(selected), "unclassified score relation")
        result["categories"][category] = {
            "labels": len(selected), "distinct_plaintexts": len({r["text"] for r in selected}),
            "wins": wins, "ties": ties, "losses": losses,
        }
    cats = result["categories"]
    require(cats["exact_text"]["wins"] == cats["exact_text"]["losses"] == 0,
            "identical text has a different score")
    result.update(
        any_wrong_win=bool(cats["near_wrong"]["wins"] + cats["below95"]["wins"]),
        any_below95_win=bool(cats["below95"]["wins"]),
        any_wrong_tie=bool(cats["near_wrong"]["ties"] + cats["below95"]["ties"]),
        any_below95_tie=bool(cats["below95"]["ties"]),
    )
    return result


def best_witness(records, score, inverse1, inverse2, predicate):
    candidates = [i for i, record in enumerate(records) if predicate(record["matches"])]
    if not candidates:
        return None
    # Python max returns the first label in an exact raw-score tie.
    i = max(candidates, key=lambda j: records[j][score + "_sum_log10"])
    return {
        **records[i],
        "W1": np.argsort(inverse1[i]).tolist(),
        "W2": np.argsort(inverse2[i]).tolist(),
    }


def aggregate(cases, score):
    return {
        "wrong_win_cases": sum(c["metrics"][score]["any_wrong_win"] for c in cases),
        "below95_win_cases": sum(c["metrics"][score]["any_below95_win"] for c in cases),
        "wrong_tie_cases": sum(c["metrics"][score]["any_wrong_tie"] for c in cases),
        "below95_tie_cases": sum(c["metrics"][score]["any_below95_tie"] for c in cases),
        "categories": {
            category: {
                field: sum(c["metrics"][score]["categories"][category][field] for c in cases)
                for field in METRIC_FIELDS
            } for category in CATEGORIES
        },
    }


def run(args, root, out, events):
    protocol = args.protocol.resolve()
    verified = verify_protocol(root, protocol)
    events.add("protocol_verified", files=len(verified))
    baseline_path = root / "r91/R59_LOWER4_FROM_K5.bin"
    model5_path = args.model5.resolve()
    training_path = args.training_text.resolve()
    raw4, tables4 = read_model(baseline_path, 4, MODEL4_SHA256)
    raw5, tables5 = read_model(model5_path, 5, MODEL5_SHA256)
    require(raw4[8:] == raw5[8:len(raw4)], "candidate lower tables differ from baseline")
    training_raw = training_path.read_bytes()
    require(digest_bytes(training_raw) == TRAINING_SHA256, "training text hash mismatch")
    training = re.sub(rb"[^A-Z]", b"", training_raw)
    require(len(training) > 0, "empty normalized training text")
    events.add("models_and_training_verified", lower_tables_byte_equal=True,
               baseline_bytes=len(raw4), candidate_bytes=len(raw5),
               training_bytes=len(training_raw), normalized_training_letters=len(training))
    rows = load_panel(root)
    events.add("spent_truth_loaded", cases=len(rows), truth_available_from_start=True)
    cases = []
    record_count = 0
    (out / "neighbors").mkdir(exist_ok=False)
    with (out / "CASES.jsonl").open("x", encoding="utf-8") as cf:
        for row in rows:
            metadata, inverse1, inverse2, texts = neighbors(row)
            known = letter_array(row["truth"]["pt"])
            scored = np.vstack((known[None, :], texts))
            values = {"lm4": score_batch(scored, tables4), "lm5": score_batch(scored, tables5)}
            agreements = (texts == known).sum(axis=1)
            records = []
            for j, (name, x, y) in enumerate(metadata):
                record = {
                    "id": row["id"], "inverse_wiring": name, "swap": [x, y],
                    "text": "".join(chr(65 + int(c)) for c in texts[j]),
                    "matches": int(agreements[j]),
                    "same_plaintext_on97": bool(agreements[j] == 97),
                    "lm4_sum_log10": float(values["lm4"][j + 1]),
                    "lm5_sum_log10": float(values["lm5"][j + 1]),
                    "lm4_delta": float(values["lm4"][j + 1] - values["lm4"][0]),
                    "lm5_delta": float(values["lm5"][j + 1] - values["lm5"][0]),
                    "forward_witness": True,
                }
                records.append(record)
            with (out / "neighbors" / (row["id"] + ".jsonl")).open("x", encoding="utf-8") as nf:
                for record in records:
                    line_json(nf, record, MAX_SHARD_BYTES)
            offset = training.find(row["truth"]["pt"].encode("ascii"))
            case = {
                "id": row["id"], "cell": row["cell"], "label": row["label"],
                "ciphertext": row["ciphertext"], "neighbors_evaluated": len(records),
                "distinct_plaintexts": len({r["text"] for r in records}),
                "truth": {
                    "text": row["truth"]["pt"], "W1": row["truth"]["W1"],
                    "W2": row["truth"]["W2"],
                    "lm4_sum_log10": float(values["lm4"][0]),
                    "lm5_sum_log10": float(values["lm5"][0]),
                },
                "training_overlap": {
                    "present": offset >= 0,
                    "first_normalized_offset": offset if offset >= 0 else None,
                },
                "metrics": {}, "witnesses": {}, "margins": {},
            }
            for score in SCORES:
                base = float(values[score][0])
                case["metrics"][score] = case_metric(records, score, base)
                wrong = best_witness(records, score, inverse1, inverse2, lambda m: m < 97)
                low = best_witness(records, score, inverse1, inverse2, lambda m: m < 95)
                case["witnesses"][score] = {"best_wrong": wrong, "best_below95": low}
                case["margins"][score] = {
                    "best_wrong_delta": None if wrong is None else wrong[score + "_sum_log10"] - base,
                    "best_below95_delta": None if low is None else low[score + "_sum_log10"] - base,
                }
            line_json(cf, case)
            cf.flush()
            cases.append(case)
            record_count += len(records)
            events.add("case_saved", id=row["id"], neighbor_records=len(records))
            check_retention(out)
    require(record_count == 31200 and len(cases) == 48, "incomplete challenge coverage")
    metrics = {score: aggregate(cases, score) for score in SCORES}
    below95_cases = metrics["lm5"]["below95_win_cases"]
    summary = {
        "status": "COMPLETE", "mode": "SPENT_SYNTHETIC_DEVELOPMENT",
        "cases": len(cases), "neighbors_evaluated": record_count,
        "score_evaluations_per_score": len(cases) + record_count,
        "score_order": list(SCORES), "epsilon": EPSILON,
        "primary_endpoint": "cases with any below95 neighbor above truth + epsilon",
        "go_max_cases": GO_MAX_CASES,
        "candidate_verdict": ("GO_FOR_CONDITIONAL_DEVELOPMENT"
                              if below95_cases <= GO_MAX_CASES else "SCORE_NO_GO"),
        "decision_pending_separate_verification": True,
        "metrics": metrics,
        "by_cell": {
            cell: {
                "cases": sum(c["cell"] == cell for c in cases),
                "metrics": {score: aggregate([c for c in cases if c["cell"] == cell], score)
                            for score in SCORES},
            } for cell in CELLS
        },
        "training_overlap": {
            "cases_present": sum(c["training_overlap"]["present"] for c in cases),
            "normalized_training_letters": len(training), "rows_discarded": 0,
        },
        "interpretation_limits": {
            "blind_recovery_test": False, "fresh_holdout": False,
            "global_objective_certificate": False, "cipher_family_excluded": False,
            "a_pass_allows_conditional_development_only": True,
            "independent_model_review": "NONE",
            "same_plaintext_is_not_full_operator_equivalence": True,
            "aggregate_distinct_plaintexts_is_sum_of_per_case_counts": True,
        },
    }
    save_json(out / "SUMMARY.json", summary)
    events.add("challenge_complete", cases=len(cases), neighbor_records=record_count)
    events.close()
    names = (*[f"neighbors/D_{i:03d}.jsonl" for i in range(48)],
             "CASES.jsonl", "SUMMARY.json", "EVENTS.jsonl")
    receipt = {
        "status": "COMPLETE", "protocol_sha256": digest_file(protocol),
        "protocol_files_sha256": verified,
        "source_sha256": digest_file(Path(__file__).resolve()),
        "input_sha256": {
            "r94/inputs/PANEL.tsv": verified["r94/inputs/PANEL.tsv"],
            "r94/inputs/PANEL_TRUTH.json": verified["r94/inputs/PANEL_TRUTH.json"],
        },
        "models": {
            "lm4": {"sha256": MODEL4_SHA256, "bytes": len(raw4), "order": 4},
            "lm5": {"sha256": MODEL5_SHA256, "bytes": len(raw5), "order": 5,
                    "definition": "K=5 builder top order uses raw counts; not the old K=6 order5 table"},
            "lower_tables_byte_equal": True,
        },
        "training": {"sha256": TRAINING_SHA256, "bytes": len(training_raw),
                     "normalized_letters": len(training), "filter": "retain ASCII A-Z only",
                     "overlap_is_diagnostic_only": True},
        "runtime": {"python": sys.version, "numpy": np.__version__,
                    "argv": sys.argv, "threads_requested": 1},
        "output_sha256": {name: digest_file(out / name) for name in names},
        "output_manifest_relative_to": "repository root",
        "retention_byte_caps": {"neighbor_shard": MAX_SHARD_BYTES,
                                "json_or_cases_file": MAX_JSON_BYTES,
                                "event_file": MAX_EVENT_BYTES,
                                "all_controlled_outputs": MAX_OUTPUT_BYTES},
        "truth_available_from_start": True, "random_restarts": 0,
        "optimization_calls": 0, "retries": 0,
    }
    save_json(out / "RECEIPT.json", receipt)
    manifest = "".join(
        f"{digest_file(out / name)}  {(out / name).relative_to(root).as_posix()}\n"
        for name in (*names, "RECEIPT.json")
    )
    require(len(manifest.encode("utf-8")) <= 256 * 1024, "output manifest exceeds byte cap")
    with (out / "OUTPUTS.sha256").open("x", encoding="utf-8") as stream:
        stream.write(manifest)
    check_retention(out)
    # Keep scientific results in the files so the publication can precede interpretation.
    print(json.dumps({"status": "COMPLETE", "cases_written": 48,
                      "neighbor_records_written": 31200, "output": str(out)}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--model5", type=Path, required=True)
    parser.add_argument("--training-text", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root, out = args.repo.resolve(), args.out.resolve()
    require(root == HERE.parent, "repository must be the source checkout")
    require(out != HERE and out.is_relative_to(HERE), "output must be a fresh r95 subdirectory")
    # Refusal on an existing directory occurs before opening any file in it.
    out.mkdir(parents=True, exist_ok=False)
    events = None
    try:
        events = Events(out / "EVENTS.jsonl")
        events.add("attempt_started", mode="SPENT_SYNTHETIC_DEVELOPMENT")
        run(args, root, out, events)
    except Exception as exc:
        if events is not None and not events.stream.closed:
            events.add("attempt_failed", error_type=type(exc).__name__, error=str(exc))
            events.close()
        save_json(out / "FAILURE.json", {
            "status": "INCOMPLETE", "error_type": type(exc).__name__, "error": str(exc),
            "no_scientific_conclusion": True,
        })
        print(json.dumps({"status": "INCOMPLETE", "output": str(out),
                          "error_type": type(exc).__name__}), file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
