#!/usr/bin/env python3
"""Blind side: write route files from K3 geometry rules only (no clue information).
  routes_f1.txt: identity + the 20 R27 routes x {S_then_T, T_then_S}   (41 lines)
  routes_f2.txt: R{w1}x{w2}/{CW,CCW}/{fwd,inv}, w1,w2 in 4..28, both orders (5,000 lines)
Line format: NAME ORDER p0,p1,...,p96   (perm as in k4common.route; ORDER = ID | S_then_T | T_then_S)"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Copied from tools/k4common.py (rot, inv, route, R27_ROUTES) so that the blind side imports nothing that holds clues.


def rot(n, w, cw):
    rows = [list(range(i, min(i + w, n))) for i in range(0, n, w)]
    out = []
    for c in range(w):
        cc = c if cw else w - 1 - c
        for r in (range(len(rows) - 1, -1, -1) if cw else range(len(rows))):
            if cc < len(rows[r]):
                out.append(rows[r][cc])
    return out


def inv(p):
    q = [0] * len(p)
    for j, i in enumerate(p):
        q[i] = j
    return q


def route(name, n=97):
    dims, cwn, kind = name[1:].split("/")
    w1, w2 = map(int, dims.split("x"))
    cw = cwn == "CW"
    p1, p2 = rot(n, w1, cw), rot(n, w2, cw)
    p = [p1[i] for i in p2]
    return p if kind == "fwd" else inv(p)


R27_ROUTES = [f"R{a}x{b}/{d}/{k}" for a, b in ((24, 8), (23, 8), (25, 8), (24, 7), (24, 9))
              for d in ("CW", "CCW") for k in ("fwd", "inv")]

out = HERE.parent / "runs"
out.mkdir(exist_ok=True)
with open(out / "routes_f1.txt", "w") as f:
    f.write("ID ID " + ",".join(map(str, range(97))) + "\n")
    for name in R27_ROUTES:
        for order in ("S_then_T", "T_then_S"):
            f.write(f"{name} {order} {','.join(map(str, route(name)))}\n")
n = 0
with open(out / "routes_f2.txt", "w") as f:
    for w1 in range(4, 29):
        for w2 in range(4, 29):
            for d in ("CW", "CCW"):
                for kind in ("fwd", "inv"):
                    name = f"R{w1}x{w2}/{d}/{kind}"
                    p = ",".join(map(str, route(name)))
                    for order in ("S_then_T", "T_then_S"):
                        f.write(f"{name} {order} {p}\n")
                        n += 1
print("routes_f1: 41 lines; routes_f2:", n, "lines")
