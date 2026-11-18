#!/usr/bin/env python3
"""Tests for r79/audit/replay_kw.py (T6 item 2). Synthetic only: no K4 ciphertext, no published letters (K4's
published POSITIONS are used for layout, as r83/tests does). The original code is imported HERE only, to compare.
1 every slot rule (R79's 982 + R81a's G4 rules) equals the ENCRYPTION-side state machine of the originals
  (r79/families.py _State; r81a/families81.py State: a separate path from the vectorised slot_map that the
  original exact checks used) on random ciphertexts;
2 the K1-K3 text streams equal r79's; the setting counts per family equal the pre-registered totals;
3 on toy keyword lengths (m 1-2) feasibility equals an exhaustive search over every keyword through the originals'
  explicit decrypt(), on planted, altered and random ciphertexts, for all eight families;
4 plants at the largest keyword length (m 12) are feasible; a plant with ONE PLAINTEXT LETTER wrong (ciphertext
  re-enciphered from the altered text) is either still feasible or drop-one-flagged at that position.
Usage: python3 -I r79/audit/tests/test_replay_kw.py"""
import itertools
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "r79" / "audit"), str(ROOT / "r81a"), str(ROOT / "r79"), str(ROOT / "r75")]
import replay_kw as K  # noqa: E402
import families as F79  # noqa: E402
import families81 as F81  # noqa: E402

AZ = K.AZ
POS = list(range(21, 34)) + list(range(63, 74))


def rand_ct(rng):
    return "".join(rng.choice(AZ) for _ in range(97))


def test_slots(rng):
    n = 0
    for _ in range(3):
        ct = rand_ct(rng)
        for r, p, m in K.lib_defs():
            st = F79._State(r, tuple(p), m)
            enc = []
            for ch in ct:
                enc.append(st.cur())
                st.feed(ch)
            assert K.slots(r, p, m, ct) == enc, (r, p, m)
            n += 1
        for r, p, m, _ in K.g4_defs():
            st = F81.State(r, tuple(p), m)
            enc = []
            for ch in ct:
                enc.append(st.cur())
                st.feed(ch)
            assert K.slots(r, p, m, ct) == enc, (r, p, m)
            n += 1
    assert len(K.lib_defs()) == len(F79.mapdefs()) and len(K.g4_defs()) == len(F81.g4defs())
    print("1 ok: every slot rule equals the originals' encryption-side state machine;", n, "rule-ciphertext pairs")


def test_counts():
    assert K.k13_texts() == F79.texts()
    m12 = K.MKEY
    defs = K.lib_defs()
    nonrep = [d for d in defs if d[0] != "REP"]
    g4 = K.g4_defs()
    counts = {
        "H7CT": len(K.CONV24) * 48 * m12,
        "H7TXT": len(K.CONV24) * len(K.text_streams()) * m12,
        "LIB": len(K.CONV8) * len(defs) + 7 * len(K.CONV24) * len(nonrep),
        "PROG": len(K.PROG79) * 2 * 3 * 650 * m12,
        "H7CT_A": len(K.NEWK) * 48 * m12,
        "LIB_A": len(K.NEW32) * len(defs) + 7 * len(K.NEWK) * len(nonrep),
        "LIB_G4": len(K.CONV32) * len(g4) + 7 * len(K.CONVK) * sum(d[3] for d in g4),
        "PROG_A": len(K.PROG81) * 2 * 3 * 650 * m12,
    }
    want = {"H7CT": 13824, "H7TXT": 774720, "LIB": 170816, "PROG": 374400,
            "H7CT_A": 41472, "LIB_A": 512448, "LIB_G4": 168000, "PROG_A": 1123200}
    assert counts == want, (counts, want)
    print("2 ok: text streams equal r79's; setting counts equal the pre-registered totals:", counts)
    return counts


def brute(mod, ct, st, m):
    """Exhaustive over every keyword of length m through the original explicit decrypt()."""
    ka = st.get("ka", "AZ")
    for kw in itertools.product(AZ, repeat=m):
        t = mod.decrypt(ct, {**st, "key": "".join(kw), "m": m})
        if all(t[i] == pt_at for i, pt_at in zip(POS, PK)):
            return True
    return False


