#!/usr/bin/env python3
"""Post-freeze artifact review; no experiment-module imports or optimizer calls."""
import argparse
import array
from collections import Counter
import csv
import hashlib
import io
import json
import math
from pathlib import Path, PurePosixPath
import random
import re
import statistics
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALPH = {k: "".join(dict.fromkeys(w + AZ)) for k, w in
        (("AZ", ""), ("KRY", "KRYPTOS"), ("PAL", "PALIMPSEST"), ("ABS", "ABSCISSA"))}
CELLS = ("n1t3", "n1t4", "n2t1", "n2t2", "n3t1", "n3t2", "n4t0", "n4t1")
FREQ = (8.2, 1.5, 2.8, 4.3, 12.7, 2.2, 2.0, 6.1, 7.0, .15, .77, 4.0, 2.4,
        6.7, 7.5, 1.9, .095, 6.0, 6.3, 9.1, 2.8, .98, 2.4, .15, 2.0, .074)
LOGF = [math.log10(f / sum(FREQ)) for f in FREQ]
EPS = 1e-9
TOL = 1e-7
PREREG = "567f418961cc18847207008468679115074f4c93"
MODEL_SHA = "85b4adf264619a12c9ed646c7d4fc952ef76025db67dd96f2b668ea1e1cf1f41"
CIPHER_SHA = "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
CLUE_SHA = "63121ceaddaa577427dec10d169975a96b6c21c9e4f344ccc7d4c4064650425b"
CACHE = {}
HASHED = {}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def raw(name):
    if name not in CACHE:
        path = PurePosixPath(name)
        assert not path.is_absolute() and ".." not in path.parts, name
        CACHE[name] = (ROOT / name).read_bytes()
    return CACHE[name]


def obj(name):
    return json.loads(raw(name))


def lines(name):
    return [json.loads(line) for line in raw(name).decode().splitlines() if line.strip()]


def git(*args, check=True):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=check)


def committed(commit, name):
    assert re.fullmatch(r"[0-9a-f]{40}", commit)
    data = git("show", f"{commit}:{name}").stdout
    assert data == raw(name), f"committed/local difference: {commit}:{name}"
    return data


def before(earlier, later):
    assert earlier != later
    git("merge-base", "--is-ancestor", earlier, later)


def manifest(commit, name, required=()):
    data = committed(commit, name)
    covered = {}
    for line in data.decode().splitlines():
        expected, path = line.split(maxsplit=1)
        assert re.fullmatch(r"[0-9a-f]{64}", expected)
        assert path not in covered
        assert digest(committed(commit, path)) == expected, path
        covered[path] = expected
        HASHED[path] = expected
    assert set(required) <= set(covered), (name, set(required) - set(covered))
    HASHED[name] = digest(data)
    return covered


def resource_log(name, wall, cpu, memory):
    r = obj(name)
    assert r["status"] == "COMPLETE" and r["exit_code"] == 0 and r["reason"] is None
    for key, cap in (("wall_seconds", wall), ("cpu_seconds", cpu), ("max_rss_mb", memory)):
        assert 0 <= r[key] <= cap, (name, key, r[key], cap)
    assert r["budget"] == {"max_wall_seconds": wall, "max_ram_mb": memory, "max_cpu_seconds": cpu}
    assert r["max_rss_mb"] == r["aggregate_peak_rss_mb"]
    assert r["wrapper"] == "audit/run_bounded_agg.py" and "aggregate" in r["semantics"]
    return {k: r[k] for k in ("status", "wall_seconds", "cpu_seconds", "max_rss_mb", "budget")}


def close(a, b, label="numeric comparison"):
    assert math.isfinite(a) and math.isfinite(b) and abs(a - b) < TOL, (label, a, b)


def integer(value, lower=0, upper=None):
    assert type(value) is int and value >= lower and (upper is None or value <= upper), value


def inverse(w):
    assert len(w) == 26 and sorted(w) == list(range(26))
    inv = [None] * 26
    for i, v in enumerate(w):
        inv[v] = i
    return inv


def clocks(label):
    ei, eo, n, phase, h, d1, d2 = label
    assert ei in ALPH and eo in ALPH and n in (1, 2, 3, 4)
    assert 0 <= phase < n and 0 <= h < 26 and d1 in (-1, 1) and d2 in (-1, 1)
    fast = slow = 0
    until_fast, until_slow = n - phase, 26 - h
    answer = []
    for _ in range(97):
        answer.append((fast % 26, slow % 26))
        until_fast -= 1
        if until_fast == 0:
            fast += d1
            until_fast = n
            until_slow -= 1
            if until_slow == 0:
                slow += d2
                until_slow = 26
    return answer


