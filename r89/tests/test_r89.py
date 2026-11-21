#!/usr/bin/env python3
"""Tests for R89 (synthetic only; no K4 ciphertext is read and no published letter is used: K4's published POSITIONS
are used for layout only, as r83/tests does).
 1 round trips: F26L, bare F26 and RCT on 3,000 random texts of length 1-98 each; K1/K2 openings through the outer
   tableau; every block length 1-30 for every (b, u, v) of F26 (all final-block lengths, coinciding residues);
 2 the independent witness encipherers (witness89) equal the references on 600 random settings, all sub-families;
 3 F26 alphabet list: 20 alphabets, 20 distinct equivalence classes; a reversed alphabet is equivalent (so it is not
   a new setting); the witness and exact-check copy of the list equals r89/f26l.py's;
 4 the exhaustive F26 solver enumerates exactly 139,120 settings and its index maps decode exactly like f26l.decrypt
   for every (b, u, v) on random ciphertexts; on 12 plants of K1-K3 English the top candidate is the plant (on a word
   LIST, not prose, a block-rotated decode (u-k, v-k) can outscore it: see r89/REVIEW_PR98.md);
 5 the RCT kernel frame scores exactly the quadgram score of rct.decrypt;
 6 exact checks: exact89.f26_hits equals a full decryption's match count on 200 random settings and is 24 at a
   plant's true setting; exact89.rct_feasible == rct.exact_check on 3,000 setting cases, and plants are feasible;
 7 error propagation as stated: one F26L ciphertext error changes at most 2 plaintext letters (300 trials); one RCT
   ciphertext error can change later letters (it does in some trials);
 8 the witness check fails on a changed letter, setting, ciphertext letter, arm label or best; passes when honest;
 9 make89: counts, every positive re-encrypts, the mask is applied to exactly the first item of each cell, extras
   carry one error each, deterministic for a seed;
10 gate89.judge: per-arm bars applied as pre-registered;
11 the sandbox builder refuses extra fields, a published word, a short row and a reused sandbox.
Usage: python3 -I r89/tests/test_r89.py"""
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "r89"), str(ROOT / "r89" / "blind"), str(ROOT / "r89" / "sealed"), str(ROOT / "r87")]
import f26l as F  # noqa: E402
import rct as R  # noqa: E402
import f26_solve as FS  # noqa: E402
import rct_solve as RS  # noqa: E402
import witness89 as WIT  # noqa: E402
import exact89 as EX  # noqa: E402
import gate89 as G  # noqa: E402
import make_sandbox89 as SB  # noqa: E402
import rotor87  # noqa: E402

AZ = F.AZ
POS = list(range(21, 34)) + list(range(63, 74))


def rtext(rng, n=97):
    return "".join(rng.choice(AZ) for _ in range(n))


def rf26(rng, bare=None):
    a, b, u, v = rng.choice(F.inner_settings())
    o = None if (bare if bare is not None else rng.random() < 0.2) else rng.choice(F.outer_options())
    return (a, b, u, v, o)


def rrct(rng):
    W = list(range(26))
    rng.shuffle(W)
    return W, (rng.choice(R.A4), rng.choice(R.A4)) + rng.choice(R.SCHEDULES)


def f26_dict(st):
    a, b, u, v, o = st
    return {"alphabet": a, "b": b, "u": u, "v": v, "outer": None if o is None else {"key": o[0], "sign": o[1], "phase": o[2]}}


def rct_dict(W, st):
    return {"ein": st[0], "eout": st[1], "d": st[2], "m": st[3], "q": st[4], "wiring": W}


def test_roundtrip(rng):
    assert F.outer_enc("BETWEENSUB", "PAL", 1, 0) == "EMUFPHZLRF" and F.outer_enc("ITWASTOTAL", "ABS", 1, 0) == "VFPJUDEEHZ"
    for _ in range(3000):
        pt = rtext(rng, rng.randint(1, 98))
        st = rf26(rng)
        assert F.decrypt(F.encrypt(pt, st), st) == pt
        W, s = rrct(rng)
        assert R.decrypt(R.encrypt(pt, W, *s), W, *s) == pt
    for n in range(1, 31):
        pt = rtext(rng, n)
        for b in F.BLOCKS:
            for (u, v) in F.pairs(b):
                assert F.f26_dec(F.f26_enc(pt, "QWERTY", b, u, v), "QWERTY", b, u, v) == pt
    print("1 ok: 3,000 round trips per family, K1/K2 openings, every block length 1-30 for all 188 (b, u, v)")


