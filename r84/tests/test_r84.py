#!/usr/bin/env python3
"""R84 tests (synthetic only; no K4 data, no published letters).
1 the independent witness encipherer (r84/sealed/witness84.py) equals R80a's reference cipher (r80a/two80.py) on 400
  random settings of all four families, and two80.decrypt inverts it;
2 the witness check passes R80a's 1,762 archived holdout witnesses and FAILS when one decoded letter, one setting
  letter or one ciphertext letter is changed (negative controls);
3 the sandbox builder refuses an input with extra fields, an input containing a published K4 word, and a reused box;
4 the sealed evaluation, on SYNTHETIC rows only (R80a holdout items relabelled), refuses files missing from the freeze
  and a failed witness check, and computes p_family from the shuffles.
Usage: python3 -I r84/tests/test_r84.py"""
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "r84" / "sealed"), str(ROOT / "r80a")]
import witness84 as W  # noqa: E402
import two80 as T  # noqa: E402


def test_cipher(rng):
    for k in range(400):
        fam = T.FAMS[k % 4]
        st = T.random_setting(rng, fam, 1, 12)
        pt = "".join(rng.choice(T.AZ) for _ in range(97))
        ct = T.encrypt(pt, st)
        assert W.encipher(pt, st) == ct, st
        assert T.decrypt(ct, st) == pt
    print("1 ok: independent encipherer equals R80a's reference on 400 settings")


def test_witness(tmp):
    tsv, res = ROOT / "r80a/holdout/blind.tsv", ROOT / "r80a/holdout/run/RESULTS.jsonl"
    assert W.check(tsv, res)["passed"]
    lines = res.read_text().splitlines()
    r = json.loads(lines[3])
    bad = []
    t = r["top"][0]["text"]
    r1 = json.loads(lines[3]); r1["top"][0]["text"] = t[:5] + ("A" if t[5] != "A" else "B") + t[6:]; r1["best"] = r1["top"][0]
    bad.append(r1)
    r2 = json.loads(lines[3]); f = r2["top"][0]["setting"]["free"]
    r2["top"][0]["setting"]["free"] = ("A" if f[0] != "A" else "B") + f[1:]; r2["best"] = r2["top"][0]
    bad.append(r2)
    for k, rb in enumerate(bad):
        p = tmp / f"bad{k}.jsonl"
        p.write_text("\n".join(lines[:3] + [json.dumps(rb)] + lines[4:]) + "\n")
        assert not W.check(tsv, p)["passed"], k
    rows = tsv.read_text().splitlines()
    rid, ct = rows[4].split("\t")
    rows[4] = rid + "\t" + ("A" if ct[0] != "A" else "B") + ct[1:]
    p = tmp / "bad.tsv"
    p.write_text("\n".join(rows) + "\n")
    assert not W.check(p, res)["passed"]
    print("2 ok: 1,762 archived witnesses pass; a changed decode letter, key letter or ciphertext letter fails")


def test_sandbox(tmp):
    lm = Path("/nonexistent")
    def run(box, inp):
        return subprocess.run([sys.executable, "-I", str(ROOT / "r84/sealed/make_sandbox.py"), str(box), str(lm),
                               str(inp)], capture_output=True, text=True)
    # these must fail before or at the input check; a missing letter model fails first, so test the input rules
    # through the checker's own regular expressions
    import make_sandbox as MS
    assert MS.CLUE.search(b"XXBERLINXX") and MS.CLUE.search(b"eastnortheast")
    assert MS.CLUE_NAME.search("r73/sealed/reveal_k4.py") and MS.CLUE_NAME.search("sealed_truth.json")
    assert not any(MS.CLUE_NAME.search(f) for f in MS.CODE + MS.DICTS)
    good = "id\tciphertext\nX1\t" + "A" * 97 + "\n"
    cases = {"extra field": "id\tciphertext\nX1\t" + "A" * 97 + "\tKEY\n",
             "published word": "id\tciphertext\nX1\t" + "A" * 91 + "BERLIN" + "\n",
             "short row": "id\tciphertext\nX1\t" + "A" * 96 + "\n"}
    for name, text in cases.items():
        (tmp / "in.tsv").write_text(text)
        r = run(tmp / f"box_{name.replace(' ', '_')}", tmp / "in.tsv")
        assert r.returncode != 0 and ("tripwire" in r.stderr or "input must be" in r.stderr), (name, r.stderr[-300:])
    (tmp / "in.tsv").write_text(good)
    r = run(tmp / "box_good", tmp / "in.tsv")
    assert r.returncode != 0 and "No such file" in r.stderr, r.stderr[-300:]      # passes the input, stops at the model
    box = tmp / "box"
    box.mkdir()
    assert "refusing to reuse" in run(box, tmp / "in.tsv").stderr
    print("3 ok: sandbox refuses extra fields, a published word, a short row and a reused box; tripwire patterns")


