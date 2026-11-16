#!/usr/bin/env python3
"""Tests for r83/audit/replay_exact.py (T6 item 1). Synthetic only: no K4 ciphertext and no published letters.
1 brute force on toy keys: each check equals an exhaustive search over every key (SL: all A, B in 26^m x 26^m;
  SL-A: all A; SS: all keywords in 26^m; LK: all keywords in 26^m), through r83/models83.py's reference cipher, on
  planted, one-letter-altered and random ciphertexts;
2 planted 97-letter messages at the largest parameters (SL/SL-A m 26 and 10, SS m 25, LK m 20 with w 48 and 2,
  d -1, both rotations; LK m 2) are feasible under their own setting;
3 agreement with R83a's original engine (r83/exact83.py) on random ciphertexts: SLX, SLX-A and SSX in full; LX on 300
  random conventions x every cell.
Usage: python3 -I r83/audit/tests/test_replay_exact.py"""
import itertools
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "r83" / "audit"), str(ROOT / "r83"), str(ROOT / "r75")]
import replay_exact as R  # noqa: E402
import models83 as MD  # noqa: E402

AZ = MD.AZ


def codes(t):
    return [AZ.index(x) for x in t]


def K_of(ct, pt, pos, pa, ca, s):
    return [R.need(AZ.index(ct[i]), AZ.index(pt[i]), pa, ca, s) for i in pos]