def cipher(text, W1, W2, label, decrypt=False):
    assert len(text) == 97 and all(c in AZ for c in text)
    I1, I2 = inverse(W1), inverse(W2)
    ai, ao = ALPH[label[0]], ALPH[label[1]]
    output = []
    for letter, (fast, slow) in zip(text, clocks(label)):
        if decrypt:
            contact = I2[(ao.index(letter) + slow) % 26]
            contact = I1[(contact - slow + fast) % 26]
            output.append(ai[(contact - fast) % 26])
        else:
            contact = W1[(ai.index(letter) + fast) % 26]
            contact = W2[(contact - fast + slow) % 26]
            output.append(ao[(contact - slow) % 26])
    return "".join(output)


def load_model():
    data = raw("r91/R59_LOWER4_FROM_K5.bin")
    assert digest(data) == MODEL_SHA and data[:8] == b"R59LM\x04\x00\x00"
    values = array.array("f")
    assert values.itemsize == 4
    values.frombytes(data[8:])
    if sys.byteorder != "little":
        values.byteswap()
    assert len(values) == sum(26 ** k for k in range(1, 5))
    tables, offset = [], 0
    for k in range(1, 5):
        tables.append(values[offset:offset + 26 ** k])
        offset += 26 ** k
    return tables


def lm4(text, tables):
    x = [ord(c) - 65 for c in text]
    score = 0.0
    for i in range(len(x)):
        k = min(4, i + 1)
        index = 0
        for j in range(i - k + 1, i + 1):
            index = index * 26 + x[j]
        score += tables[k - 1][index]
    return score


def unigram(text):
    return sum(LOGF[ord(c) - 65] for c in text)


def matches(text, truth):
    assert len(text) == len(truth) == 97
    return sum(a == b for a, b in zip(text, truth))


def witness(candidate, panel, tables):
    assert candidate["forward_witness"] is True
    text, W1, W2 = candidate["text"], candidate["W1"], candidate["W2"]
    assert cipher(text, W1, W2, panel["label"]) == panel["ciphertext"]
    assert cipher(panel["ciphertext"], W1, W2, panel["label"], True) == text
    close(unigram(text), candidate["unigram_sum_log10"], "unigram witness")
    close(lm4(text, tables), candidate["lm4_sum_log10"], "scalar order4 witness")


def equivalence(candidate, truth, label):
    W1, W2, T1, T2 = candidate["W1"], candidate["W2"], truth["W1"], truth["W2"]
    gauge = any(all(W1[x] == (T1[x] + shift) % 26 for x in range(26)) and
                all(W2[(z + shift) % 26] == T2[z] for z in range(26)) for shift in range(26))
    operator = True
    for fast, slow in clocks(label):
        for p in range(26):
            c = (W2[(W1[(p + fast) % 26] - fast + slow) % 26] - slow) % 26
            t = (T2[(T1[(p + fast) % 26] - fast + slow) % 26] - slow) % 26
            if c != t:
                operator = False
                break
        if not operator:
            break
    return {"gauge_equivalent": gauge, "operator_equivalent_97": operator,
            "raw_wirings_equal": W1 == T1 and W2 == T2}


def recovery_summary(rows):
    def group(selected):
        return {"cases": len(selected),
                "top1_ge95": sum(r["top1_matches"] >= 95 for r in selected),
                "top1_exact": sum(r["top1_matches"] == 97 for r in selected),
                "any_retained_ge95": sum(r["any_retained_matches"] >= 95 for r in selected),
                "any_final_state_ge95": sum(r["best_final_state_matches"] >= 95 for r in selected),
                "maximum_top1_matches": max(r["top1_matches"] for r in selected),
                "maximum_final_state_matches": max(r["best_final_state_matches"] for r in selected),
                "median_top1_matches": float(statistics.median(r["top1_matches"] for r in selected))}
    return {"total": group(rows), "by_cell": {c: group([r for r in rows if r["cell"] == c]) for c in CELLS},
            "rows": rows}


def check_lm_trace(candidate, maximum_blocks, initial):
    t = candidate["trace"]
    trace = t["lm4_trace"]
    close(trace[0], initial, "initial order4 trace")
    close(trace[-1], candidate["lm4_sum_log10"], "final order4 trace")
    assert all(b > a + EPS for a, b in zip(trace, trace[1:]))
    for k in ("assignment_or_cycle", "best_transposition", "none"):
        integer(t[k], upper=maximum_blocks)
    accepted = t["assignment_or_cycle"] + t["best_transposition"]
    blocks = accepted + t["none"]
    assert accepted == len(trace) - 1 and blocks <= maximum_blocks
    fallback = t["best_transposition"] + t["none"]
    integer(t["scored_counterfactual_or_legal_texts"], 1 + 677 * blocks + 325 * fallback,
            1 + 690 * blocks + 325 * fallback)
    return blocks, t["scored_counterfactual_or_legal_texts"]


