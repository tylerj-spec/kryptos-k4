#!/usr/bin/env python3
"""Tests for R90 (synthetic only; no K4 ciphertext is read and no published letter is used: K4's published POSITIONS
are used for layout only).
 1 round trips on 3,000 random texts of length 1-98 (with and without the outer stage); every block length 1-30 for
   all 188 (b, u, v); the K1 opening through the outer tableau;
 2 the independent witness encipherer equals the reference on 300 random settings;
 3 catalog: the 15 alphabets are 15 distinct F26 classes, none in R89's 20; witness/exact copies equal f26c's;
   same_key treats a column-relabelled alphabet as the same key and a block rotation (u-k, v-k) as a different one;
 4 the exhaustive solver: 104,340 settings; index maps decode like f26c.decrypt for every (b, u, v); 12 plants of
   K1-K3 English rank first; the retained list has 256 distinct tags;
 5 exact90.hits equals a full decryption's match count on 200 random settings and is 24 at plants;
 6 one ciphertext substitution changes at most 2 decoded letters (the >= 22 screen is the right necessary bound);
 7 the witness fails on a changed letter, setting, ciphertext letter, arm label, best or retained list;
 8 make90: counts, masks, extras, all generators, re-encryption, determinism;
 9 gate90.judge: bars applied as pre-registered (incl. the key criterion and the retention bar);
10 the sandbox builder refuses extra fields, a published word, a short row and a reused sandbox.
Usage: python3 -I r90/tests/test_r90.py"""
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "r90"), str(ROOT / "r90" / "blind"), str(ROOT / "r90" / "sealed"), str(ROOT / "r89")]
import f26c as F  # noqa: E402
import f26c_solve as FS  # noqa: E402
import witness90 as WIT  # noqa: E402
import exact90 as EX  # noqa: E402
import gate90 as G  # noqa: E402
import make_sandbox90 as SB  # noqa: E402
import f26l as L89  # noqa: E402

AZ = F.AZ
POS = list(range(21, 34)) + list(range(63, 74))


def rtext(rng, n=97):
    return "".join(rng.choice(AZ) for _ in range(n))


def rset(rng, bare=None):
    a, b, u, v = rng.choice(F.inner_settings())
    o = None if (bare if bare is not None else rng.random() < 0.2) else rng.choice(F.outer_options())
    return (a, b, u, v, o)


def sd(st):
    a, b, u, v, o = st
    return {"alphabet": a, "b": b, "u": u, "v": v, "outer": None if o is None else {"key": o[0], "sign": o[1], "phase": o[2]}}


def test_roundtrip(rng):
    assert F.outer_enc("BETWEENSUB", "PAL", 1, 0) == "EMUFPHZLRF"
    for _ in range(3000):
        pt = rtext(rng, rng.randint(1, 98))
        st = rset(rng)
        assert F.decrypt(F.encrypt(pt, st), st) == pt
    A = F.ALPHABETS["CIPHER"]
    for n in range(1, 31):
        pt = rtext(rng, n)
        for b in F.BLOCKS:
            for (u, v) in F.pairs(b):
                assert F.f26_dec(F.f26_enc(pt, A, b, u, v), A, b, u, v) == pt
    print("1 ok: 3,000 round trips, every block length 1-30 for all 188 (b, u, v), K1 opening")


def test_witness_equal(rng):
    for _ in range(300):
        pt = rtext(rng)
        st = rset(rng)
        assert WIT.encipher({"arm": "F26C" if st[4] else "F26", "text": pt, "setting": sd(st)}) == F.encrypt(pt, st)
    print("2 ok: independent witness equals the reference on 300 random settings")


def test_catalog(rng):
    c = [F.canonical(A) for A in F.ALPHABETS.values()]
    assert len(F.ALPHABETS) == 15 and len(set(c)) == 15
    assert not set(c) & {L89.canonical(A) for A in L89.F26_ALPHABETS.values()}
    assert WIT.ALPH == F.ALPHABETS and tuple(WIT.WORDS) == F.WORDS and WIT.OUTER_KEYS == F.KEYS
    assert len(EX.settings()) == 104340
    A = F.ALPHABETS["GARDEN"]
    relab = A[13:] + A[:13]                                    # row swap: same F26 cipher
    pt = rtext(rng)
    alph = dict(F.ALPHABETS, _S=relab)
    st, st2 = ("GARDEN", 7, 2, 5, ("PAL", 1, 3)), ("_S", 7, 2, 5, ("PAL", 1, 3))
    assert F.encrypt(pt, st) == F.encrypt(pt, st2, alph) and F.same_key(st, st2, alph)
    assert not F.same_key(st, ("GARDEN", 7, 1, 4, ("PAL", 1, 3)))      # (u-1, v-1): block-rotated decode, other key
    print("3 ok: 15 distinct classes, none in R89's list; same_key: row swap same key, block rotation different")