def brute_sl(ct, pt, pos, st, same):
    pa, ca, s = st["conv"]
    m = len(st["A"])
    rng_b = [None] if same else list(itertools.product(range(26), repeat=m))
    for A in itertools.product(range(26), repeat=m):
        for B in rng_b:
            B = A if same else B
            keys = [((A[i % m] + (i // m) * B[i % m]) if not same else ((i // m + 1) * A[i % m])) % 26 for i in pos]
            if all(MD.enc1(pt[i], k, pa, ca, s) == ct[i] for i, k in zip(pos, keys)):
                return True
    return False


def brute_ss(ct, pt, pos, st):
    pa, ca, ka, s = st["conv"]
    m = len(st["W"])
    for W in itertools.product(AZ, repeat=m):
        ks = MD.ss_keys(max(pos) + 1, {**st, "W": "".join(W)})
        if all(MD.enc1(pt[i], ks[i], pa, ca, s) == ct[i] for i in pos):
            return True
    return False


def brute_lk(ct, pt, pos, st):
    pa1, ca1, pa2, ca2, s1, s2, t2, ka1, ka2 = st["conv"]
    m = len(st["x"])
    pi = MD.lk_pi(ka1, ka2)
    for x in itertools.product(range(26), repeat=m):
        ok = True
        for i in pos:
            a, b = MD.lk_slots(i, m, st["w"], st["d"], st["rot"])
            if MD.enc1(MD.enc1(pt[i], x[a], pa1, ca1, s1), t2 * pi[x[b]], pa2, ca2, s2) != ct[i]:
                ok = False
                break
        if ok:
            return True
    return False


def check(fam, ct, pt, pos, st):
    if fam in ("SL", "SLA"):
        m = len(st["A"])
        return R.slx_ok(K_of(ct, pt, pos, *st["conv"]), pos, m, fam == "SLA")
    if fam == "SS":
        pa, ca, ka, s = st["conv"]
        return R.ssx_ok(K_of(ct, pt, pos, pa, ca, s), pos, len(st["W"]), tuple(st["conv"]))
    maps = R.lx_edge_maps(codes(ct), pos, codes("".join(pt[i] for i in pos)), tuple(st["conv"]))
    m = len(st["x"])
    return R.lx_feasible(maps, [R.lx_slots(i, m, st["w"], st["d"], st["rot"]) for i in pos], m)[0]


def plant(rng, fam, m, **kw):
    base = "SL" if fam == "SLA" else ("LK" if fam == "LK" else fam)
    st = MD.random_setting(rng, base, m=m, **kw)
    if fam == "SLA":
        st["B"] = list(st["A"])          # k = A + j*A = (j+1)*A
    pt = "".join(rng.choice(AZ) for _ in range(97))
    return st, pt, MD.encrypt(pt, st)


def test_brute(rng):
    layouts = [[4, 5, 6, 13, 14, 20, 21], [3, 7, 8, 9, 15, 16, 22, 27]]
    tally = {}
    for fam, m, reps in (("SL", 1, 6), ("SL", 2, 2), ("SLA", 1, 4), ("SLA", 3, 4), ("SS", 2, 6), ("SS", 3, 2),
                         ("LK", 2, 8), ("LK", 3, 3)):
        for _ in range(reps):
            pos = rng.choice(layouts)
            kw = {"w": rng.randint(2, 6), "d": rng.choice((1, -1))} if fam == "LK" else {}
            st, pt, ct = plant(rng, fam, m, **kw)
            kind = rng.randrange(3)
            if kind == 1:
                i = rng.choice(pos)
                ct = ct[:i] + rng.choice([x for x in AZ if x != ct[i]]) + ct[i + 1:]
            elif kind == 2:
                ct = "".join(rng.choice(AZ) for _ in range(97))
            b = {"SL": lambda: brute_sl(ct, pt, pos, st, False), "SLA": lambda: brute_sl(ct, pt, pos, st, True),
                 "SS": lambda: brute_ss(ct, pt, pos, st), "LK": lambda: brute_lk(ct, pt, pos, st)}[fam]()
            got = check(fam, ct, pt, pos, st)
            assert b == got, (fam, m, st, pos, b, got)
            if kind == 0:
                assert got
            tally[(fam, b)] = tally.get((fam, b), 0) + 1
    print("1 ok: checks equal exhaustive key search on toy keys:", tally)


def test_plants(rng):
    n = 0
    for fam, m, kw in (("SL", 26, {}), ("SL", 10, {}), ("SLA", 26, {}), ("SLA", 10, {}), ("SS", 25, {}),
                       ("SS", 1, {}), ("LK", 20, {"w": 48, "d": -1, "rot": 1}), ("LK", 20, {"w": 48, "d": -1, "rot": 2}),
                       ("LK", 20, {"w": 2, "d": 1, "rot": 2}), ("LK", 2, {"w": 2, "d": -1, "rot": 1}),
                       ("LK", 20, {"w": 97, "d": 1, "rot": 2})):
        for _ in range(3):
            st, pt, ct = plant(rng, fam, m, **kw)
            assert MD.decrypt(ct, st) == pt
            assert check(fam, ct, pt, R.POS, st), (fam, m, kw)
            n += 1
    print("2 ok:", n, "max-parameter plants feasible under their own setting")


def test_vs_r83(rng):
    import numpy as np
    import exact83 as X
    pos = np.array(R.POS)
    nlx = 0
    for k in range(3):
        c = [rng.randrange(26) for _ in range(97)]
        pk = [rng.randrange(26) for _ in R.POS]
        t = X.Tally(list_min=-99, cap=10 ** 9)
        X.slx(np.array(c), pos, np.array(pk), t)
        X.ssx(np.array(c), pos, np.array(pk), t)
        ct = "".join(AZ[v] for v in c)
        _, mine = R.slots_one(("x", ct, R.POS, pk))
        for fam in ("SLX", "SLX-A", "SSX"):
            old = {(tuple(r["conv"]), r["m"]) for r in t.rows[fam] if r["checks"] >= 3}
            new = {(tuple(r["conv"]), r["m"]) for r in mine[fam]["feasible_ge3"]}
            assert old == new, (fam, len(old), len(new))
            assert {int(a): b for a, b in t.feasible[fam].items() if b} == \
                {int(a): b for a, b in mine[fam]["feasible_by_checks"].items()}, fam
            assert {int(a): b for a, b in t.tested[fam].items()} == \
                {int(a): b for a, b in mine[fam]["tested_by_checks"].items()}, fam
        # LX: 100 random conventions x every cell, cell by cell against exact83.lk_check
        cis = rng.sample(range(len(R.CONVS)), 100)
        convs = [R.CONVS[i] for i in cis]
        assert convs == [X.lk_conventions()[i] for i in cis]
        G, GI = X.lk_maps(np.array(c), pos, np.array(pk), convs)
        maps = [R.lx_edge_maps(c, R.POS, pk, cv) for cv in convs]
        for cell in R.ALL_CELLS:
            m, w, d, rot = cell
            ends = [R.lx_slots(i, m, w, d, rot) for i in R.POS]
            old, ck, _ = X.lk_check(G, GI, [MD.lk_slots(int(p), m, w, d, rot) for p in pos], len(convs))
            for j in range(len(convs)):
                ok, ck2 = R.lx_feasible(maps[j], ends, m)
                assert ok == bool(old[j]) and ck == ck2, (convs[j], cell)
                nlx += 1
    print("3 ok: SLX, SLX-A, SSX equal exact83 in full on 3 random ciphertexts; LX equal on", nlx, "settings")


def main():
    rng = random.Random(83_0616)
    test_brute(rng)
    test_plants(rng)
    test_vs_r83(rng)
    print("T6 L172 EXACT REPLAY TESTS OK")


if __name__ == "__main__":
    main()