def check_r94(source, freeze):
    before(source, freeze)
    assert git("cat-file", "-e", f"{source}:r94/development/RESULT.json", check=False).returncode != 0
    manifest(source, "r94/PROTOCOL.sha256")
    complete = manifest(freeze, "r94/audit/RUN_FROZEN.sha256",
                        ("r94/development/OUTPUTS.sha256", "r94/RESOURCE_LOG.json", "r94/PROTOCOL.sha256"))
    outputs = manifest(freeze, "r94/development/OUTPUTS.sha256")
    assert set(outputs) <= set(complete)
    actual = {p.relative_to(ROOT).as_posix() for p in (ROOT / "r94/development").iterdir() if p.is_file()}
    assert actual == set(outputs) | {"r94/development/OUTPUTS.sha256"}
    assert "r94/development/INCOMPLETE.json" not in actual
    resource = resource_log("r94/RESOURCE_LOG.json", 1800, 1800, 2048)
    report = obj("r94/development/RESULT.json")
    assert report["status"] == "COMPLETE_DIAGNOSTIC"
    for name in ("k4_authorized", "formal_gate_pass", "new_holdout", "original_lm5_or_lm6_replayed"):
        assert report[name] is False
    assert report["negative_control_count"] == 0
    assert report["input_receipt"] == obj("r94/SOURCE_RECEIPT.json")
    phases = report["phases"]
    caps = {"mathematical_checks": 60, "A": 300, "B": 900, "diagnostics_and_archive_replay": 300}
    assert set(phases) == set(caps)
    for name, cap in caps.items():
        p = phases[name]
        assert p["status"] == "COMPLETE" and p["cap_wall_and_cpu_seconds"] == cap
        assert 0 <= p["wall_seconds"] <= cap and 0 <= p["cpu_seconds"] <= cap
    assert sum(p["wall_seconds"] for p in phases.values()) <= resource["wall_seconds"] + .1
    assert sum(p["cpu_seconds"] for p in phases.values()) <= resource["cpu_seconds"] + .1
    tests = obj("r94/development/TESTS.json")
    assert tests == {"status": "PASS", "conditional_assignment_exhaustive": 24,
                     "cycle_parameterization": 54, "reference_roundtrip": 24,
                     "lm4_scalar_batch": 24, "replacement_objectives": 144}
    unknown_hashes = obj("r94/development/UNKNOWN_OUTPUTS_BEFORE_TRUTH.json")
    assert unknown_hashes == {v: digest(raw(f"r94/development/VERSION_{v}.jsonl")) for v in ("A", "B")}
    assert report["unknown_outputs_before_truth"] == unknown_hashes
    events = lines("r94/development/EVENTS.jsonl")
    for key in ("monotonic_seconds", "process_cpu_seconds"):
        assert all(b[key] >= a[key] for a, b in zip(events, events[1:]))
    opened = [i for i, e in enumerate(events) if e["event"] == "opening_public_spent_truth"]
    assert len(opened) == 1 and events[opened[0]]["unknown_output_sha256"] == unknown_hashes
    closures = [e for e in events[:opened[0]] if e["event"] == "candidate_file_closed"]
    assert [e["version"] for e in closures] == ["A", "B"]
    assert all(e["rows"] == 48 and e["sha256"] == unknown_hashes[e["version"]] for e in closures)
    trigger = [e for e in events if e["event"] == "version_B_trigger"]
    assert len(trigger) == 1 and trigger[0]["decision"] == "RUN" and trigger[0]["A_rows"] == 48
    assert trigger[0]["selftests"] == "PASS" and trigger[0]["truth_used"] is False
    assert trigger[0]["score_or_recovery_cutoff"] is False
    panel = list(csv.DictReader(io.StringIO(raw("r94/inputs/PANEL.tsv").decode()), delimiter="\t"))
    for row in panel:
        fields = row["label"].split(",")
        row["label"] = fields[:2] + list(map(int, fields[2:]))
        ts = clocks(row["label"])
        turnovers = sum(a[1] != b[1] for a, b in zip(ts, ts[1:]))
        row["cell"] = f"n{row['label'][2]}t{turnovers}"
    ids = [f"D_{i:03d}" for i in range(48)]
    assert [r["id"] for r in panel] == ids
    assert Counter(r["cell"] for r in panel) == {c: 6 for c in CELLS}
    by_id = {r["id"]: r for r in panel}
    truth = obj("r94/inputs/PANEL_TRUTH.json")
    assert set(truth) == set(ids)
    for rid, t in truth.items():
        row = by_id[rid]
        assert t["ct"] == row["ciphertext"] and t["label"] == row["label"] and t["cell"] == row["cell"]
        assert cipher(t["pt"], t["W1"], t["W2"], t["label"]) == t["ct"]
    tables = load_model()
    saved, reconstructed = {}, {}
    new_witnesses = assignments = blocks = score_calls = 0
    for version in ("A", "B"):
        batch = lines(f"r94/development/VERSION_{version}.jsonl")
        assert [r["id"] for r in batch] == ids
        saved[version] = {r["id"]: r for r in batch}
        recovery_rows = []
        for result in batch:
            rid = result["id"]
            row, t = by_id[rid], truth[rid]
            assert result["version"] == version and result["label"] == row["label"] and result["cell"] == row["cell"]
            states = result["final_states"]
            assert len(states) == 8 and [c["start"] for c in states] == list(range(8))
            seed_body = f"940101|{rid}|{row['ciphertext']}|{','.join(map(str, row['label']))}"
            rng = random.Random(int(hashlib.sha256(seed_body.encode()).hexdigest()[:16], 16))
            for j, candidate in enumerate(states):
                witness(candidate, row, tables)
                new_witnesses += 1
                if version == "A":
                    U, V = list(range(26)), list(range(26))
                    rng.shuffle(U); rng.shuffle(V)
                    start_text = cipher(row["ciphertext"], inverse(U), inverse(V), row["label"], True)
                    trace = candidate["trace"]
                    values = trace["unigram_trace"]
                    close(values[0], unigram(start_text), "registered initial state")
                    close(values[-1], candidate["unigram_sum_log10"])
                    assert all(b > a + EPS for a, b in zip(values, values[1:]))
                    integer(trace["assignment_calls"], 2, 32)
                    assert trace["accepted_updates"] == len(values) - 1 <= trace["assignment_calls"]
                    assignments += trace["assignment_calls"]
                else:
                    start_score = saved["A"][rid]["final_states"][j]["lm4_sum_log10"]
                    assert candidate["lm4_sum_log10"] >= start_score - EPS
                    b, s = check_lm_trace(candidate, 48, start_score)
                    blocks += b; score_calls += s
            ranked = sorted(states, key=lambda c: (-c["lm4_sum_log10"], -c["unigram_sum_log10"],
                                                   c["text"], c["W1"], c["W2"]))
            keep, seen = [], set()
            for candidate in ranked:
                if candidate["text"] not in seen:
                    keep.append(candidate); seen.add(candidate["text"])
            assert result["retained"] == keep[:8]
            recovery_rows.append({"id": rid, "cell": row["cell"],
                "top1_matches": matches(keep[0]["text"], t["pt"]),
                "any_retained_matches": max(matches(c["text"], t["pt"]) for c in keep),
                "best_final_state_matches": max(matches(c["text"], t["pt"]) for c in states),
                "retained_count": len(keep), "top1_equivalence": equivalence(keep[0], t, row["label"])})
        reconstructed[version] = recovery_summary(recovery_rows)
    assert reconstructed == obj("r94/development/RECOVERY.json")
    assert report["unknown_two_wiring"] == {v: reconstructed[v]["total"] for v in ("A", "B")}
    assert assignments <= 12288 and blocks <= 18432
    outcome = "SOLVER_NO_POWER" if all(reconstructed[v]["total"]["any_final_state_ge95"] == 0 for v in ("A", "B")) else "DEVELOPMENT_RECOVERY_OBSERVED"
    assert report["bounded_solver_outcome"] == outcome
    diag = check_diagnostics(by_id, truth, tables)
    new_witnesses += diag["saved_states_verified"]
    assert new_witnesses <= 1008
    archived = check_archives(truth)
    return {"status": "PASS", "bounded_solver_outcome": outcome, "unknown_two_wiring": report["unknown_two_wiring"],
            "by_cell": {v: reconstructed[v]["by_cell"] for v in ("A", "B")},
            "new_saved_states_verified": new_witnesses, "unigram_assignment_calls": assignments,
            "unknown_B_block_updates": blocks, "unknown_B_reported_score_calls": score_calls,
            "diagnostics": diag, "archived": archived, "resource": resource,
            "truth_order": "Both unknown-output hashes match recorded closure events before the truth-opening event; ordinary filesystem convention, not OS isolation.",
            "optimizers_invoked": False, "independent_model_review": "NONE"}


