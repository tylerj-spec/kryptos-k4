#!/usr/bin/env python3
"""R72 novelty and provenance check (PR #60 reviews). Each of the 9 double-turn orderings of a 98-cell sheet becomes
a 97-letter route by removing the extra cell (first or last), in both directions (the route and its inverse are
different trials in a layered cipher). Every route is classified, as an exact tuple (convention CT[j] = X[perm[j]]):
  CONFIRMED_EXECUTED  identical to a route in a run artifact committed in this repository (listed with its experiment);
  LEDGER_DOCUMENTED   identical to a member of a family the ledger says was run, with no route artifact in the repo
                      (L06 columnars w2-10; L07/L47 decimations mod 97; L47 K3-style same-direction double turns w2-48,
                      rebuilt here from the ledger description because L47's generator is not in the repository);
  GENERATED_ONLY      identical only to a member of a larger generated superset never documented as run (ragged single
                      turns of every width; mixed-direction double turns beyond R35's 4-28); computational equivalence,
                      not evidence of a run;
  NEW                 none of the above.
Usage: python3 -I r72/novelty.py   (writes r72/data/NOVELTY.json)"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "r72"))
import reconstruct as R  # noqa: E402

N = 97
ARTIFACTS = {   # route file -> experiments that ran it on K4 (ledger rows)
    "k4kit/r32/runs/routes_f1.txt": "R32 / R34 E2 (strictblind R27 set)",
    "k4kit/r32/runs/routes_f2.txt": "R32 / R34 E3 (double rotations 4-28; L115, L124)",
    "r34/e2_c7_r27/routes.txt": "R34 E2",
    "r34/e3_carter_rot/routes.txt": "R34 E3 (L124)",
    "r35/p0_k1k3_mixed/routes.txt": "R35 P0 mixed-direction 4-28 (L126)",
    "r35/p1_carter_k3_mixed/routes.txt": "R35 P1",
    "r41/x1_route_pafree/out/routes_A.txt": "R41 X1 (routes_A)",
    "r41/x1_route_pafree/out/routes_B.txt": "R41 X1 (routes_B)",
    "r41/x1_route_pafree/out/routes_r27.txt": "R41 X1 (R27 set)",
    "r41/x1_route_pafree/out/routes_rot.txt": "R41 X1 (rotations)",
    "r41/x1_route_pafree/out/routes_rotmixed.txt": "R41 X1 (mixed rotations)",
    "r61/routes.txt": "R61, R64, R65, R66 Part A, R67 controls, R68",
    "r63/numeric/exp/routes.txt": "R63 C (numeric keys)",
    "r66/data/feas_routes.txt": "R66 Part B (post-freeze, crib-assisted exact check)",
    "r69/data/patterns.txt": "R69 (German-key stage 1 only)",
}


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


def executed():
    """Exact routes from committed run artifacts: tuple -> list of 'experiment: route name'."""
    out = {}
    for path, exp in ARTIFACTS.items():
        for line in (ROOT / path).read_text().splitlines():
            if not line.strip():
                continue
            name, _order, p = line.split()
            t = tuple(int(x) for x in p.split(","))
            if len(t) == N:
                out.setdefault(t, []).append(f"{exp}: {name}")
    return out


def ledger_families():
    """Families described as run in the ledger but with no route artifact here (both directions)."""
    fams = {}

    def add(name, p):
        for q in (tuple(p), tuple(inv(p))):
            fams.setdefault(q, name)
    for a in range(1, N):
        for b in range(N):
            add(f"L07/L47 decimation {a}i+{b} mod 97", [(a * i + b) % N for i in range(N)])
    for w in range(2, 11):
        for rf in (False, True):
            for sn in (False, True):
                for rr in (False, True):
                    add(f"L06/L47 columnar w{w} revfill={rf} snake={sn} revread={rr}", columnar(w, rf, sn, rr))
    for w1 in range(2, 49):
        for w2 in range(2, 49):
            for cw in (True, False):
                add(f"L47 double turn {w1}x{w2} {'CW' if cw else 'CCW'}",
                    R.compose(R.turn(N, w1, cw), R.turn(N, w2, cw)))
    return fams


def generated_superset():
    """A larger generated set never documented as run: computational equivalence only."""
    fams = {}

    def add(name, p):
        for q in (tuple(p), tuple(inv(p))):
            fams.setdefault(q, name)
    for w in range(2, N):
        for cw in (True, False):
            add(f"single ragged turn w{w} {'CW' if cw else 'CCW'}", R.turn(N, w, cw))
    for w1 in range(2, 49):
        t = {cw: R.turn(N, w1, cw) for cw in (True, False)}
        for w2 in range(2, 49):
            for c1, c2 in ((True, False), (False, True)):
                add(f"mixed double turn {w1}x{w2} {'CW' if c1 else 'CCW'}-{'CW' if c2 else 'CCW'}",
                    R.compose(t[c1], R.turn(N, w2, c2)))
    return fams


def classify():
    ex, led, gen = executed(), ledger_families(), generated_superset()
    seen98 = {}
    for w1 in (2, 7, 14, 49):
        for w2 in (2, 7, 14, 49):
            for cw in (True, False):
                p = R.compose(R.turn(98, w1, cw), R.turn(98, w2, cw))
                seen98.setdefault(R.decimation(p), p)
    rows = []
    for k, o in sorted(seen98.items()):
        for cell, label in ((0, "extra cell first"), (97, "extra cell last")):
            r = drop_cell(o, cell)
            for direction, q in (("forward", r), ("inverse", inv(r))):
                t = tuple(q)
                if t in ex:
                    status, where = "CONFIRMED_EXECUTED", ex[t]
                elif t in led:
                    status, where = "LEDGER_DOCUMENTED", [led[t]]
                elif t in gen:
                    status, where = "GENERATED_ONLY", [gen[t]]
                else:
                    status, where = "NEW", []
                rows.append({"k_mod_99": k, "extra_cell": label, "direction": direction, "status": status,
                             "matches": where[:4],
                             "sha256": hashlib.sha256(",".join(map(str, t)).encode()).hexdigest()[:16]})
    return rows, len(ex), len(led), len(gen)


def main():
    rows, n_ex, n_led, n_gen = classify()
    from collections import Counter
    counts = Counter(r["status"] for r in rows)
    out = {"artifact_routes": n_ex, "ledger_family_routes": n_led, "generated_superset_routes": n_gen,
           "directed_route_counts": dict(counts), "rows": rows,
           "note": "36 directed rows = 9 orderings x 2 extra-cell placements x 2 directions; a route and its inverse "
                   "are distinct trials in a layered cipher. Only CONFIRMED_EXECUTED rows are proven to have been run."}
    (ROOT / "r72/data/NOVELTY.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"artifact routes {n_ex}, ledger-family routes {n_led}, generated superset {n_gen}")
    for r in rows:
        print(f"k={r['k_mod_99']:>2} {r['extra_cell']:<17} {r['direction']:<8} {r['status']:<19} {'; '.join(r['matches'][:2])}")
    print("directed route counts:", dict(counts))


if __name__ == "__main__":
    main()
