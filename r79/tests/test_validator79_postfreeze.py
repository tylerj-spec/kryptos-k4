#!/usr/bin/env python3
"""Synthetic-only regression tests for the independent R79 post-freeze audit.

No K4 ciphertext or published clues are loaded. Run:
  python3 -I r79/tests/test_validator79_postfreeze.py
"""
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
for p in ("r75", "r79", "r79/sealed", "r79/tests"):
    sys.path.insert(0, str(ROOT / p))
import core  # noqa: E402
import families as F  # noqa: E402
import validate79_postfreeze as A  # noqa: E402
from test_r79 import locate  # noqa: E402

RNG = random.Random(790991)
SAMPLE = F.texts()["K13PT"]


def window():
    i = RNG.randrange(len(SAMPLE) - F.N)
    return SAMPLE[i:i + F.N]


def keyword_tests():
    inv = np.argsort(F.bank()[0], axis=2)
    pos = np.arange(24, dtype=np.int64)
    for fam in A.KEYWORD_FAMILIES:
        pt = window()
        setting = F.random_setting(RNG, fam, 2, 10)
        ct = F.encrypt(pt, setting)
        (z, r, _m, oi, _info), row = locate(setting, ct)
        want = core.codes(pt)[pos].astype(np.int64)
        feasible, checks = A.slot_consistency(
            z[row:row + 1], r[row:row + 1], oi[row:row + 1], pos, want, inv)
        assert feasible.tolist() == [True], (fam, setting)
        assert checks[0] >= 12, (fam, int(checks[0]))

        # Deliberately contradict one known letter at a position sharing a
        # keyword slot with an earlier anchor; the true setting must fail.
        rp = r[row, pos]
        second = next(j for j in range(1, len(pos)) if rp[j] in rp[:j])
        wrong = want.copy()
        wrong[second] = (wrong[second] + 1) % 26
        bad, _ = A.slot_consistency(
            z[row:row + 1], r[row:row + 1], oi[row:row + 1], pos, wrong, inv)
        assert bad.tolist() == [False], fam
        assert F.decrypt(ct, setting) == pt, fam
        print(f"{fam}: planted setting accepted; incompatible anchor rejected")

        if fam == "H7CT":
            # Exercise the complete independent family enumeration too.
            hist = A.keyword_counts(ct, pos, want, families=("H7CT",))["H7CT"]
            assert sum(hist.values()) >= 1, hist


def h11_tests():
    names, perms = F.routes()
    target = (np.arange(F.N) + 1) % F.N
    matches = np.flatnonzero(np.all(perms == target[None, :], axis=1))
    assert len(matches) == 1
    r = int(matches[0])
    fixture = ([names[r]], perms[r:r + 1])
    st = {"fam": "H11", "route": names[r], "pa": "AZ", "ka": "AZ", "ca": "KRY", "op": "VIG"}
    label = "AZ/AZ/KRY/VIG"
    pt = window()
    ct = F.encrypt(pt, st)
    pos = np.arange(24, dtype=np.int64)
    want = core.codes(pt)[pos].astype(np.int64)
    yes = A.h11_check(ct, pos, want, routes=fixture)
    assert yes["anchor_only_feasible_by_checks"][label] == {"23": 1}
    assert yes["cycle_and_crib_feasible_by_checks"][label] == {"23": 1}
    assert any(x["route"] == names[r] and x["convention"] == label for x in yes["survivors"])

    wrong = want.copy()
    wrong[0] = (wrong[0] + 1) % 26
    no_anchor = A.h11_check(ct, pos, wrong, routes=fixture)
    assert no_anchor["anchor_only_feasible_by_checks"][label] == {}
    assert no_anchor["cycle_and_crib_feasible_by_checks"][label] == {}

    # All 23 local anchor checks still pass, but changing an *unpublished*
    # ciphertext letter flips the global sum parity. No complete H11
    # Vigenere plaintext can exist under this same-alphabet convention.
    changed = list(ct)
    ci = F.ALPH["KRY"].index(changed[-1])
    changed[-1] = F.ALPH["KRY"][(ci + 1) % 26]
    no_cycle = A.h11_check("".join(changed), pos, want, routes=fixture)
    assert no_cycle["anchor_only_feasible_by_checks"][label] == {"23": 1}
    assert no_cycle["cycle_and_crib_feasible_by_checks"][label] == {}
    print("H11: true full cycle accepted; false anchor and false cycle rejected")


if __name__ == "__main__":
    keyword_tests()
    h11_tests()
    print("R79 POST-FREEZE SYNTHETIC TESTS OK")
