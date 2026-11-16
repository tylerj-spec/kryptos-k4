#!/usr/bin/env python3
"""Tests for r83/audit/exact_drop.py (T1). Synthetic only: no K4 ciphertext and no published letters are read.
K4's published POSITIONS (0-based 21-33, 63-73) are used for layout in the 97-letter plants, as r83/tests does.

1 brute force, toy sizes: for every published position b, the checker's exact and drop_excl verdicts equal an
  exhaustive search over every key U (m <= 3), every start pointer per run (WP), and every trial letter x, done with
  the reference per-letter encryptor of r83/models83.py, under the same semantics (published positions only).
2 true-model soundness, toy sizes: exhaustive search over U, start pointer / primer, with FULL decryption of the toy
  ciphertext (unpublished letters fixed by decryption). Whatever is feasible there must be feasible in the checker.
3 planted 97-letter messages at the largest parameters (WP m = 26; PF m = 26 and lag 12, plus lags 1 and 4), one
  PLAINTEXT letter wrong at the first, last and interior published positions, ciphertext enciphered from the TRUE
  plaintext: the true setting must survive drop-one at that position.
4 the two counterexamples of r83/audit/plaintext_drop.py --synthetic (and its extra corrupted positions) survive.
5 the exact checker's x = published case equals R83a's original exact83 PFX/WPX masks on random ciphertexts (a second
  implementation of the EXACT step), and every exact drop-one survivor is also a survivor of the conservative
  necessary-only checker in r83/audit/plaintext_drop.py.
Usage: python3 -I r83/audit/tests/test_exact_drop.py"""
import random
import sys
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "r83" / "audit"), str(ROOT / "r83"), str(ROOT / "r75")]
import exact_drop as ED  # noqa: E402
import models83 as MD  # noqa: E402

AZ = MD.AZ
K4POS = list(range(21, 34)) + list(range(63, 74))


def L2C(t):
    return [AZ.index(ch) for ch in t]


# ------------------------------------------------------------------------------------------------ brute forces
def wp_runs(pos):
    out = []
    for p in pos:
        if out and p == out[-1][-1] + 1:
            out[-1].append(p)
        else:
            out.append([p])
    return out


def brute_wp(ct, pos, letters, st, m):
    """Exhaustive over U in 26^m, a start pointer per run, letters as given (published-position semantics)."""
    pa, ca, s = st["conv"]
    R = wp_runs(pos)
    lt = dict(zip(pos, letters))
    for U in product(range(26), repeat=m):
        ok_all = True
        for run in R:
            ok_run = False
            for start in range(m):
                ptr, ok = start, True
                for i in run:
                    if MD.enc1(lt[i], U[ptr], pa, ca, s) != ct[i]:
                        ok = False
                        break
                    ptr = (ptr + st["d"] * (MD.ix(st["alpha"], lt[i]) + st["e"])) % m
                if ok:
                    ok_run = True
                    break
            if not ok_run:
                ok_all = False
                break
        if ok_all:
            return True
    return False


def brute_pf(ct, pos, letters, st, m):
    pa, ca, s = st["conv"]
    lt = dict(zip(pos, letters))
    L = st["L"]
    eqs = [i for i in pos if i - L in lt]
    for U in product(range(26), repeat=m):
        if all(MD.enc1(lt[i], (U[i % m] + st["f"] * MD.ix(st["beta"], lt[i - L])) % 26, pa, ca, s) == ct[i]
               for i in eqs):
            return True
    return False


def brute_drop(brute, ct, pos, pk, st, m):
    """(exact, drop_excl per position) by exhaustive search, trying every x != published at each position."""
    ex = brute(ct, pos, pk, st, m)
    dx = []
    for b in range(len(pos)):
        hit = False
        for x in AZ:
            if x == pk[b]:
                continue
            alt = list(pk)
            alt[b] = x
            if brute(ct, pos, alt, st, m):
                hit = True
                break
        dx.append(hit)
    return ex, dx


def checker(fam, ct, pos, pk, st, m):
    c, p = L2C(ct), L2C("".join(pk))
    if fam == "WP":
        return ED.wpx_setting(c, pos, p, st["conv"], st["alpha"], st["e"], st["d"], m)
    return ED.pfx_setting(c, pos, p, st["conv"], st["beta"], st["f"], st["L"], m)


