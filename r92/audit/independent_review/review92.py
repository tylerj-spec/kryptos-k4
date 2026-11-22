#!/usr/bin/env python3
"""Independent R92 aggregate audit; imports no original cipher or evaluator.

Synthetic mode reads no target files. Audit mode requires a published code/plan
commit and must be launched through audit/run_bounded_agg.py. It forward-checks
saved strings but emits no strings, assignments, completed keys or survivors.
"""
import argparse
import ast
from collections import Counter
import hashlib
from itertools import permutations, product
import json
import math
from pathlib import Path
import random
import re
import subprocess


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BASE = "9e4bd400e64c6aa46ae3afdc9ba0d82a1a927fd1"
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KEYWORDS = {"AZ": "", "KRY": "KRYPTOS", "PAL": "PALIMPSEST", "ABS": "ABSCISSA"}
ALPH = {name: "".join(dict.fromkeys(word + AZ)) for name, word in KEYWORDS.items()}
RXP = [(a, b, n, r, d) for a in ALPH for b in ALPH
       for n in (2, 3, 4) for r in range(1, n) for d in (-1, 1)]
RX0 = [(a, b, n, 0, d) for a in ALPH for b in ALPH
       for n in range(1, 5) for d in (-1, 1)]


def require(condition, explanation):
    if not condition:
        raise AssertionError(explanation)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git(*args, check=True):
    return subprocess.run(["git", *args], cwd=ROOT, check=check,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def source_bytes(relative):
    p = ROOT / relative
    return p.read_bytes() if p.is_file() else git("show", f"{BASE}:{relative}").stdout


def read_json(relative):
    return json.loads(source_bytes(relative))


def write_report(path, report):
    p = Path(path)
    require(not p.exists(), "refusing to overwrite an audit result")
    p.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")


def shift_sequence(length, n, r, d, q):
    """Independent advancing-counter implementation, not the floor formula."""
    counter, angle, shifts = r, 0, []
    for _ in range(length):
        shifts.append(angle)
        counter += 1
        if counter == n:
            counter = 0
            angle = (angle + d) % q
    return shifts


def encipher_numbers(plain, wiring, n, r, d):
    q = len(wiring)
    return tuple((wiring[(p + s) % q] - s) % q
                 for p, s in zip(plain, shift_sequence(len(plain), n, r, d, q)))


def encipher(text, wiring, setting):
    ein, eout, n, r, d = setting
    plain = [ALPH[ein].index(ch) for ch in text]
    return "".join(ALPH[eout][v] for v in encipher_numbers(plain, wiring, n, r, d))


def decipher(text, wiring, setting):
    ein, eout, n, r, d = setting
    inv = [wiring.index(i) for i in range(26)]
    cipher = [ALPH[eout].index(ch) for ch in text]
    return "".join(ALPH[ein][v] for v in encipher_numbers(cipher, inv, n, r, d))


def conflict_decisions(xs, ys):
    """Return (exact, allowed-deletion bits) without constructing any map/key.

    A deletion succeeds iff its vertex touches every contradictory pair.
    Intersection zero is final: later edges cannot restore a vertex.
    """
    require(len(xs) == len(ys), "coordinate lengths differ")
    candidates = (1 << len(xs)) - 1
    exact = True
    for i in range(len(xs)):
        for j in range(i):
            if (xs[i] == xs[j]) != (ys[i] == ys[j]):
                exact = False
                candidates &= (1 << i) | (1 << j)
                if not candidates:
                    return False, 0
    return exact, candidates


def coordinates(cipher, positions, letters, setting):
    ein, eout, n, r, d = setting
    xs, ys = [], []
    for i, p in zip(positions, letters):
        s = d * ((i + r) // n)
        xs.append((ALPH[ein].index(p) + s) % 26)
        ys.append((ALPH[eout].index(cipher[i]) + s) % 26)
    return xs, ys


def synthetic_checks():
    count = 0
    schedules = [(2, 1, 1), (3, 1, -1), (3, 2, 1), (4, 3, -1)]
    for q in (2, 3, 4):
        strings = list(product(range(q), repeat=4))
        wirings = list(permutations(range(q)))
        for n, r, d in schedules:
            shifts = [d * ((i + r) // n) for i in range(4)]
            for plain in strings:
                encrypted = {encipher_numbers(plain, w, n, r, d) for w in wirings}
                projected = [{c[:j] + c[j + 1:] for c in encrypted} for j in range(4)]
                xs = [(p + s) % q for p, s in zip(plain, shifts)]
                for cipher in strings:
                    ys = [(c + s) % q for c, s in zip(cipher, shifts)]
                    expected = (cipher in encrypted,
                                sum(1 << j for j in range(4)
                                    if cipher[:j] + cipher[j + 1:] in projected[j]))
                    require(conflict_decisions(xs, ys) == expected, "toy permutation oracle disagreement")
                    count += 1
    require(count == 289412, "toy-case count drift")
    rng = random.Random(921105)
    plants = pt_errors = ct_errors = embeddings = 0
    for setting in RXP + RX0:
        plain = "".join(rng.choice(AZ) for _ in range(97))
        wiring = list(range(26))
        rng.shuffle(wiring)
        cipher = encipher(plain, wiring, setting)
        require(decipher(cipher, wiring, setting) == plain, "planted inverse failure")
        positions = sorted([0, 96] + rng.sample(range(1, 96), 22))
        letters = [plain[i] for i in positions]
        require(conflict_decisions(*coordinates(cipher, positions, letters, setting))[0], "planted conflict")
        for j in range(97):
            altered_plain = plain[:j] + AZ[(AZ.index(plain[j]) + 1) % 26] + plain[j + 1:]
            from_pt_error = encipher(altered_plain, wiring, setting)
            require(sum(a != b for a, b in zip(cipher, from_pt_error)) == 1,
                    "plaintext substitution has nonlocal propagation")
            altered_cipher = cipher[:j] + AZ[(AZ.index(cipher[j]) + 1) % 26] + cipher[j + 1:]
            require(sum(a != b for a, b in zip(plain, decipher(altered_cipher, wiring, setting))) == 1,
                    "ciphertext substitution has nonlocal propagation")
            for changed in (from_pt_error, altered_cipher):
                exact, drops = conflict_decisions(*coordinates(changed, positions, letters, setting))
                if j in positions:
                    require(bool(drops & (1 << positions.index(j))), "correct one-error deletion rejected")
                else:
                    require(exact, "unobserved substitution changes feasibility")
            pt_errors += 1
            ct_errors += 1
        ein, eout, n, r, d = setting
        for h, d2 in ((0, -1), (0, 1), (25, -1), (25, 1)):
            for i, p in enumerate(plain):
                t = (i + r) // n
                s1, s2 = d * t, d2 * ((t + h) // 26)
                middle = (wiring[(ALPH[ein].index(p) + s1) % 26] - s1) % 26
                output = ((middle + s2) % 26 - s2) % 26  # identity second wiring
                require(ALPH[eout][output] == cipher[i], "RX2 identity embedding failed")
            embeddings += 1
        translation = [(i + 7) % 26 for i in range(26)]
        require(encipher(plain, translation, setting) ==
                encipher(plain, translation, (ein, eout, 4, 0, -1)), "translation overlap failed")
        plants += 1
    require(len(RXP) == len(set(RXP)) == 192 and len(RX0) == 128, "scope count drift")
    return {"status": "PASS", "mode": "SYNTHETIC_ONLY", "seed": 921105,
            "toy_cases": count, "toy_sizes": [2, 3, 4], "toy_schedules": schedules,
            "plants_and_inverse_checks": plants, "plaintext_substitution_checks": pt_errors,
            "ciphertext_substitution_checks": ct_errors, "identity_second_rotor_embeddings": embeddings,
            "translation_overlap_examples": plants, "rxp_labels": len(RXP), "rx0_subset_labels": len(RX0),
            "remaining_n5_to_96_nonzero_labels": 32 * sum(n - 1 for n in range(5, 97)),
            "reads_original_implementation": False, "reads_k4_or_its_mask": False,
            "checker_sha256": digest(Path(__file__).read_bytes())}


def table(relative):
    lines = source_bytes(relative).decode().splitlines()
    require(lines[0] == "id\tciphertext", "wrong input header")
    pairs = [line.split("\t") for line in lines[1:] if line]
    require(all(len(p) == 2 for p in pairs), "bad input columns")
    result = dict(pairs)
    require(len(result) == len(pairs), "duplicate input ID")
    require(all(len(c) == 97 and set(c) <= set(AZ) for c in result.values()), "bad ciphertext alphabet/length")
    return result


def witness_audit(stage, inputs):
    relative = f"r92/{stage}/run/RESULTS.jsonl"
    rows = [json.loads(line) for line in source_bytes(relative).splitlines() if line]
    data = {row["id"]: row for row in rows}
    require(len(rows) == len(data) and set(data) == set(inputs), "candidate IDs differ")
    witnessed = 0
    for rid, row in data.items():
        require(row["n_settings"] == 192, "saved structural count differs")
        top = row["top"]
        require(len(top) == 5 and row["best"] == top[0], "best/top record inconsistent")
        scores = [x["lm_per_letter"] for x in top]
        require(all(math.isfinite(s) for s in scores) and scores == sorted(scores, reverse=True), "invalid saved ranking")
        for candidate in top:
            st = candidate["setting"]
            setting = tuple(st[k] for k in ("ein", "eout", "n", "r", "d"))
            w = st["wiring"]
            text = candidate["text"]
            require(setting in RXP and sorted(w) == list(range(26)), "candidate key outside scope")
            require(len(text) == 97 and set(text) <= set(AZ), "candidate text invalid")
            require(encipher(text, w, setting) == inputs[rid], "saved forward witness failed")
            require(math.isfinite(candidate["word_per_letter"]), "nonfinite saved word score")
            witnessed += 1
    old = read_json(f"r92/{stage}/run/WITNESS.json")
    require(old["passed"] and old["witnesses"] == witnessed, "archived witness disagrees")
    return data, {"inputs": len(data), "forward_witnesses": witnessed, "all_passed": True}


def gate_audit(inputs, results):
    truth = read_json("r92/holdout/TRUTH.json")
    require(set(truth) == set(inputs), "truth IDs differ")
    commitment = source_bytes("r92/holdout/TRUTH_SHA256").decode().split()[0]
    require(digest(source_bytes("r92/holdout/TRUTH.json")) == commitment, "truth commitment mismatch")
    expected_classes = {"POS": 48, "NEG": 150, "EXTRA": 4}
    require(dict(Counter(t["class"] for t in truth.values())) == expected_classes, "control class counts differ")
    positives, negatives, extras = [], [], []
    truth_witnesses = 0
    for rid, t in truth.items():
        require(t["ct"] == inputs[rid], "truth/input ciphertext mismatch")
        best = results[rid]["best"]
        conf = best["lm_per_letter"] >= -1.30 and best["word_per_letter"] >= -2.50
        if t["class"] == "NEG":
            negatives.append({"id": rid, "generator": t["generator"], "confident": conf,
                              "lm": round(best["lm_per_letter"], 4), "word": round(best["word_per_letter"], 4)})
            continue
        true = t["setting"]
        setting = tuple(true[k] for k in ("ein", "eout", "n", "r", "d"))
        require(setting in RXP and sorted(true["wiring"]) == list(range(26)), "planted key outside scope")
        encoded = t["enciphered"]
        encrypted = encipher(encoded, true["wiring"], setting)
        if t.get("kind") == "CTERR":
            require(encrypted == t["ct_clean"] and encoded == t["pt"], "CTERR clean witness failed")
            changed = [i for i, (a, b) in enumerate(zip(encrypted, t["ct"])) if a != b]
            require(changed == [t["error_at"]], "CTERR not one stated substitution")
        else:
            require(encrypted == t["ct"], "positive/extra truth witness failed")
            if t.get("kind") == "PTERR":
                require(sum(a != b for a, b in zip(encoded, t["pt"])) == 1, "PTERR not one substitution")
            else:
                wanted = t["pt"].translate(str.maketrans("CW", "KV")) if t["masked"] else t["pt"]
                require(encoded == wanted, "masked truth differs from declared transform")
        truth_witnesses += 1
        correct = sum(a == b for a, b in zip(best["text"], encoded))
        fields_match = all(best["setting"][k] == true[k] for k in ("ein", "eout", "n", "r", "d"))
        shifts = shift_sequence(97, true["n"], true["r"], true["d"], 26)
        used = {(ALPH[true["ein"]].index(p) + s) % 26 for p, s in zip(encoded, shifts)}
        used_match = fields_match and all(best["setting"]["wiring"][u] == true["wiring"][u] for u in used)
        row = {"id": rid, "letters": correct, "ok": correct >= 95 and conf,
               "exact": correct == 97 and conf, "setting_right": fields_match,
               "key_on_used_contacts": used_match, "lm": round(best["lm_per_letter"], 4),
               "genre": t["genre"], "confident": conf}
        if t["class"] == "POS":
            row.update(cell=t["cell"], masked=t["masked"])
            positives.append(row)
        else:
            row["kind"] = t["kind"]
            extras.append(row)
    expected_cells = [f"n{n}r{r}" for n in (2, 3, 4) for r in range(1, n)]
    require(Counter(r["cell"] for r in positives) == Counter({c: 8 for c in expected_cells}), "cell allocation differs")
    require(Counter(r["genre"] for r in positives) == Counter({g: 16 for g in ("G1", "G2", "G3")}), "genre allocation differs")
    require(all(sum(p["masked"] for p in positives if p["cell"] == c) == 2 for c in expected_cells), "mask allocation differs")
    generators = Counter(r["generator"] for r in negatives)
    require(len(generators) == 10 and set(generators.values()) == {15}, "negative allocation differs")

    def count(key, val):
        group = [p for p in positives if p[key] == val]
        return [sum(p["ok"] for p in group), len(group)]

    summary = {"positives_ok": sum(p["ok"] for p in positives), "positives": len(positives),
               "positives_exact": sum(p["exact"] for p in positives),
               "by_cell_ok": {c: count("cell", c) for c in expected_cells},
               "by_genre_ok": {g: count("genre", g) for g in ("G1", "G2", "G3")},
               "masked_ok": count("masked", True), "setting_right": sum(p["setting_right"] for p in positives),
               "key_on_used_contacts": sum(p["key_on_used_contacts"] for p in positives),
               "recovered_min_lm": min(p["lm"] for p in positives if p["ok"]),
               "negatives_confident": sum(p["confident"] for p in negatives), "negatives": len(negatives),
               "negatives_max_lm": max(p["lm"] for p in negatives),
               "negatives_max_word": max(p["word"] for p in negatives),
               "negatives_by_generator_max_lm": {g: max(p["lm"] for p in negatives if p["generator"] == g) for g in generators},
               "extras": [{k: p[k] for k in ("id", "kind", "letters", "ok")} for p in extras]}
    passed = (summary["positives_ok"] >= 42 and summary["positives_exact"] >= 36
              and all(v[0] >= 6 for v in summary["by_cell_ok"].values())
              and all(v[0] >= 13 for v in summary["by_genre_ok"].values())
              and summary["masked_ok"][0] >= 8 and summary["negatives_confident"] <= 1)
    archived = read_json("r92/holdout/GATE.json")
    require(summary == archived["summary"], "saved gate summary disagrees")
    require(archived["verdict"] == ("GO" if passed else "NO-GO"), "gate decision disagrees")
    return {"verdict": archived["verdict"], "summary": summary, "truth_forward_checks": truth_witnesses,
            "negative_generators": dict(generators), "truth_commitment_verified": True,
            "positive_plaintexts_unique": len({t["enciphered"] for t in truth.values() if t["class"] == "POS"}),
            "saved_score_arithmetic_only": True, "original_optimizer_or_lm_rerun": False}


def observations():
    tree = ast.parse(source_bytes("r73/sealed/reveal_k4.py"))
    clues = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "CLUES" for t in node.targets):
            clues = ast.literal_eval(node.value)
    require(clues is not None, "published observation declaration missing")
    pairs = [(offset + j, c) for offset, word in clues for j, c in enumerate(word)]
    require(len(pairs) == 24 and len({i for i, _ in pairs}) == 24, "observation count differs")
    return [i for i, _ in pairs], [c for _, c in pairs]


def exact_audit(inputs, positions, letters):
    archive = read_json("r92/k4/EXACT.json")
    groups = {}
    for label, settings in (("R92_RXP", RXP), ("R87_ZERO_PHASE_N1_TO_4", RX0)):
        per_input = {}
        for rid, cipher in inputs.items():
            exact_count, exact_max, any_drop = 0, -1, 0
            drop_counts, drop_maxima = [0] * 24, [-1] * 24
            for setting in settings:
                xs, ys = coordinates(cipher, positions, letters, setting)
                exact, mask = conflict_decisions(xs, ys)
                if exact:
                    exact_count += 1
                    exact_max = max(exact_max, 24 - len(set(xs)))
                any_drop += bool(mask)
                for j in range(24):
                    if mask & (1 << j):
                        drop_counts[j] += 1
                        drop_maxima[j] = max(drop_maxima[j], 23 - len(set(xs[:j] + xs[j + 1:])))
            result = {"exact_feasible_labels": exact_count, "exact_max_checks": exact_max,
                      "drop_feasible_setting_deletion_pairs": sum(drop_counts),
                      "labels_admitting_any_deletion": any_drop,
                      "drop_counts_in_published_position_order": drop_counts,
                      "drop_max_checks_by_position": drop_maxima}
            per_input[rid] = result
            if label == "R92_RXP":
                olde, oldd = archive["exact"][rid], archive["drop"][rid]
                require((exact_count, exact_max) == (olde["feasible"], olde["max_checks"]), "R92 exact aggregate mismatch")
                require((sum(drop_counts), max(drop_maxima)) == (oldd["feasible"], oldd["max_checks"]), "R92 drop aggregate mismatch")
                for old in oldd["by_dropped_position"]:
                    j = positions.index(old["dropped_position"])
                    require((drop_counts[j], drop_maxima[j]) == (old["feasible"], old["max_checks"]), "R92 retained per-deletion mismatch")
        groups[label] = {"settings": len(settings), "inputs": len(inputs),
                         "base_decisions": len(settings) * len(inputs),
                         "single_deletion_decisions": 24 * len(settings) * len(inputs),
                         "per_input": per_input}
    r92 = groups["R92_RXP"]["per_input"]
    k = r92["K4"]
    if k["exact_feasible_labels"] == 0:
        require(archive["verdict_exact"] == "EXCLUDED", "R92 exact verdict mismatch")
    if k["drop_feasible_setting_deletion_pairs"] == 0:
        require(archive["verdict_drop"] == "EXCLUDED", "R92 drop verdict mismatch")
    require(archive["shuffles_with_feasible_exact"] == sum(v["exact_feasible_labels"] > 0 for rid, v in r92.items() if rid != "K4"), "R92 null exact count differs")
    require(archive["shuffles_with_feasible_drop"] == sum(v["drop_feasible_setting_deletion_pairs"] > 0 for rid, v in r92.items() if rid != "K4"), "R92 null drop count differs")
    cross = read_json("r92/k4/EXACT_CROSSCHECK.json")
    require(cross["k4_exact_feasible"] == k["exact_feasible_labels"] and
            cross["k4_drop_feasible_by_position"] == k["drop_counts_in_published_position_order"], "R92 archived crosscheck differs")
    original = read_json("r87/k4/EXACT.json")
    subset = groups["R87_ZERO_PHASE_N1_TO_4"]["per_input"]["K4"]
    if original["exact"]["K4"]["feasible"] == 0:
        require(subset["exact_feasible_labels"] == 0, "R87 subset contradicts archived zero aggregate")
    if original["drop"]["K4"]["feasible"] == 0:
        require(subset["drop_feasible_setting_deletion_pairs"] == 0, "R87 subset contradicts archived drop zero")
    return {"groups": groups, "positions": 24, "logical_decisions": 320 * 201 * 25,
            "all_R92_retained_exact_aggregates_agree": True,
            "R87_comparison_scope": "K4 n<=4 zero-phase subset only; no old null or full n<=96 replay"}


def evaluation_audit(inputs, results, positions, letters):
    def hits(text):
        return sum(text[i] == c for i, c in zip(positions, letters))
    best = results["K4"]["best"]
    null_ids = [i for i in inputs if i != "K4"]
    scores = sorted(results[i]["best"]["lm_per_letter"] for i in null_ids)
    above = sum(v >= best["lm_per_letter"] for v in scores)
    clears = best["lm_per_letter"] >= -1.30 and best["word_per_letter"] >= -2.50
    confident = clears and best["lm_per_letter"] > scores[-1]
    hit = hits(best["text"])
    outcome = ("SIGNAL" if hit >= 10 else "SCORE_ANOMALY") if confident else "NO_SIGNAL"
    k4_max = max(hits(c["text"]) for c in results["K4"]["top"])
    null_hits = [max(hits(c["text"]) for c in results[i]["top"]) for i in null_ids]
    out = {"outcome": outcome, "k4_best_hits": hit, "k4_best_clears_cuts": clears,
           "n_nulls": len(null_ids), "null_best_lm_max": scores[-1],
           "null_best_lm_median": scores[len(scores) // 2], "nulls_at_or_above_k4": above,
           "p_family": (1 + above) / (1 + len(null_ids)),
           "nulls_clearing_both_cuts": sum(results[i]["best"]["lm_per_letter"] >= -1.30 and
                                            results[i]["best"]["word_per_letter"] >= -2.50 for i in null_ids),
           "k4_max_hits_any_frozen_decode": k4_max, "null_max_hits_any_frozen_decode": max(null_hits),
           "nulls_reaching_k4_max_hits": sum(v >= k4_max for v in null_hits), "witnesses_checked": 1005}
    archived = read_json("r92/k4/EVALUATION.json")
    require(all(archived[k] == v for k, v in out.items()), "saved evaluation arithmetic differs")
    contenders = sum(hits(c["text"]) >= 12 for c in results["K4"]["top"])
    require(contenders == len(archived["contenders"]), "saved contender count differs")
    out.update(contenders=contenders, k4_best_lm=best["lm_per_letter"], k4_best_word=best["word_per_letter"],
               score_scope="saved pruned-pipeline maximum; not exhaustive LM optimum",
               full_original_optimizer_rerun=False, lm_rescoring_rerun=False)
    return out


def verify_hashes_and_history():
    verified, model_refs = [], []
    standard = ["r92/PROTOCOL.sha256", "r92/holdout/GATE_FROZEN.sha256", "r92/k4/FROZEN.sha256"]
    for manifest in standard:
        for line in source_bytes(manifest).decode().splitlines():
            if line.strip():
                h, relative = line.split()[0], line.split()[-1]
                data = source_bytes(relative)
                require(digest(data) == h, "frozen hash mismatch: " + relative)
                require(digest(git("show", f"{BASE}:{relative}").stdout) == h, "baseline hash mismatch: " + relative)
                verified.append({"manifest": manifest, "path": relative, "sha256": h})
    shared = {"runner": "r92/blind/run92.py", "solver": "r92/blind/solve92.py", "kernel": "r87/blind/anneal.c",
              "family": "r92/rotor92.py", "scorer": "r75/core.py", "quadgrams": "k4kit/data/quad_log10.f32",
              "word_model": "k4kit/data/word_model_orth.tsv"}
    lm_hash = source_bytes("r59/blind/LM_SHA256").decode().split()[0]
    for stage, input_name in (("holdout", "BLIND.tsv"), ("k4", "TARGET.tsv")):
        manifest = f"r92/{stage}/run/RUNNER_FROZEN.sha256"
        mapping = {**shared, "input": f"r92/{stage}/{input_name}", "results": f"r92/{stage}/run/RESULTS.jsonl"}
        for line in source_bytes(manifest).decode().splitlines():
            if not line.strip():
                continue
            h, label = line.split()[:2]
            if label == "letter_model":
                require(h == lm_hash, "runner model commitment differs")
                model_refs.append({"manifest": manifest, "sha256": h, "actual_binary_rehashed": False})
            else:
                relative = mapping[label]
                require(digest(source_bytes(relative)) == h, "runner hash mismatch: " + label)
                verified.append({"manifest": manifest, "path": relative, "sha256": h})
        sandbox = read_json(f"r92/{stage}/run/SANDBOX.json")
        require(len(sandbox["files"]) == 8 and sandbox["letter_model_sha256"] == lm_hash, "sandbox allowlist/model differs")
        require(sandbox["input"]["sha256"] == digest(source_bytes(mapping["input"])), "sandbox input mismatch")
        for relative, h in sandbox["files"].items():
            require(digest(source_bytes(relative)) == h, "sandbox copied-file hash mismatch")
    qa = read_json("r92/QA_MANIFEST.json")
    require(digest(source_bytes(qa["preregistration_path"])) == qa["preregistration_sha256"], "QA preregistration hash differs")
    paths = ["r92/PREREGISTRATION.md", "r92/holdout/BLIND.tsv", "r92/holdout/GATE_FROZEN.sha256",
             "r92/holdout/GATE.json", "r92/k4/TARGET.tsv", "r92/k4/FROZEN.sha256",
             "r92/k4/EVALUATION.json", "r92/k4/EXACT.json", "r92/k4/EXACT_CROSSCHECK.json"]
    first = {}
    for path in paths:
        commits = git("log", "--reverse", "--format=%H", "--diff-filter=A", BASE, "--", path).stdout.decode().split()
        require(bool(commits), "missing artifact introduction commit")
        first[path] = commits[0]
    require(first[paths[0]] == qa["preregistration_commit"], "QA prerequisite commit differs")
    for a, b in zip(paths, paths[1:]):
        # The blinded stages must be separate commits. The two archived exact
        # implementations published their results together; that is reported,
        # not invented as a separate publication boundary.
        same_allowed = b == "r92/k4/EXACT_CROSSCHECK.json"
        require((same_allowed or first[a] != first[b]) and
                git("merge-base", "--is-ancestor", first[a], first[b], check=False).returncode == 0,
                "stage commit ordering failure")
    freeze_gate, freeze_target = first[paths[2]], first[paths[5]]
    require(git("cat-file", "-e", freeze_gate + ":r92/holdout/TRUTH.json", check=False).returncode != 0,
            "truth already present at gate freeze")
    require(git("cat-file", "-e", freeze_target + ":r92/k4/EVALUATION.json", check=False).returncode != 0,
            "evaluation already present at target freeze")
    for commit, manifest in ((freeze_gate, standard[1]), (freeze_target, standard[2])):
        for line in source_bytes(manifest).decode().splitlines():
            if line.strip():
                h, relative = line.split()[0], line.split()[-1]
                require(digest(git("show", f"{commit}:{relative}").stdout) == h, "file not frozen at stated historical commit")
    resources = {}
    for stage in ("holdout/run", "k4/run"):
        log = read_json(f"r92/{stage}/RESOURCE_LOG.json")
        bounds = qa["resource_budget"]
        require(log["status"] == "COMPLETE" and log["wall_seconds"] <= bounds["max_wall_seconds"]
                and log["cpu_seconds"] <= bounds["max_cpu_seconds"]
                and log["aggregate_peak_rss_mb"] <= bounds["max_ram_mb"], "recorded formal resource overrun")
        resources[stage] = {k: log[k] for k in ("status", "wall_seconds", "cpu_seconds", "aggregate_peak_rss_mb", "budget")}
    exact_log = read_json("r92/k4/EXACT_RESOURCE_LOG.json")
    require(exact_log["status"] == "COMPLETE", "original exact job incomplete")
    resources["k4/exact"] = {k: exact_log[k] for k in ("status", "wall_seconds", "cpu_seconds", "aggregate_peak_rss_mb", "budget")}
    return {"hash_entries_verified": len(verified), "verified_entries": verified,
            "untracked_model_commitments": model_refs, "introduction_commits": first,
            "commit_order_valid": True,
            "exact_and_original_crosscheck_published_together": first[paths[-2]] == first[paths[-1]],
            "historical_push_or_first_read_timing_proven": False,
            "truth_absent_at_gate_freeze": True, "evaluation_absent_at_target_freeze": True,
            "resources": resources, "isolation_reexecuted": False,
            "sampling_caveat": "summed resident pages can double-count shared maps and miss sub-interval peaks"}


def audit(publication):
    require(publication and re.fullmatch(r"[0-9a-f]{40}", publication), "published audit commit required")
    for filename in ("PLAN.md", "BUDGET.json", "SYNTHETIC_BUDGET.json", "review92.py", "SYNTHETIC.json"):
        relative = str((HERE / filename).relative_to(ROOT))
        require(git("show", f"{publication}:{relative}").stdout == (HERE / filename).read_bytes(),
                "audit input not present unchanged at published commit: " + filename)
    synthetic = json.loads((HERE / "SYNTHETIC.json").read_text())
    require(synthetic["status"] == "PASS" and synthetic["checker_sha256"] == digest(Path(__file__).read_bytes()),
            "synthetic evidence does not certify this checker")
    integrity = verify_hashes_and_history()
    holdout = table("r92/holdout/BLIND.tsv")
    gate_results, gate_witnesses = witness_audit("holdout", holdout)
    gate = gate_audit(holdout, gate_results)
    targets = table("r92/k4/TARGET.tsv")
    require(len(targets) == 201 and "K4" in targets, "target count differs")
    canonical = source_bytes("r39/ic_gate/k4_ciphertext.txt")
    require(digest(canonical) == "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
            and canonical.decode().strip() == targets["K4"], "canonical ciphertext mismatch")
    rng = random.Random(920400)
    rows = ["id\tciphertext", "K4\t" + targets["K4"]]
    seen = {targets["K4"]}
    while len(rows) < 202:
        chars = list(targets["K4"])
        rng.shuffle(chars)
        value = "".join(chars)
        if value not in seen:
            seen.add(value)
            rows.append(f"NULL_{len(rows)-2:03d}\t{value}")
    require(("\n".join(rows) + "\n").encode() == source_bytes("r92/k4/TARGET.tsv"), "frozen shuffle sequence differs")
    target_results, target_witnesses = witness_audit("k4", targets)
    positions, letters = observations()
    evaluation = evaluation_audit(targets, target_results, positions, letters)
    exact = exact_audit(targets, positions, letters)
    return {"status": "PASS", "reviewer": "ChatGPT", "original_builder": "Claude Code",
            "baseline_commit": BASE, "audit_publication_commit": publication,
            "mode": "POSTFREEZE_CRIB_ASSISTED_AGGREGATE_AUDIT", "gate": gate,
            "gate_witnesses": gate_witnesses, "target_witnesses": target_witnesses,
            "evaluation": evaluation, "exact": exact, "integrity": integrity,
            "shuffles_reproduced_byte_for_byte": True, "synthetic": synthetic,
            "checker_sha256": digest(Path(__file__).read_bytes()),
            "limitations": ["No original blind optimizer or LM rescoring rerun.",
                            "Raw book freshness, nonoverlap and unavailable model binary not certified.",
                            "Development budget deviation remains; no retroactive compliance certification.",
                            "R87 review restricted to zero phase n<=4 on current frozen R92 inputs.",
                            "No blind candidate generation, unknown key completion or survivor disclosure."]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("synthetic", "audit"))
    parser.add_argument("--out", required=True)
    parser.add_argument("--publication-commit")
    args = parser.parse_args()
    result = synthetic_checks() if args.mode == "synthetic" else audit(args.publication_commit)
    write_report(args.out, result)
    print(json.dumps({"status": result["status"], "mode": args.mode,
                      "output": str(Path(args.out).relative_to(ROOT)) if Path(args.out).is_absolute() else args.out}))


if __name__ == "__main__":
    main()
