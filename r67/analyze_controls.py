#!/usr/bin/env python3
"""R67 post-freeze descriptive analysis. NEVER supplies or fits K4 clue letters.

Usage:
 python3 r67/analyze_controls.py CONTROL_DIR R65_RESULTS.jsonl VERIFICATION.json REPORT.json

Requires an independent PASSED verifier and fully frozen result SHA before
opening synthetic truth. No tuning or rerunning from analysis outputs.
"""
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAKE = "SNAKE_L"
MIRROR = "SNAKE_R"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def quantile(sorted_values, q):
    if not sorted_values:
        return None
    return sorted_values[int(q * (len(sorted_values) - 1))]


def features(row):
    stage = {x["route"]: x["total"] for x in row["stage1"]}
    vals = sorted(stage.values(), reverse=True)
    return {"best": vals[0], "second": vals[1],
            "snake_minus_mirror": stage[SNAKE] - stage[MIRROR],
            "snake_total": stage[SNAKE], "mirror_total": stage[MIRROR],
            "gap": row["gap"], "route": row["best_route"]}


def summary(items, threshold, k4):
    n = len(items)
    g = sorted(x["gap"] for x in items)
    above = sum(x["gap"] >= threshold for x in items)
    joint = sum(x["gap"] >= threshold and x["best_route"] == SNAKE for x in items)
    parts = [features(x) for x in items]
    return {
        "n": n,
        "ge_k4_gap": above,
        "descriptive_plus_one_rate": (1 + above) / (n + 1),
        "joint_best_snake_and_ge_k4_gap": joint,
        "best_route_snake": sum(x["best_route"] == SNAKE for x in items),
        "gap_median": quantile(g, 0.5),
        "gap_max": g[-1] if n else None,
        "best_total_ge_k4": sum(x["best"] >= k4["best"] for x in parts),
        "second_best_total_ge_k4": sum(x["second"] >= k4["second"] for x in parts),
        "snake_minus_mirror_ge_k4": sum(
            x["snake_minus_mirror"] >= k4["snake_minus_mirror"] for x in parts),
        "snake_minus_mirror_median": quantile(
            sorted(x["snake_minus_mirror"] for x in parts), 0.5),
        "best_total_median": quantile(sorted(x["best"] for x in parts), 0.5),
        "second_best_total_median": quantile(sorted(x["second"] for x in parts), 0.5)
    }


def positive_stats(pairs, threshold):
    return {
        "n": len(pairs),
        "correct_route": sum(t["route"] == r["best_route"] for t, r in pairs),
        "gap_ge_k4": sum(r["gap"] >= threshold for _, r in pairs),
        "correct_route_and_gap_ge_k4": sum(
            t["route"] == r["best_route"] and r["gap"] >= threshold for t, r in pairs),
        "median_gap": quantile(sorted(r["gap"] for _, r in pairs), 0.5)
    }