def test_brute(rng):
    layouts = [[3, 4, 5, 10, 11], [2, 3, 4, 5, 12, 13, 14]]
    n, kinds = 0, {"exact_T": 0, "exact_F": 0, "drop_T": 0, "drop_F": 0}
    for fam, m, reps in (("WP", 2, 10), ("WP", 3, 2), ("PF", 1, 6), ("PF", 2, 8), ("PF", 3, 3)):
        for _ in range(reps):
            pos = rng.choice(layouts)
            N = 16
            st = MD.random_setting(rng, fam, m=m)
            if fam == "PF":
                st["L"] = rng.choice((1, 2, 3, 7))
                st["primer"] = "".join(rng.choice(AZ) for _ in range(st["L"]))
            pt = "".join(rng.choice(AZ) for _ in range(N))
            ct = MD.encrypt(pt, st)
            pk = [pt[i] for i in pos]
            kind = rng.randrange(3)
            if kind == 1:                      # one published plaintext letter wrong (ciphertext from the true text)
                b = rng.randrange(len(pos))
                pk[b] = rng.choice([x for x in AZ if x != pk[b]])
            elif kind == 2:                    # random ciphertext
                ct = "".join(rng.choice(AZ) for _ in range(N))
            want = brute_drop(brute_wp if fam == "WP" else brute_pf, ct, pos, pk, st, m)
            got = checker(fam, ct, pos, pk, st, m)
            assert want == got, (fam, m, st, pos, want, got)
            kinds["exact_T" if want[0] else "exact_F"] += 1
            kinds["drop_T"] += sum(want[1])
            kinds["drop_F"] += len(want[1]) - sum(want[1])
            n += 1
    print("1 ok: checker equals exhaustive search on", n, "toy settings x every position;", kinds)
    return kinds


def test_true_model(rng):
    """Full-decryption exhaustive search on toy sizes: true feasibility implies checker feasibility."""
    pos = [3, 4, 5, 9, 10, 11]
    N = 14
    n_true = 0
    for fam, m, L in (("WP", 2, None), ("WP", 3, None), ("PF", 1, 1), ("PF", 1, 2), ("PF", 2, 1)) * 3:
        st = MD.random_setting(rng, fam, m=m)
        if fam == "PF":
            st["L"] = L
            st["primer"] = "".join(rng.choice(AZ) for _ in range(L))
        pt = "".join(rng.choice(AZ) for _ in range(N))
        ct = MD.encrypt(pt, st)
        if rng.random() < 0.5:
            ct = "".join(rng.choice(AZ) for _ in range(N))
        pk = [pt[i] for i in pos]
        if rng.random() < 0.5:
            b0 = rng.randrange(len(pos))
            pk[b0] = rng.choice([x for x in AZ if x != pk[b0]])
        ex, dx = checker(fam, ct, pos, pk, st, m)
        if fam == "WP":
            hidden = [{**st, "U": list(U), "ptr0": p0} for U in product(range(26), repeat=m) for p0 in range(m)]
        else:
            hidden = [{**st, "U": list(U), "primer": "".join(pr)} for U in product(range(26), repeat=m)
                      for pr in product(AZ, repeat=st["L"])]
        for h in hidden:
            dec = MD.decrypt(ct, h)
            wrong = [k for k, i in enumerate(pos) if dec[i] != pk[k]]
            if not wrong:
                assert ex, (fam, st, "true exact feasible but checker says no")
                n_true += 1
            elif len(wrong) == 1:
                assert dx[wrong[0]], (fam, st, wrong, "true one-error feasible but checker says no")
                n_true += 1
    print("2 ok: every true-model (full decryption) feasible case is feasible in the checker;", n_true, "cases")
    return n_true


def test_plants(rng):
    out = []
    for fam, m, L in (("WP", 26, None), ("WP", 26, None), ("WP", 13, None), ("PF", 26, 12), ("PF", 26, 1),
                      ("PF", 13, 4), ("PF", 26, 4)):
        st = MD.random_setting(rng, fam, m=m)
        if fam == "PF":
            st["L"] = L
            st["primer"] = "".join(rng.choice(AZ) for _ in range(L))
        pt = "".join(rng.choice(AZ) for _ in range(97))
        ct = MD.encrypt(pt, st)
        assert MD.decrypt(ct, st) == pt
        for bpos in (21, 33, 63, 73, 27, 66):
            b = K4POS.index(bpos)
            pk = [pt[i] for i in K4POS]
            pk[b] = rng.choice([x for x in AZ if x != pk[b]])
            ex, dx = checker(fam, ct, K4POS, pk, st, m)
            assert dx[b], (fam, m, L, bpos)
            out.append((fam, m, L, bpos, ex))
        ex0, _ = checker(fam, ct, K4POS, [pt[i] for i in K4POS], st, m)
        assert ex0
    strict = sum(1 for o in out if not o[4])
    print("3 ok: true setting survives drop-one at the wrong letter in", len(out), "max-parameter plants;",
          strict, "of them infeasible as they stand (the error matters)")
    return len(out), strict


