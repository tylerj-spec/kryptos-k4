#!/usr/bin/env python3
"""R83 historical erratum: *plaintext* corruption propagates in PFX and WPX.

CONSERVATIVE / necessary-condition audit. The original R83 preregistered
source and frozen outputs are NOT edited. This checker is post-freeze,
crib-assisted in --k4 mode and may produce FALSE FEASIBLE settings, but
cannot produce a false exclusion for a single unknown plaintext clue.

--synthetic: independently generated toy positions, never real K4 clues.
--k4 OUT: public K4 clues are loaded ONLY inside this post-freeze audit;
          report necessary conditions, not a discovered plaintext.

Never derive, rank, emit or complete a K4 plaintext/key candidate.
"""
import json
import sys
from pathlib import Path
from collections import Counter

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "r75"), str(ROOT / "r83")]
import exact83 as X  # noqa: E402
import models83 as MD  # noqa: E402


def _need(ct, pos, pk, conv):
    """Required numeric key for known plaintext letters, independent of U."""
    pa, ca, sign = conv
    return (X.I64[ca][ct[pos]] - sign * X.I64[pa][pk]) % 26


def _can_slot(values, positions, m):
    """Necessary/sufficient repeated-slot agreement on CONSTRAINED rows."""
    slots = {}
    for v, i in zip(values, positions):
        r = int(i) % m
        if r in slots and slots[r] != int(v):
            return False
        slots[r] = int(v)
    return True


def pfx_possible_after_unknown_plaintext(ct, pos, pk, conv, beta, sign, lag, m, dropped):
    """Sound *upper bound* for a single inaccurate published PLAINTEXT symbol.

    If position dropped is unknown, both the equation at that position
    AND the feedback equation at position dropped+lag must be relaxed.
    The latter can be constrained by the unknown plaintext letter, but
    relaxing it entirely is safe when asking whether a family is excluded.
    """
    at = {int(i): int(v) for i, v in zip(pos, pk)}
    if dropped not in at:
        raise ValueError("dropped position absent")
    required = _need(ct, pos, pk, conv)
    known = dict(zip((int(i) for i in pos), (int(v) for v in required)))
    rows, vals = [], []
    for i in pos:
        i = int(i)
        prior = i - lag
        if i == dropped or prior == dropped or prior not in at:
            continue
        rows.append(i)
        vals.append((known[i] - sign * int(X.I64[beta][at[prior]])) % 26)
    return _can_slot(vals, rows, m)


def wpx_necessary_after_unknown_plaintext(ct, pos, pk, conv, alpha, e, direction, m, dropped):
    """Conservative, independent **within-run** constraints.

    Treat one suspect plaintext as UNKNOWN and remove its own equation.
    It also changes the pointer trajectory. Split its observed run at
    the suspect position; unknown step can realize any residue mod m
    because alpha permutes 0..25 and 2<=m<=26.

    The unknown phase of each now-independent consecutive known run is
    not constrained against other runs here. Cross-run constraints can
    further eliminate candidates; a feasible return is NOT an exact
    solution, an infeasible return IS a sound exclusion for this setting.
    """
    if not 2 <= m <= 26:
        raise ValueError("m outside supported 2..26")
    at = {int(i): int(v) for i, v in zip(pos, pk)}
    if dropped not in at:
        raise ValueError("dropped position absent")
    req = _need(ct, pos, pk, conv)
    known = {int(i): int(v) for i, v in zip(pos, req) if int(i) != dropped}
    letters = {int(i): int(v) for i, v in zip(pos, pk) if int(i) != dropped}
    runs, active = [], []
    for i in sorted(letters):
        if active and i != active[-1] + 1:
            runs.append(active)
            active = []
        active.append(i)
    if active:
        runs.append(active)
    for run in runs:
        by_slot, offset = {}, 0
        for i in run:
            slot = offset % m
            if slot in by_slot and by_slot[slot] != known[i]:
                return False
            by_slot[slot] = known[i]
            offset += direction * (int(X.I64[alpha][letters[i]]) + e)
    return True


def _old_drop_recovers_true_setting(ct, pos, pk, st, bad):
    """Diagnostic ONLY: consult frozen legacy drop-one behavior (not a fix)."""
    c = np.array(ct, dtype=np.int64)
    t = X.Tally(list_min=-99, cap=100000)
    X.wpx(c, np.array(pos), np.array(pk), t, mmax=len(st["U"]), drop=True)
    return any(
        z.get("m") == len(st["U"]) and tuple(z.get("conv", [])) == tuple(st["conv"]) and
        z.get("alpha") == st["alpha"] and z.get("e") == st["e"] and
        z.get("d") == st["d"] and bad in z.get("dropped", [])
        for z in t.drows["WPX"]
    )


