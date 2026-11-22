#!/usr/bin/env python3
"""Separate, post-freeze R91 result audit; imports neither gate nor solver.

Run only after the output freeze has been published and truth released. This
checks saved outputs, not original optimization or unknown-method power.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import subprocess

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
ALPH = {"AZ": AZ, "KRY": KRY}


def load_rows(path):
    rows = [json.loads(s) for s in path.read_text().splitlines() if s]
    ans = {r["id"]: r for r in rows}
    assert len(ans) == len(rows)
    return ans


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hash_manifest(root, path):
    count = 0
    for line in path.read_text().splitlines():
        expected, name = line.split(maxsplit=1)
        assert digest(root / name) == expected, name
        count += 1
    return count


def linked_at(symbol, key, width, position):
    m = len(key)
    first = ord(key[position % m]) - 65
    second = ord(key[(position + position // width) % m]) - 65
    middle = ord(KRY[(symbol + first) % 26]) - 65
    return (middle + second) % 26


def linked_forward(text, key, width):
    return "".join(AZ[linked_at(ord(p) - 65, key, width, i)] for i, p in enumerate(text))


def linked_equivalent(a, b, width):
    assert len(a) == len(b)
    return all(linked_at(x, a, width, i) == linked_at(x, b, width, i)
               for i in range(len(a) * width) for x in range(26))


def ptak_forward(text, key, row):
    pa, ca, op = row["convention"]
    permutation = row["permutation"]
    inverse = [permutation.index(i) for i in range(97)]
    # Derive path-order coordinates independently by explicit inverse indices.
    path = text if row["model"] == "M1" else "".join(text[inverse[i]] for i in range(97))
    x = [ALPH[pa].index(c) for c in path]
    stream = [ord(c) - 65 for c in key] + x[:97-len(key)]
    signs = {"VIG": (1, 1), "BEAU": (-1, 1), "VARB": (1, -1)}
    a, b = signs[op]
    y = [ALPH[ca][(a*p + b*k) % 26] for p, k in zip(x, stream)]
    return "".join(y[i] for i in permutation)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("out", type=Path)
    args = ap.parse_args()
    root = args.root.resolve()
    rnd = root / "r91"
    result = json.loads((rnd / "RESULT.json").read_text())
    frozen_commit = result["freeze_commit"]
    committed = subprocess.check_output(["git", "show", f"{frozen_commit}:r91/holdout/FROZEN.sha256"], cwd=root)
    assert committed == (rnd / "holdout/FROZEN.sha256").read_bytes()
    for revealed in ("r91/holdout/TRUTH.json", "r91/RESULT.json"):
        assert subprocess.run(["git", "cat-file", "-e", f"{frozen_commit}:{revealed}"], cwd=root,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0
    entries = [line.split(maxsplit=1) for line in committed.decode().splitlines()]
    covered = {name for _, name in entries}
    assert len(covered) == len(entries)
    required = {"r91/PROTOCOL.sha256", "r91/QA_MANIFEST.json", "r91/R59_LOWER4_FROM_K5.bin",
                "r91/holdout/R82_INPUT.jsonl", "r91/holdout/PTAK_INPUT.jsonl", "r91/holdout/TRUTH_SHA256",
                "r91/holdout/run/R82_OUTPUT.jsonl", "r91/holdout/run/PTAK_OUTPUT.jsonl",
                "r91/holdout/run/R82_RESOURCE_LOG.json", "r91/holdout/run/PTAK_RESOURCE_LOG.json",
                "r91/holdout/run/PTAK_INPUT.tsv", "r91/holdout/run/BUILD_RECEIPT.json",
                "r91/holdout/run/EXECUTION_RECEIPT.json", "r91/holdout/run/WITNESSES.json"}
    required.update(line.split(maxsplit=1)[1] for line in (rnd / "PROTOCOL.sha256").read_text().splitlines())
    assert required <= covered
    for expected, name in entries:
        at_freeze = subprocess.check_output(["git", "show", f"{frozen_commit}:{name}"], cwd=root)
        assert hashlib.sha256(at_freeze).hexdigest() == expected, name
    counts = {"protocol": hash_manifest(root, rnd / "PROTOCOL.sha256"),
              "freeze": hash_manifest(root, rnd / "holdout/FROZEN.sha256"),
              "inputs": hash_manifest(root, rnd / "holdout/INPUTS.sha256")}
    truth_path = rnd / "holdout/TRUTH.json"
    assert digest(truth_path) == (rnd / "holdout/TRUTH_SHA256").read_text().strip()
    truth = json.loads(truth_path.read_text())
    public = load_rows(rnd / "holdout/R82_INPUT.jsonl")
    public.update(load_rows(rnd / "holdout/PTAK_INPUT.jsonl"))
    saved = load_rows(rnd / "holdout/run/R82_OUTPUT.jsonl")
    for rid, row in load_rows(rnd / "holdout/run/PTAK_OUTPUT.jsonl").items():
        short = rid.split("__")[0]
        assert short not in saved
        saved[short] = row["best"]
        p = public[short]
        assert rid == f"{short}__{p['path_index']}__{p['model']}"
        assert row["best"]["family"] == "PTAK" and int(row["best"]["param"]) == p["lag"]
        assert row["best"]["convention"] == f"{p['convention'][0]}/{p['convention'][1]}_{p['convention'][2]}"
    assert set(public) == set(saved) == set(truth) and len(truth) == 600
    assert len({t["plaintext"] for t in truth.values()}) == 600
    windows = defaultdict(list)
    strata = defaultdict(dict)
    genre_counts = defaultdict(Counter)
    witnesses = 0
    equivalent_not_identical = 0
    for rid, row in public.items():
        t, s = truth[rid], saved[rid]
        assert row["arm"] == t["arm"]
        assert len(t["plaintext"]) == len(s["plaintext"]) == 97
        assert set(t["plaintext"] + s["plaintext"] + t["key"] + s["key"]) <= set(AZ)
        key_length = len(t["key"])
        assert key_length > 0 and all(t["key"] != t["key"][:d] * (key_length // d)
                                      for d in range(1, key_length) if key_length % d == 0)
        if row["arm"] == "R82_LINKED":
            assert (row["m"], row["w"]) == (t["m"], t["w"])
            assert len(s["key"]) == len(t["key"]) == row["m"]
            label = f"m{row['m']}_w{row['w']}"
            forward = lambda pt, key: linked_forward(pt, key, row["w"])
            key_ok = linked_equivalent(t["key"], s["key"], row["w"])
        else:
            for field in ("lag", "convention", "path", "model"):
                assert row[field] == t[field]
            assert sorted(row["permutation"]) == list(range(97))
            assert len(s["key"]) == len(t["key"]) == row["lag"]
            label = f"L{row['lag']}"
            forward = lambda pt, key: ptak_forward(pt, key, row)
            key_ok = t["key"] == s["key"]
        assert label == t["stratum"]
        assert forward(t["plaintext"], t["key"]) == row["ciphertext"]
        assert forward(s["plaintext"], s["key"]) == row["ciphertext"]
        witnesses += 1
        right = sum(a == b for a, b in zip(t["plaintext"], s["plaintext"]))
        raw_key = t["key"] == s["key"]
        equivalent_not_identical += int(key_ok and not raw_key)
        c = strata[row["arm"]].setdefault(label, dict.fromkeys(
            ("n", "exact_message_key", "plain97", "plain95", "key_exact", "key_equivalent"), 0))
        for field, increment in (("n", 1), ("exact_message_key", right == 97 and key_ok),
                                 ("plain97", right == 97), ("plain95", right >= 95),
                                 ("key_exact", raw_key), ("key_equivalent", key_ok)):
            c[field] += int(increment)
        genre_counts[row["arm"]][t["genre"]] += 1
        windows[t["source_file"]].append(t["offset"])
    expected_l = {f"m{m}_w{w}" for m in (3, 4, 5, 7, 9, 12) for w in (m, m+2, 31)}
    expected_p = {f"L{lag}" for lag in range(13, 25)}
    assert set(strata["R82_LINKED"]) == expected_l and set(strata["PTAK_R68"]) == expected_p
    assert all(c["n"] == 20 for arm in strata.values() for c in arm.values())
    assert dict(strata) == result["strata"]
    assert len(windows) == 3 and all(len(offsets) == 200 for offsets in windows.values())
    for offsets in windows.values():
        ordered = sorted(offsets)
        assert all(b-a >= 97 for a, b in zip(ordered, ordered[1:]))
    decisions = {}
    for arm, cells in strata.items():
        failures = sorted(label for label, cell in cells.items() if cell["exact_message_key"] < 18)
        outcome = "SOLVER_NO_POWER" if failures else "SCREEN_PASS_ONLY"
        assert result["decisions"][arm]["outcome"] == outcome
        assert sorted(result["decisions"][arm]["failed_strata"]) == failures
        assert not result["decisions"][arm]["k4_run_allowed"]
        decisions[arm] = {"outcome": outcome, "passing_strata": len(cells)-len(failures),
                          "strata": len(cells), "exact_message_key": sum(c["exact_message_key"] for c in cells.values()),
                          "messages": sum(c["n"] for c in cells.values())}
    for filename in ("R82_RESOURCE_LOG.json", "PTAK_RESOURCE_LOG.json"):
        r = json.loads((rnd / "holdout/run" / filename).read_text())
        assert r["status"] == "COMPLETE" and r["exit_code"] == 0
        assert r["wall_seconds"] <= 1800 and r["cpu_seconds"] <= 1800 and r["max_rss_mb"] <= 2048
    audit = {"status": "PASS", "kind": "Separate same-model post-freeze aggregate and forward audit",
             "imports_gate_or_solver": False, "decisions": decisions, "strata": dict(strata),
             "candidate_forward_witnesses": witnesses, "truth_forward_witnesses": witnesses,
             "equivalent_nonidentical_keys": equivalent_not_identical, "hash_entries": counts,
             "critical_artifacts_present_at_freeze": True, "truth_and_verdict_absent_at_freeze": True,
             "true_keys_primitive": True,
             "genre_counts": {k: dict(v) for k, v in genre_counts.items()},
             "source_windows_nonoverlapping": True, "truth_sha256": digest(truth_path),
             "freeze_commit": frozen_commit, "scope": "Saved synthetic outcomes only; no K4 or independent-model gate certification."}
    args.out.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "decisions": decisions, "witnesses": witnesses}))


if __name__ == "__main__":
    main()