def check_diagnostics(panel, truth, tables):
    rows = lines("r94/development/CONDITIONAL_DIAGNOSTICS.jsonl")
    assert [r["id"] for r in rows] == list(panel)
    conditional = {k: {v: [] for v in ("A", "B")} for k in ("U", "V")}
    neighbors = wrong_cases = witnesses = diag_blocks = diag_scores = 0
    for item in rows:
        rid = item["id"]
        row, t = panel[rid], truth[rid]
        assert item["cell"] == row["cell"]
        U, V = inverse(t["W1"]), inverse(t["W2"])
        truth_score = lm4(t["pt"], tables)
        assert [c["fixed_true_inverse_wiring"] for c in item["conditions"]] == ["U", "V"]
        for condition in item["conditions"]:
            fixed = condition["fixed_true_inverse_wiring"]
            key = "W1" if fixed == "U" else "W2"
            for version in ("A", "B"):
                c = condition[version]
                witness(c, row, tables); witnesses += 1
                assert c[key] == t[key]
                assert c["matches"] == matches(c["text"], t["pt"])
                assert c["equivalence"] == equivalence(c, t, row["label"])
                close(c["lm4_gap_to_truth"], c["lm4_sum_log10"] - truth_score)
                conditional[fixed][version].append(c)
            assert condition["A"]["trace"]["assignment_calls"] == 1
            b, s = check_lm_trace(condition["B"], 24, condition["A"]["lm4_sum_log10"])
            diag_blocks += b; diag_scores += s
        clock = clocks(row["label"])
        ao = ALPH[row["label"][1]]
        ac = [(ao.index(c) + slow) % 26 for c, (_, slow) in zip(row["ciphertext"], clock)]
        bc = [(V[a] - slow + fast) % 26 for a, (fast, slow) in zip(ac, clock)]
        assert item["observed_U_contacts"] == len(set(bc))
        assert item["observed_V_contacts"] == len(set(ac))
        n = item["true_neighborhood"]
        close(n["true_lm4_sum_log10"], truth_score)
        assert n["neighbors_evaluated"] == 650
        above, maximum = set(), None
        for block in (0, 1):
            for x in range(26):
                for y in range(x + 1, 26):
                    trial = [U.copy(), V.copy()]
                    trial[block][x], trial[block][y] = trial[block][y], trial[block][x]
                    text = cipher(row["ciphertext"], inverse(trial[0]), inverse(trial[1]), row["label"], True)
                    score = lm4(text, tables)
                    neighbors += 1
                    if score > truth_score + EPS:
                        assert text != t["pt"]
                        above.add(text)
                        maximum = score if maximum is None else max(maximum, score)
        assert n["distinct_wrong_plaintexts_above_true"] == len(above)
        if above:
            wrong_cases += 1
            c = n["best_witness"]
            witness(c, row, tables); witnesses += 1
            assert c["text"] in above
            close(c["lm4_sum_log10"], maximum)
            cand_inverse = [inverse(c["W1"]), inverse(c["W2"])]
            differing = [[i for i in range(26) if a[i] != b[i]] for a, b in zip(cand_inverse, (U, V))]
            assert sorted(map(len, differing)) == [0, 2]
        else:
            assert n["best_witness"] is None
    summary = {}
    for fixed, versions in conditional.items():
        summary["true_" + fixed] = {}
        for version, values in versions.items():
            assert len(values) == 48
            summary["true_" + fixed][version] = {
                "cases": len(values), "ge95": sum(c["matches"] >= 95 for c in values),
                "exact": sum(c["matches"] == 97 for c in values),
                "median_matches": float(statistics.median(c["matches"] for c in values)),
                "max_matches": max(c["matches"] for c in values),
                "wrong_text_above_true_lm4": sum(c["matches"] < 97 and c["lm4_gap_to_truth"] > EPS for c in values),
                "true_lm4_above_found": sum(c["lm4_gap_to_truth"] < -EPS for c in values)}
    assert neighbors == 31200 and diag_blocks <= 2304
    summary["true_key_neighborhood"] = {"cases": 48, "neighbors_evaluated": neighbors,
                                          "cases_with_wrong_text_above_true": wrong_cases}
    assert summary == obj("r94/development/CONDITIONAL_SUMMARY.json")
    assert summary == obj("r94/development/RESULT.json")["truth_assisted_diagnostic"]
    return {"summary": summary, "saved_states_verified": witnesses, "scalar_neighbor_rescores": neighbors,
            "conditional_B_block_updates": diag_blocks, "conditional_B_reported_score_calls": diag_scores}


