#!/usr/bin/env python3
"""Independent post-freeze R90 review, with aggregate-only exact outputs.

This script imports no R90 implementation. It independently specifies the
catalog, checks forward coordinate constraints, re-encrypts frozen witnesses,
recomputes gate/evaluation arithmetic, and checks evidence hashes/history.
It does not run a blind solver or emit candidate plaintexts.
Run through audit/run_bounded_agg.py using r90/QA_MANIFEST.json.
"""
import ast
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import random
import subprocess
import sys

import numpy as np

ROOT = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
BASE = "bef9e7d7bcbecc1ca870fa46f0dd78d8a0805d77"
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
WORDS = ("ORCHARD", "MYSTERY", "TRAVEL", "MECHANIC", "RIVER", "PHILOSOPHY", "HORIZON", "GARDEN", "SECRET", "TEMPLE",
         "MARKET", "TUNNEL", "LIBRARY", "MIRROR", "CIPHER")


def keyed(word):
    return "".join(dict.fromkeys(word + AZ))


ALPHABETS = {word: keyed(word) for word in WORDS}
KEYS = {"PAL": "PALIMPSEST", "ABS": "ABSCISSA"}
KRY = keyed("KRYPTOS")
INNER = [(b, u, v) for b in (5, 7, 9, 11) for u in range(1, b) for v in range(1, b) if u != v]
OUTER = [None] + [(name, sign, phase) for name, word in KEYS.items()
                 for sign in (1, -1) for phase in range(len(word))]
STATES = [(a, b, u, v, o) for o in OUTER for a in ALPHABETS for b, u, v in INNER]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def jread(path):
    return json.loads((ROOT / path).read_text())


def read_rows(path):
    lines = (ROOT / path).read_text().splitlines()
    assert lines[0] == "id\tciphertext"
    pairs = [line.split("\t") for line in lines[1:] if line]
    rows = dict(pairs)
    assert len(rows) == len(pairs)
    assert all(len(s) == 97 and set(s) <= set(AZ) for s in rows.values())
    return rows


def records(path):
    data = [json.loads(line) for line in (ROOT / path).read_text().splitlines() if line]
    res = {r["id"]: r for r in data}
    assert len(res) == len(data)
    return res


def canonical(a):
    return (frozenset((frozenset(a[:13]), frozenset(a[13:]))),
            frozenset(frozenset((a[j], a[j + 13])) for j in range(13)))


def setting(st):
    o = st["outer"]
    result = (st["alphabet"], st["b"], st["u"], st["v"],
              None if o is None else (o["key"], o["sign"], o["phase"]))
    assert result[0] in ALPHABETS and result[1:4] in INNER and result[4] in OUTER
    return result


def tag(st):
    a, b, u, v, o = st
    return f"{a}|{b}|{u}|{v}|" + ("-|-|-" if o is None else f"{o[0]}|{o[1]}|{o[2]}")


