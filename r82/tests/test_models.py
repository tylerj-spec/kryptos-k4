#!/usr/bin/env python3
"""Synthetic-only tests for reversible R82 models. Run: python3 -I r82/tests/test_models.py

Never loads real K4, publicly known K4 plaintext, or any repository source
outside r82/. The tests are capability/sanity checks, not an R82 sealed gate.
"""
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import models as M  # noqa: E402

RNG = random.Random(820082)
SAMPLE = (
    "THEMESSAGEWASPREPAREDINORDINARYENGLISHANDWRITTENBYHAND"
    "THEWRITERTHENAPPLIEDASEQUENCEOFSIMPLECIPHEROPERATIONS"
    "TOOBSCURETHELANGUAGEDISTRIBUTIONWITHOUTAMACHINE"
)
PLAINS = [SAMPLE[:97], "".join(RNG.choice(M.AZ) for _ in range(97))]
assert all(len(t) == 97 for t in PLAINS)


class SyntheticModels(unittest.TestCase):
    def test_bijective_alphabets(self):
        for name in M.ALPH:
            self.assertEqual(len(M.alphabet(name)), 26)
            self.assertEqual(set(M.alphabet(name)), set(M.AZ))

    def test_fractionation_round_trip_and_margins(self):
        for a in M.ALPH:
            for b in (2, 3, 4, 7, 10, 13, 16, 25):
                for row, col in (("id", "rev"), ("rot1", "id"),
                                 ("evenodd", "rev"), ("rev", "rev")):
                    for pt in PLAINS:
                        ct = M.frac26_encrypt(pt, a, b, row, col)
                        self.assertEqual(len(ct), 97)
                        self.assertEqual(M.frac26_decrypt(ct, a, b, row, col), pt)
                        self.assertEqual(M.frac26_margins(ct, a, b),
                                         M.frac26_margins(pt, a, b))
                        if row == col:
                            expected = "".join(
                                part[j] for off in range(0, len(pt), b)
                                for part in [pt[off:off + b]]
                                for j in M.permutation(len(part), row)
                            )
                            self.assertEqual(ct, expected)

    def test_fractionation_is_not_generally_pure_transposition(self):
        pt = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 3 + "ABCDEFGHIJKLMNOPQRS"
        self.assertEqual(len(pt), 97)
        ct = M.frac26_encrypt(pt, "AZ", 7, "id", "rev")
        self.assertNotEqual(sorted(ct), sorted(pt))
        self.assertEqual(M.frac26_decrypt(ct, "AZ", 7, "id", "rev"), pt)

    def test_distinct_tableaux_round_trip(self):
        for a1 in M.ALPH:
            for a2 in M.ALPH:
                if a1 == a2:
                    continue
                for sign1 in (-1, 1):
                    for sign2 in (-1, 1):
                        first = M.Stage("AZ", a1, "PALIMPSEST", sign1)
                        second = M.Stage(a2, "ABS", "FRACTION", sign2)
                        for pt in PLAINS:
                            ct = M.two_tableau_encrypt(pt, first, second)
                            self.assertEqual(M.two_tableau_decrypt(ct, first, second), pt)

    def test_no_exact_equivalent_key_pairs_in_named_tableaux(self):
        # Verify fixed-letter substitution distinctness for all 12 ordered
        # intermediate-alphabet pairs. This does NOT imply blind recoverability.
        for a1 in M.ALPH:
            for a2 in M.ALPH:
                if a1 == a2:
                    continue
                x, y = M.alphabet(a1), M.alphabet(a2)
                signatures = set()
                for k1 in range(26):
                    for k2 in range(26):
                        signature = tuple((y.index(x[(p + k1) % 26]) + k2) % 26
                                          for p in range(26))
                        self.assertNotIn(signature, signatures)
                        signatures.add(signature)
                self.assertEqual(len(signatures), 676)

    def test_same_intermediate_tableau_rejected(self):
        first = M.Stage("AZ", "KRY", "AMBER")
        second = M.Stage("KRY", "AZ", "RIVER")
        with self.assertRaises(ValueError):
            M.two_tableau_encrypt(PLAINS[0], first, second)

    def test_evolving_keys_round_trip_and_key_cancellation(self):
        for a in M.ALPH:
            for period in range(1, 13):
                initial = [RNG.randrange(26) for _ in range(period)]
                increments = [RNG.randrange(26) for _ in range(period)]
                for sign in (-1, 1):
                    for pt in PLAINS:
                        ct = M.evolving_encrypt(pt, a, initial, increments, sign)
                        self.assertEqual(M.evolving_decrypt(ct, a, initial, increments, sign), pt)
                        dp = M.second_differences(pt, a, period)
                        dc = M.second_differences(ct, a, period)
                        self.assertEqual(dc, [(sign * v) % 26 for v in dp])

    def test_old_transposition_models_as_controls(self):
        for width in range(2, 14):
            for snake in (False, True):
                route = M.column_route(97, width, snake)
                self.assertEqual(sorted(route), list(range(97)))
                for pt in PLAINS:
                    self.assertEqual(M.untranspose(M.transpose(pt, route), route), pt)
                    stage = M.Stage("AZ", "KRY", "TOWER", -1)
                    ct_sub_then_route = M.transpose(M.stage_encrypt(pt, stage), route)
                    ct_route_then_sub = M.stage_encrypt(M.transpose(pt, route), stage)
                    self.assertEqual(
                        M.stage_decrypt(M.untranspose(ct_sub_then_route, route), stage), pt)
                    self.assertEqual(
                        M.untranspose(M.stage_decrypt(ct_route_then_sub, stage), route), pt)


if __name__ == "__main__":
    unittest.main(verbosity=2)