def check_archives(truth):
    expected = obj("r94/development/ARCHIVED_REPLAY.json")
    answer = {}
    ranked_witnesses = 0
    for version, starts in (("v2", 32), ("v3", 8)):
        base = f"audit/backlog/multirotor/solver/dev/{version}/run/"
        raw_rows, ranked = lines(base + "ANNEAL.jsonl"), lines(base + "RESULTS.jsonl")
        assert len(raw_rows) == len(ranked) == 48
        assert len({r["id"] for r in raw_rows}) == len({r["id"] for r in ranked}) == 48
        assert {r["id"] for r in raw_rows} == {r["id"] for r in ranked} == set(truth)
        witnesses = hits = max_raw = top_hits = any_hits = max_top = 0
        for row in raw_rows:
            t = truth[row["id"]]
            assert row["ct"] == t["ct"] and row["label"] == t["label"] and len(row["restarts"]) == starts
            for c in row["restarts"]:
                assert cipher(c["text"], c["W1"], c["W2"], row["label"]) == t["ct"]
                assert cipher(t["ct"], c["W1"], c["W2"], row["label"], True) == c["text"]
                witnesses += 1
                n = matches(c["text"], t["pt"]); hits += n >= 95; max_raw = max(max_raw, n)
        for row in ranked:
            t = truth[row["id"]]
            assert row["label"] == t["label"] and 1 <= len(row["keep"]) <= 8
            assert row["best"] == max(row["keep"], key=lambda c: c["lm_per_letter"])
            for c in row["keep"]:
                assert cipher(c["text"], c["W1"], c["W2"], row["label"]) == t["ct"]
                assert cipher(t["ct"], c["W1"], c["W2"], row["label"], True) == c["text"]
                ranked_witnesses += 1
            n = matches(row["best"]["text"], t["pt"])
            top_hits += n >= 95; max_top = max(max_top, n)
            any_hits += max(matches(c["text"], t["pt"]) for c in row["keep"]) >= 95
        answer[version] = {"saved_final_restart_witnesses": witnesses, "saved_final_restart_ge95": hits,
                           "maximum_saved_final_restart_matches": max_raw, "top1_ge95": top_hits,
                           "any_retained_ge95": any_hits, "maximum_top1_matches": max_top,
                           "raw_sha256": digest(raw(base + "ANNEAL.jsonl")),
                           "ranked_sha256": digest(raw(base + "RESULTS.jsonl")),
                           "original_order5_or_6_scores_recomputed": False}
        assert answer[version] == expected[version]
    versions = expected["resources"]["versions"]
    assert set(versions) == {"v1", "v2", "v3"}
    total_jobs = 0; total_wall = total_cpu = 0.0
    for version, item in versions.items():
        files = sorted((ROOT / "audit/backlog/multirotor/solver/dev" / version).glob("*RESOURCE*.json"))
        assert [x["path"] for x in item["logs"]] == [p.relative_to(ROOT).as_posix() for p in files]
        assert item["jobs"] == len(files)
        total_jobs += len(files)
        for x in item["logs"]:
            assert digest(raw(x["path"])) == x["sha256"] and obj(x["path"]) == x["log"]
        wall = sum(x["log"]["wall_seconds"] for x in item["logs"])
        cpu = sum(x["log"]["cpu_seconds"] for x in item["logs"])
        assert item["wall_seconds"] == round(wall, 3) and item["cpu_seconds"] == round(cpu, 3)
        assert wall <= 1800 and cpu <= 1800
        total_wall += wall; total_cpu += cpu
    assert total_jobs == 17
    assert expected["resources"]["total_wall_seconds"] == round(total_wall, 3)
    assert expected["resources"]["total_cpu_seconds"] == round(total_cpu, 3)
    assert expected["v1"] == {"status": "INCOMPLETE", "saved_candidate_evidence": False, "recovery_rate": None}
    return {"versions": answer, "ranked_witnesses_verified": ranked_witnesses,
            "committed_resource_logs": total_jobs, "wall_seconds_sum": round(total_wall, 3),
            "cpu_seconds_sum": round(total_cpu, 3), "v1_status": "INCOMPLETE",
            "original_lm5_or_lm6_replayed": False}


