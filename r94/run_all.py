#!/usr/bin/env python3
"""One cumulative, synthetic-only R94 attempt. Run through the aggregate wrapper."""
import os

for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_name] = "1"

import csv
import hashlib
import importlib.metadata
import json
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import numpy as np
import reference as R
import selftest
import structured as S

OUT = HERE / "development"
TRUTH_PATH = HERE / "inputs/PANEL_TRUTH.json"
MODEL_SHA = "85b4adf264619a12c9ed646c7d4fc952ef76025db67dd96f2b668ea1e1cf1f41"
EVENTS = []
PHASES = {}
ATTEMPT_STARTED_HERE = False


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")


def event(name, **kw):
    obj = {"event": name, "monotonic_seconds": time.monotonic(),
           "process_cpu_seconds": time.process_time(), **kw}
    EVENTS.append(obj)
    with (OUT / "EVENTS.jsonl").open("a") as f:
        f.write(json.dumps(obj, allow_nan=False) + "\n")
        f.flush()


class Phase:
    def __init__(self, name, cap):
        self.name, self.cap = name, cap
        self.wall, self.cpu = time.monotonic(), time.process_time()
        event("phase_start", phase=name, wall_and_cpu_cap=cap)

    def check(self):
        wall = time.monotonic() - self.wall
        cpu = time.process_time() - self.cpu
        if max(wall, cpu) > self.cap:
            raise TimeoutError(f"{self.name} phase exceeded {self.cap}s: wall={wall},cpu={cpu}")

    def finish(self):
        self.check()
        rep = {"wall_seconds": time.monotonic() - self.wall,
               "cpu_seconds": time.process_time() - self.cpu,
               "cap_wall_and_cpu_seconds": self.cap, "status": "COMPLETE"}
        PHASES[self.name] = rep
        event("phase_complete", phase=self.name, **rep)


def verify_environment():
    receipt = json.loads((HERE / "SOURCE_RECEIPT.json").read_text())
    versions = {k: importlib.metadata.version(k) for k in receipt["packages"]}
    assert versions == receipt["packages"], (versions, receipt["packages"])
    deferred = []
    verified = 0
    for line in (HERE / "PROTOCOL.sha256").read_text().splitlines():
        digest, path = line.split(maxsplit=1)
        path = ROOT / path.strip()
        if path == TRUTH_PATH:
            deferred.append(path.relative_to(ROOT).as_posix())
            continue
        assert path.is_file(), str(path)
        assert sha(path) == digest, str(path)
        verified += 1
    assert deferred == ["r94/inputs/PANEL_TRUTH.json"]
    event("environment_verified", packages=versions, protocol_files=verified,
          truth_digest_check_deferred=deferred)
    return receipt


def load_model():
    path = ROOT / "r91/R59_LOWER4_FROM_K5.bin"
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == MODEL_SHA
    assert raw[:8] == b"R59LM\x04\x00\x00"
    values = np.frombuffer(raw[8:], dtype="<f4")
    assert len(values) == sum(26 ** k for k in range(1, 5))
    tables, off = [], 0
    for k in range(1, 5):
        tables.append(values[off:off + 26 ** k])
        off += 26 ** k
    return tables


def load_panel():
    with (HERE / "inputs/PANEL.tsv").open() as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    assert len(rows) == 48
    assert [row["id"] for row in rows] == [f"D_{i:03d}" for i in range(48)]
    for row in rows:
        fields = row.pop("label").split(",")
        row["label"] = [*fields[:2], *map(int, fields[2:])]
        assert tuple(row["label"]) in R.LABELS
        assert len(row["ciphertext"]) == 97
        assert all(c in R.AZ for c in row["ciphertext"])
        row["cell"] = R.cell_of(*row["label"][2:5])
    assert Counter(row["cell"] for row in rows) == {cell: 6 for cell in R.CELLS}
    return rows


def arrays_for(row):
    ei, eo, n, r, h, d1, d2 = row["label"]
    s1, s2 = map(lambda x: np.array(x, dtype=np.int64), R.shifts(97, n, r, h, d1, d2))
    return ((np.array([R.IDX[eo][c] for c in row["ciphertext"]]) + s2) % 26,
            s1, (s2 - s1) % 26, np.array([ord(c) - 65 for c in R.ALPH[ei]]))