def test_evaluate():
    import hashlib
    res = [json.loads(l) for l in (ROOT / "r80a/holdout/run/RESULTS.jsonl").read_text().splitlines()[:5]]
    cts = dict(l.split("\t") for l in (ROOT / "r80a/holdout/blind.tsv").read_text().splitlines()[1:6])
    ids = ["K4", "NULL_000", "NULL_001", "NULL_002", "NULL_003"]
    with tempfile.TemporaryDirectory(dir=ROOT / "r84") as d:
        d = Path(d)
        rows = []
        for new, r in zip(ids, res):
            rows.append((new, cts[r["id"]]))
            r["id"] = new
        (d / "T.tsv").write_text("id\tciphertext\n" + "".join(f"{a}\t{b}\n" for a, b in rows))
        (d / "R.jsonl").write_text("".join(json.dumps(r) + "\n" for r in res))
        W.check(d / "T.tsv", d / "R.jsonl")
        (d / "W.json").write_text(json.dumps(W.check(d / "T.tsv", d / "R.jsonl")))
        rel = lambda p: str(p.relative_to(ROOT))  # noqa: E731
        h = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()  # noqa: E731
        ev = [sys.executable, "-I", str(ROOT / "r84/sealed/evaluate84.py"), str(d / "T.tsv"), str(d / "R.jsonl"),
              str(d / "W.json"), str(d / "F.sha256"), str(d / "REP.json")]
        (d / "F.sha256").write_text(f"{h(d / 'T.tsv')}  {rel(d / 'T.tsv')}\n{h(d / 'R.jsonl')}  {rel(d / 'R.jsonl')}\n")
        r = subprocess.run(ev, capture_output=True, text=True)
        assert r.returncode != 0 and "is not frozen" in r.stderr, r.stderr[-300:]
        (d / "F.sha256").write_text("".join(f"{h(d / n)}  {rel(d / n)}\n" for n in ("T.tsv", "R.jsonl", "W.json")))
        r = subprocess.run(ev, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr[-500:]
        rep = json.loads((d / "REP.json").read_text())
        k4 = res[0]["best"]["lm_per_letter"]
        n_ge = sum(x["best"]["lm_per_letter"] >= k4 for x in res[1:])
        assert rep["nulls_at_or_above_k4"] == n_ge and abs(rep["p_family"] - (1 + n_ge) / 5) < 1e-12
        wj = json.loads((d / "W.json").read_text()); wj["passed"] = False
        (d / "W.json").write_text(json.dumps(wj))
        (d / "F.sha256").write_text("".join(f"{h(d / n)}  {rel(d / n)}\n" for n in ("T.tsv", "R.jsonl", "W.json")))
        r = subprocess.run(ev, capture_output=True, text=True)
        assert r.returncode != 0 and "witness check did not pass" in r.stderr, r.stderr[-300:]
    print("4 ok: evaluation refuses unfrozen files and a failed witness check; p_family computed from the shuffles")


def main():
    rng = random.Random(840601)
    with tempfile.TemporaryDirectory() as d:
        test_cipher(rng)
        test_witness(Path(d))
        test_sandbox(Path(d))
    test_evaluate()
    print("R84 TESTS OK")


if __name__ == "__main__":
    main()
