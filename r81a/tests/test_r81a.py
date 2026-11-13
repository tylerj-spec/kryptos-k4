#!/usr/bin/env python3
"""R81a unit tests (synthetic only; no K4, no published letters). Run: python3 -I r81a/tests/test_r81a.py
  1 counts; the new conventions do not repeat R79's
  2 explicit cipher round trip for every family, keyword length 1..12
  3 decode path: the chunk row of a planted setting, with the true shifts, gives the plaintext and the setting back;
    the solver recovers it from that row alone
  4 G4 rules: encryption-side counters equal the decode-side formulas"""
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r75"))
sys.path.insert(0, str(ROOT / "r79"))
sys.path.insert(0, str(ROOT / "r81a"))
import core  # noqa: E402
import families81 as F  # noqa: E402
import solver as SV  # noqa: E402

RNG = random.Random(810900)
EXACT = []
SAMPLE = F.F79.texts()["K13PT"]


def window():
    i = RNG.randrange(len(SAMPLE) - 97)
    return SAMPLE[i:i + 97]


def find_row(st, ct):
    for Z, R, M, OI, info in F.chunks(st["fam"], ct):
        for j in range(len(Z)):
            got = F.setting(info, j, np.zeros(SV.MMAX, dtype=np.uint8))
            if all(got[k] == st[k] for k in st if k != "key"):
                return (Z, R, M, OI, info), j
    raise AssertionError("not found")


def main():
    assert not set(F.NEW192) & set(F.F79.CONV24) and len(F.NEW192) == 168 and len(F.NEW32) == 24
    assert len(F.PROG_NEW) == 24
    print("1 ok:", len(F.g4defs()), "G4 rules;", {k: round(v, 2) for k, v in F.log10_settings().items()})
    for fam in F.FAMS:
        for _ in range(50):
            st, p = F.random_setting(RNG, fam, 1 if fam != "LIB_G4" else 2, 12), window()
            assert F.decrypt(F.encrypt(p, st), st) == p, st
    print("2 ok: round trip, 200 plants")
    B = F.bank()[0]
    for fam in F.FAMS:
        for _ in range(3):
            st, p = F.random_setting(RNG, fam, 2, 10), window()
            c = F.encrypt(p, st)
            (Z, R, M, OI, info), row = find_row(st, c)
            s, t = F.OPS[st["op"]]
            d = np.zeros(SV.MMAX, dtype=np.uint8)
            d[:st["m"]] = (-s * t * F.IDX[st["ka"]][core.codes(st["key"]).astype(np.int64)]) % 26
            assert "".join(core.AZ[B[OI[row], i, (Z[row, i] + d[R[row, i]]) % 26]] for i in range(97)) == p, st
            assert F.setting(info, row, d) == st
            sc, de = SV.slot_batch(Z[row][None], R[row][None], M[row:row + 1], OI[row:row + 1], B, 6, 1, 0)
            got = F.decrypt(c, F.setting(info, row, de[0]))
            L = core.codes(p).astype(np.int64)
            truth = float(SV.QUAD[((L[:-3] * 26 + L[1:-2]) * 26 + L[2:-1]) * 26 + L[3:]].mean())
            assert got == p or sc[0] >= truth - 1e-4, (st, sc[0], truth)   # the solver never ends below the truth
            EXACT.append(got == p)
    print("3 ok: decode path matches the explicit cipher; solver reaches the truth's score on 12 planted rows "
          f"(exact {sum(EXACT)}/12)")
    for r, par, m, _ in F.g4defs():
        assert [F.State(r, par, m).seq[i] for i in range(97)] == [int(v) for v in F.g4_slot_map(r, par, m)], (r, par)
    print("4 ok: G4 counters agree with the decode-side formulas")
    print("R81a TESTS OK")


if __name__ == "__main__":
    main()