def test_solver(rng):
    keys, IR, IH = FS.maps(97)
    for _ in range(4):
        ct = rtext(rng)
        for k, (b, u, v) in enumerate(keys):
            A = F.ALPHABETS["TEMPLE"]
            place = [A.index(ch) for ch in ct]
            assert "".join(A[13 * (place[IR[k][i]] // 13) + place[IH[k][i]] % 13] for i in range(97)) == \
                F.f26_dec(ct, A, b, u, v)
    t = "".join(ch for ch in (ROOT / "k4kit/data/k1k3_plaintext.txt").read_text().upper() if "A" <= ch <= "Z")
    for k in range(12):
        o = rng.randrange(len(t) - 97)
        pt = t[o:o + 97]
        st = rset(rng, bare=(k % 4 == 0))
        out, n = FS.solve(F.encrypt(pt, st))
        assert n == 104340 and len(out) == 256 and len({e["tag"] for e in out}) == 256
        assert out[0]["text"] == pt and out[0]["tag"] == FS.tag(st), (st, out[0]["tag"])
    print("4 ok: exhaustive solver: 104,340 settings, maps equal f26c.decrypt, 12/12 plants first, 256 retained")


def test_exact(rng):
    sts = EX.settings()
    for _ in range(200):
        ct = rtext(rng)
        lets = [rng.choice(AZ) for _ in POS]
        st = rng.choice(sts)
        full = F.decrypt(ct, st)
        assert EX.hits(ct, POS, lets, [st])[0] == sum(full[p] == x for p, x in zip(POS, lets))
    for _ in range(10):
        pt = rtext(rng)
        st = rset(rng)
        assert EX.hits(F.encrypt(pt, st), POS, [pt[p] for p in POS], [st])[0] == 24
    print("5 ok: exact hit counts equal full decryption (200) and are 24 at plants")


def test_ct_error(rng):
    worst = 0
    for _ in range(300):
        pt = rtext(rng)
        st = rset(rng)
        ct = F.encrypt(pt, st)
        j = rng.randrange(97)
        ct2 = ct[:j] + rng.choice([x for x in AZ if x != ct[j]]) + ct[j + 1:]
        worst = max(worst, sum(a != b for a, b in zip(F.decrypt(ct2, st), pt)))
    assert worst <= 2
    print("6 ok: one ciphertext substitution changes at most", worst, "decoded letters (screen >= 22/24 is necessary)")


def test_witness_fail(rng):
    pt = rtext(rng)
    st = rset(rng, bare=False)
    ct = F.encrypt(pt, st)
    e = {"text": pt, "arm": "F26C", "setting": sd(st), "lm_per_letter": -1.0, "word_per_letter": -2.0}
    tags = [f"T{i}" for i in range(256)]
    with tempfile.TemporaryDirectory() as d:
        tsv, res = Path(d) / "t.tsv", Path(d) / "r.jsonl"

        def run(ct_in, e, best=None, retained=tags):
            rec = {"id": "H_000", "best": best or e, "top": [e], "best_by_arm": {e["arm"]: e}, "retained": retained}
            tsv.write_text(f"id\tciphertext\nH_000\t{ct_in}\n")
            res.write_text(json.dumps(rec) + "\n")
            return WIT.check(tsv, res)["passed"]

        assert run(ct, e)
        assert not run(ct, {**e, "text": pt[:5] + ("A" if pt[5] != "A" else "B") + pt[6:]})
        assert not run(ct, {**e, "setting": {**e["setting"], "u": e["setting"]["v"], "v": e["setting"]["u"]}})
        assert not run(ct[:9] + ("A" if ct[9] != "A" else "B") + ct[10:], e)
        assert not run(ct, {**e, "arm": "F26"})
        assert not run(ct, e, best={**e, "lm_per_letter": -0.5})
        assert not run(ct, e, retained=tags[:255])
    print("7 ok: witness fails on a changed letter, setting, ciphertext, arm label, best or retained list")


def test_make(rng):
    words = [l.split("\t")[0] for l in (ROOT / "k4kit/data/word_model_orth.tsv").read_text().splitlines()[1:3000]]
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        r2 = random.Random(5)
        for g in ("a", "b", "c", "k"):
            (d / f"{g}.txt").write_text(" ".join(r2.choice(words) for _ in range(6000)))
        outs = []
        for k in range(2):
            subprocess.run([sys.executable, "-I", str(ROOT / "r90/sealed/make90.py"), f"{d}/a.txt,{d}/b.txt,{d}/c.txt",
                            str(d / "k.txt"), "123", str(d / f"o{k}"), "--n-per-cell", "2", "--neg-scale", "0.2"],
                           check=True, capture_output=True)
            outs.append((d / f"o{k}" / "TRUTH.json").read_text())
        assert outs[0] == outs[1]
        t = json.loads(outs[0])
        pos = [v for v in t.values() if v["class"] == "POS"]
        assert len(pos) == 24 and sum(v["masked"] for v in pos) == 12
        assert len([v for v in t.values() if v["class"] == "EXTRA"]) == 4
        assert {v["generator"] for v in t.values() if v["class"] == "NEG"} == {g for g, _ in __import__("make90").GENS}
        for v in t.values():
            if v["class"] == "NEG":
                continue
            s = v["setting"]
            st = (s["alphabet"], s["b"], s["u"], s["v"], (s["outer"]["key"], s["outer"]["sign"], s["outer"]["phase"]))
            enc = F.encrypt(v["enciphered"], st)
            assert (sum(a != b for a, b in zip(enc, v["ct"])) == 1) if v.get("kind") == "CTERR" else enc == v["ct"]
            if v["class"] == "POS" and v["masked"]:
                assert v["enciphered"] == v["pt"].translate(str.maketrans("CW", "KV"))
    print("8 ok: make90 counts, masks, extras, generators, re-encryption, determinism")


def test_gate():
    sett = {"alphabet": "GARDEN", "b": 5, "u": 1, "v": 2, "outer": {"key": "PAL", "sign": 1, "phase": 0}}
    tag = FS.tag(("GARDEN", 5, 1, 2, ("PAL", 1, 0)))

    def build(nok, neg_conf, lost=0, masked_fail=0):
        truth, res, k = {}, {}, 0
        for si in range(4):
            for gi in range(3):
                for c in range(4):
                    n = (si * 3 + gi) * 4 + c
                    good = n < nok and not (c == 0 and si * 3 + gi < masked_fail)
                    truth[f"H_{k}"] = {"class": "POS", "stratum": f"S{si + 1}", "param": 5, "genre": f"G{gi + 1}",
                                       "masked": c == 0, "enciphered": "A" * 97, "setting": sett}
                    b = {"arm": "F26C", "text": "A" * 97 if good else "B" * 97, "setting": sett,
                         "lm_per_letter": -1.0, "word_per_letter": -2.0}
                    res[f"H_{k}"] = {"best": b, "retained": ([] if n < lost else [tag])}
                    k += 1
        for j in range(150):
            truth[f"H_{k}"] = {"class": "NEG", "generator": "VIG"}
            res[f"H_{k}"] = {"best": {"arm": "F26C", "text": "C" * 97, "setting": sett, "word_per_letter": -2.0,
                                      "lm_per_letter": -1.0 if j < neg_conf else -1.6}, "retained": []}
            k += 1
        return truth, res

    assert G.judge(*build(48, 1))[0]["go"]
    assert not G.judge(*build(48, 2))[0]["go"]
    assert not G.judge(*build(41, 0))[0]["go"]
    assert not G.judge(*build(48, 0, lost=3))[0]["go"]          # retained 45 < 46
    s = G.judge(*build(48, 0, masked_fail=5))[0]
    assert not s["go"] and s["ok"] == 43
    print("9 ok: gate bars (42/48 with key, retention 46/48, masked, <= 1/150 negatives) applied")


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
    print("10 ok: sandbox refuses extra fields, a published word, a short row and a reused sandbox")


def main():
    rng = random.Random(900901)
    test_roundtrip(rng)
    test_witness_equal(rng)
    test_catalog(rng)
    test_solver(rng)
    test_exact(rng)
    test_ct_error(rng)
    test_witness_fail(rng)
    test_make(rng)
    test_gate()
    test_sandbox(rng)
    print("R90 TESTS OK")


if __name__ == "__main__":
    main()