def state(U, V, row, arrays, tables, trace, start=None):
    assert sorted(U) == list(range(26)) and sorted(V) == list(range(26))
    x = S.decode(U, V, *arrays)
    text = ''.join(chr(65 + int(c)) for c in x)
    W1, W2 = S.inv(U).tolist(), S.inv(V).tolist()
    assert R.decrypt(row["ciphertext"], W1, W2, *row["label"]) == text
    assert R.encrypt(text, W1, W2, *row["label"]) == row["ciphertext"]
    return {"start": start, "W1": W1, "W2": W2, "text": text,
            "unigram_sum_log10": S.uni_score(U, V, arrays),
            "lm4_sum_log10": float(S.lm4_batch(x, tables)[0]), "trace": trace,
            "forward_witness": True}


def rank(states):
    ordered = sorted(states, key=lambda t: (-t["lm4_sum_log10"], -t["unigram_sum_log10"],
                                          t["text"], t["W1"], t["W2"]))
    out, seen = [], set()
    for candidate in ordered:
        if candidate["text"] not in seen:
            seen.add(candidate["text"])
            out.append(candidate)
    return out[:8]


def run_candidates(rows, tables, version, previous=None):
    phase = Phase(version, 300 if version == "A" else 900)
    out = {}
    with (OUT / f"VERSION_{version}.jsonl").open("x") as f:
        for row in rows:
            phase.check()
            arrays = arrays_for(row)
            if version == "A":
                initials = S.starts(row["id"], row["ciphertext"], row["label"])
            else:
                initials = [(S.inv(c["W1"]), S.inv(c["W2"]))
                            for c in previous[row["id"]]["final_states"]]
            candidates = []
            for j, (U, V) in enumerate(initials):
                if version == "A":
                    U, V, trace = S.alternate_unigram(U, V, arrays, check=phase.check)
                else:
                    U, V, trace = S.refine_lm4(U, V, arrays, tables, check=phase.check)
                candidates.append(state(U, V, row, arrays, tables, trace, j))
            result = {"id": row["id"], "label": row["label"], "cell": row["cell"],
                      "version": version, "final_states": candidates, "retained": rank(candidates)}
            assert len(candidates) == 8 and result["retained"]
            if version == "B":
                assert all(b["lm4_sum_log10"] >= a["lm4_sum_log10"] - S.EPS
                           for a, b in zip(previous[row["id"]]["final_states"], candidates))
            out[row["id"]] = result
            f.write(json.dumps(result, allow_nan=False) + "\n")
            f.flush()
            event("candidate_row_saved", version=version, id=row["id"], states=8)
    phase.finish()
    event("candidate_file_closed", version=version,
          sha256=sha(OUT / f"VERSION_{version}.jsonl"), rows=len(out))
    return out


def equivalent(candidate, truth, label):
    W1, W2 = np.array(candidate["W1"]), np.array(candidate["W2"])
    T1, T2 = np.array(truth["W1"]), np.array(truth["W2"])
    shift = (W1 - T1) % 26
    gauge = bool(np.all(shift == shift[0]) and
                 np.array_equal(W2[(np.arange(26) + shift[0]) % 26], T2))
    # Supplied alphabets and structure are identical, so contact-level equality
    # for every input at every distinct schedule proves equality on97 positions.
    s1, s2 = R.shifts(97, *label[2:])
    operator = True
    for a, b in set(zip(s1, s2)):
        p = np.arange(26)
        cand_map = (W2[(W1[(p + a) % 26] - a + b) % 26] - b) % 26
        true_map = (T2[(T1[(p + a) % 26] - a + b) % 26] - b) % 26
        if not np.array_equal(cand_map, true_map):
            operator = False
            break
    return {"gauge_equivalent": gauge, "operator_equivalent_97": operator,
            "raw_wirings_equal": bool(np.array_equal(W1, T1) and np.array_equal(W2, T2))}


def matches(text, true):
    assert len(text) == len(true) == 97
    return sum(a == b for a, b in zip(text, true))


