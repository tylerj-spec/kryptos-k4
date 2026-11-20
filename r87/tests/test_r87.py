#!/usr/bin/env python3
"""Tests for R87 (synthetic only; no K4 ciphertext is read and no published letter is used: K4's published POSITIONS
are used for layout only, as r83/tests does).
1 rotor87 encrypt/decrypt round-trip; the independent witness encipherer (witness87) equals rotor87.encrypt on 400
  random settings (all 16 alphabet pairs, n 1-96, d +-1);
2 the C kernel's decode equals the explicit decryptor: its returned score equals the quadgram score of
  rotor87.decrypt under the returned wiring, on random settings;
3 exact checks: rotor87.exact_check == exact87.feasible == a constructive completion of the wiring (5 random positions, every
  7th setting) on planted, altered and random cases; a plant's true setting is always feasible at K4's positions;
4 the witness check fails when one decoded letter, the wiring (one swap) or one ciphertext letter is changed, and when
  best != top[0]; it passes on an honest record;
5 the sandbox builder refuses extra fields, a published word, a short row and a reused sandbox;
6 make87: counts per class, every positive re-encrypts, every CTERR differs from its clean ciphertext in exactly one
  letter, deterministic for a seed;
7 gate87.judge: bars applied as pre-registered (a constructed pass and three constructed failures).
Usage: python3 -I r87/tests/test_r87.py"""
import itertools
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "r87"), str(ROOT / "r87" / "blind"), str(ROOT / "r87" / "sealed")]
import rotor87 as R  # noqa: E402
import solve87 as S  # noqa: E402
import witness87 as WIT  # noqa: E402
import exact87 as EX  # noqa: E402
import make_sandbox87 as SB  # noqa: E402
import gate87 as G  # noqa: E402

AZ = R.AZ
POS = list(range(21, 34)) + list(range(63, 74))


def rsetting(rng, nmax=96):
    W = list(range(26))
    rng.shuffle(W)
    return W, (rng.choice(R.A4), rng.choice(R.A4), rng.randint(1, nmax), rng.choice((1, -1)))


def rtext(rng, n=97):
    return "".join(rng.choice(AZ) for _ in range(n))


def test_cipher(rng):
    for _ in range(400):
        W, st = rsetting(rng)
        pt = rtext(rng)
        ct = R.encrypt(pt, W, *st)
        assert R.decrypt(ct, W, *st) == pt
        assert WIT.encipher(pt, {"ein": st[0], "eout": st[1], "n": st[2], "d": st[3], "wiring": W}) == ct
    print("1 ok: round trip; independent witness encipherer equals rotor87.encrypt on 400 random settings")


def test_kernel(rng):
    Q = R.Quad()
    for _ in range(12):
        W, st = rsetting(rng, 32)
        ct = R.encrypt(rtext(rng), W, *st)
        sc, W2 = S.run_one(ct, st, 1, 300, 2.0, rng.randrange(1, 2 ** 60))
        assert sorted(W2) == list(range(26))
        t = R.decrypt(ct, W2, *st)
        assert R.encrypt(t, W2, *st) == ct
        assert abs(Q.score(t) - sc) < 1e-2, (Q.score(t), sc)
    print("2 ok: kernel score equals the quadgram score of the explicit decrypt under its wiring (12 settings)")


