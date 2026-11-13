#!/usr/bin/env python3
"""R80a unit tests (synthetic only; no K4 data, no published letters).
1 counts: 96 conventions per family, the listed-key and short-key lists, Theorem K counts;
2 round trip: the explicit encryptor and decryptor are inverse, 400 random settings over the four families;
3 decode path: the solver tables (two_build) with the true free-key shifts decode the plant exactly, and setting()
  maps the shifts back to the true free key, both directions;
4 pass 0: the fast scan (two_scan) equals the one-key-at-a-time reference (two_scan_ref) on 2,000 keys x 3
  conventions per family;
5 solver: on 12 planted rows (3 per family), R79's solver with 6 starts on the true listed key and convention never
  ends below the truth's score, and its decode re-encrypts.
Usage: python3 -I r80a/tests/test_r80a.py"""
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r79"))
sys.path.insert(0, str(ROOT / "r80a"))
import families as F79  # noqa: E402
import solver as SV  # noqa: E402
import two80 as T  # noqa: E402

TEXT = F79.texts()["K13PT"]


def plant(rng, fam, mlo=1, mhi=12):
    st = T.random_setting(rng, fam, mlo, mhi)
    o = rng.randrange(len(TEXT) - 97)
    p = TEXT[o:o + 97]
    return st, p, T.encrypt(p, st)


def main():
    rng = random.Random(800900)
    assert len(T.CONVS) == 96 and len(set(T.CONVS)) == 96
    assert len(T.short_keys()) == 18278 and len(T.word_list()) > 25000
    assert all(3 <= len(w) <= 15 for w in T.word_list())
    lk = T.log10_settings()
    print("1 ok:", len(T.word_list()), "listed keys,", len(T.short_keys()), "short keys;",
          {k: round(v, 2) for k, v in lk.items()})

    for _ in range(400):
        fam = rng.choice(T.FAMS)
        st, p, ct = plant(rng, fam)
        assert T.decrypt(ct, st) == p and len(ct) == 97
    print("2 ok: round trip, 400 plants")

    for _ in range(200):
        fam = rng.choice(T.FAMS)
        st, p, ct = plant(rng, fam)
        ci = T.CONVS.index(tuple(st["conv"]))
        wi = T.keys_for(fam).index(st["word"])
        z, out = T.build(ct, fam, ci, wi)
        delta = np.array([(-T.AZ.index(ch)) % 26 for ch in st["free"]])
        assert T.decode_with(z, out, len(delta), delta) == p
        s2 = T.setting(fam, ci, wi, len(delta), delta)
        assert s2["free"] == st["free"] and T.decrypt(ct, s2) == p and T.encrypt(p, s2) == ct
    print("3 ok: decode path and setting mapping, 200 plants")

    ct = "".join(rng.choice(T.AZ) for _ in range(97))
    for fam in T.FAMS:
        for ci in rng.sample(range(96), 3):
            a = T.scan(ct, fam, ci)[:2000]
            b = T.scan_ref(ct, fam, ci, 0, 2000)
            assert np.array_equal(a, b), (fam, ci)
    print("4 ok: fast pass 0 equals the reference")

    n_exact = 0
    for fam in T.FAMS:
        for _ in range(3):
            st, p, ct = plant(rng, fam, 2, 10)
            ci = T.CONVS.index(tuple(st["conv"]))
            wi = T.keys_for(fam).index(st["word"])
            m = len(st["free"])
            z, out = T.build(ct, fam, ci, wi)
            R = np.array([[i % m for i in range(97)]], dtype=np.uint8)
            sc, de = SV.slot_batch(z[None], R, np.array([m], dtype=np.int32), np.zeros(1, dtype=np.int32), out[None],
                                   6, 800901, 0)
            got = T.decode_with(z, out, m, de[0])
            truth = SV.QUAD[[((T.AZ.index(p[j]) * 26 + T.AZ.index(p[j + 1])) * 26 + T.AZ.index(p[j + 2])) * 26
                             + T.AZ.index(p[j + 3]) for j in range(94)]].sum() / 94
            assert got == p or sc[0] >= truth - 1e-4, (fam, st, sc[0], truth)
            s2 = T.setting(fam, ci, wi, m, de[0])
            assert T.encrypt(got, s2) == ct
            n_exact += got == p
    print(f"5 ok: solver reaches the truth's score on 12 planted rows (exact {n_exact}/12)")
    print("R80a TESTS OK")


if __name__ == "__main__":
    main()