def check_scope(saved):
    def schedule(n, phase, direction):
        remaining, angle, values = n - phase, 0, []
        for _ in range(97):
            values.append(angle % 26)
            remaining -= 1
            if remaining == 0:
                angle += direction
                remaining = n
        return tuple(values)
    clocks = Counter(schedule(n, phase, direction) for n in range(5, 97)
                     for phase in range(1, n) for direction in (-1, 1))
    zero = {schedule(n, 0, direction) for n in range(1, 97) for direction in (-1, 1)}
    old_phase = {schedule(n, phase, direction) for n in range(2, 5)
                 for phase in range(1, n) for direction in (-1, 1)}
    shared = set(clocks) & zero
    expected = {
        "all_n2_n96_nonzero_phase_labels": 145920, "r92_n2_n4_labels": 192,
        "registered_labels": 16 * sum(clocks.values()), "clock_labels": sum(clocks.values()),
        "distinct_clock_sequences": len(clocks), "distinct_clock_contact_labels": 16 * len(clocks),
        "r87_zero_phase_shared_clocks": len(shared), "r87_zero_phase_shared_clock_contact_labels": 16 * len(shared),
        "raw_labels_equivalent_to_r87_clocks": 16 * sum(clocks[s] for s in shared),
        "remaining_distinct_clock_contact_labels": 16 * (len(clocks) - len(shared)),
        "r92_shared_clocks": len(set(clocks) & old_phase), "largest_clock_multiplicity": max(clocks.values()),
        "clock_multiplicity_histogram": {str(k): v for k, v in Counter(clocks.values()).items()},
        "primary_base_calls_201_inputs": 145728 * 201,
        "logical_exact_and_delete_tests_201_inputs": 145728 * 201 * 25}
    for name, value in expected.items():
        assert saved[name] == value, (name, saved[name], value)
    assert expected["registered_labels"] == 145728 and expected["distinct_clock_sequences"] == 4690
    assert expected["raw_labels_equivalent_to_r87_clocks"] == 36096
    assert expected["remaining_distinct_clock_contact_labels"] == 73536
    return expected