def test_witness_equal(rng):
    for _ in range(300):
        pt = rtext(rng)
        st = rf26(rng)
        assert WIT.encipher({"arm": "F26L" if st[4] else "F26", "text": pt, "setting": f26_dict(st)}) == F.encrypt(pt, st)
        W, s = rrct(rng)
        assert WIT.encipher({"arm": "RCT", "text": pt, "setting": rct_dict(W, s)}) == R.encrypt(pt, W, *s)
    print("2 ok: independent witness encipherers equal the references on 600 random settings")


def test_alphabets():
    c = [F.canonical(A) for A in F.F26_ALPHABETS.values()]
    assert len(F.F26_ALPHABETS) == 20 and len(set(c)) == 20
    assert all(sorted(A) == list(AZ) for A in F.F26_ALPHABETS.values())
    rng = random.Random(4)
    for A in list(F.F26_ALPHABETS.values())[:5]:
        F.F26_ALPHABETS["_R"] = A[::-1]
        pt = rtext(rng)
        for b in F.BLOCKS:
            u, v = F.pairs(b)[3]
            assert F.f26_enc(pt, "_R", b, u, v) == F.f26_enc(pt, [k for k, x in F.F26_ALPHABETS.items() if x == A][0], b, u, v)
        del F.F26_ALPHABETS["_R"]
    assert dict(WIT.F26_ALPH) == dict(F.F26_ALPHABETS) and WIT.OUTER_KEYS == F.KEYS
    assert len(EX.f26_settings()) == 139120 and len(EX.rct_settings()) == len(RS.settings()) == 448
    print("3 ok: 20 alphabets in 20 distinct F26 classes; reversal is an equivalence; witness/exact list equal")


