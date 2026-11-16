#!/usr/bin/env python3
"""Independent post-freeze audit of R83 T1 WPX 'effective checks' labeling.

NO completed key, decoded plaintext, candidate generator, score, or
trial plaintext symbol is emitted. The published clues enter ONLY the
isolated post-freeze verification path. The historical R83 frozen outputs
are read-only and SHA checked before use.

Finding being tested:
  Changing the suspected PLAINTEXT symbol changes the future pointer
  residues in its run. The number of independent constraints therefore
  must be calculated under the *changed* symbol and the *feasible*
  pointer offset, not the original published spelling.

This file independently implements the fixed, already-reported structural
WPX settings, and does not import Claude's exact_drop.py.
"""
import hashlib
import importlib.util
import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
def keyed(w):
    return "".join(dict.fromkeys(w + AZ))

PA = keyed("ABSCISSA")
CA = keyed("KRYPTOS")
STEP = keyed("PALIMPSEST")
M = 26
E = 1
BPOS = (25, 28)  # already reported in T1; 0-based published locations


def blocks(pos):
    groups = []
    for k, p in enumerate(pos):
        if groups and p == pos[groups[-1][-1]] + 1:
            groups[-1].append(k)
        else:
            groups.append([k])
    if len(groups) != 2:
        raise AssertionError("expected two consecutive published runs")
    return groups


def residues(plain, groups, direction):
    rel = [0] * len(plain)
    for g in groups:
        cursor = 0
        for k in g:
            rel[k] = cursor
            cursor = (cursor + direction * (STEP.index(plain[k]) + E)) % M
    return rel


def old_strength(plain, groups, direction):
    rel = residues(plain, groups, direction)
    first, second = groups
    return min(len(plain) - len(
        set(rel[k] for k in first) |
        {(rel[k] + off) % M for k in second}
    ) for off in range(M))


def feasible_strengths(ct, positions, plain, groups, direction):
    """Only yields check counts; keys and substituted letters never returned."""
    rel = residues(plain, groups, direction)
    first, second = groups
    needed = [(CA.index(ct[i]) - PA.index(p)) % 26
              for i, p in zip(positions, plain)]
    counts = []
    for offset in range(M):
        r = list(rel)
        for k in second:
            r[k] = (r[k] + offset) % M
        seen = {}
        consistent = True
        for idx, keyslot in enumerate(r):
            v = needed[idx]
            if keyslot in seen and seen[keyslot] != v:
                consistent = False
                break
            seen[keyslot] = v
        if consistent:
            counts.append(len(positions) - len(seen))
    return counts


def synthetic_regression():
    rng = random.Random(830118)
    n = 97
    positions = list(range(9, 21)) + list(range(56, 68))
    groups = blocks(positions)
    truth_kept = 0
    disagreement_seen = False
    for direction in (-1, 1):
        for case in range(24):
            pt = "".join(rng.choice(AZ) for _ in range(n))
            key = [rng.randrange(26) for _ in range(M)]
            ptr = rng.randrange(M)
            ct = []
            for p in pt:
                ct.append(CA[(PA.index(p) + key[ptr]) % 26])
                ptr = (ptr + direction * (STEP.index(p) + E)) % M
            ct = "".join(ct)
            published = [pt[i] for i in positions]
            index = (case * 7 + 3) % len(positions)
            wrong = rng.choice([z for z in AZ if z != published[index]])
            published[index] = wrong
            old = old_strength(published, groups, direction)
            valid = []
            for x in AZ:
                if x == wrong:
                    continue
                check = published.copy()
                check[index] = x
                valid.extend(feasible_strengths(ct, positions, check, groups, direction))
            assert valid, "a genuine one-error plaintext plant must survive"
            truth_kept += 1
            if any(c != old for c in valid):
                disagreement_seen = True
    assert disagreement_seen, "stale-check effect should have a synthetic counterexample"
    return {"synthetic_97_letter_plants": truth_kept,
            "true_settings_retained": truth_kept,
            "stale_strength_counterexample_present": disagreement_seen}


def published_postfreeze():
    target = ROOT / "r83/k4/TARGET.tsv"
    frozen = ROOT / "r83/k4/run/FROZEN.sha256"
    expected = [line.split()[0] for line in frozen.read_text().splitlines()
                if line.endswith("r83/k4/TARGET.tsv")]
    assert len(expected) == 1
    assert expected[0] == hashlib.sha256(target.read_bytes()).hexdigest()
    rows = dict(line.split("\t") for line in target.read_text().splitlines()[1:] if line)
    ct = rows["K4"]
    assert len(ct) == 97 and set(ct) <= set(AZ)

    # Published plaintext is accessible ONLY in this post-freeze auditor.
    file = ROOT / "r73/sealed/reveal_k4.py"
    spec = importlib.util.spec_from_file_location("r83_t1_postfreeze_clues", file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    pos = [i for i, _ in module.POS]
    original = [c for _, c in module.POS]
    assert len(pos) == 24 and set(pos) == set(range(21, 34)) | set(range(63, 74))
    groups = blocks(pos)
    result = []
    for direction in (-1, 1):
        original_checks = old_strength(original, groups, direction)
        assert original_checks == 4, "T1's archived WPX check strength changed"
        for bpos in BPOS:
            b = pos.index(bpos)
            check_counts = []
            letters_changed = 0
            for x in AZ:
                if x == original[b]:
                    continue
                alternate = original.copy()
                alternate[b] = x
                vals = feasible_strengths(ct, pos, alternate, groups, direction)
                if vals:
                    letters_changed += 1
                    check_counts.extend(vals)
            # No candidate plaintext letter, pointer offset or key is exposed.
            assert letters_changed == 1 and len(check_counts) == 1
            assert check_counts == [1 if bpos == 25 else 2]
            result.append({
                "family": "WPX",
                "convention": "PA=ABS CA=KRY additive alpha=PAL e=1 m=26",
                "d": direction,
                "dropped_position_0_based": bpos,
                "archived_checks_under_published_letter": original_checks,
                "feasible_one_error_witnesses": len(check_counts),
                "witness_actual_checks": list(check_counts),
                "survives_at_checks_ge3": any(v >= 3 for v in check_counts),
            })
    return {
        "classification": "POST-FREEZE, CRIB-ASSISTED, EXCLUSION-ONLY RECHECK",
        "source_verified_against_R83_freeze": True,
        "prints_replacement_plaintext_letter": False,
        "prints_key_or_decryption": False,
        "statement": "T1 WPX changed-letter survivors are NOT at effective constraint strength 4; their feasible witnesses have 1 or 2 checks. Do not use the original 12/20 shuffled control comparison until all nulls are re-calibrated using the corrected strength.",
        "results": result,
    }


def main():
    if len(sys.argv) != 3 or sys.argv[1] != "--postfreeze":
        raise SystemExit("usage: wpx_strength_recheck.py --postfreeze OUTPUT.json")
    synth = synthetic_regression()
    res = published_postfreeze()
    res["synthetic"] = synth
    out = Path(sys.argv[2])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "synthetic": synth,
        "archived_eff4": sorted(set(r["archived_checks_under_published_letter"]
                                    for r in res["results"])),
        "actual_feasible_check_levels": sorted(set(v for r in res["results"]
                                                    for v in r["witness_actual_checks"])),
        "K4_structural_survivors_at_ge3": any(r["survives_at_checks_ge3"]
                                             for r in res["results"]),
        "note": "Only the known two K4 structural settings audited; shuffled controls not recalibrated",
    }))


if __name__ == "__main__":
    main()