def check_r93(source, gate_commit, freeze):
    before(PREREG, source); before(source, gate_commit); before(gate_commit, freeze)
    source_hashes = manifest(source, "r93/PROTOCOL.sha256")
    manifest(gate_commit, "r93/holdout/GATE_FROZEN.sha256",
             ("r93/holdout/CHECKER_GATE.json", "r93/holdout/VALIDATION_RESOURCE.json", "r93/PROTOCOL.sha256"))
    frozen = manifest(freeze, "r93/k4/FROZEN.sha256", ("r93/k4/INPUTS.tsv", "r93/k4/AGGREGATES.json",
                      "r93/k4/SOURCE_RECEIPT.json", "r93/QA_MANIFEST.json", "r93/TARGET_RESOURCE_LOG.json"))
    gate = obj("r93/holdout/CHECKER_GATE.json")
    assert gate["status"] == "COMPLETE" and gate["gate_verdict"] == "GO"
    assert gate["gate_type"] == "EXACT_CHECKER_CORRECTNESS" and gate["blind_recovery_certified"] is False
    assert gate["synthetic_only"] is True and gate["source_commit"] == source and gate["sources"] == source_hashes
    scope = check_scope(gate["scope"])
    toy = gate["toy_oracle"]
    assert toy["cases"] == 141793
    assert toy["false_exclusions"] == toy["false_feasibilities"] == toy["omission_mask_disagreements"] == 0
    assert toy["strata"] == {str(q): {"max_observations": k, "cases": sum((q*q)**j for j in range(1,k+1))}
                              for q,k in ((2,6),(3,5),(4,4))}
    plants = gate["boundary_plants"]
    assert plants["parameter_plants"] == 8832 and plants["setting_checks"] == 44160
    assert plants["forward_inverse_roundtrips"] == 17664 and plants["false_exclusions"] == 0
    assert plants["by_period"] == {str(n): 96 for n in range(5, 97)}
    for key in ("plaintext_reencrypt_single_position_checks", "wrong_plaintext_dropout_checks",
                "observed_ciphertext_dropout_checks", "outside_observations_exact_checks"):
        assert plants[key] == 8832
    assert [x["registered_label_index"] for x in plants["first_and_last_bulk_catalog_plants"]] == [0, 145727]
    adv = gate["adversarial"]
    assert adv["one_conflict_valid_deletions"] == 2 and adv["disjoint_conflict_valid_deletions"] == 0
    assert adv["lost_update_changed_positions"] > 1 and adv["lost_update_covered_by_drop"] is False
    bench = gate["benchmark"]
    assert bench["inputs"] == 3 and bench["scope_settings_per_input"] == 145728
    close(bench["forecast_target_wall_seconds"], 134 * bench["wall_seconds"] + 10)
    close(bench["forecast_target_cpu_seconds"], 134 * bench["cpu_seconds"] + 10)
    assert bench["forecast_target_wall_seconds"] < 1440 and bench["forecast_target_cpu_seconds"] < 960
    gate_resource = resource_log("r93/holdout/VALIDATION_RESOURCE.json", 180, 120, 512)
    resource = resource_log("r93/TARGET_RESOURCE_LOG.json", 1800, 1200, 512)
    qa = obj("r93/QA_MANIFEST.json")
    assert qa["mode"] == "crib_assisted" and qa["stage"] in ("frozen", "validated")
    assert qa["gate_verdict"] == "GO" and qa["gate_type"] == "EXACT_CHECKER_CORRECTNESS"
    assert qa["blind_recovery_certified"] is False and qa["preregistration_commit"] == PREREG
    assert qa["resource_budget"] == {"max_wall_seconds": 1800, "max_cpu_seconds": 1200,
        "max_ram_mb": 512, "max_candidates": 1, "max_retries": 0, "max_decoded_candidates": 0,
        "max_surviving_setting_outputs": 0, "max_aggregate_records": 201}
    canonical = raw("r39/ic_gate/k4_ciphertext.txt")
    assert digest(canonical) == CIPHER_SHA
    target = canonical.decode().strip()
    rng = random.Random(930400)
    inputs, seen, draws = [("K4", target)], {target}, 0
    while len(inputs) < 201 and draws < 10000:
        chars = list(target); rng.shuffle(chars); draws += 1
        ct = "".join(chars)
        if ct not in seen:
            seen.add(ct); inputs.append((f"SHUF_{len(inputs)-1:03d}", ct))
    expected_input = "id\tciphertext\n" + "".join(f"{rid}\t{ct}\n" for rid, ct in inputs)
    assert len(inputs) == 201 and expected_input.encode() == raw("r93/k4/INPUTS.tsv")
    assert all(len(ct) == 97 and Counter(ct) == Counter(target) for _, ct in inputs)
    receipt = obj("r93/k4/SOURCE_RECEIPT.json")
    assert receipt["preregistration_commit"] == PREREG and receipt["source_commit"] == source
    assert receipt["gate_commit"] == gate_commit and receipt["source_sha256"] == source_hashes
    assert receipt["gate_sha256"] == digest(raw("r93/holdout/CHECKER_GATE.json"))
    assert receipt["gate_resource_sha256"] == digest(raw("r93/holdout/VALIDATION_RESOURCE.json"))
    assert receipt["input_sha256"] == digest(expected_input.encode())
    assert receipt["canonical_ciphertext_file_sha256"] == CIPHER_SHA and receipt["observation_source_sha256"] == CLUE_SHA
    assert receipt["shuffle_seed"] == 930400 and receipt["shuffle_draws"] == draws
    assert receipt["build"]["source_sha256"] == source_hashes["r93/checker93.cpp"]
    result = obj("r93/k4/AGGREGATES.json")
    assert result["status"] == "COMPLETE" and result["mode"] == "CRIB_ASSISTED_AGGREGATE_ONLY"
    assert result["gate_type"] == "EXACT_CHECKER_CORRECTNESS" and result["blind_recovery_certified"] is False
    assert result["settings_per_input"] == 32 * sum(n - 1 for n in range(5, 97)) == 145728
    assert result["input_count"] == 201 and result["base_setting_input_calls"] == 29291328
    assert result["logical_exact_or_one_deletion_tests"] == 732283200 and result["observations"] == 24
    assert result["count_arithmetic"] == "Python int"
    assert result["decoded_plaintexts"] == result["wiring_completions"] == result["published_surviving_settings"] == 0
    assert result["candidate_or_strength_ranking"] is False
    assert result["interpretive_verdict_deferred_until_published_freeze"] is True
    aggregates = result["inputs"]
    assert set(aggregates) == {rid for rid, _ in inputs}
    for row in aggregates.values():
        assert set(row) == {"settings", "exact_feasible_labels", "drop_feasible_labels", "drop_feasible_label_observation_pairs"}
        assert row["settings"] == 145728
        e, d, p = (row[k] for k in ("exact_feasible_labels", "drop_feasible_labels", "drop_feasible_label_observation_pairs"))
        integer(e, 0, 145728); integer(d, e, 145728)
        # A nonexact compatible deletion intersects at least one two-endpoint edge.
        integer(p, 24 * e + d - e, 24 * e + 2 * (d - e))
    stream = result["kernel_stream"]
    assert stream["labels_per_input"] == 145728 and stream["input_count"] == 201
    assert stream["bitfield_stream_persisted"] is False and stream["count_arithmetic"] == "Python int"
    assert re.fullmatch(r"[0-9a-f]{64}", stream["bitfield_stream_sha256"])
    primary = aggregates["K4"]
    return {"status": "PASS", "settings_per_input": 145728, "inputs": 201, "primary": primary,
            "scope": scope,
            "nulls_with_exact_feasibility": sum(r["exact_feasible_labels"] > 0 for k,r in aggregates.items() if k != "K4"),
            "nulls_with_drop_feasibility": sum(r["drop_feasible_labels"] > 0 for k,r in aggregates.items() if k != "K4"),
            "exact_verdict": "EXACT_SCOPE_EXCL" if primary["exact_feasible_labels"] == 0 else "COMPATIBLE_OPEN",
            "drop_verdict": "EXACT_SCOPE_EXCL" if primary["drop_feasible_labels"] == 0 else "COMPATIBLE_OPEN",
            "gate_resource": gate_resource, "target_resource": resource,
            "full_target_scan_rerun": False, "bitfield_stream_recomputed": False,
            "independent_model_review": "NONE", "freeze_entries": len(frozen)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-commit", required=True)
    ap.add_argument("--r93-gate-commit", required=True)
    ap.add_argument("--r93-freeze-commit", required=True)
    ap.add_argument("--r94-freeze-commit", required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    assert not args.out.exists(), "review output exists; do not overwrite or automatically retry"
    for commit in (args.source_commit, args.r93_gate_commit, args.r93_freeze_commit, args.r94_freeze_commit):
        assert re.fullmatch(r"[0-9a-f]{40}", commit)
        git("merge-base", "--is-ancestor", commit, "HEAD")
    before(PREREG, args.source_commit)
    report = {"status": "PASS_INTERNAL_RESULT_REVIEW", "independent_model_review": "NONE",
              "source_commit": args.source_commit, "r93_gate_commit": args.r93_gate_commit,
              "r93_freeze_commit": args.r93_freeze_commit, "r94_freeze_commit": args.r94_freeze_commit,
              "checker_sha256": digest(Path(__file__).read_bytes()),
              "review_budget_sha256": digest(raw("audit/rotor_followup/BUDGET.json"))}
    report["r93"] = check_r93(args.source_commit, args.r93_gate_commit, args.r93_freeze_commit)
    report["r94"] = check_r94(args.source_commit, args.r94_freeze_commit)
    report["verified_hashes"] = dict(sorted(HASHED.items()))
    report["verified_artifact_count"] = len(HASHED)
    report["limitations"] = [
        "Same-model internal review; no independent-model ledger promotion.",
        "R93 mathematical target scan and transient bitfield stream are not independently rerun here.",
        "R94 optimizers are not rerun; reported intermediate trace values are checked but intermediate wirings were not saved.",
        "Only frozen/spent synthetic observations are reviewed; no fresh gate, false-positive estimate or K4 authorization follows.",
        "Historical full order5/order6 scores, unlogged work and operating-system isolation are not certified.",
        "Git verifies commit ancestry and bytes, not the instant of a historical push or first local data read."]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as f:
        json.dump(report, f, indent=2, sort_keys=True, allow_nan=False); f.write("\n")
    print(json.dumps({"status": report["status"], "r93": report["r93"]["exact_verdict"],
                      "r94": report["r94"]["bounded_solver_outcome"],
                      "verified_artifact_count": report["verified_artifact_count"]}))


if __name__ == "__main__":
    main()