def test_f26_solver(rng):
    keys, IR, IH = FS.maps(97)
    assert len(keys) == 188
    for _ in range(5):
        ct = rtext(rng)
        for k, (b, u, v) in enumerate(keys):
            for a in ("AZ", "KRYPTOS"):
                A = F.F26_ALPHABETS[a]
                place = [A.index(ch) for ch in ct]
                dec = "".join(A[13 * (place[IR[k][i]] // 13) + place[IH[k][i]] % 13] for i in range(97))
                assert dec == F.f26_dec(ct, a, b, u, v)
    t = "".join(ch for ch in (ROOT / "k4kit/data/k1k3_plaintext.txt").read_text().upper() if "A" <= ch <= "Z")
    for k in range(12):
        o = rng.randrange(len(t) - 97)
        pt = t[o:o + 97]
        st = rf26(rng, bare=(k % 4 == 0))
        out, n = FS.solve(F.encrypt(pt, st), keep=8)
        assert n == 139120 and out[0]["text"] == pt, (st, out[0]["setting"])
    print("4 ok: exhaustive F26 solver: 139,120 settings; index maps equal f26l.decrypt; 12/12 plants top-ranked")


def test_rct_kernel(rng):
    Q = rotor87.Quad()
    for _ in range(10):
        W, s = rrct(rng)
        ct = R.encrypt(rtext(rng), W, *s)
        sc, W2 = RS.run_one(ct, s, 1, 300, 2.0, rng.randrange(1, 2 ** 60))
        t = R.decrypt(ct, W2, *s)
        assert R.encrypt(t, W2, *s) == ct and abs(Q.score(t) - sc) < 1e-2
    print("5 ok: RCT kernel score equals the quadgram score of rct.decrypt")


def test_exact(rng):
    sts = EX.f26_settings()
    for _ in range(200):
        ct = rtext(rng)
        lets = [rng.choice(AZ) for _ in POS]
        st = rng.choice(sts)
        h = EX.f26_hits(ct, POS, lets, [st])[0]
        full = F.decrypt(ct, st)
        assert h == sum(full[p] == x for p, x in zip(POS, lets))
    for _ in range(10):
        pt = rtext(rng)
        st = rf26(rng)
        assert EX.f26_hits(F.encrypt(pt, st), POS, [pt[p] for p in POS], [st])[0] == 24
    n = 0
    for case in range(60):
        W, s = rrct(rng)
        pt = rtext(rng)
        ct = R.encrypt(pt, W, *s)
        pos = sorted(rng.sample(range(97), 6))
        lets = [pt[p] for p in pos]
        if case % 3 == 1:
            lets[0] = rng.choice([x for x in AZ if x != lets[0]])
        if case % 3 == 2:
            ct = rtext(rng)
        for s2 in RS.settings()[case % 9::9]:
            assert R.exact_check(ct, pos, lets, *s2) == EX.rct_feasible(ct, pos, lets, s2)
            n += 1
        if case % 3 == 0:
            assert EX.rct_feasible(ct, pos, lets, s)[0]
    for _ in range(20):
        W, s = rrct(rng)
        pt = rtext(rng)
        assert EX.rct_feasible(R.encrypt(pt, W, *s), POS, [pt[p] for p in POS], s)[0]
    print("6 ok: F26 hit counts equal full decryption (200) and are 24 at plants; RCT exact checks agree on", n, "cases")


def test_propagation(rng):
    prop = 0
    for _ in range(300):
        pt = rtext(rng)
        st = rf26(rng)
        ct = F.encrypt(pt, st)
        j = rng.randrange(97)
        ct2 = ct[:j] + rng.choice([x for x in AZ if x != ct[j]]) + ct[j + 1:]
        assert sum(a != b for a, b in zip(F.decrypt(ct2, st), pt)) <= 2
        W, s = rrct(rng)
        ct = R.encrypt(pt, W, *s)
        ct2 = ct[:j] + rng.choice([x for x in AZ if x != ct[j]]) + ct[j + 1:]
        prop += sum(a != b for a, b in zip(R.decrypt(ct2, W, *s), pt)) > 1
    assert prop > 0
    print("7 ok: one F26L ciphertext error changes <= 2 plaintext letters; one RCT error propagated in", prop, "of 300")


def test_witness_fail(rng):
    pt = rtext(rng)
    st = rf26(rng, bare=False)
    ct = F.encrypt(pt, st)
    e = {"text": pt, "arm": "F26L", "setting": f26_dict(st), "lm_per_letter": -1.0, "word_per_letter": -2.0}
    W, s = rrct(rng)
    with tempfile.TemporaryDirectory() as d:
        tsv, res = Path(d) / "t.tsv", Path(d) / "r.jsonl"

        def run(ct_in, e, best=None):
            rec = {"id": "H_000", "best": best or e, "top": [e], "best_by_arm": {e["arm"]: e}}
            tsv.write_text(f"id\tciphertext\nH_000\t{ct_in}\n")
            res.write_text(json.dumps(rec) + "\n")
            return WIT.check(tsv, res)["passed"]

        assert run(ct, e)
        assert not run(ct, {**e, "text": pt[:5] + ("A" if pt[5] != "A" else "B") + pt[6:]})
        assert not run(ct, {**e, "setting": {**e["setting"], "u": e["setting"]["v"], "v": e["setting"]["u"]}})
        assert not run(ct[:9] + ("A" if ct[9] != "A" else "B") + ct[10:], e)
        assert not run(ct, {**e, "arm": "F26"})
        assert not run(ct, e, best={**e, "lm_per_letter": -0.5})
        ct3 = R.encrypt(pt, W, *s)
        e3 = {"text": pt, "arm": "RCT", "setting": rct_dict(W, s), "lm_per_letter": -1.0, "word_per_letter": -2.0}
        assert run(ct3, e3)
        assert not run(ct3, {**e3, "setting": {**e3["setting"], "q": (s[4] + 1) % s[3]}})
    print("8 ok: witness passes honest records and fails on a changed letter, setting, ciphertext, arm label or best")


def test_make(rng):
    words = [l.split("\t")[0] for l in (ROOT / "k4kit/data/word_model_orth.tsv").read_text().splitlines()[1:3000]]
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        r2 = random.Random(5)
        for g in ("a", "b", "c", "k"):
            (d / f"{g}.txt").write_text(" ".join(r2.choice(words) for _ in range(6000)))
        outs = []
        for k in range(2):
            subprocess.run([sys.executable, "-I", str(ROOT / "r89/sealed/make89.py"),
                            f"{d}/a.txt,{d}/b.txt,{d}/c.txt", str(d / "k.txt"), "123", str(d / f"o{k}"),
                            "--n-per-cell", "2", "--neg-scale", "0.2"], check=True, capture_output=True)
            outs.append((d / f"o{k}" / "TRUTH.json").read_text())
        assert outs[0] == outs[1]
        t = json.loads(outs[0])
        pos = [v for v in t.values() if v["class"] == "POS"]
        assert len(pos) == 48 and sum(v["masked"] for v in pos) == 24
        assert len([v for v in t.values() if v["class"] == "EXTRA"]) == 9
        assert {v["generator"] for v in t.values() if v["class"] == "NEG"} == {g for g, _ in __import__("make89").GENS}
        for v in t.values():
            if v["class"] == "NEG":
                continue
            s = v["setting"]
            if v["arm"] == "F26L":
                st = (s["alphabet"], s["b"], s["u"], s["v"], (s["outer"]["key"], s["outer"]["sign"], s["outer"]["phase"]))
                enc = F.encrypt(v["enciphered"], st)
            else:
                key = (s["wiring"], s["ein"], s["eout"], s["d"], s["m"], s["q"])
                enc = R.encrypt(v["enciphered"], *key, skip_at=v.get("missed_after"))
            if v.get("kind") == "CTERR":
                assert sum(a != b for a, b in zip(enc, v["ct"])) == 1
            else:
                assert enc == v["ct"]
            if v["class"] == "POS" and v["masked"]:
                assert v["enciphered"] == v["pt"].translate(str.maketrans("CW", "KV"))
    print("9 ok: make89 counts, masks, extras, re-encryption, determinism")


def test_gate():
    def build(ok_f, ok_r, neg_conf, masked_fail=0):
        truth, res, k = {}, {}, 0
        for arm, okc in (("F26L", ok_f), ("RCT", ok_r)):
            for si in range(4):
                for gi in range(3):
                    for c in range(4):
                        n = (si * 3 + gi) * 4 + c
                        good = n < okc and not (c == 0 and si * 3 + gi < masked_fail)
                        truth[f"H_{k}"] = {"class": "POS", "arm": arm, "stratum": f"S{si + 1}", "param": si, "genre": f"G{gi + 1}",
                                           "masked": c == 0, "enciphered": "A" * 97, "setting": {}}
                        res[f"H_{k}"] = {"best": {"arm": arm if good else "F26", "text": "A" * 97, "setting": {},
                                                  "lm_per_letter": -1.0, "word_per_letter": -2.0}}
                        k += 1
        for j in range(150):
            truth[f"H_{k}"] = {"class": "NEG", "generator": "VIG"}
            res[f"H_{k}"] = {"best": {"arm": "RCT", "text": "C" * 97, "setting": {}, "word_per_letter": -2.0,
                                      "lm_per_letter": -1.0 if j < neg_conf else -1.6}}
            k += 1
        return truth, res

    G.setting_right = lambda arm, found, true: found["arm"] == arm
    s, _ = G.judge(*build(48, 48, 1))
    assert s["arms"]["F26L"]["go"] and s["arms"]["RCT"]["go"]
    s, _ = G.judge(*build(48, 48, 2))
    assert not s["arms"]["F26L"]["go"] and not s["arms"]["RCT"]["go"]
    s, _ = G.judge(*build(41, 48, 0))
    assert not s["arms"]["F26L"]["go"] and s["arms"]["RCT"]["go"]
    s, _ = G.judge(*build(48, 48, 0, masked_fail=5))
    assert not s["arms"]["F26L"]["go"] and s["arms"]["F26L"]["ok"] == 43
    print("10 ok: per-arm gate bars (42/48, strata, genres, masked >= 8/12, <= 1/150 negatives) applied")


def test_sandbox(rng):
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        for name, body in {"extra field": "id\tciphertext\tkey\nX_1\t" + rtext(rng) + "\tABC\n",
                           "published word": "id\tciphertext\nX_1\t" + rtext(rng, 91) + "BERLIN\n",
                           "short row": "id\tciphertext\nX_1\t" + rtext(rng, 96) + "\n"}.items():
            p = d / f"{name}.tsv"
            p.write_text(body)
            try:
                SB.build(d / ("box_" + name.replace(" ", "_")), d / "nolm.bin", p)
                raise AssertionError(f"accepted: {name}")
            except SystemExit:
                pass
        (d / "used").mkdir()
        (d / "g.tsv").write_text("id\tciphertext\nX_1\t" + rtext(rng) + "\n")
        try:
            SB.build(d / "used", d / "nolm.bin", d / "g.tsv")
            raise AssertionError("accepted a reused sandbox")
        except SystemExit:
            pass
    print("11 ok: sandbox refuses extra fields, a published word, a short row and a reused sandbox")


def main():
    rng = random.Random(890901)
    test_roundtrip(rng)
    test_witness_equal(rng)
    test_alphabets()
    test_f26_solver(rng)
    test_rct_kernel(rng)
    test_exact(rng)
    test_propagation(rng)
    test_witness_fail(rng)
    test_make(rng)
    test_gate()
    test_sandbox(rng)
    print("R89 TESTS OK")


if __name__ == "__main__":
    main()
