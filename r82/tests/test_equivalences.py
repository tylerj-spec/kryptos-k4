#!/usr/bin/env python3
"""R82 synthetic-only exact algebraic equivalence tests E1, E2, E3.

These prove redundancies in the reference 2x13 coordinate-cipher model.
They do not read K4 or use any known plaintext clues.
Run: python3 -I r82/tests/test_equivalences.py
"""
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import models as M

R = random.Random(821319)
PLAINS = [
    ("THECOMPONENTSAREREARRANGEDBYTWOINDEPENDENTROUTESAND"
     "THENRECOMBINEDWITHALPHABETICCOORDINATESINORDER" * 2)[:97],
    "".join(R.choice(M.AZ) for _ in range(97)),
]


def relabeled_alphabet(a, row_swap, column_permutation):
    """A'[13*sigma(r)+tau(c)] = A[13*r+c]."""
    out = [None] * 26
    for i, ch in enumerate(a):
        row, col = divmod(i, 13)
        rr = 1 - row if row_swap else row
        out[13 * rr + column_permutation[col]] = ch
    assert len(out) == 26 and set(out) == set(M.AZ)
    return "".join(out)


def relative_route_canonical(pt, a, b, row, column):
    """Canonical row=identity output plus an overall whole-letter route.

    In each block y[j] = (R[pr[j]], C[pc[j]]).
    The canonical output w[i] = (R[i], C[pc[pr^-1[i]]]).
    The original y is simply w[pr[j]].
    """
    a = M.alphabet(a)
    out = []
    for off in range(0, len(pt), b):
        chunk = pt[off:off + b]
        n = len(chunk)
        pr, pc = M.permutation(n, row), M.permutation(n, column)
        invpr = [None] * n
        for j, i in enumerate(pr):
            invpr[i] = j
        rc = [divmod(a.index(ch), 13) for ch in chunk]
        canonical = [a[13 * rc[i][0] + rc[pc[invpr[i]]][1]] for i in range(n)]
        out.extend(canonical[pr[j]] for j in range(n))
    return "".join(out)


class Equivalences(unittest.TestCase):
    def test_e1_independent_row_column_relabeling(self):
        # Two distinct affine permutations of the 13 column names.
        permuts = [
            [(7 * i + 3) % 13 for i in range(13)],
            [(5 * i + 9) % 13 for i in range(13)],
        ]
        for a in M.ALPH:
            for row_swap in (False, True):
                for tau in permuts:
                    a2 = relabeled_alphabet(M.alphabet(a), row_swap, tau)
                    for b in (2, 3, 7, 13, 16):
                        for rr, rc in (("id", "rev"), ("rev", "rot1"),
                                       ("evenodd", "id"), ("rot1", "evenodd")):
                            for pt in PLAINS:
                                self.assertEqual(
                                    M.frac26_encrypt(pt, a, b, rr, rc),
                                    M.frac26_encrypt(pt, a2, b, rr, rc))
                                self.assertEqual(
                                    M.frac26_decrypt(M.frac26_encrypt(pt, a, b, rr, rc),
                                                     a2, b, rr, rc), pt)

    def test_e2_relative_route_and_whole_letter_transposition(self):
        for a in M.ALPH:
            for b in (2, 3, 7, 13, 16, 25):
                for rr in ("id", "rev", "rot1", "evenodd"):
                    for rc in ("id", "rev", "rot1", "evenodd"):
                        for pt in PLAINS:
                            self.assertEqual(
                                M.frac26_encrypt(pt, a, b, rr, rc),
                                relative_route_canonical(pt, M.alphabet(a), b, rr, rc))

    def test_e3_global_and_blockwise_marginal_conservation(self):
        for a in M.ALPH:
            for b in (3, 7, 13):
                for rr, rc in (("id", "rev"), ("rot1", "evenodd")):
                    for pt in PLAINS:
                        enc = M.frac26_encrypt(pt, a, b, rr, rc)
                        self.assertEqual(
                            M.frac26_margins(enc, a, b),
                            M.frac26_margins(pt, a, b))
                        self.assertEqual(
                            M.frac26_margins(enc, a, 97),
                            M.frac26_margins(pt, a, 97))
                        self.assertEqual(M.frac26_decrypt(enc, a, b, rr, rc), pt)


if __name__ == "__main__":
    unittest.main(verbosity=2)