def brute(ct, pos, letters, st):
    ein, eout, n, d = st
    need = {}
    for i, p in zip(pos, letters):
        s = d * (i // n)
        need.setdefault((R.IDX[ein][p] + s) % 26, set()).add((R.IDX[eout][ct[i]] + s) % 26)
    if any(len(v) > 1 for v in need.values()):
        return False
    xs = sorted(need)
    ys = [next(iter(need[x])) for x in xs]
    # search for a permutation of 0..25 extending x -> y (exists iff ys distinct); verify by construction
    if len(set(ys)) != len(ys):
        return False
    rest = [y for y in range(26) if y not in ys]
    W = [None] * 26
    for x, y in zip(xs, ys):
        W[x] = y
    it = iter(rest)
    W = [w if w is not None else next(it) for w in W]
    return all(W[(R.IDX[ein][p] + d * (i // n)) % 26] == (R.IDX[eout][ct[i]] + d * (i // n)) % 26
               for i, p in zip(pos, letters))


def test_exact(rng):
    n_cases = 0
    for case in range(60):
        W, st = rsetting(rng)
        pt = rtext(rng)
        ct = R.encrypt(pt, W, *st)
        pos = sorted(rng.sample(range(97), 5))
        lets = [pt[i] for i in pos]
        if case % 3 == 1:
            lets[0] = rng.choice([x for x in AZ if x != lets[0]])
        if case % 3 == 2:
            ct = rtext(rng)
        for s2 in EX.SETTINGS[::7]:
            a = R.exact_check(ct, pos, lets, *s2)
            b = EX.feasible(ct, pos, lets, s2)
            c = brute(ct, pos, lets, s2)
            assert a[0] == b[0] == c and a[1] == b[1], (s2, a, b, c)
            n_cases += 1
        assert EX.feasible(ct if case % 3 != 2 else ct, pos, lets, st)[0] or case % 3 != 0
    for _ in range(40):
        W, st = rsetting(rng)
        pt = rtext(rng)
        ct = R.encrypt(pt, W, *st)
        ok, c = EX.feasible(ct, POS, [pt[i] for i in POS], st)
        assert ok and c == R.exact_check(ct, POS, [pt[i] for i in POS], *st)[1]
    print("3 ok: exact checks agree three ways on", n_cases, "setting cases; 40 plants feasible at K4's positions")


def record(ct, text, W, st, lm=-1.0):
    e = {"text": text, "setting": {"ein": st[0], "eout": st[1], "n": st[2], "d": st[3], "wiring": W},
         "lm_per_letter": lm, "word_per_letter": -2.0}
    return {"id": "H_000", "n_settings": 1024, "best": e, "top": [e]}


def test_witness(rng):
    W, st = rsetting(rng, 32)
    pt = rtext(rng)
    ct = R.encrypt(pt, W, *st)
    with tempfile.TemporaryDirectory() as d:
        tsv, res = Path(d) / "t.tsv", Path(d) / "r.jsonl"

        def run(ct_in, rec):
            tsv.write_text(f"id\tciphertext\nH_000\t{ct_in}\n")
            res.write_text(json.dumps(rec) + "\n")
            return WIT.check(tsv, res)["passed"]

        assert run(ct, record(ct, pt, W, st))
        bad = pt[:10] + ("A" if pt[10] != "A" else "B") + pt[11:]
        assert not run(ct, record(ct, bad, W, st))
        W2 = list(W)
        W2[0], W2[1] = W2[1], W2[0]
        assert not run(ct, record(ct, pt, W2, st))
        ct2 = ct[:50] + ("A" if ct[50] != "A" else "B") + ct[51:]
        assert not run(ct2, record(ct, pt, W, st))
        r = record(ct, pt, W, st)
        r["best"] = dict(r["best"], lm_per_letter=-0.5)
        assert not run(ct, r)
    print("4 ok: witness passes an honest record and fails on a changed letter, wiring, ciphertext, or best")


def test_sandbox(rng):
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        good = "id\tciphertext\nX_1\t" + rtext(rng) + "\n"
        cases = {"extra field": "id\tciphertext\tkey\nX_1\t" + rtext(rng) + "\tABC\n",
                 "published word": "id\tciphertext\nX_1\t" + rtext(rng, 91) + "BERLIN\n",
                 "short row": "id\tciphertext\nX_1\t" + rtext(rng, 96) + "\n"}
        for name, body in cases.items():
            p = d / f"{name}.tsv"
            p.write_text(body)
            try:
                SB.build(d / ("box_" + name.replace(" ", "_")), d / "nolm.bin", p)
                raise AssertionError(f"accepted: {name}")
            except SystemExit:
                pass
        (d / "used").mkdir()
        (d / "g.tsv").write_text(good)
        try:
            SB.build(d / "used", d / "nolm.bin", d / "g.tsv")
            raise AssertionError("accepted a reused sandbox")
        except SystemExit:
            pass
    print("5 ok: sandbox refuses extra fields, a published word, a short row and a reused sandbox")


def test_make(rng):
    words = [l.split("\t")[0] for l in (ROOT / "k4kit/data/word_model_orth.tsv").read_text().splitlines()[1:3000]]
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        r2 = random.Random(5)
        (d / "a.txt").write_text(" ".join(r2.choice(words) for _ in range(6000)))
        (d / "b.txt").write_text(" ".join(r2.choice(words) for _ in range(6000)))
        outs = []
        for k in range(2):
            subprocess.run([sys.executable, "-I", str(ROOT / "r87/sealed/make87.py"), str(d / "a.txt"),
                            str(d / "b.txt"), "123", "2", "1", "1", str(d / f"o{k}")], check=True, capture_output=True)
            outs.append((d / f"o{k}" / "TRUTH.json").read_text())
        assert outs[0] == outs[1]
        t = json.loads(outs[0])
        cls = [v["class"] for v in t.values()]
        assert cls.count("POS") == 8 and cls.count("CTERR") == 4 and cls.count("NEG") == 9
        for v in t.values():
            if v["class"] != "NEG":
                s = v["setting"]
                key = (s["wiring"], s["ein"], s["eout"], s["n"], s["d"])
                if v["class"] == "POS":
                    assert R.encrypt(v["enciphered"], *key) == v["ct"]
                else:
                    assert R.encrypt(v["pt"], *key) == v["ct_clean"]
                    assert sum(a != b for a, b in zip(v["ct"], v["ct_clean"])) == 1
    print("6 ok: make87 counts, re-encryption, one-letter ciphertext errors, determinism")


def test_gate():
    def truth_res(n_ok_per_stratum, neg_conf):
        truth, res = {}, {}
        k = 0
        for s in ("S1", "S2", "S3", "S4"):
            for j in range(12):
                txt = "A" * 97
                ok = j < n_ok_per_stratum[s]
                truth[f"H_{k}"] = {"class": "POS", "stratum": s, "kind": "plain" if j % 2 == 0 else "changed2",
                                   "enciphered": txt, "setting": {"ein": "AZ", "eout": "AZ", "n": 1, "d": 1}}
                b = {"text": txt if ok else "B" * 97, "lm_per_letter": -1.0, "word_per_letter": -2.0,
                     "setting": {"ein": "AZ", "eout": "AZ", "n": 1, "d": 1}}
                res[f"H_{k}"] = {"best": b}
                k += 1
        for j in range(90):
            truth[f"H_{k}"] = {"class": "NEG", "generator": "VIG"}
            res[f"H_{k}"] = {"best": {"text": "C" * 97, "word_per_letter": -2.0,
                                      "lm_per_letter": -1.0 if j < neg_conf else -1.6}}
            k += 1
        return truth, res

    assert G.judge(*truth_res({"S1": 10, "S2": 10, "S3": 10, "S4": 10}, 1))[0]
    assert not G.judge(*truth_res({"S1": 10, "S2": 10, "S3": 10, "S4": 9}, 0))[0]       # 39 < 40
    assert not G.judge(*truth_res({"S1": 12, "S2": 12, "S3": 12, "S4": 8}, 0))[0]       # stratum 8 < 9
    assert not G.judge(*truth_res({"S1": 12, "S2": 12, "S3": 12, "S4": 12}, 2))[0]      # 2 negatives confident
    print("7 ok: gate bars (40/48, 9/12 per stratum, <= 1/90 negatives) applied as pre-registered")


def main():
    rng = random.Random(870901)
    test_cipher(rng)
    test_kernel(rng)
    test_exact(rng)
    test_witness(rng)
    test_sandbox(rng)
    test_make(rng)
    test_gate()
    print("R87 TESTS OK")


if __name__ == "__main__":
    main()
