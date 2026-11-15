#!/usr/bin/env python3
"""Synthetic-only, independently calculated F1X feasibility regressions.

No real K4 ciphertext or known-plaintext clue is read. All inputs are
generated inside this file with a separate explicit encryption formula.
Run: python3 -I r75/audit/tests/test_f1x_safe.py
"""
import itertools
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import f1x_safe as S  # noqa: E402

R = random.Random(750915)
PLAINS = ["".join(R.choice(S.AZ) for _ in range(97)) for _ in range(4)]
POS = list(range(9, 21)) + list(range(56, 68))


def independent_encrypt(pt, cfg, first, second):
    pa1, ca1, pa2, ca2, s1, s2 = cfg
    out = []
    for i, ch in enumerate(pt):
        intermediate = S.ALPH[ca1][
            (s1 * S.ALPH[pa1].index(ch) + first[i % len(first)]) % 26
        ]
        out.append(S.ALPH[ca2][
            (s2 * S.ALPH[pa2].index(intermediate) + second[i % len(second)]) % 26
        ])
    return "".join(out)


def independent_bruteforce(c, pt, positions, cfg, m1, m2):
    """Tiny-period oracle, enumerating exactly 26**(m1+m2) full keys."""
    total = 0
    for all_keys in itertools.product(range(26), repeat=m1+m2):
        first, second = all_keys[:m1], all_keys[m1:]
        generated = independent_encrypt(pt, cfg, first, second)
        if all(generated[i] == c[i] for i in positions):
            total += 1
    return total


class SafeF1XTests(unittest.TestCase):
    def test_synthetic_plants_all_tableaux_and_max_periods(self):
        cfgs = (
            ("AZ", "KRY", "PAL", "ABS", 1, -1),
            ("PAL", "ABS", "AZ", "KRY", -1, 1),
            ("ABS", "PAL", "KRY", "AZ", -1, -1),
            ("KRY", "AZ", "ABS", "PAL", 1, 1),
        )
        for cfg in cfgs:
            for m1,m2 in ((1,1),(1,2),(2,3),(5,7),(18,18),(26,26)):
                pt = R.choice(PLAINS)
                k1 = [R.randrange(26) for _ in range(m1)]
                k2 = [R.randrange(26) for _ in range(m2)]
                ct = independent_encrypt(pt, cfg, k1, k2)
                got = S.check_setting(ct, POS, "".join(pt[i] for i in POS), cfg, m1, m2)
                self.assertTrue(got["feasible"], (cfg,m1,m2))
                self.assertGreater(got["total_solution_count"], 0)
                self.assertEqual(got["count_type"], "arbitrary_precision_integer")
                self.assertFalse(got["creates_plaintext"])
                self.assertFalse(got["creates_completed_keys"])
                self.assertGreaterEqual(got["unused_key_slots"], 0)
                self.assertGreaterEqual(got["checks"], 0)

    def test_independent_exhaustive_small_key_oracle(self):
        cfg = ("AZ", "KRY", "PAL", "ABS", 1, -1)
        for m1,m2 in ((1,1),(1,2),(2,1)):
            pt = R.choice(PLAINS)
            k1 = [R.randrange(26) for _ in range(m1)]
            k2 = [R.randrange(26) for _ in range(m2)]
            ct = independent_encrypt(pt, cfg, k1, k2)
            known = "".join(pt[i] for i in POS)
            got = S.check_setting(ct, POS, known, cfg, m1, m2)
            total = independent_bruteforce(ct, pt, POS, cfg, m1, m2)
            self.assertEqual(got["total_solution_count"], total)
            self.assertEqual(got["feasible"], total > 0)

    def test_exact_negative_cycle(self):
        c = "AB" + "A" * 95
        result = S.check_setting(
            c, [0,1], "AA", ("AZ","AZ","AZ","AZ",1,1), 1,1)
        self.assertFalse(result["feasible"])
        self.assertEqual(result["total_solution_count"], 0)
        self.assertEqual(result["checks"], 1)
        self.assertEqual(result["components"], 1)

    def test_nonoverflow_26_to_17_and_unconstrained_periods(self):
        # 17 independent edges, each component has all 26 first-key
        # root possibilities. This must NOT wrap a signed int64 and
        # must NOT trigger candidate/decode enumeration.
        pt = "A" * 97
        got = S.check_setting(
            pt, list(range(17)), "A" * 17,
            ("AZ","AZ","AZ","AZ",1,1),18,18)
        self.assertEqual(got["components"],17)
        self.assertEqual(got["checks"],0)
        self.assertEqual(got["active_solution_count"],26**17)
        self.assertEqual(got["unused_key_slots"],2)
        self.assertEqual(got["total_solution_count"],26**19)
        self.assertGreater(got["active_solution_count"],2**63)

    def test_explicit_bounded_period_list(self):
        c = "A"*97
        cfg=("AZ","KRY","PAL","ABS",1,1)
        with self.assertRaises(ValueError):
            list(S.enumerated_periods(c,[5], "A", cfg))
        v=list(S.enumerated_periods(c,[5],"A",cfg,periods=[(1,1),(26,26)]))
        self.assertEqual([(m1,m2) for m1,m2,_ in v],[(1,1),(26,26)])

    def test_reject_bad_inputs(self):
        cf=("AZ","AZ","AZ","AZ",1,1)
        for args in [
            ("A"*97,[3,3],"AA",cf,1,1),
            ("A"*97,[3,4],"A",cf,1,1),
            ("A"*97,[3],"A",cf,0,1),
            ("A"*97,[3],"A",("MISSING","AZ","AZ","AZ",1,1),1,1),
            ("A"*97,[98],"A",cf,1,1),
            ("A"*97,[3],"*",cf,1,1),
        ]:
            with self.assertRaises(ValueError):
                S.check_setting(*args)


if __name__ == "__main__":
    unittest.main(verbosity=2)