def single(fam, ct, st):
    """Feasibility of exactly one setting, computed with replay_kw's own primitives."""
    s, conv = st, (st["pa"], st["ca"], st.get("ka", "AZ"), st["op"])
    m = st["m"]
    if fam in ("H7CT", "H7CT_A"):
        w = K.needed(ct, POS, PK, *conv, K.ct_stream(ct, conv[2], s["L"]))
        sl = [p % m for p in POS]
    elif fam == "H7TXT":
        T = K.k13_texts()[s["text"]]
        S = [K.IDX[conv[2]][T[s["o"] + s["d"] * i]] for i in range(97)]
        w = K.needed(ct, POS, PK, *conv, S)
        sl = [p % m for p in POS]
    elif fam in ("LIB", "LIB_A", "LIB_G4"):
        w = K.needed(ct, POS, PK, *conv, K.ct_stream(ct, conv[2], s["L"]) if s["L"] else None)
        full = K.slots(s["rule"], tuple(s["rp"]), m, ct)
        sl = [full[p] for p in POS]
    else:
        key = (s["A1"], s["a"], s["b"])
        w = K.needed(ct, POS, PK, conv[0], conv[1], "AZ", conv[3], None,
                     inner=key if s["where"] == "inner" else None, outer=key if s["where"] == "outer" else None)
        sl = [p % m for p in POS]
    return K.judge(w, sl)


PK = None


def make(rng, fam, mlo, mhi):
    if fam in F79.FAMS:
        st = F79.random_setting(rng, fam, mlo, mhi)
        mod = F79
    else:
        st = F81.random_setting(rng, fam, mlo, mhi)
        mod = F81
    return mod, st


def test_brute(rng):
    global PK
    n = {}
    for fam in ("H7CT", "H7TXT", "LIB", "PROG", "H7CT_A", "LIB_A", "LIB_G4", "PROG_A"):
        for k in range(6):
            mod, st = make(rng, fam, 1, 2) if fam not in ("LIB", "LIB_A", "LIB_G4") else make(rng, fam, 2, 2)
            pt = "".join(rng.choice(AZ) for _ in range(97))
            ct = mod.encrypt(pt, st)
            assert mod.decrypt(ct, st) == pt
            PK = [pt[i] for i in POS]
            kind = k % 3
            if kind == 1:
                i = rng.choice(POS)
                PK = list(PK)
                PK[POS.index(i)] = rng.choice([x for x in AZ if x != PK[POS.index(i)]])
            elif kind == 2:
                ct = rand_ct(rng)
            b = brute(mod, ct, st, st["m"])
            e = single(fam, ct, st)[0]
            assert b == e, (fam, st, b, e)
            if kind == 0:
                assert e
            n[fam] = n.get(fam, 0) + 1
    print("3 ok: feasibility equals exhaustive keyword search through the originals' decrypt():", n)


def test_plants(rng):
    global PK
    strict = total = 0
    for fam in ("H7CT", "H7TXT", "LIB", "PROG", "H7CT_A", "LIB_A", "LIB_G4", "PROG_A"):
        for _ in range(3):
            mod, st = make(rng, fam, 12, 12) if fam not in ("LIB_G4",) else make(rng, fam, 10, 12)
            pt = list("".join(rng.choice(AZ) for _ in range(97)))
            ct = mod.encrypt("".join(pt), st)
            PK = [pt[i] for i in POS]
            assert single(fam, ct, st)[0], (fam, st)
            b = rng.randrange(len(POS))
            pt2 = list(pt)
            pt2[POS[b]] = rng.choice([x for x in AZ if x != pt[POS[b]]])
            ct2 = mod.encrypt("".join(pt2), st)              # ciphertext re-enciphered from the altered plaintext
            PK = [pt[i] for i in POS]                       # the published letter at POS[b] is now WRONG
            ok, ck, drop = single(fam, ct2, st)
            assert ok or (POS.index(POS[b]) in drop), (fam, st, ok, drop)
            strict += (not ok)
            total += 1
    print("4 ok: max-length plants feasible; one-wrong-plaintext-letter plants still feasible or flagged at that "
          "position;", strict, "of", total, "were infeasible as they stood (the error mattered)")


def main():
    rng = random.Random(790616)
    test_slots(rng)
    test_counts()
    test_brute(rng)
    test_plants(rng)
    print("T6 R79/R81a KEYWORD REPLAY TESTS OK")


if __name__ == "__main__":
    main()
