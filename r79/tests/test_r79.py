#!/usr/bin/env python3
"""R79 unit tests (synthetic only; no K4, no published letters). Run: python3 -I r79/tests/test_r79.py
  1 fixed inputs: text lengths, stream and rule counts
  2 explicit cipher: decrypt(encrypt(p)) == p for every keyword family
  3 decode path: the vectorised chunk row of a planted setting, with the true shifts, gives the plaintext, and
    setting(row, shifts) gives back the planted setting
  4 solver: SLOTSOLVE on the planted row alone recovers the plaintext
  5 H11: the true start letters close every cycle; the cycle solver's text re-encrypts; the sum invariant holds
    for same-alphabet Vigenere plants (r78 Theorem 2)
  6 Theorem K counts are finite; slot rules depend only on earlier ciphertext"""
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r75"))
sys.path.insert(0, str(ROOT / "r79"))
import core  # noqa: E402
import families as F  # noqa: E402
import solver as SV  # noqa: E402

RNG = random.Random(790900)
SAMPLE = F.texts()["K13PT"]          # ordinary English for the plants (no K4 text)


def window():
    i = RNG.randrange(len(SAMPLE) - 97)
    return SAMPLE[i:i + 97]


def locate(st, ct):
    """(chunk, row) of a planted keyword setting, computed directly from the chunk layout."""
    fam = st["fam"]
    for k, ch in enumerate(F.chunks(fam, ct)):
        info = ch[4]
        if fam == "H7CT":
            ci = F.CONV24.index((st["pa"], st["ca"], st["ka"], st["op"]))
            return ch, (ci * 48 + st["L"] - 1) * F.MKEY + st["m"] - 1
        if fam == "H7TXT" and F.CONV24[info[1]] == (st["pa"], st["ca"], st["ka"], st["op"]):
            return ch, F.streams()[0].index((st["text"], st["d"], st["o"])) * F.MKEY + st["m"] - 1
        if fam == "LIB":
            _, L, ci, rows = info
            conv = (F.CONV8 if L == 0 else F.CONV24)[ci]
            if L == st["L"] and conv == (st["pa"], st["ca"], st["ka"], st["op"]):
                d = F.mapdefs().index(next(x for x in F.mapdefs() if x[0] == st["rule"] and list(x[1]) == st["rp"]
                                           and x[2] == st["m"]))
                return ch, int(np.flatnonzero(rows == d)[0])
        if fam == "PROG":
            _, where, pa, ca, op, keys = info
            if (where, pa, ca, op) == (st["where"], st["pa"], st["ca"], st["op"]):
                return ch, keys.index((st["A1"], st["a"], st["b"])) * F.MKEY + st["m"] - 1
    raise AssertionError("not found")


def main():
    T = F.texts()
    assert len(T["K13PT"]) == 769 and len(T["K13CT"]) == 768
    assert len(F.streams()[0]) == 2 * 673 + 2 * 672
    defs = F.mapdefs()
    print("1 ok:", len(defs), "slot rules;", len(F.routes()[0]), "routes;", {k: round(v, 2) for k, v in
                                                                             F.log10_settings().items()})
    B = F.bank()[0]
    for fam in ("H7CT", "H7TXT", "LIB", "PROG"):
        for _ in range(60):
            st, p = F.random_setting(RNG, fam, 1, 12), window()
            c = F.encrypt(p, st)
            assert F.decrypt(c, st) == p, st
    print("2 ok: explicit cipher round trip, 240 plants")
    for fam in ("H7CT", "H7TXT", "LIB", "PROG"):
        for _ in range(6):
            st, p = F.random_setting(RNG, fam, 2, 10), window()
            c = F.encrypt(p, st)
            (Z, R, M, OI, info), row = locate(st, c)
            s, t = F.OPS[st["op"]]
            u = F.IDX[st["ka"]][core.codes(st["key"]).astype(np.int64)]
            d = np.zeros(SV.MMAX, dtype=np.uint8)
            d[:st["m"]] = (-s * t * u) % 26
            dec = "".join(core.AZ[B[OI[row], i, (Z[row, i] + d[R[row, i]]) % 26]] for i in range(core.N))
            assert dec == p, (fam, st)
            got = F.setting(info, row, d)
            assert {k: v for k, v in got.items() if k != "control"} == {k: v for k, v in st.items() if k != "control"}, \
                (got, st)
            sc, de = SV.slot_batch(Z[row][None], R[row][None], M[row:row + 1], OI[row:row + 1], B, 6, 1, 0)
            assert F.decrypt(c, F.setting(info, row, de[0])) == p, (fam, st)
    print("3-4 ok: decode path matches the explicit cipher; solver recovers 24 planted rows")
    names, P = F.routes()
    steps, lets = F.h11_tables()
    for k in range(40):
        st, p = F.random_setting(RNG, "H11"), window()
        c = F.encrypt(p, st)
        cv = F.H11_CONV.index((st["pa"], st["ka"], st["ca"], st["op"]))
        r = names.index(st["route"])
        y = F.IDX[st["ca"]][core.codes(c).astype(np.int64)]
        x = F.IDX[st["pa"]][core.codes(p).astype(np.int64)]
        step = steps[cv].reshape(26, 26)
        perm = P[r]
        assert all(step[y[i], x[i]] == x[perm[i]] for i in range(core.N))
        txt, sc = SV.cyc_text(y, perm, steps[cv], lets[cv], 4, 1, 0)
        assert txt is not None and F.encrypt(core.text(txt), st) == c
        if st["pa"] == st["ka"]:
            assert int(y.sum()) % 2 == 0
    print("5 ok: H11 cycles close at the truth, cycle-solver output re-encrypts, sum invariant holds (40 plants)")
    c = core.text(np.array([RNG.randrange(26) for _ in range(core.N)]))
    for rule, par, m, _ in defs:
        full = F.slot_map(rule, par, m, c)
        for cut in (10, 50):
            assert F.slot_map(rule, par, m, c[:cut] + "A" * (core.N - cut))[:cut + 1] == full[:cut + 1], rule
        assert max(full) < m
    print("6 ok: every slot rule uses only earlier ciphertext and stays below m")
    print("R79 TESTS OK")


if __name__ == "__main__":
    main()