def main():
    if len(sys.argv) != 5:
        raise SystemExit(__doc__)
    control, resfile, verfile, outfile = map(Path, sys.argv[1:])
    if outfile.exists():
        raise SystemExit("refusing to overwrite analysis")
    manifest = json.loads((control / "MANIFEST.json").read_text())
    verified = json.loads(verfile.read_text())
    freeze = resfile.parent / "FROZEN.sha256"
    work = resfile.parent / "WORK.sha256"
    matching = [line.split("  ")[0] for line in freeze.read_text().splitlines()
                if "  results  " in line]
    if (verified.get("status") != "PASSED"
        or len(matching) != 1
        or matching[0] != sha(resfile)
        or verified.get("results_sha256") != sha(resfile)
        or verified.get("freeze_manifest_sha256") != sha(freeze)
        or verified.get("work_manifest_sha256") != sha(work)
        or verified.get("input_sha256") != manifest.get("blind_sha256")):
        raise SystemExit("raw solver run not frozen and independently verified")
    prereg_expected = (ROOT / "r67/PROTOCOL.sha256").read_text().split()[0]
    if (manifest.get("preregistration_sha256") != prereg_expected
        or sha(ROOT / "r67/PREREGISTRATION.md") != prereg_expected
        or verified.get("preregistration_sha256") != prereg_expected):
        raise SystemExit("R67 preregistration hash mismatch")
    truthpath, blindpath = control / "SEALED_TRUTH.json", control / "BLIND.tsv"
    if sha(truthpath) != manifest["truth_sha256"] or sha(blindpath) != manifest["blind_sha256"]:
        raise SystemExit("sealed truth / ciphertext manifest mismatch")
    truth = json.loads(truthpath.read_text())
    blind = dict(l.split("\t") for l in blindpath.read_text().splitlines()[1:] if l)
    if len(truth) != 216 or len(blind) != 216:
        raise SystemExit("wrong control sample size")
    for t in truth:
        if blind.get(t["id"]) != t["ciphertext"]:
            raise SystemExit("synthetic truth does not match sealed ciphertexts")
    result_rows = rows(resfile)
    res = {r["id"]: r for r in result_rows}
    if len(res) != len(result_rows) or set(res) != set(blind):
        raise SystemExit("missing or duplicated scored controls")
    for r in result_rows:
        if len(r["stage1"]) != 10 or len(set(x["route"] for x in r["stage1"])) != 10:
            raise SystemExit("incomplete stage-1 route scores")
        ordered = sorted(r["stage1"], key=lambda x: -x["total"])
        if (abs(ordered[0]["total"] - ordered[1]["total"] - r["gap"]) > 1e-5
                or ordered[0]["route"] != r["best_route"]):
            raise SystemExit("incorrect stage-1 gap")
    k4r = next((x for x in rows(ROOT / "r65/k4/run/RESULTS.jsonl") if x["id"] == "K4"), None)
    if k4r is None or abs(k4r["gap"] - 28.4979) > 0.001 or k4r["best_route"] != SNAKE:
        raise SystemExit("K4 frozen comparator differs from R65")
    k4 = features(k4r)
    threshold = k4r["gap"]
    buckets = defaultdict(list)
    positive = []
    details = defaultdict(list)
    for t in truth:
        r = res[t["id"]]
        family = t["family"]
        if family == "POS_GERMAN":
            positive.append((t, r))
        else:
            buckets[family].append(r)
            if family in ("PERIODIC_VIG", "QUAG_III", "QUAG_III_ROUTE"):
                details[family + "_period"].append(len(t["key"]))
            if family == "PLAINTEXT_AUTOKEY":
                details["autokey_lag"].append(t["lag"])
            if family == "HOMOPHONIC_ROUTE":
                details["homophone_map_size"].append(sum(map(len, t["homophones"].values())))
                details["homophone_max_per_letter"].append(max(map(len, t["homophones"].values())))
    families = {"OTP", "PERIODIC_VIG", "QUAG_III", "PLAINTEXT_AUTOKEY",
                "QUAG_III_ROUTE", "HOMOPHONIC_ROUTE"}
    if set(buckets) != families or any(len(x) != 32 for x in buckets.values()) or len(positive) != 24:
        raise SystemExit("unbalanced sealed controls")
    nuisance = [r for family in sorted(buckets) for r in buckets[family]]
    pos_snake = [(t, r) for t, r in positive if t["route"] == SNAKE]
    pos_other = [(t, r) for t, r in positive if t["route"] != SNAKE]
    if len(pos_snake) != 12 or len(pos_other) != 12:
        raise SystemExit("incorrect positive route split")
    report = {
        "experiment": "R67: structured-cipher control calibration only, NOT K4 solution",
        "k4_frozen_comparison": k4,
        "r65_legacy_shuffle_p": 1 / 301,
        "nuisance_pooled": summary(nuisance, threshold, k4),
        "nuisance_by_family": {k: summary(v, threshold, k4) for k, v in sorted(buckets.items())},
        "positive_controls": {"overall": positive_stats(positive, threshold),
                              "SNAKE_L": positive_stats(pos_snake, threshold),
                              "other_routes": positive_stats(pos_other, threshold)},
        "ic_matching_selection": {
            "accepted_vs_attempted_by_family": manifest["family_counts"],
            "period_lag_homophone_distributions": {
                name: dict(sorted(Counter(vals).items()))
                for name, vals in sorted(details.items())},
            "warning": "IC/coverage filtering selects distribution tails; no unmatched companion run."},
        "freeze_integrity": {
            "preregistration_sha256": prereg_expected,
            "result_sha256": sha(resfile),
            "verification_sha256": sha(verfile),
            "control_blind_sha256": manifest["blind_sha256"],
            "control_truth_sha256": manifest["truth_sha256"]},
        "interpretation": "Post-selection descriptive calibration only, not a newly independent p-value. "
                          "A low hit rate only applies to these six IC-matched cipher families and "
                          "does not identify a correct route, cipher, key or K4 plaintext."}
    outfile.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