def archived_scalar_witness(plain, cipher, W1, W2, label):
    """Independent loop for the archived saved-state replay; no reference encrypt/decrypt call."""
    ei, eo, n, r, h, d1, d2 = label
    alphabet_in, alphabet_out = R.ALPH[ei], R.ALPH[eo]
    assert sorted(W1) == sorted(W2) == list(range(26))
    inverse1 = {value: index for index, value in enumerate(W1)}
    inverse2 = {value: index for index, value in enumerate(W2)}
    encoded, decoded = [], []
    for i, (p, c) in enumerate(zip(plain, cipher)):
        tick = (i + r) // n
        fast, slow = d1 * tick, d2 * ((tick + h) // 26)
        between = W1[(alphabet_in.index(p) + fast) % 26] - fast
        encoded.append(alphabet_out[(W2[(between + slow) % 26] - slow) % 26])
        backward = inverse2[(alphabet_out.index(c) + slow) % 26] - slow
        decoded.append(alphabet_in[(inverse1[(backward + fast) % 26] - fast) % 26])
    assert ''.join(encoded) == cipher and ''.join(decoded) == plain


def recovery_summary(result, truth):
    rows = []
    for rid, candidate in result.items():
        t = truth[rid]
        keep = candidate["retained"]
        states = candidate["final_states"]
        rows.append({"id": rid, "cell": candidate["cell"],
                     "top1_matches": matches(keep[0]["text"], t["pt"]),
                     "any_retained_matches": max(matches(c["text"], t["pt"]) for c in keep),
                     "best_final_state_matches": max(matches(c["text"], t["pt"]) for c in states),
                     "retained_count": len(keep),
                     "top1_equivalence": equivalent(keep[0], t, candidate["label"])})
    def summarize(selected):
        return {"cases": len(selected),
                "top1_ge95": sum(r["top1_matches"] >= 95 for r in selected),
                "top1_exact": sum(r["top1_matches"] == 97 for r in selected),
                "any_retained_ge95": sum(r["any_retained_matches"] >= 95 for r in selected),
                "any_final_state_ge95": sum(r["best_final_state_matches"] >= 95 for r in selected),
                "maximum_top1_matches": max(r["top1_matches"] for r in selected),
                "maximum_final_state_matches": max(r["best_final_state_matches"] for r in selected),
                "median_top1_matches": float(np.median([r["top1_matches"] for r in selected]))}
    return {"total": summarize(rows),
            "by_cell": {cell: summarize([r for r in rows if r["cell"] == cell]) for cell in R.CELLS},
            "rows": rows}


def true_neighborhood(U, V, row, arrays, tables):
    base = float(S.lm4_batch(S.decode(U, V, *arrays), tables)[0])
    best = None
    wrong_above = set()
    evaluated = 0
    for block in (0, 1):
        current = [U, V][block]
        ps = []
        for x in range(26):
            for y in range(x + 1, 26):
                p = current.copy()
                p[x], p[y] = p[y], p[x]
                ps.append(p)
        texts = S.legal_texts(ps, U, V, arrays, block)
        scores = S.lm4_batch(texts, tables)
        evaluated += len(scores)
        for i, score in enumerate(scores):
            if score > base + S.EPS:
                text = ''.join(chr(65 + int(c)) for c in texts[i])
                wrong_above.add(text)
                if best is None or float(score) > best[0]:
                    best = (float(score), block, ps[i])
    witness = None
    if best is not None:
        trial = [U, V]
        trial[best[1]] = best[2]
        witness = state(*trial, row, arrays, tables,
                        {"diagnostic": "best_true_key_single_transposition"})
    return {"true_lm4_sum_log10": base, "neighbors_evaluated": evaluated,
            "distinct_wrong_plaintexts_above_true": len(wrong_above), "best_witness": witness}


def run_diagnostics(rows, tables, truth, phase):
    out = []
    with (OUT / "CONDITIONAL_DIAGNOSTICS.jsonl").open("x") as f:
        for row in rows:
            phase.check()
            t, arrays = truth[row["id"]], arrays_for(row)
            U, V = S.inv(t["W1"]), S.inv(t["W2"])
            true_score = float(S.lm4_batch(np.array([ord(c) - 65 for c in t["pt"]]), tables)[0])
            conditions = []
            for fixed in (0, 1):
                block = 1 - fixed
                matrix = S.unigram_matrix(U, V, *arrays, block)
                proposal = S.exact_assignment(matrix)
                trial = [U.copy(), V.copy()]
                trial[block] = proposal
                optimum = float(matrix[np.arange(26), proposal].sum())
                assert abs(optimum - S.uni_score(*trial, arrays)) < 1e-7
                a = state(*trial, row, arrays, tables,
                          {"diagnostic": "one_true_wiring_exact_conditional_unigram",
                           "assignment_calls": 1})
                pU, pV, trace = S.refine_lm4(*trial, arrays, tables, fixed=fixed, check=phase.check)
                assert np.array_equal([pU, pV][fixed], [U, V][fixed])
                b = state(pU, pV, row, arrays, tables, trace)
                for candidate in (a, b):
                    candidate["matches"] = matches(candidate["text"], t["pt"])
                    candidate["equivalence"] = equivalent(candidate, t, row["label"])
                    candidate["lm4_gap_to_truth"] = candidate["lm4_sum_log10"] - true_score
                conditions.append({"fixed_true_inverse_wiring": "U" if fixed == 0 else "V",
                                   "A": a, "B": b})
            neighborhood = true_neighborhood(U, V, row, arrays, tables)
            a, s1, delta, english = arrays
            item = {"id": row["id"], "cell": row["cell"], "conditions": conditions,
                    "true_neighborhood": neighborhood,
                    "observed_U_contacts": len(set(((V[a] - delta) % 26).tolist())),
                    "observed_V_contacts": len(set(a.tolist()))}
            out.append(item)
            f.write(json.dumps(item, allow_nan=False) + "\n")
            f.flush()
    summary = {}
    for fixed in ("U", "V"):
        cases = [c for r in out for c in r["conditions"] if c["fixed_true_inverse_wiring"] == fixed]
        summary["true_" + fixed] = {}
        for version in ("A", "B"):
            values = [c[version] for c in cases]
            summary["true_" + fixed][version] = {
                "cases": len(values), "ge95": sum(c["matches"] >= 95 for c in values),
                "exact": sum(c["matches"] == 97 for c in values),
                "median_matches": float(np.median([c["matches"] for c in values])),
                "max_matches": max(c["matches"] for c in values),
                "wrong_text_above_true_lm4": sum(c["matches"] < 97 and c["lm4_gap_to_truth"] > S.EPS
                                                for c in values),
                "true_lm4_above_found": sum(c["lm4_gap_to_truth"] < -S.EPS for c in values)}
    summary["true_key_neighborhood"] = {
        "cases": len(out), "neighbors_evaluated": sum(r["true_neighborhood"]["neighbors_evaluated"] for r in out),
        "cases_with_wrong_text_above_true": sum(r["true_neighborhood"]["distinct_wrong_plaintexts_above_true"] > 0
                                                for r in out)}
    return summary


def audit_archived(truth, phase):
    root = ROOT / "audit/backlog/multirotor/solver/dev"
    output = {}
    for version in ("v2", "v3"):
        phase.check()
        raw_path = root / version / "run/ANNEAL.jsonl"
        ranked_path = root / version / "run/RESULTS.jsonl"
        raw = [json.loads(line) for line in raw_path.read_text().splitlines()]
        ranked = [json.loads(line) for line in ranked_path.read_text().splitlines()]
        assert len(raw) == len(ranked) == 48
        assert {r["id"] for r in raw} == set(truth) == {r["id"] for r in ranked}
        witnesses = saved_ge95 = 0
        best_raw = best_top1 = 0
        top1_ge95 = keep_ge95 = 0
        for row in raw:
            t = truth[row["id"]]
            assert row["ct"] == t["ct"] and row["label"] == t["label"]
            assert len(row["restarts"]) == (32 if version == "v2" else 8)
            for candidate in row["restarts"]:
                archived_scalar_witness(candidate["text"], row["ct"], candidate["W1"], candidate["W2"], row["label"])
                witnesses += 1
                count = matches(candidate["text"], t["pt"])
                saved_ge95 += count >= 95
                best_raw = max(best_raw, count)
        for row in ranked:
            t = truth[row["id"]]
            keep = row["keep"]
            assert len(keep) <= 8 and row["best"] == max(keep, key=lambda c: c["lm_per_letter"])
            for c in keep:
                archived_scalar_witness(c["text"], t["ct"], c["W1"], c["W2"], row["label"])
            top = matches(row["best"]["text"], t["pt"])
            top1_ge95 += top >= 95
            keep_ge95 += max(matches(c["text"], t["pt"]) for c in keep) >= 95
            best_top1 = max(best_top1, top)
        output[version] = {"saved_final_restart_witnesses": witnesses,
                           "saved_final_restart_ge95": saved_ge95,
                           "maximum_saved_final_restart_matches": best_raw,
                           "top1_ge95": top1_ge95, "any_retained_ge95": keep_ge95,
                           "maximum_top1_matches": best_top1,
                           "raw_sha256": sha(raw_path), "ranked_sha256": sha(ranked_path),
                           "original_order5_or_6_scores_recomputed": False}
    # Include failed logs. Do not assert absence of unlogged historical work.
    total_wall = total_cpu = 0.0
    resources = {}
    for version in ("v1", "v2", "v3"):
        paths = sorted((root / version).glob("*RESOURCE*.json"))
        logs = [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p),
                 "log": json.loads(p.read_text())} for p in paths]
        wall = sum(x["log"]["wall_seconds"] for x in logs)
        cpu = sum(x["log"]["cpu_seconds"] for x in logs)
        resources[version] = {"jobs": len(logs), "wall_seconds": round(wall, 3),
                              "cpu_seconds": round(cpu, 3), "logs": logs}
        total_wall += wall
        total_cpu += cpu
    assert sum(r["jobs"] for r in resources.values()) == 17
    output["resources"] = {"versions": resources, "total_wall_seconds": round(total_wall, 3),
                           "total_cpu_seconds": round(total_cpu, 3)}
    output["v1"] = {"status": "INCOMPLETE", "saved_candidate_evidence": False,
                    "recovery_rate": None}
    output["interpretation"] = "Final saved restart states only; no exhaustive visited-state record or full LM replay."
    return output


