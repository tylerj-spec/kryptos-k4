#!/usr/bin/env python3
"""Independent R79 post-freeze crib audit.

The original pre-registered validator and all frozen blind outputs remain untouched.
The functions below take synthetic anchors explicitly; only main() imports the
published clues. H11 now requires *both* the anchor equations and an actual
cycle-consistent plaintext for every cycle of the proposed route.

Usage:
  python3 -I r79/sealed/validate79_postfreeze.py \
    r79/k4/TARGET.tsv r79/k4/VALIDATE.json OUT.json
"""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r75"))
sys.path.insert(0, str(ROOT / "r79"))
import core  # noqa: E402
import families as F  # noqa: E402

KEYWORD_FAMILIES = ("H7CT", "H7TXT", "LIB", "PROG")
MIN_H11_CHECKS = 3


def slot_consistency(z, r, oi, positions, wanted, inverse_bank):
    """Exact keyword feasibility, independently of the original pairwise test.

    For every published position, invert the corresponding output alphabet to
    obtain the required shift. Equal slots must require equal shifts.
    Sorting by slot makes adjacent comparisons sufficient.
    Returns (feasible per setting, number of independent consistency checks).
    """
    pos = np.asarray(positions, dtype=np.int64)
    want = np.asarray(wanted, dtype=np.int64)
    if not len(pos) or len(pos) != len(want) or len(set(pos.tolist())) != len(pos):
        raise ValueError("anchors must be nonempty, distinct, and paired")
    z = np.asarray(z)
    r = np.asarray(r)
    oi = np.asarray(oi)
    v = inverse_bank[oi[:, None], pos[None, :], want[None, :]]
    d = (v.astype(np.int16) - z[:, pos].astype(np.int16)) % 26
    slots = r[:, pos]
    order = np.argsort(slots, axis=1, kind="stable")
    ss = np.take_along_axis(slots, order, axis=1)
    dd = np.take_along_axis(d, order, axis=1)
    same = ss[:, 1:] == ss[:, :-1]
    feasible = ~(same & (dd[:, 1:] != dd[:, :-1])).any(axis=1)
    checks = len(pos) - 1 - (~same).sum(axis=1)
    return feasible, checks


def keyword_counts(ct, positions, wanted, families=KEYWORD_FAMILIES):
    """Re-enumerate all keyword settings on one ciphertext; no solver used."""
    inverse_bank = np.argsort(F.bank()[0], axis=2)
    out = {}
    for fam in families:
        hist = Counter()
        for z, r, _m, oi, _info in F.chunks(fam, ct):
            feasible, checks = slot_consistency(z, r, oi, positions, wanted, inverse_bank)
            values, counts = np.unique(checks[feasible], return_counts=True)
            for v, n in zip(values, counts):
                hist[int(v)] += int(n)
        out[fam] = {str(k): hist[k] for k in sorted(hist)}
    return out


def h11_route_feasible(y, perm, step, fixed):
    """Exact full-cipher feasibility with fixed plaintext-index anchors.

    Each permutation cycle must have a fixed point of the composed step map.
    If a cycle contains an anchor, start there with its uniquely required
    value; otherwise try all 26 possible starts. This is an existence test,
    not a language-model search.
    """
    n = len(y)
    seen = np.zeros(n, dtype=bool)
    for first in range(n):
        if seen[first]:
            continue
        cycle = []
        j = first
        while not seen[j]:
            seen[j] = True
            cycle.append(j)
            j = int(perm[j])
        if j != first:
            return False  # not a permutation
        anchor_offset = next((k for k, i in enumerate(cycle) if i in fixed), None)
        if anchor_offset is None:
            starts = range(26)
        else:
            cycle = cycle[anchor_offset:] + cycle[:anchor_offset]
            starts = (fixed[cycle[0]],)
        for x0 in starts:
            x = int(x0)
            for i in cycle:
                if i in fixed and x != fixed[i]:
                    break
                x = int(step[int(y[i]), x])
            else:
                if x == x0:
                    break
        else:
            return False
    return True