def test_counterexamples(rng):
    pos = list(range(9, 21)) + list(range(56, 68))
    pt = "A" * 97
    st_pf = {"fam": "PF", "conv": ("AZ", "AZ", 1), "U": [0, 3, 7], "L": 1, "beta": "AZ", "f": 1, "primer": "A"}
    st_wp = {"fam": "WP", "conv": ("AZ", "AZ", 1), "U": [0, 5, 11], "alpha": "AZ", "e": 1, "d": 1, "ptr0": 0}
    res = {}
    for st in (st_pf, st_wp):
        ct = MD.encrypt(pt, st)
        for bpos in (11, 9, 10, 12, 17, 56, 57, 66):
            pk = ["A"] * len(pos)
            b = pos.index(bpos)
            pk[b] = "B" if bpos == 11 else AZ[rng.randrange(1, 26)]
            ex, dx = checker(st["fam"], ct, pos, pk, st, len(st["U"]))
            assert dx[b], (st["fam"], bpos)
            res[(st["fam"], bpos)] = ex
    assert not res[("PF", 11)] and not res[("WP", 11)], res
    print("4 ok: both plaintext_drop.py counterexamples (and the extra positions) survive; at 11 both are "
          "infeasible as they stand")


def test_vs_r83_and_conservative(rng):
    import numpy as np
    import exact83 as X
    import plaintext_drop as PD
    pos = np.array(K4POS)
    n_cmp = n_sub = 0
    for _ in range(3):
        c = [rng.randrange(26) for _ in range(97)]
        pk = [rng.randrange(26) for _ in K4POS]
        cn, pkn = np.array(c), np.array(pk)
        # R83a EXACT masks, recomputed by the original engine (its feasible list, uncapped)
        t = X.Tally(list_min=-99, cap=10 ** 9)
        X.wpx(cn, pos, pkn, t)
        X.pfx(cn, pos, pkn, t)
        old_w = {(tuple(r["conv"]), r["alpha"], r["e"], r["d"], r["m"]) for r in t.rows["WPX"]}
        old_p = {(tuple(r["conv"]), r["beta"], r["f"], r["L"], r["m"]) for r in t.rows["PFX"]}
        w = ED.wpx_scan(c, K4POS, pk)
        p = ED.pfx_scan(c, K4POS, pk)
        new_w = {(ED.CONV1[b], r["alpha"], r["e"], r["d"], r["m"]) for r in w for b in ED.bits(r["exact"])}
        new_p = set()
        for r in p:
            for b in ED.bits(r["exact"]):
                cv, beta, f = ED.PF_CONV[b]
                new_p.add((cv, beta, f, r["L"], r["m"]))
        # exact83.pfx lists only cells with at least one constrained position, as does pfx_scan
        assert old_w == new_w, (len(old_w), len(new_w))
        assert old_p == new_p, (len(old_p), len(new_p))
        n_cmp += 1
        # every exact drop survivor is a conservative survivor
        for r in w:
            for b, v in enumerate(r["drop_excl"]):
                for bit in ED.bits(v):
                    assert PD.wpx_necessary_after_unknown_plaintext(cn, pos, pkn, ED.CONV1[bit], r["alpha"], r["e"],
                                                                   r["d"], r["m"], K4POS[b])
                    n_sub += 1
        for r in p:
            for b, v in enumerate(r["drop_excl"]):
                for bit in ED.bits(v):
                    cv, beta, f = ED.PF_CONV[bit]
                    assert PD.pfx_possible_after_unknown_plaintext(cn, pos, pkn, cv, beta, f, r["L"], r["m"],
                                                                   K4POS[b])
                    n_sub += 1
    print("5 ok: EXACT step equals R83a's exact83 on", n_cmp, "random ciphertexts (WPX and PFX);",
          n_sub, "exact drop survivors all inside the conservative bound")


def main():
    rng = random.Random(83_1115)
    test_brute(rng)
    test_true_model(rng)
    test_plants(rng)
    test_counterexamples(rng)
    test_vs_r83_and_conservative(rng)
    print("T1 EXACT-DROP TESTS OK")


if __name__ == "__main__":
    main()