def synthetic_tests():
    """Two independent proof-of-regression counterexamples; no K4 materials."""
    rng = np.random.default_rng(838301)
    pos = np.array(list(range(9, 21)) + list(range(56, 68)), dtype=np.int64)
    pt = "A" * 97
    bad = 11  # inside a known run, with later published feedback/steps
    corrupted = np.array([0 if i != bad else 1 for i in pos], dtype=np.int64)
    exact = np.zeros(97, dtype=np.int64)
    st_pf = {"fam": "PF", "conv": ("AZ", "AZ", 1), "U": [0, 3, 7],
             "L": 1, "beta": "AZ", "f": 1, "primer": "A"}
    ct_pf = MD.encrypt(pt, st_pf)
    c_pf = np.array([MD.AZ.index(x) for x in ct_pf], dtype=np.int64)
    assert pfx_possible_after_unknown_plaintext(
        c_pf, pos, corrupted, st_pf["conv"], "AZ", 1, 1, 3, bad)
    # Old slot_check drop-one removes only i=bad's equation while
    # retaining its corrupted plaintext as feedback into i=bad+1.
    x = {int(v): k for k, v in enumerate(pos)}
    paired = [k for k, i in enumerate(pos) if int(i)-1 in x]
    want = [(int(c_pf[i]) - int(corrupted[k]) - int(corrupted[x[int(i)-1]])) % 26
            for k, i in enumerate(pos) if int(i)-1 in x]
    source = [int(pos[k]) for k in paired]
    old_drop = X.slot_check(np.array(source) % 3,
                            np.array([want], dtype=np.int64))[1][0]
    assert not old_drop.any(), "synthetic PF counterexample no longer breaks old code"

    st_wp = {"fam": "WP", "conv": ("AZ", "AZ", 1), "U": [0, 5, 11],
             "alpha": "AZ", "e": 1, "d": 1, "ptr0": 0}
    ct_wp = MD.encrypt(pt, st_wp)
    c_wp = np.array([MD.AZ.index(x) for x in ct_wp], dtype=np.int64)
    assert wpx_necessary_after_unknown_plaintext(
        c_wp, pos, corrupted, st_wp["conv"], "AZ", 1, 1, 3, bad)
    old_recovered = _old_drop_recovers_true_setting(c_wp, pos, corrupted, st_wp, bad)
    assert not old_recovered, "synthetic WP counterexample no longer breaks old code"
    assert MD.decrypt(ct_pf, st_pf) == pt
    assert MD.decrypt(ct_wp, st_wp) == pt
    # Deliberately corrupt another, downstream-relevant plaintext
    # index and verify no unsafe excluded returns for true settings.
    for b in (9, 10, 12, 17, 56, 57, 66):
        xpk = np.array([0 if i != b else int(rng.integers(1, 26)) for i in pos])
        assert pfx_possible_after_unknown_plaintext(
            c_pf, pos, xpk, st_pf["conv"], "AZ", 1, 1, 3, b)
        assert wpx_necessary_after_unknown_plaintext(
            c_wp, pos, xpk, st_wp["conv"], "AZ", 1, 1, 3, b)
    return {"synthetic_anchor_positions": pos.tolist(),
            "old_PFX_drop_detects_correct_setting": bool(old_drop.any()),
            "old_WPX_drop_detects_correct_setting": bool(old_recovered),
            "new_PFX_conservative_detects": True,
            "new_WPX_conservative_detects": True,
            "diagnosis": "old one-equation dropout mistakes a plaintext variable for a single constraint"}


def k4_audit(out_path):
    """Post-freeze conservative K4 scan; false positives possible, false exclusions not."""
    X.guard()
    sys.path.insert(0, str(ROOT / "r73" / "sealed"))
    from reveal_k4 import CLUES  # noqa: E402 -- ONLY in post-freeze audit
    cts = dict(line.split("\t") for line in (ROOT / "r83/k4/TARGET.tsv").read_text().splitlines()[1:] if line)
    c = np.array([MD.AZ.index(x) for x in cts["K4"]], dtype=np.int64)
    pos = np.array([o + j for o, t in CLUES for j in range(len(t))], dtype=np.int64)
    pk = np.array([MD.AZ.index(ch) for _, t in CLUES for ch in t], dtype=np.int64)
    assert len(pos) == 24 and len(c) == 97

    # Necessary WPX checks *within* each known run. An unknown p at
    # the dropped position splits that run and allows a new phase.
    # This is a deliberately generous upper bound, never an exclusion
    # of a genuinely feasible linked state.
    survivors = set()
    by_drop = {}
    for bad in pos:
        n = 0
        for conv in X.CONV1:
            for alpha in X.A4:
                for e in (0, 1):
                    for direction in (1, -1):
                        for m in range(2, 27):
                            if wpx_necessary_after_unknown_plaintext(
                                c, pos, pk, conv, alpha, e, direction, m, int(bad)):
                                survivors.add((conv, alpha, e, direction, m))
                                n += 1
        by_drop[str(int(bad))] = n

    report = {
        "classification": "POST-FREEZE CRIB-ASSISTED, CONSERVATIVE UPPER BOUND",
        "source_run": "R83a frozen, not modified",
        "meaning": "WPX setting not eliminated by within-run necessary conditions after suspect plaintext letter and its pointer step become unknown; cross-run consistency may rule it out.",
        "important": "A positive conservative survivor is NOT a feasible K4 decryption; zero survivors would safely exclude this WPX range under the exact assumptions.",
        "WPX_conservative_unique_settings": len(survivors),
        "WPX_conservative_by_dropped_position": by_drop,
        "WPX_examples": [
            {"conv": list(st[0]), "alpha": st[1], "e": st[2],
             "d": st[3], "m": st[4]} for st in sorted(survivors)[:20]],
        "PFX": "Original DROP=CHANCE. Its exact one-plaintext-error count is unverified; prior 17 survivors are not a complete enumeration of robust PFX settings.",
    }
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"WPX_conservative_unique_settings": len(survivors),
                      "nonzero_drops": sum(v > 0 for v in by_drop.values()),
                      "smallest_drop_count": min(by_drop.values()),
                      "largest_drop_count": max(by_drop.values())}), flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "--synthetic":
        print(json.dumps(synthetic_tests(), indent=2))
    elif sys.argv[1] == "--k4":
        k4_audit(sys.argv[2])
    else:
        raise SystemExit(__doc__)
