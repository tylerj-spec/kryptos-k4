#!/usr/bin/env python3
"""R67 synthetic-only unit tests. No published K4 plaintext or known offsets."""
import hashlib
import importlib.util
import random
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'r67/sealed/make_controls.py'
spec = importlib.util.spec_from_file_location('r67_controls', SOURCE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class R67ControlsTests(unittest.TestCase):
    def test_alphabets_and_conventions_invert(self):
        for alphabet in (m.AZ, m.KRY):
            ix = {c: i for i, c in enumerate(alphabet)}
            p = alphabet * 4
            k = alphabet[::-1] * 4
            for op in ('VIG', 'BEAU', 'VARB'):
                ct = m.encrypt(p, k, alphabet, op)
                recovered = ''
                for c, b in zip(ct, k):
                    x, y = ix[c], ix[b]
                    if op == 'VIG':
                        value = x - y
                    elif op == 'BEAU':
                        value = y - x
                    else:
                        value = x + y
                    recovered += alphabet[value % 26]
                self.assertEqual(recovered, p)

    def test_routes_exact_bijections(self):
        routes = m.load_routes()
        self.assertEqual(len(routes), 10)
        for name, perm in routes:
            self.assertEqual(len(perm), 97, name)
            self.assertEqual(sorted(perm), list(range(97)), name)
            seq = ''.join(chr(33 + (i % 90)) for i in range(97))
            scrambled = m.transpose(seq, (name, perm))
            restored = [''] * 97
            for j, src in enumerate(perm):
                restored[src] = scrambled[j]
            self.assertEqual(''.join(restored), seq)

    def test_homophonic_is_fixed_letter_map(self):
        p = ''.join(random.Random(44 + i).choice(m.AZ) for i in range(97))
        ct, mapping = m.homophonic(p, random.Random(67))
        self.assertEqual(len(ct), 97)
        inverse = {cipher: plain for plain, ciphers in mapping.items() for cipher in ciphers}
        self.assertEqual(''.join(inverse[c] for c in ct), p)
        self.assertEqual(len(inverse), len(set(inverse)))
        self.assertLessEqual(max(map(len, mapping.values())), 4)

    def test_sampled_cipher_family_lengths(self):
        routes = m.load_routes()
        r = random.Random(6107)
        rng_data = random.Random(44)
        letters = m.AZ
        en = ''.join(rng_data.choices(letters, k=1200))
        de = ''.join(rng_data.choices(letters, k=1200))
        for family in m.FAMILIES:
            ciphertext, truth = m.make_case(family, en, de, r, routes)
            self.assertEqual(len(ciphertext), 97, family)
            self.assertTrue(set(ciphertext) <= set(m.AZ), family)
            self.assertEqual(len(truth['plaintext']), 97)
        for route in routes:
            ciphertext, truth = m.positive_case(en, de, r, route, (m.KRY, 'BEAU'))
            self.assertEqual(len(ciphertext), 97)
            self.assertEqual(truth['route'], route[0])
            self.assertEqual(
                ciphertext,
                m.transpose(m.encrypt(truth['plaintext'], truth['key'],
                                      truth['alphabet'], truth['operation']), route))

    def test_k4_ciphertext_byte_integrity(self):
        raw = m.K4.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), m.K4_HASH)
        self.assertEqual(len(raw.strip()), 97)
        self.assertTrue(raw.decode().strip().isupper())


if __name__ == '__main__':
    unittest.main()