def forward(pt, st):
    """Independent row/column gathering and pointwise outer encryption."""
    a, b, u, v, outer = st
    alphabet = ALPHABETS[a]
    middle = []
    for start in range(0, len(pt), b):
        vals = [alphabet.index(ch) for ch in pt[start:start + b]]
        t = len(vals)
        middle.extend(alphabet[13 * (vals[(j + u) % t] // 13) + vals[(j + v) % t] % 13] for j in range(t))
    if outer is None:
        return "".join(middle)
    name, sign, phase = outer
    key = KEYS[name]
    return "".join(KRY[(KRY.index(ch) + sign * KRY.index(key[(i + phase) % len(key)])) % 26]
                   for i, ch in enumerate(middle))


def counts_at_known_positions(ct, positions, letters):
    """Forward-coordinate consistency; no complete candidate is reconstructed."""
    raw = np.asarray([AZ.index(c) for c in ct], dtype=np.int16)
    kry_i = np.asarray([KRY.index(c) for c in AZ], dtype=np.int16)
    kry_chars = np.asarray([AZ.index(c) for c in KRY], dtype=np.int16)
    middle = [raw]
    for name, sign, phase in OUTER[1:]:
        shifts = np.asarray([KRY.index(KEYS[name][(i + phase) % len(KEYS[name])]) for i in range(len(ct))])
        middle.append(kry_chars[(kry_i[raw] - sign * shifts) % 26])
    middle = np.asarray(middle)
    row_at, col_at = [], []
    positions = np.asarray(positions, dtype=np.int16)
    for b, u, v in INNER:
        start = positions // b * b
        length = np.minimum(b, len(ct) - start)
        row_at.append(start + (positions - start - u) % length)
        col_at.append(start + (positions - start - v) % length)
    row_at, col_at = np.asarray(row_at), np.asarray(col_at)
    per_alphabet = []
    for alphabet in ALPHABETS.values():
        index = np.asarray([alphabet.index(c) for c in AZ], dtype=np.int16)
        known = np.asarray([alphabet.index(c) for c in letters], dtype=np.int16)
        values = index[middle]
        matches = ((values[:, row_at] // 13 == known[None, None, :] // 13) &
                   (values[:, col_at] % 13 == known[None, None, :] % 13))
        per_alphabet.append(matches.sum(2))
    # Restore outer/alphabet/inner setting order used in the preregistered list.
    counts = np.asarray(per_alphabet).transpose(1, 0, 2).ravel()
    assert len(counts) == 104340
    return counts


def toy_controls():
    """Exhaust all 2x3 toy plaintexts up to five symbols, all tested block residues.

    Encrypt by gathering; invert by scattering each coordinate back to its
    source position. This exercises short blocks, including coincident residues.
    """
    cases, checks, coincident = 0, 0, 0
    for b in (3, 4, 5):
        for length in range(1, b + 1):
            plain = np.asarray(list(itertools.product(range(6), repeat=length)), dtype=np.int16)
            j = np.arange(length)
            for u in range(1, b):
                for v in range(1, b):
                    if u == v:
                        continue
                    row_source, col_source = (j + u) % length, (j + v) % length
                    ciphertext = 3 * (plain[:, row_source] // 3) + plain[:, col_source] % 3
                    rows, cols = np.empty_like(plain), np.empty_like(plain)
                    rows[:, row_source] = ciphertext // 3
                    cols[:, col_source] = ciphertext % 3
                    assert np.array_equal(3 * rows + cols, plain)
                    assert len(np.unique(ciphertext, axis=0)) == len(plain)
                    cases += 1
                    checks += len(plain)
                    coincident += int(u % length == v % length)
    # Actual 26-letter catalog plants: all blocks/short tails, signs, phases,
    # and alphabet classes. The independent full-family counts must recognize
    # the planted setting. No K4 input or published letter is used here.
    rng = random.Random(901122)
    plants = 0
    for k in range(60):
        st = STATES[(k * 1729 + 13) % len(STATES)]
        n = 1 + (k * 37) % 98
        pt = "".join(rng.choice(AZ) for _ in range(n))
        ct = forward(pt, st)
        known_positions = np.arange(n)
        hits = counts_at_known_positions(ct, known_positions, pt)
        assert hits[STATES.index(st)] == n
        changed_at = n // 2
        ct_bad = ct[:changed_at] + AZ[(AZ.index(ct[changed_at]) + 13) % 26] + ct[changed_at + 1:]
        bad_hits = counts_at_known_positions(ct_bad, known_positions, pt)
        assert bad_hits[STATES.index(st)] >= n - 2
        pt_bad = pt[:changed_at] + AZ[(AZ.index(pt[changed_at]) + 7) % 26] + pt[changed_at + 1:]
        ct_from_bad_pt = forward(pt_bad, st)
        assert sum(a != b for a, b in zip(ct, ct_from_bad_pt)) <= 2
        plants += 1
    return {"toy_alphabet_size": 6, "toy_rectangle": [2, 3], "toy_parameter_cases": cases,
            "exhaustive_toy_plaintext_parameter_cases": checks,
            "coincident_short_block_parameter_cases": coincident,
            "actual_catalog_random_plants": plants, "actual_catalog_ciphertext_error_checks": plants,
            "actual_catalog_plaintext_error_checks": plants, "passed": True}


def review_catalog():
    old = jread("r89/audit/evidence/ALPHABET_SCOPE.json")
    assert list(WORDS) == old["old_classes_not_covered"]
    assert len(set(canonical(a) for a in ALPHABETS.values())) == 15
    tree = ast.parse((ROOT / "r90/f26c.py").read_text())
    declared = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "WORDS" for t in n.targets))
    assert tuple(declared) == WORDS
    original_names = ("", "KRYPTOS", "PALIMPSEST", "ABSCISSA", "ORCHARD", "CANDLE", "MYSTERY", "TRAVEL", "MECHANIC",
                      "RIVER", "PHILOSOPHY", "HORIZON", "GARDEN", "SECRET", "TEMPLE", "MARKET", "TUNNEL", "LIBRARY", "MIRROR", "CIPHER")
    r89_names = ("KRYPTOS", "PALIMPSEST", "ABSCISSA", "NUANCE", "MAGNETIC", "PASSAGE", "CANDLE", "SANBORN", "SCHEIDT",
                 "LANGLEY", "WEBSTER", "SHADING", "IQLUSION", "UNDERGRUUND", "DESPARATLY", "LAYERTWO", "INVISIBLE")
    r89 = [AZ, "QWERTYUIOPASDFGHJKLZXCVBNM", AZ[::2] + AZ[1::2]] + [keyed(w) for w in r89_names]
    prior = set(map(canonical, r89))
    now = set(map(canonical, ALPHABETS.values()))
    original = set(canonical(keyed(w)) for w in original_names)
    assert not (prior & now) and original <= prior | now and len(prior | now) == 35
    return {"keywords": WORDS, "distinct_classes": len(now), "prior_classes_overlap": len(prior & now),
            "joint_classes": len(prior | now), "original_classes_covered_jointly": len(original),
            "inner_settings_per_alphabet": len(INNER), "outer_options_including_none": len(OUTER),
            "total_settings": len(STATES)}


def review_frozen_witnesses(prefix, inputs, res):
    assert set(inputs) == set(res)
    checks = 0
    candidate_tags = set(map(tag, STATES))
    for rid, record in res.items():
        assert record["n_settings"] == 104340 and record["kept"] == 256
        assert len(record["retained"]) == len(set(record["retained"])) == 256
        assert set(record["retained"]) <= candidate_tags
        assert record["best"] == record["top"][0]
        scores = [e["lm_per_letter"] for e in record["top"]]
        assert scores == sorted(scores, reverse=True)
        assert max(e["lm_per_letter"] for e in record["best_by_arm"].values()) == scores[0]
        for e in record["top"] + list(record["best_by_arm"].values()):
            st = setting(e["setting"])
            assert tag(st) == e["tag"] and e["tag"] in record["retained"]
            assert e["arm"] == ("F26" if st[4] is None else "F26C")
            assert len(e["text"]) == 97 and set(e["text"]) <= set(AZ)
            assert forward(e["text"], st) == inputs[rid]
            checks += 1
    reported = jread(prefix + "/run/WITNESS.json")
    assert reported["passed"] and reported["witnesses"] == checks and reported["ciphertexts"] == len(res)
    return {"records": len(res), "witnesses": checks, "passed": True}


def review_gate():
    inputs = read_rows("r90/holdout/BLIND.tsv")
    truth = jread("r90/holdout/TRUTH.json")
    res = records("r90/holdout/run/RESULTS.jsonl")
    assert set(truth) == set(inputs) == set(res)
    assert all(truth[rid]["ct"] == inputs[rid] for rid in inputs)
    assert sha(ROOT / "r90/holdout/TRUTH.json") == (ROOT / "r90/holdout/TRUTH_SHA256").read_text().split()[0]
    witnesses = review_frozen_witnesses("r90/holdout", inputs, res)
    pos, neg, extra = [], [], []
    for rid, t in truth.items():
        best = res[rid]["best"]
        confidence = best["lm_per_letter"] >= -1.30 and best["word_per_letter"] >= -2.50
        if t["class"] == "NEG":
            neg.append({"id": rid, "generator": t["generator"], "confident": confidence,
                        "lm": best["lm_per_letter"], "word": best["word_per_letter"]})
            continue
        true, found = setting(t["setting"]), setting(best["setting"])
        key_right = (best["arm"] == "F26C" and canonical(ALPHABETS[true[0]]) == canonical(ALPHABETS[found[0]])
                     and true[1:] == found[1:])
        matches = sum(a == b for a, b in zip(t["enciphered"], best["text"]))
        true_tag = tag(true)
        retained = true_tag in res[rid]["retained"]
        row = {"id": rid, "key_right": key_right, "letters": matches, "confident": confidence,
               "ok": key_right and matches >= 95 and confidence,
               "retained": retained, "rank": res[rid]["retained"].index(true_tag) + 1 if retained else None}
        row["exact"] = row["ok"] and matches == 97
        encoded = forward(t["enciphered"], true)
        if t["class"] == "POS":
            assert encoded == inputs[rid]
            assert t["enciphered"] == (t["pt"].translate(str.maketrans("CW", "KV")) if t["masked"] else t["pt"])
            assert t["param"] == true[1] and t["stratum"] == f"S{(5,7,9,11).index(true[1])+1}"
            row.update(genre=t["genre"], stratum=t["stratum"], masked=t["masked"])
            pos.append(row)
        else:
            assert t["class"] == "EXTRA"
            if t["kind"] == "CTERR":
                assert sum(a != b for a, b in zip(encoded, inputs[rid])) == 1
            else:
                assert encoded == inputs[rid] and sum(a != b for a, b in zip(t["pt"], t["enciphered"])) == 1
            row.update(kind=t["kind"])
            extra.append(row)
    assert len(pos) == 48 and len(neg) == 150 and len(extra) == 4
    count = lambda key, val: [sum(p["ok"] for p in pos if p[key] == val), sum(p[key] == val for p in pos)]
    summary = {"positives": len(pos), "ok": sum(p["ok"] for p in pos), "exact": sum(p["exact"] for p in pos),
               "key_right": sum(p["key_right"] for p in pos), "retained": sum(p["retained"] for p in pos),
               "stage1_rank_max": max(p["rank"] for p in pos if p["rank"] is not None),
               "by_stratum": {s: count("stratum", s) for s in ("S1","S2","S3","S4")},
               "by_genre": {g: count("genre", g) for g in ("G1","G2","G3")},
               "masked": count("masked", True), "unmasked": count("masked", False),
               "negatives": len(neg), "negatives_confident": sum(p["confident"] for p in neg)}
    go = (summary["ok"] >= 42 and summary["exact"] >= 36 and summary["retained"] >= 46
          and all(x[0] >= 9 for x in summary["by_stratum"].values())
          and all(x[0] >= 12 for x in summary["by_genre"].values())
          and summary["masked"][0] >= 8 and summary["negatives_confident"] <= 1 and witnesses["passed"])
    saved = jread("r90/holdout/GATE.json")
    for key, value in summary.items():
        assert saved["summary"][key] == value, key
    assert saved["verdict"] == ("GO" if go else "NO-GO")
    summary.update(verdict=saved["verdict"], negative_generator_counts=dict(sorted(Counter(n["generator"] for n in neg).items())),
                   negatives_max_lm=max(n["lm"] for n in neg), negatives_max_word=max(n["word"] for n in neg),
                   extras_ok=sum(e["ok"] for e in extra), witnesses=witnesses,
                   positive_plaintexts_unique=len(set(t["enciphered"] for t in truth.values() if t["class"] == "POS")),
                   confidence_rate_95pct_one_sided_upper=1 - 0.05 ** (1 / len(neg)))
    return summary


def published_constraints():
    tree = ast.parse((ROOT / "r73/sealed/reveal_k4.py").read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "CLUES" for t in node.targets):
            clues = ast.literal_eval(node.value)
            return [o + i for o, word in clues for i in range(len(word))], "".join(word for _, word in clues)
    raise RuntimeError("missing published constraints")


def review_k4():
    inputs = read_rows("r90/k4/TARGET.tsv")
    res = records("r90/k4/run/RESULTS.jsonl")
    witnesses = review_frozen_witnesses("r90/k4", inputs, res)
    assert len(inputs) == 201 and len(set(inputs.values())) == 201
    original = (ROOT / "r39/ic_gate/k4_ciphertext.txt").read_text().strip()
    assert inputs["K4"] == original and all(Counter(c) == Counter(original) for c in inputs.values())
    rng, seen, generated = random.Random(900400), {original}, {}
    while len(generated) < 200:
        chars = list(original)
        rng.shuffle(chars)
        value = "".join(chars)
        if value not in seen:
            seen.add(value)
            generated[f"NULL_{len(generated):03d}"] = value
    assert generated == {rid: ct for rid, ct in inputs.items() if rid != "K4"}
    pos, letters = published_constraints()
    hits = lambda text: sum(text[i] == ch for i, ch in zip(pos, letters))
    best = res["K4"]["best"]
    nulls = [record for rid, record in res.items() if rid != "K4"]
    reach = sum(record["best"]["lm_per_letter"] >= best["lm_per_letter"] for record in nulls)
    k4_all = res["K4"]["top"] + list(res["K4"]["best_by_arm"].values())
    evaluation = {"n_nulls": len(nulls), "nulls_at_or_above_k4": reach, "p_family": (1 + reach)/(1 + len(nulls)),
                  "k4_best_hits": hits(best["text"]), "k4_max_hits_any_frozen_decode": max(hits(e["text"]) for e in k4_all),
                  "contenders": sum(hits(e["text"]) >= 12 for e in k4_all),
                  "k4_best_lm": best["lm_per_letter"], "k4_best_word": best["word_per_letter"],
                  "shuffles_reproduced_from_seed": True, "witnesses": witnesses}
    saved = jread("r90/k4/EVALUATION.json")
    for key in ("n_nulls", "nulls_at_or_above_k4", "p_family", "k4_best_hits", "k4_max_hits_any_frozen_decode"):
        assert evaluation[key] == saved[key], key
    assert evaluation["contenders"] == len(saved["contenders"])
    confident = best["lm_per_letter"] >= -1.30 and best["word_per_letter"] >= -2.50 and reach == 0
    evaluation["outcome"] = ("SIGNAL" if hits(best["text"]) >= 10 else "SCORE_ANOMALY") if confident else "NO_SIGNAL"
    assert evaluation["outcome"] == saved["outcome"]
    exact_saved = jread("r90/k4/EXACT.json")
    exact = {}
    for rid, ct in inputs.items():
        values = counts_at_known_positions(ct, pos, letters)
        row = {"max_hits": int(values.max()), "n_at_max": int(np.count_nonzero(values == values.max())),
               "n_24": int(np.count_nonzero(values == 24)), "n_ge_23": int(np.count_nonzero(values >= 23)),
               "n_ge_22": int(np.count_nonzero(values >= 22))}
        expected = exact_saved["k4"] if rid == "K4" else exact_saved["shuffles"][rid]
        for key in ("max_hits", "n_ge_22"):
            assert row[key] == expected[key], (rid, key)
        if rid == "K4":
            assert row["n_24"] == expected["n_24"] and row["n_ge_23"] == expected["n_ge_23"]
        exact[rid] = row
    maximums = [e["max_hits"] for rid, e in exact.items() if rid != "K4"]
    assert sorted(maximums, reverse=True) == exact_saved["shuffle_max_hits"]
    return {"evaluation": evaluation, "exact": {"settings_per_input": len(STATES), "inputs": len(inputs),
            "k4": exact["K4"], "null_max": max(maximums),
            "nulls_at_least_k4": sum(n >= exact["K4"]["max_hits"] for n in maximums),
            "one_ciphertext_substitution_max_match_bound": exact["K4"]["max_hits"] + 2,
            "all_recorded_comparisons_equal": True, "per_input": exact}}


def review_hashes_history():
    manifests = ("r90/PROTOCOL.sha256", "r90/holdout/GATE_FROZEN.sha256", "r90/k4/FROZEN.sha256")
    checks, missing = [], []
    for manifest in manifests:
        for line in (ROOT / manifest).read_text().splitlines():
            if not line.strip():
                continue
            digest, path = line.split()[0], line.split()[-1]
            target = ROOT / path
            if not target.exists():
                missing.append({"manifest": manifest, "path": path})
                continue
            assert sha(target) == digest, (manifest, path)
            checks.append({"manifest": manifest, "path": path, "sha256": digest})
    paths = ("r90/PREREGISTRATION.md", "r90/holdout/BLIND.tsv", "r90/AMENDMENT_1.md",
             "r90/holdout/run/RESULTS.jsonl", "r90/holdout/TRUTH.json", "r90/k4/TARGET.tsv",
             "r90/k4/run/RESULTS.jsonl", "r90/k4/EVALUATION.json", "r90/k4/EXACT.json")
    commits = []
    for path in paths:
        output = subprocess.check_output(["git", "log", "--format=%H", "--diff-filter=A", BASE, "--", path], cwd=ROOT, text=True)
        sha1 = output.splitlines()[-1]
        commits.append({"path": path, "first_commit": sha1})
    for before, after in zip(commits, commits[1:]):
        assert before["first_commit"] != after["first_commit"]
        subprocess.run(["git", "merge-base", "--is-ancestor", before["first_commit"], after["first_commit"]], cwd=ROOT, check=True)
    manifest = jread("r90/QA_MANIFEST.json")
    assert manifest["preregistration_commit"] == commits[0]["first_commit"]
    assert manifest["preregistration_sha256"] == sha(ROOT / "r90/PREREGISTRATION.md")
    logs = {path: jread(path) for path in ("r90/holdout/launch1_aborted/RESOURCE_LOG.json", "r90/holdout/run/RESOURCE_LOG.json",
                                        "r90/k4/run/RESOURCE_LOG.json", "r90/k4/EXACT_RESOURCE_LOG.json")}
    for path, data in logs.items():
        assert data["status"] == ("INCOMPLETE" if "launch1_aborted" in path else "COMPLETE")
    return {"hashes_checked": len(checks), "verified_hashes": checks, "missing_manifest_paths": missing,
            "first_commit_sequence": commits, "commit_order_valid": True,
            "historical_push_timing_independently_proven": False,
            "resource_statuses": {p: {k: data.get(k) for k in ("status", "wall_seconds", "max_rss_mb", "cpu_seconds", "reason")}
                                  for p, data in logs.items()},
            "operational_retry_disclosure": "One aborted four-worker launch followed by a two-worker relaunch; Amendment 1 precedes frozen output. Original max_retries=0 was not literally satisfied."}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report = {"reviewer": "ChatGPT", "source_commit": BASE, "scope": "R90 independent exact exclusion and saved-evidence audit",
              "catalog": review_catalog(), "toy_controls": toy_controls(),
              "gate": review_gate(), "hashes_and_history": review_hashes_history()}
    report.update(review_k4())
    report["limitations"] = ["No fresh blind solver or unrecorded candidate was generated.",
        "Gate arithmetic and witnesses are independently checked; recorded model scores and complete top-256 membership were not recomputed from the untracked letter-model binary.",
        "Commit ordering is independently checked; historical push timing and absence of operator truth access are not proven by source history alone.",
        "The exact exclusion is independent of the language model and gate recovery rate."]
    (OUT / "REVIEW_RESULTS.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"catalog": report["catalog"], "toy_controls": report["toy_controls"], "gate": report["gate"],
                      "evaluation": report["evaluation"], "exact": {k: v for k,v in report["exact"].items() if k != "per_input"},
                      "hashes_checked": report["hashes_and_history"]["hashes_checked"],
                      "missing_paths": report["hashes_and_history"]["missing_manifest_paths"]}, indent=2))


if __name__ == "__main__":
    main()
