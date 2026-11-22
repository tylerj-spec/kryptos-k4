#!/usr/bin/env python3
"""Tests for R92 (synthetic only; K4's published POSITIONS are used for layout only, no letters).
1 round trips (400 random settings); the witness encipherer equals rotor92.encrypt; 192 settings; every boundary-phase
  schedule differs from zero phase by a NON-constant offset (so r is not an absorbable starting angle); r = 0 and n = 1
  are not in the set;
2 a synthetic phase oracle: with q = 26, n = 2, r = 1 and a wiring swapping two contacts, the time-dependent maps
  satisfy F0 != F1 == F2, which no zero-phase schedule produces (the multi-rotor review's counterexample);
3 the kernel frame: its score equals the quadgram score of rotor92.decrypt, and a long anneal at the true setting
  recovers plants;
4 exact checks: rotor92.exact_check == exact92.feasible == a constructive completion (5 random positions, every 7th
  setting) on planted, altered and random cases; plants feasible at K4's positions; one wrong letter of either kind
  at a published position changes exactly one pair;
5 the witness fails on a changed letter, wiring, ciphertext letter, phase or best;
6 make92: counts, cells, genre balance 16/16/16, masks, generators, re-encryption, determinism;
7 gate92 bars; 8 sandbox refusals. Usage: python3 -I r92/tests/test_r92.py"""
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "r92"), str(ROOT / "r92" / "blind"), str(ROOT / "r92" / "sealed"), str(ROOT / "r87")]
import rotor92 as R  # noqa: E402
import solve92 as S  # noqa: E402
import witness92 as WIT  # noqa: E402
import exact92 as EX  # noqa: E402
import gate92 as G  # noqa: E402
import make_sandbox92 as SB  # noqa: E402
import rotor87  # noqa: E402

AZ = R.AZ
POS = list(range(21, 34)) + list(range(63, 74))


def rset(rng):
    W = list(range(26))
    rng.shuffle(W)
    return W, rng.choice(R.SETTINGS)


def rtext(rng, n=97):
    return "".join(rng.choice(AZ) for _ in range(n))


def sd(W, st):
    return {"ein": st[0], "eout": st[1], "n": st[2], "r": st[3], "d": st[4], "wiring": W}


