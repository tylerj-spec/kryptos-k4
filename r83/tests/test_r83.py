#!/usr/bin/env python3
"""R83 unit tests (synthetic only; no K4 data, no published letters; the published POSITIONS are used for layout).
1 round trip: every family's explicit encryptor and decryptor are inverse (r83/models83.py), 300 random settings;
2 brute force: on small keys, each exact check (r83/exact83.py) says FEASIBLE exactly when an exhaustive search over
  every key, run through the explicit encryptor, finds a key that sends the published-position plaintext to the
  ciphertext: planted ciphertexts (feasible) and the same ciphertexts with one published letter changed;
3 plants: the planted setting is listed feasible by its own family's check (20 plants);
4 checks: the positions-only check table agrees with the checks the engines report.
Usage: python3 -I r83/tests/test_r83.py"""
import itertools
import random
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import exact83 as X  # noqa: E402
import models83 as MD  # noqa: E402

AZ = MD.AZ
POS = X.published_positions()
N = 97


def codes(t):
    return np.array([AZ.index(x) for x in t])


def plant(rng, fam, **kw):
    st = MD.random_setting(rng, fam, **kw)
    pt = "".join(rng.choice(AZ) for _ in range(N))
    return st, pt, MD.encrypt(pt, st)


def altered(ct, rng):
    """The same ciphertext with one published position's letter changed."""
    i = int(rng.choice(POS))
    ch = rng.choice([x for x in AZ if x != ct[i]])
    return ct[:i] + ch + ct[i + 1:]


def brute(fam, st, pt, ct):
    """Exhaustive: is there ANY key (and hidden start state) of this setting's shape that sends pt to ct at every
    published position? Uses only the explicit encryptor's per-letter rules."""
    want = {int(p): ct[p] for p in POS}
    if fam == "LK":
        m = len(st["x"])
        for x in itertools.product(range(26), repeat=m):
            s2 = {**st, "x": list(x)}
            pa1, ca1, pa2, ca2, s1, s_2, t2, ka1, ka2 = s2["conv"]
            pi = MD.lk_pi(ka1, ka2)
            ok = True
            for i in POS:
                a, b = MD.lk_slots(int(i), m, st["w"], st["d"], st["rot"])
                q = MD.enc1(pt[i], x[a], pa1, ca1, s1)
                if MD.enc1(q, t2 * pi[x[b]], pa2, ca2, s_2) != want[int(i)]:
                    ok = False
                    break
            if ok:
                return True
        return False
    pa, ca, s = st["conv"][:2] + (st["conv"][-1],)
    kneed = {int(i): MD.key_value(pt[i], ct[i], pa, ca, s) for i in POS}
    if fam == "PF":
        m, L = len(st["U"]), st["L"]
        idx = [int(i) for i in POS if int(i) - L in kneed]
        for U in itertools.product(range(26), repeat=m):
            if all((U[i % m] + st["f"] * MD.ix(st["beta"], pt[i - L])) % 26 == kneed[i] for i in idx):
                return True
        return False
    if fam == "WP":
        m = len(st["U"])
        runs = [list(range(21, 34)), list(range(63, 74))]
        for u1 in range(m):
            for u2 in range(m):
                need, ok = {}, True
                for run, u in zip(runs, (u1, u2)):
                    ptr = u
                    for i in run:
                        if need.setdefault(ptr, kneed[i]) != kneed[i]:
                            ok = False
                        ptr = (ptr + st["d"] * (MD.ix(st["alpha"], pt[i]) + st["e"])) % m
                if ok:
                    return True
        return False
    if fam == "SL":
        m = len(st["A"])
        for r in range(m):
            es = [int(i) for i in POS if int(i) % m == r]
            if es and not any(all((a + (i // m) * b) % 26 == kneed[i] for i in es)
                              for a in range(26) for b in range(26)):
                return False
        return True
    if fam == "SS":
        m = len(st["W"])
        for W in itertools.product(AZ, repeat=m):
            ks = MD.ss_keys(N, {**st, "W": "".join(W)})
            if all(ks[i] == kneed[i] for i in kneed):
                return True
        return False
    raise ValueError(fam)


def engine(fam, st, ct, pt):
    """The exact check's verdict for exactly this setting."""
    c, p = codes(ct), codes(pt)
    return X.setting_feasible(fam, st, c, POS, p[POS])


def main():
    rng = random.Random(830900)
    for _ in range(300):
        fam = rng.choice(("LK", "PF", "WP", "SL", "SS"))
        st, pt, ct = plant(rng, fam)
        assert MD.decrypt(ct, st) == pt, fam
    print("1 ok: round trip, 300 settings")

    agree = {}
    for fam, m, reps in (("LK", 2, 6), ("LK", 3, 3), ("PF", 2, 6), ("PF", 3, 3), ("WP", 3, 6), ("WP", 7, 4),
                         ("SL", 3, 6), ("SL", 9, 4), ("SS", 2, 6), ("SS", 3, 2)):
        for _ in range(reps):
            st, pt, ct = plant(rng, fam, m=m)
            for target, expect in ((ct, True), (altered(ct, rng), None)):
                b, e = brute(fam, st, pt, target), engine(fam, st, target, pt)
                assert b == e, (fam, m, st, b, e)
                if expect:
                    assert e
                agree[fam] = agree.get(fam, 0) + 1
    print("2 ok: exact checks equal exhaustive search,", agree)

    found = 0
    for fam in ("LK", "PF", "WP", "SL", "SS"):
        for _ in range(4):
            st, pt, ct = plant(rng, fam, m=rng.randint(2, 8))
            found += engine(fam, st, ct, pt)
    assert found == 20
    print("3 ok: 20/20 plants feasible under their own setting")

    tab = X.check_table()
    G = np.zeros((1, len(POS), 26), dtype=np.int16)
    for rot in (1, 2):
        for m, w in ((5, 7), (12, 31), (9, 11)):
            ends = [MD.lk_slots(int(i), m, w, 1, rot) for i in POS]
            assert tab[f"LX_rot{rot}_d1"][m][w] == X.lk_check(G, G, ends, 1)[1]
    print("4 ok: check table matches the engine")
    print("R83 TESTS OK")


if __name__ == "__main__":
    main()
