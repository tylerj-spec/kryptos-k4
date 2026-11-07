#!/usr/bin/env python3
"""R71 tests. Run: python3 -I r71/tests/test_r71.py SRC_DIR
  1. no R71 code holds K4 plaintext words (R71 never uses the published letters);
  2. the exact residue-count probability matches simulation; R_w and A_w match brute force;
  3. every family is invertible and follows its definition (decryption recovers x; x is a per-row relabelling of the
     plaintext; periodic, Gromark and autokey keys obey their rules; homophonic text un-routes and decodes to P)."""
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r71"))
import features as F  # noqa: E402
import generators as G  # noqa: E402
import run as R  # noqa: E402

bad = []
for f in sorted((ROOT / "r71").rglob("*.py")):
    if f.name == "test_r71.py":
        continue
    t = f.read_text()
    for w in ("EASTNORTHEAST", "NORTHEAST", "BERLINCLOCK", "BERLIN", "CLOCK"):
        if w in t:
            bad.append(f"{f.name}: {w}")

r = random.Random(1)
hit = sum(max(Counter(x % 7 for x in r.sample(range(96), 6)).values()) >= 5 for _ in range(40000)) / 40000
if abs(hit - F.p_max_residue_ge(7, 6, 5)) > 0.0006:
    bad.append(f"P1 exact vs simulation {F.p_max_residue_ge(7, 6, 5)} {hit}")
rng = np.random.default_rng(3)
C = rng.integers(0, 26, size=(200, 97)).astype(np.int16)
for w in (3, 7, 21, 48):
    rep = F.repeats(C, w)
    for i in range(0, 200, 37):
        c = Counter((int(C[i, j]), int(C[i, j + w])) for j in range(97 - w))
        if rep[i] != sum(v - 1 for v in c.values()):
            bad.append(f"repeats w={w}")
_, D, A = F.t1(C)
for i in range(0, 200, 41):
    starts = [j for j in range(96) if C[i, j] == C[i, j + 1]]
    if D[i] != len(starts) or (starts and A[7][i] != max(Counter(s % 7 for s in starts).values())):
        bad.append("A_7 / D")

src = Path(sys.argv[1])
pt = np.concatenate([R.letters(src / "2360.txt"), R.letters(src / "974.txt")])
kt = R.letters(src / "558.txt")
routes = [[int(x) for x in l.split()[2].split(",")] for l in (ROOT / "r61/routes.txt").read_text().splitlines()]
for arm in G.ARMS:
    g = np.random.default_rng(11)
    C, par, d = G.gen(arm, g, 300, pt, kt, routes, debug=True)
    P = d["P"]
    if arm == "HOMOPHONIC":
        for i in range(300):
            perm = routes[d["routes"][i]]
            X = [0] * 97
            for j, s in enumerate(perm):
                X[s] = int(C[i, j])
            m = {}
            if any(m.setdefault(c, p) != p for c, p in zip(X, P[i])):
                bad.append("homophonic not a function of the cipher letter")
                break
        continue
    x, k, op = d["x"], d["k"], d["op"]
    o = np.asarray(op)[:, None]
    back = np.where(o == 0, C - k, np.where(o == 1, k - C, C + k)) % 26
    if not np.array_equal(back, x % 26):
        bad.append(f"{arm}: decryption does not recover x")
    for i in range(0, 300, 29):
        m = {}
        if any(m.setdefault(int(p), int(v)) != int(v) for p, v in zip(P[i], x[i])) or len(set(m.values())) != len(m):
            bad.append(f"{arm}: x is not a relabelling of P")
            break
    if arm == "PERIODIC" and not all(all(k[i, t] == k[i, t % par[i]] for t in range(97)) for i in range(0, 300, 13)):
        bad.append("PERIODIC key not periodic")
    if arm == "GROMARK" and not np.array_equal(k[:, 5:], (k[:, :-5] + k[:, 1:-4]) % 10):
        bad.append("GROMARK recurrence")
    if arm in ("CTAK", "PTAK"):
        fb = C if arm == "CTAK" else x
        for i in range(0, 300, 7):
            L = int(d["L"][i])
            if any(k[i, t] != fb[i, t - L] for t in range(L, 97)):
                bad.append(f"{arm} feedback rule")
                break

if bad:
    print("R71 TEST FAIL:", bad[:10])
    sys.exit(1)
print("R71 TESTS OK: clue-free; exact P1 = simulation; features = brute force; all 7 families invertible and as defined")