def main():
    global ATTEMPT_STARTED_HERE
    # Exclusive creation also refuses an existing empty directory. In
    # particular, a rejected repeat cannot overwrite earlier failure evidence.
    OUT.mkdir(exist_ok=False)
    ATTEMPT_STARTED_HERE = True
    event("attempt_start", truth_opened=False)
    receipt = verify_environment()
    tables, rows = load_model(), load_panel()
    phase = Phase("mathematical_checks", 60)
    tests = selftest.run(tables, phase.check)
    phase.finish()
    write("TESTS.json", tests)
    a = run_candidates(rows, tables, "A")
    # B's trigger is correctness/completion/resource-only. Truth has not been opened.
    event("version_B_trigger", decision="RUN", selftests="PASS", A_rows=len(a),
          truth_used=False, score_or_recovery_cutoff=False)
    b = run_candidates(rows, tables, "B", a)
    frozen_unknown = {v: sha(OUT / f"VERSION_{v}.jsonl") for v in ("A", "B")}
    write("UNKNOWN_OUTPUTS_BEFORE_TRUTH.json", frozen_unknown)
    phase = Phase("diagnostics_and_archive_replay", 300)
    event("opening_public_spent_truth", unknown_output_sha256=frozen_unknown)
    truth_bytes = TRUTH_PATH.read_bytes()
    assert hashlib.sha256(truth_bytes).hexdigest() == receipt["inputs"]["r94/inputs/PANEL_TRUTH.json"]
    truth = json.loads(truth_bytes)
    assert set(truth) == {row["id"] for row in rows}
    for row in rows:
        t = truth[row["id"]]
        assert t["ct"] == row["ciphertext"] and t["label"] == row["label"]
        assert t["cell"] == row["cell"] and len(t["pt"]) == 97
        assert R.encrypt(t["pt"], t["W1"], t["W2"], *row["label"]) == t["ct"]
    summaries = {"A": recovery_summary(a, truth), "B": recovery_summary(b, truth)}
    conditional = run_diagnostics(rows, tables, truth, phase)
    archived = audit_archived(truth, phase)
    phase.finish()
    write("ARCHIVED_REPLAY.json", archived)
    write("RECOVERY.json", summaries)
    write("CONDITIONAL_SUMMARY.json", conditional)
    no_power = all(summaries[v]["total"]["any_final_state_ge95"] == 0 for v in ("A", "B"))
    report = {"status": "COMPLETE_DIAGNOSTIC",
              "bounded_solver_outcome": "SOLVER_NO_POWER" if no_power else "DEVELOPMENT_RECOVERY_OBSERVED",
              "unknown_two_wiring": {v: summaries[v]["total"] for v in ("A", "B")},
              "truth_assisted_diagnostic": conditional, "phases": PHASES,
              "input_receipt": receipt, "unknown_outputs_before_truth": frozen_unknown,
              "k4_authorized": False, "formal_gate_pass": False,
              "new_holdout": False, "negative_control_count": 0,
              "original_lm5_or_lm6_replayed": False}
    write("RESULT.json", report)
    manifest = []
    for path in sorted(OUT.iterdir()):
        if path.is_file() and path.name != "OUTPUTS.sha256":
            manifest.append(f"{sha(path)}  {path.relative_to(ROOT).as_posix()}")
    (OUT / "OUTPUTS.sha256").write_text("\n".join(manifest) + "\n")
    print(json.dumps({"status": report["status"], "bounded_solver_outcome": report["bounded_solver_outcome"],
                      "unknown_two_wiring": report["unknown_two_wiring"], "phases": PHASES}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        if ATTEMPT_STARTED_HERE:
            write("INCOMPLETE.json", {"status": "INCOMPLETE", "error": repr(exc), "phases": PHASES})
        raise
