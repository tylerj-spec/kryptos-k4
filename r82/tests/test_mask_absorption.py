#!/usr/bin/env python3
"""R82 synthetic theorem: reversible letter-for-letter pre-masking is just
a change of the plaintext alphabet, not a new cipher layer.

No K4 ciphertext, published K4 plaintext or positions are accessed.
Run: python3 -I r82/tests/test_mask_absorption.py
"""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import models as M


def swaps():
    z = {x:x for x in M.AZ}
    for a,b in (("V","W"),("C","K"),("I","J")):
        z[a],z[b] = z[b],z[a]
    assert set(z.values()) == set(M.AZ)
    return z


class MaskAbsorption(unittest.TestCase):
    def test_bijective_letter_map_can_be_absorbed_into_plain_chart(self):
        mask = swaps()
        unmask = {v:k for k,v in mask.items()}
        message = ("WEWROTEEVERYLETTERONPAPERANDTURNEDTHEALPHABET"
                   "OVERTODEMONSTRATETHEHIDDENDEPENDENCYBETWEENALPHABETTABLES"
                   "ANDKEYS")[:97]
        for pchart in M.ALPH:
            old = M.alphabet(pchart)
            replacement_chart = "".join(unmask[ch] for ch in old)
            assert set(replacement_chart)==set(M.AZ)
            transformed = "".join(mask[ch] for ch in message)
            for cchart in M.ALPH:
                for sign in (-1,1):
                    for key in ("MARBLE","PAPERWORK"):
                        baseline = M.Stage(pchart,cchart,key,sign)
                        rewritten = M.Stage(replacement_chart,cchart,key,sign)
                        self.assertEqual(
                            M.stage_encrypt(transformed,baseline),
                            M.stage_encrypt(message,rewritten))
                        self.assertEqual(
                            M.stage_decrypt(M.stage_encrypt(message,rewritten),rewritten),
                            message)

    def test_noninjective_single_letter_replacement_is_not_reversible(self):
        def badmask(ch):
            return "W" if ch in ("V","W") else ch
        self.assertEqual(badmask("V"), badmask("W"))
        for ca in M.ALPH:
            st=M.Stage("AZ",ca,"MARBLE")
            self.assertEqual(
                M.stage_encrypt(badmask("V"),st),
                M.stage_encrypt(badmask("W"),st))


if __name__=="__main__":
    unittest.main(verbosity=2)
