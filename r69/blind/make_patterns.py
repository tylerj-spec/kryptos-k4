#!/usr/bin/env python3
"""R69 BLIND reading list (no K4 data). Convention as R61: CT[j] = X[perm[j]] (X = text in reading order).
Two families of readings of the 97 carved cells:
  F (16, primary): K4's four carved rows (row 1 = cols 27-30 of the sculpture's 31-wide rows, rows 2-4 = cols 0-30)
     read top to bottom, each row left-to-right (bit 0) or right-to-left (bit 1). Name F_b1b2b3b4.
     F_0000 = carved order, F_0101 = SNAKE_L, F_1010 = SNAKE_R (asserted against r61/routes.txt).
  B (62, secondary): boustrophedon over 31-wide rows if K4 started at column c (0-30) of a 31-wide grid: cell i sits at
     (r, col) = divmod(c + i, 31); rows top to bottom; row r read right-to-left iff (r + q) is odd, q in {0, 1}.
     Name B_cCC_qQ. B_c27_q0 = SNAKE_L and B_c27_q1 = SNAKE_R.
Usage: make_patterns.py OUT.txt   (line format: NAME S_then_T p0,...,p96)"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
N = 97
W = 31


def f_family():
    sites = [(0, c) for c in range(27, 31)] + [(r, c) for r in (1, 2, 3) for c in range(31)]
    idx = {cell: i for i, cell in enumerate(sites)}
    out = []
    for b in range(16):
        bits = [(b >> (3 - r)) & 1 for r in range(4)]
        seq = []
        for r in range(4):
            row = [x for x in sites if x[0] == r]
            seq += row[::-1] if bits[r] else row
        out.append(("F_" + "".join(map(str, bits)), [idx[c] for c in seq]))
    return out


def b_family():
    out = []
    for c in range(W):
        cells = [divmod(c + i, W) for i in range(N)]
        idx = {cell: i for i, cell in enumerate(cells)}
        nrows = cells[-1][0] + 1
        for q in (0, 1):
            seq = []
            for r in range(nrows):
                row = [x for x in cells if x[0] == r]
                seq += row[::-1] if (r + q) % 2 else row
            out.append((f"B_c{c:02d}_q{q}", [idx[x] for x in seq]))
    return out


def main():
    out = f_family() + b_family()
    for name, p in out:
        assert sorted(p) == list(range(N)), name
    ref = {l.split()[0]: [int(x) for x in l.split()[2].split(",")] for l in (ROOT / "r61/routes.txt").read_text().splitlines()}
    d = dict(out)
    assert d["F_0000"] == list(range(N))
    assert d["F_0101"] == ref["SNAKE_L"] == d["B_c27_q0"]
    assert d["F_1010"] == ref["SNAKE_R"] == d["B_c27_q1"]
    assert len(out) == 78 and len(d) == 78
    Path(sys.argv[1]).write_text("".join(f"{n} S_then_T {','.join(map(str, p))}\n" for n, p in out))
    print(f"wrote {len(out)} readings (16 F + 62 B; F_0101 = B_c27_q0 = SNAKE_L, F_1010 = B_c27_q1 = SNAKE_R)")


if __name__ == "__main__":
    main()