def test_family(rng):
    for _ in range(400):
        W, st = rset(rng)
        pt = rtext(rng)
        ct = R.encrypt(pt, W, *st)
        assert R.decrypt(ct, W, *st) == pt and WIT.encipher(pt, sd(W, st)) == ct
    assert len(R.SETTINGS) == 192 == len(set(R.SETTINGS)) == len(EX.SETTINGS)
    assert all(st[3] >= 1 and st[2] >= 2 for st in R.SETTINGS)
    norm = set()
    for n, r, d in R.SCHEDS:
        a = R.offsets(97, n, r, d)
        for n2 in range(1, 97):                   # no R87 zero-phase schedule (n 1-96, d +-1) equals it up to a constant
            for d2 in (1, -1):
                assert len({(x - d2 * (i // n2)) % 26 for i, x in enumerate(a)}) > 1
        norm.add(tuple((x - a[0]) % 26 for x in a))
    assert len(norm) == 12                        # the 12 clocks are distinct up to a constant
    print("1 ok: round trips and witness on 400 settings; 192 labels; no clock equals an R87 schedule (n 1-96) up to a"
          " constant; the 12 clocks are distinct")


def test_phase_oracle():
    W = list(range(26))
    W[0], W[1] = W[1], W[0]

    def F(t, n, r):                       # the full map at time t: x -> W[x + s] - s
        s = (t + r) // n
        return tuple((W[(x + s) % 26] - s) % 26 for x in range(26))
    assert F(0, 2, 1) != F(1, 2, 1) == F(2, 2, 1)
    for n in (2, 3, 4):                   # zero phase, n >= 2: F0 == F1 always
        assert F(0, n, 0) == F(1, n, 0)
    print("2 ok: n=2, r=1 gives F0 != F1 == F2; every zero-phase schedule with n >= 2 has F0 == F1")


def test_kernel(rng):
    Q = rotor87.Quad()
    t = "".join(ch for ch in (ROOT / "k4kit/data/k1k3_plaintext.txt").read_text().upper() if "A" <= ch <= "Z")
    for k in range(8):
        W, st = rset(rng)
        o = rng.randrange(len(t) - 97)
        ct = R.encrypt(t[o:o + 97], W, *st)
        sc, W2 = S.run_one(ct, st, 1, 300, 2.0, rng.randrange(1, 2 ** 60))
        assert abs(Q.score(R.decrypt(ct, W2, *st)) - sc) < 1e-2
        if k < 3:
            sc, W3 = S.run_one(ct, st, 12, 40000, 4.0, 9)
            assert sum(a == b for a, b in zip(R.decrypt(ct, W3, *st), t[o:o + 97])) >= 95
    print("3 ok: kernel score equals the quadgram score of rotor92.decrypt; true-setting anneals recover plants")


def construct(ct, pos, letters, st):
    ein, eout, n, r, d = st
    s = R.offsets(len(ct), n, r, d)
    need = {}
    for i, p in zip(pos, letters):
        need.setdefault((R.IDX[ein][p] + s[i]) % 26, set()).add((R.IDX[eout][ct[i]] + s[i]) % 26)
    if any(len(v) > 1 for v in need.values()):
        return False
    ys = [next(iter(v)) for v in need.values()]
    return len(set(ys)) == len(ys)


def test_exact(rng):
    n = 0
    for case in range(60):
        W, st = rset(rng)
        pt = rtext(rng)
        ct = R.encrypt(pt, W, *st)
        pos = sorted(rng.sample(range(97), 5))
        lets = [pt[p] for p in pos]
        if case % 3 == 1:
            lets[0] = rng.choice([x for x in AZ if x != lets[0]])
        if case % 3 == 2:
            ct = rtext(rng)
        for s2 in R.SETTINGS[case % 7::7]:
            a, b = R.exact_check(ct, pos, lets, *s2), EX.feasible(ct, pos, lets, s2)
            assert a == b and a[0] == construct(ct, pos, lets, s2)
            n += 1
        if case % 3 == 0:
            assert EX.feasible(ct, pos, lets, st)[0]
    for _ in range(20):
        W, st = rset(rng)
        pt = rtext(rng)
        ct = R.encrypt(pt, W, *st)
        assert EX.feasible(ct, POS, [pt[p] for p in POS], st)[0]
        j = rng.choice(POS)                                       # one wrong ciphertext letter at a published position
        ct2 = ct[:j] + rng.choice([x for x in AZ if x != ct[j]]) + ct[j + 1:]
        assert sum(a != b for a, b in zip(R.decrypt(ct2, W, *st), pt)) == 1
        P2 = [p for p in POS if p != j]
        assert EX.feasible(ct2, P2, [pt[p] for p in P2], st)[0]   # DROP of that position restores feasibility
    print("4 ok: three exact-check implementations agree on", n, "cases; plants feasible; one error = one pair")


def test_witness_fail(rng):
    W, st = rset(rng)
    pt = rtext(rng)
    ct = R.encrypt(pt, W, *st)
    e = {"text": pt, "setting": sd(W, st), "lm_per_letter": -1.0, "word_per_letter": -2.0}
    with tempfile.TemporaryDirectory() as d:
        tsv, res = Path(d) / "t.tsv", Path(d) / "r.jsonl"

        def run(ct_in, e, best=None):
            tsv.write_text(f"id\tciphertext\nH_000\t{ct_in}\n")
            res.write_text(json.dumps({"id": "H_000", "best": best or e, "top": [e]}) + "\n")
            return WIT.check(tsv, res)["passed"]
        assert run(ct, e)
        assert not run(ct, {**e, "text": pt[:3] + ("A" if pt[3] != "A" else "B") + pt[4:]})
        W2 = list(W)
        W2[0], W2[1] = W2[1], W2[0]
        assert not run(ct, {**e, "setting": sd(W2, st)})
        assert not run(ct[:9] + ("A" if ct[9] != "A" else "B") + ct[10:], e)
        other = (st[0], st[1], st[2], (st[3] % (st[2] - 1)) + 1 if st[2] > 2 else st[3], st[4])
        if other != st:
            assert not run(ct, {**e, "setting": sd(W, other)})
        assert not run(ct, e, best={**e, "lm_per_letter": -0.5})
    print("5 ok: witness fails on a changed letter, wiring, ciphertext letter, phase or best")


def test_make(rng):
    words = [l.split("\t")[0] for l in (ROOT / "k4kit/data/word_model_orth.tsv").read_text().splitlines()[1:3000]]
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        r2 = random.Random(5)
        for g in ("a", "b", "c", "k"):
            (d / f"{g}.txt").write_text(" ".join(r2.choice(words) for _ in range(6000)))
        outs = []
        for k in range(2):
            subprocess.run([sys.executable, "-I", str(ROOT / "r92/sealed/make92.py"), f"{d}/a.txt,{d}/b.txt,{d}/c.txt",
                            str(d / "k.txt"), "123", str(d / f"o{k}"), "--neg-scale", "0.2"], check=True,
                           capture_output=True)
            outs.append((d / f"o{k}" / "TRUTH.json").read_text())
        assert outs[0] == outs[1]
        t = json.loads(outs[0])
        pos = [v for v in t.values() if v["class"] == "POS"]
        assert len(pos) == 48 and sum(v["masked"] for v in pos) == 12
        assert sorted(sum(v["genre"] == g for v in pos) for g in ("G1", "G2", "G3")) == [16, 16, 16]
        assert {v["cell"] for v in pos} == {"n2r1", "n3r1", "n3r2", "n4r1", "n4r2", "n4r3"}
        assert {v["generator"] for v in t.values() if v["class"] == "NEG"} == {g for g, _ in __import__("make92").GENS}
        for v in t.values():
            if v["class"] == "NEG":
                continue
            s = v["setting"]
            enc = R.encrypt(v["enciphered"], s["wiring"], s["ein"], s["eout"], s["n"], s["r"], s["d"])
            assert (sum(a != b for a, b in zip(enc, v["ct"])) == 1) if v.get("kind") == "CTERR" else enc == v["ct"]
    print("6 ok: make92 counts, cells, genre balance, masks, generators, re-encryption, determinism")


def test_gate():
    G.used_contacts_agree = lambda f, t, x: True              # judge reads the module global
    st0 = {"ein": "AZ", "eout": "AZ", "n": 2, "r": 1, "d": 1, "wiring": list(range(26))}

    def build(nok, neg_conf, exact_fail=0):
        truth, res, k = {}, {}, 0
        cells = ["n2r1", "n3r1", "n3r2", "n4r1", "n4r2", "n4r3"]
        for ci, c in enumerate(cells):
            for j in range(8):
                good = ci * 8 + j < nok
                truth[f"H_{k}"] = {"class": "POS", "cell": c, "genre": f"G{(ci + j) % 3 + 1}", "masked": j < 2,
                                   "enciphered": "A" * 97, "setting": st0}
                txt = ("A" * 96 + ("B" if ci * 8 + j < exact_fail else "A")) if good else "B" * 97
                res[f"H_{k}"] = {"best": {"text": txt, "setting": st0, "lm_per_letter": -1.0, "word_per_letter": -2.0}}
                k += 1
        for j in range(150):
            truth[f"H_{k}"] = {"class": "NEG", "generator": "VIG"}
            res[f"H_{k}"] = {"best": {"text": "C" * 97, "setting": st0, "word_per_letter": -2.0,
                                      "lm_per_letter": -1.0 if j < neg_conf else -1.6}}
            k += 1
        return truth, res

    assert G.judge(*build(48, 1))[0]
    assert not G.judge(*build(48, 2))[0]                      # 2 confident negatives
    assert not G.judge(*build(41, 0))[0]                      # 41 < 42 (and cell n4r3 drops to 1/8)
    assert not G.judge(*build(48, 0, exact_fail=13))[0]       # exact 35 < 36
    assert G.judge(*build(48, 0, exact_fail=12))[0]
    print("7 ok: gate bars (42/48, exact 36, cells, genres, masked, <= 1/150 negatives) applied")


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
    print("8 ok: sandbox refuses extra fields, a published word, a short row and a reused sandbox")


def main():
    rng = random.Random(920901)
    test_family(rng)
    test_phase_oracle()
    test_kernel(rng)
    test_exact(rng)
    test_witness_fail(rng)
    test_make(rng)
    test_gate()
    test_sandbox(rng)
    print("R92 TESTS OK")


if __name__ == "__main__":
    main()