def h11_check(ct, positions, wanted, routes=None):
    """Compare anchor-only H11 counts with full-cycle-and-anchor counts.

    Only routes with at least three anchor-to-anchor checks are counted, as
    in the frozen R79 validator. Routes with fewer checks remain OPEN.
    'routes' can be a small synthetic (names, permutations) fixture.
    """
    names, perms = F.routes() if routes is None else routes
    perms = np.asarray(perms, dtype=np.uint8)
    pos = np.asarray(positions, dtype=np.int64)
    want = np.asarray(wanted, dtype=np.int64)
    c = core.codes(ct).astype(np.int64)
    known = np.full(F.N, -1, dtype=np.int64)
    known[pos] = want
    key_pos = perms[:, pos]
    key_letters = known[key_pos]
    use = key_letters >= 0
    checks = use.sum(axis=1)
    steps, _ = F.h11_tables()
    anchor_only, joint, survivors = {}, {}, []
    for k, (pa, ka, ca, op) in enumerate(F.H11_CONV):
        label = "/".join((pa, ka, ca, op))
        s, t = F.OPS[op]
        expected = F.LET[ca][(s * F.IDX[pa][want][None, :] +
                              t * F.IDX[ka][np.maximum(key_letters, 0)]) % 26]
        ok = ((expected == c[pos][None, :]) | ~use).all(axis=1)
        candidates = np.flatnonzero(ok & (checks >= MIN_H11_CHECKS))
        hist_anchor, hist_joint = Counter(), Counter()
        for r in candidates:
            hist_anchor[int(checks[r])] += 1
        fixed = {int(i): int(F.IDX[pa][w]) for i, w in zip(pos, want)}
        y = F.IDX[ca][c]
        step = steps[k].reshape(26, 26)
        for r in candidates:
            if h11_route_feasible(y, perms[r], step, fixed):
                hist_joint[int(checks[r])] += 1
                survivors.append({"route": names[int(r)], "convention": label, "checks": int(checks[r])})
        anchor_only[label] = {str(v): hist_anchor[v] for v in sorted(hist_anchor)}
        joint[label] = {str(v): hist_joint[v] for v in sorted(hist_joint)}
    return {
        "routes_with_ge3_checks": int((checks >= MIN_H11_CHECKS).sum()),
        "anchor_only_feasible_by_checks": anchor_only,
        "cycle_and_crib_feasible_by_checks": joint,
        "survivors": survivors,
    }


def main():
    target, old_path, out_path = map(Path, sys.argv[1:4])
    sys.path.insert(0, str(ROOT / "r73" / "sealed"))
    from reveal_k4 import CLUES  # noqa: E402  # imported only after synthetic helpers

    pos = np.asarray([o + i for o, t in CLUES for i in range(len(t))], dtype=np.int64)
    want = np.asarray([ord(ch) - 65 for _, t in CLUES for ch in t], dtype=np.int64)
    cts = dict(line.split("\t") for line in target.read_text().splitlines()[1:] if line)
    old = json.loads(old_path.read_text())
    ids = list(old["rows"])
    assert ids[0] == "K4" and all(rid in cts for rid in ids)
    assert len(pos) == 24

    # Independent, sorting-based reproduction of the original exact keyword
    # exclusions on K4. No change to the sealed solver or its confidence cuts.
    keyword = keyword_counts(cts["K4"], pos, want)
    for fam in KEYWORD_FAMILIES:
        assert keyword[fam] == old["rows"]["K4"][fam]["feasible_by_checks"], fam

    routes = F.routes()
    rows = {}
    for rid in ids:
        checked = h11_check(cts[rid], pos, want, routes=routes)
        old_h11 = old["rows"][rid]["H11"]
        assert checked["routes_with_ge3_checks"] == old_h11["routes_with_ge3_checks"], rid
        assert checked["anchor_only_feasible_by_checks"] == old_h11["feasible_by_checks"], rid
        rows[rid] = checked
        print(rid, "anchor-only", sum(len(v) and sum(v.values()) for v in
              checked["anchor_only_feasible_by_checks"].values()),
              "cycle+crib", len(checked["survivors"]), flush=True)

    report = {
        "label": "POST-FREEZE INDEPENDENT CRIB AUDIT (not blind; no change to R79 gate)",
        "original_validator": str(old_path),
        "criterion": "H11 route and convention must satisfy every cycle and all 24 known letters",
        "h11_min_anchor_checks": MIN_H11_CHECKS,
        "h11_routes_below_min_checks": "not assessed; remain open",
        "keyword_k4_feasible_by_checks": keyword,
        "rows": rows,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=1) + "\n")
    print("Post-freeze audit written:", out_path)


if __name__ == "__main__":
    main()
