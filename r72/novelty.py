#!/usr/bin/env python3
"""R72 novelty check (review of PR #60, item 3). Each of the 9 double-turn orderings of a 98-cell sheet is turned into
a 97-letter route by removing the extra cell, under both placements (extra cell first or last), and in both directions
(the ordering and its inverse). Every resulting route is compared as an exact tuple (same convention as R61:
CT[j] = X[perm[j]]) with the route families this project has already run on K4:
  ragged single quarter turns of 97 letters (every width 2-96, both directions);
  K3-style double turns of 97 letters (widths 2-48 x 2-48, same or mixed direction; L47, L115, L124, R35);
  all decimations i -> a*i + b mod 97 (L07, L47);
  complete columnar transpositions, widths 2-10, natural column order, the strictblind read variants (L06);
  the 10 R61 routes and the 78 R69 readings.
Every family is included in both directions. L47's original generator is not in the repository, so its catalog is
rebuilt here from its ledger description.
Usage: python3 -I r72/novelty.py   (writes r72/data/NOVELTY.json)"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "r72"))
import reconstruct as R  # noqa: E402

N = 97


def inv(p):
    q = [0] * len(p)
    for j, i in enumerate(p):
        q[i] = j
    return q


def drop_cell(order98, cell):
    """97-letter route from a 98-cell ordering with the extra cell at input index `cell` (0 or 97)."""
    out = [i for i in order98 if i != cell]
    return [i - 1 for i in out] if cell == 0 else out


def columnar(w, revfill=False, snake=False, revread=False):
    grid = {}
    for j in range(N):
        row, col = divmod(j, w)
        if snake and row % 2:
            col = w - 1 - col
        if revfill:
            col = w - 1 - col
        grid[row, col] = j
    rows = (N + w - 1) // w
    return [grid[r, c] for c in range(w) for r in (range(rows - 1, -1, -1) if revread else range(rows)) if (r, c) in grid]


def catalog():
    fams = {}

    def add(name, p):
        assert sorted(p) == list(range(N)), name
        for q in (tuple(p), tuple(inv(p))):
            fams.setdefault(q, name)
    for w in range(2, N):
        for cw in (True, False):
            add(f"single turn w{w} {'CW' if cw else 'CCW'}", R.turn(N, w, cw))
    for w1 in range(2, 49):
        t1 = {cw: R.turn(N, w1, cw) for cw in (True, False)}
        for w2 in range(2, 49):
            for c1 in (True, False):
                for c2 in (True, False):
                    add(f"double turn {w1}x{w2} {'CW' if c1 else 'CCW'}-{'CW' if c2 else 'CCW'}",
                        R.compose(t1[c1], R.turn(N, w2, c2)))
    for a in range(1, N):
        for b in range(N):
            add(f"decimation {a}i+{b} mod 97", [(a * i + b) % N for i in range(N)])
    for w in range(2, 11):
        for rf in (False, True):
            for sn in (False, True):
                for rr in (False, True):
                    add(f"columnar w{w} revfill={rf} snake={sn} revread={rr}", columnar(w, rf, sn, rr))
    for line in (ROOT / "r61/routes.txt").read_text().splitlines():
        n, _, p = line.split()
        add(f"R61 {n}", [int(x) for x in p.split(",")])
    for line in (ROOT / "r69/data/patterns.txt").read_text().splitlines():
        n, _, p = line.split()
        add(f"R69 {n}", [int(x) for x in p.split(",")])
    return fams


def main():
    fams = catalog()
    seen98 = {}
    for w1 in (2, 7, 14, 49):
        for w2 in (2, 7, 14, 49):
            for cw in (True, False):
                p = R.compose(R.turn(98, w1, cw), R.turn(98, w2, cw))
                seen98.setdefault(R.decimation(p), p)
    rows, unique = [], {}
    for k, o in sorted(seen98.items()):
        for cell, label in ((0, "extra cell first"), (97, "extra cell last")):
            r = drop_cell(o, cell)
            for direction, q in (("forward", r), ("inverse", inv(r))):
                t = tuple(q)
                prior = fams.get(t)
                rows.append({"k_mod_99": k, "extra_cell": label, "direction": direction,
                             "sha256": hashlib.sha256(",".join(map(str, t)).encode()).hexdigest()[:16],
                             "already_tested_as": prior})
                if prior is None:
                    unique.setdefault(min(t, tuple(inv(q))), []).append(f"k={k} {label} {direction}")
    out = {"catalog_size_routes": len(fams), "rows": rows,
           "new_routes_up_to_inversion": len(unique), "new_route_labels": list(unique.values())}
    (ROOT / "r72/data/NOVELTY.json").write_text(json.dumps(out, indent=1) + "\n")
    print("catalog:", len(fams), "distinct routes (both directions)")
    for r in rows:
        print(f"k={r['k_mod_99']:>2} {r['extra_cell']:<17} {r['direction']:<8} {r['already_tested_as'] or 'NEW'}")
    print("new 97-letter routes (counting a route and its inverse once):", len(unique))


if __name__ == "__main__":
    main()
