#!/usr/bin/env python3
"""R82 linked-key adversarial synthetic tests, no actual K4 data.

Run: python3 -I r82/tests/test_linked_key.py
An ordinary period-m substitution is included as a false-attribution
control; the collision diagnostic MUST NOT identify only linked-key.
"""
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import models as M  # noqa: E402
import linked_key as L  # noqa: E402

R = random.Random(820983)
PT = ("THECODEISMADEONPAPERWITHONEKEYANDTWODIFFERENTALPHABETTABLES"
      "THENEXTROWMOVESTHEKEYBYONEPOSITIONANDCHANGESHOWLETTERSLOOK" * 2)[:97]
assert len(PT) == 97


def stage_pair(key, s1=1, s2=1, a1="KRY", a2="AZ"):
    return M.Stage("AZ", a1, key, s1), M.Stage(a2, "PAL", key, s2)


class LinkedKeyTests(unittest.TestCase):
    def test_round_trip_all_alphabets_and_signs(self):
        keys = ("CAT", "SILVER", "ORCHARD", "ABCDEFGHIJKL")
        for key in keys:
            for a1 in M.ALPH:
                for a2 in M.ALPH:
                    if a1 == a2:
                        continue
                    for s1, s2 in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
                        first, second = stage_pair(key, s1, s2, a1, a2)
                        for w in (4, 9, 11, 31, 97):
                            ct = L.encrypt(PT, first, second, w)
                            self.assertEqual(len(ct), 97)
                            self.assertEqual(L.decrypt(ct, first, second, w), PT)
                            _, violations = L.equality_mismatches(PT, ct, len(key), w)
                            self.assertEqual(violations, [], (key, a1, a2, w))

    def test_independent_formula_implementation(self):
        key = "MARBLE"
        first, second = stage_pair(key, -1, 1, "KRY", "AZ")
        ct = L.encrypt(PT, first, second, 31)
        a1, b1 = M.alphabet(first.plain), M.alphabet(first.cipher)
        a2, b2 = M.alphabet(second.plain), M.alphabet(second.cipher)
        expected = []
        for pos, ch in enumerate(PT):
            i1 = pos % len(key)
            i2 = (pos + (pos // 31)) % len(key)
            u = b1[(first.sign * a1.index(ch) + M.AZ.index(key[i1])) % 26]
            expected.append(b2[(second.sign * a2.index(u) + M.AZ.index(key[i2])) % 26])
        self.assertEqual(ct, "".join(expected))
        wrong_width = L.decrypt(ct, first, second, 30)
        self.assertNotEqual(wrong_width, PT)

    def test_joint_slot_period_is_product_for_nonconstant_key(self):
        for m in range(2, 8):
            for width in range(1, 10):
                period = m * width
                self.assertEqual(L.schedule_period(m, width), period)
                src = [L.slots(i, m, width) for i in range(3 * period)]
                self.assertEqual(src[:period], src[period:2 * period])
                # Assert no smaller period for the FULL ordered pair schedule.
                for candidate in range(1, period):
                    self.assertTrue(any(src[i] != src[i + candidate]
                                        for i in range(2 * period)), (m, width, candidate))
        self.assertEqual(L.schedule_period(1, 31), 1)

    def test_low_power_structural_pairs_are_countable(self):
        self.assertEqual(len(list(L.comparison_pairs(97, 9, 11))), 16)
        self.assertEqual(len(list(L.comparison_pairs(97, 9, 31))), 117)
        self.assertEqual(len(list(L.comparison_pairs(97, 5, 31))), 243)

    def test_collision_invariant_is_not_a_unique_method_detector(self):
        # Ordinary period-m Vigenere is a WRONG-FAMILY control that passes
        # the SAME collision invariant. Thus collision alone does NOT
        # demonstrate a linked-key two-tableau construction.
        for key in ("MARBLE", "THUNDER", "COLUMNS"):
            m = len(key)
            simple = M.Stage("AZ", "KRY", key, 1)
            ct = M.stage_encrypt(PT, simple)
            for width in (9, 11, 31):
                comparisons, bad = L.equality_mismatches(PT, ct, m, width)
                self.assertEqual(bad, [])
                self.assertGreaterEqual(comparisons, 0)

    def test_must_reject_corrupted_same_pair_identity(self):
        first, second = stage_pair("SILVER", 1, -1)
        pt = "A" * 97
        ct = L.encrypt(pt, first, second, 31)
        pairs = list(L.comparison_pairs(97, 6, 31))
        self.assertTrue(pairs)
        i, j = pairs[0]
        self.assertEqual(ct[i], ct[j])
        changed = list(ct)
        changed[i] = M.AZ[(M.AZ.index(changed[i]) + 1) % 26]
        comparisons, bad = L.equality_mismatches(pt, "".join(changed), 6, 31)
        self.assertGreater(len(bad), 0)
        self.assertGreater(comparisons, 0)

    def test_invalid_degenerate_models_are_rejected(self):
        a = M.Stage("AZ", "KRY", "MARBLE")
        b = M.Stage("KRY", "PAL", "MARBLE")
        with self.assertRaises(ValueError):
            L.encrypt(PT, a, b, 31)
        with self.assertRaises(ValueError):
            L.encrypt(PT, a, M.Stage("AZ", "PAL", "OTHER"), 31)
        with self.assertRaises(ValueError):
            L.encrypt(PT, a, M.Stage("AZ", "PAL", "MARBLE"), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
