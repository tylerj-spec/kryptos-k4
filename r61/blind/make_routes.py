#!/usr/bin/env python3
"""R61 BLIND route list (no K4 data). 10 transpositions, convention CT[j] = X[perm[j]] (X = substitution output in
plaintext order), i.e. substitute first, then transpose:
  - K3's own grid: the four 24x8 double quarter-turn rotations R24x8/{CW,CCW}/{fwd,inv} (strictblind route maker);
  - the six 4+31+31+31 engraving-site routes of R58 (COL_LT/LB/RT/RB, SNAKE_L/R), copied from r58/blind/solve.py.
Usage: make_routes.py OUT.txt   (line format: NAME S_then_T p0,...,p96)"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "strictblind/blind"))
import routes as R  # noqa: E402

N = 97


def physical_routes():
    sites = [(0, c) for c in range(27, 31)] + [(r, c) for r in (1, 2, 3) for c in range(31)]
    indices = {cell: i for i, cell in enumerate(sites)}
    mapping = {}
    for cd in ("L", "R"):
        for rd in ("T", "B"):
            cs = range(31) if cd == "L" else range(30, -1, -1)
            rs = range(4) if rd == "T" else range(3, -1, -1)
            seq = [(r, c) for c in cs for r in rs if (r, c) in indices]
            mapping["COL_" + cd + rd] = [indices[c] for c in seq]
    for start in ("L", "R"):
        seq = []
        for r in range(4):
            row = [x for x in sites if x[0] == r]
            reverse = (r % 2 == 1) == (start == "L")
            seq += row[::-1] if reverse else row
        mapping["SNAKE_" + start] = [indices[c] for c in seq]
    return mapping


def main():
    out = []
    for name in ("R24x8/CW/fwd", "R24x8/CW/inv", "R24x8/CCW/fwd", "R24x8/CCW/inv"):
        out.append((name, R.rotation(name)))
    out += list(physical_routes().items())
    for name, p in out:
        assert sorted(p) == list(range(N)), name
    Path(sys.argv[1]).write_text("".join(f"{n} S_then_T {','.join(map(str, p))}\n" for n, p in out))
    print(f"wrote {len(out)} routes")


if __name__ == "__main__":
    main()
