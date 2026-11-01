#!/usr/bin/env python3
"""R44/R44b reproducibility and data-contract tests (Claude Code; added after the owner review of PR #12).
Run from anywhere: python3 -I r44/tests/test_r44_claude.py    (needs g++; about 10 s)

Checks, in order:
 1. Pre-registration and freeze hashes (PROTOCOL.sha256, PROTOCOL_B.sha256, holdout{,_b}/FROZEN.sha256) still match
    the committed files, so nothing frozen has been edited.
 2. Every R44 C++ program compiles (blind solver, polish, word-move PT, audits).
 3. The EdgeGraph audit passes: 500 positive controls, random partial witnesses re-encrypt, impossible packing rejected.
 4. Holdout B replay: re-running polish on the frozen solver output reproduces RESULTS.jsonl exactly, and the R43
    sealed evaluator on RESULTS.jsonl reproduces EVALUATION.json (20/20 exact). The true key is supplied in this
    benchmark: it is a KNOWN-KEY result, not an unknown-key recovery.
Uses the Python standard library only."""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
R44 = ROOT / "r44"
FAIL = []


def check(ok, msg):
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok:
        FAIL.append(msg)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def hash_file(listing, base):
    for line in Path(listing).read_text().splitlines():
        if not line.strip():
            continue
        h, name = line.split(None, 1)
        p = (base / name.strip()).resolve()
        check(p.exists() and sha(p) == h, f"hash {listing.relative_to(ROOT)}: {name.strip()}")


def build(src, out):
    r = subprocess.run(["g++", "-std=c++17", "-O2", str(src), "-o", str(out)], cwd=src.parent,
                       capture_output=True, text=True)
    check(r.returncode == 0, f"compile {src.relative_to(ROOT)}" + ("" if r.returncode == 0 else "\n" + r.stderr[-2000:]))
    return r.returncode == 0


def main():
    hash_file(R44 / "PROTOCOL.sha256", R44)
    hash_file(R44 / "PROTOCOL_B.sha256", R44)
    hash_file(R44 / "holdout/FROZEN.sha256", ROOT)
    hash_file(R44 / "holdout_b/FROZEN.sha256", ROOT)

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        srcs = {"kwpa_solve": R44 / "blind/kwpa_solve.cpp", "polish": R44 / "blind/polish.cpp",
                "wordpt": R44 / "blind/wordpt.cpp", "audit_edgegraph": R44 / "audit/audit_edgegraph.cpp",
                "kw_exact_check": R44 / "audit/kw_exact_check.cpp", "rk_exact_check": R44 / "audit/rk_exact_check.cpp",
                "rot_exact_check": R44 / "audit/rot_exact_check.cpp"}
        built = {k: build(v, td / k) for k, v in srcs.items()}

        if built["audit_edgegraph"]:
            r = subprocess.run([str(td / "audit_edgegraph")], cwd=R44 / "audit", capture_output=True, text=True)
            out = r.stdout + r.stderr
            check(r.returncode == 0 and "failures 0" in out and "positive controls 500" in out
                  and "alphabets 0 (expected 1, 1, 0)" in out, "EdgeGraph audit: 500 controls, 0 failures, packing")

        if built["polish"]:
            hb = R44 / "holdout_b"
            pol = td / "polish.jsonl"
            r = subprocess.run([str(td / "polish"), str(ROOT / "k4kit/data/word_model_orth.tsv"),
                                str(ROOT / "k4kit/data/quad_log10.f32"), str(hb / "blind.tsv"), str(hb / "SOLVER.jsonl"),
                                str(pol), "1"], capture_output=True, text=True)
            check(r.returncode == 0, "polish runs on frozen holdout B solver output")
            if r.returncode == 0:
                a = [json.loads(l) for l in pol.read_text().splitlines() if l.strip()]
                b = [json.loads(l) for l in (hb / "RESULTS.jsonl").read_text().splitlines() if l.strip()]
                same = len(a) == len(b) == 20 and all(
                    x["id"] == y["id"] and x["plaintext"] == y["plaintext"]
                    and x["ciphertext_alphabet"] == y["ciphertext_alphabet"] for x, y in zip(a, b))
                check(same, "polish replay reproduces holdout B RESULTS.jsonl (20 rows)")
            rep = td / "eval.json"
            r = subprocess.run([sys.executable, "-I", str(ROOT / "r43/sealed/evaluate.py"), str(hb / "blind.tsv"),
                                str(hb / "RESULTS.jsonl"), str(hb / "sealed_truth.json"), str(rep)],
                               capture_output=True, text=True)
            check(r.returncode == 0, "R43 sealed evaluator runs on holdout B")
            if r.returncode == 0:
                new, old = json.loads(rep.read_text()), json.loads((hb / "EVALUATION.json").read_text())
                check(new.get("exact") == old.get("exact") == 20 and new.get("total") == 20
                      and new.get("all_forward_witnesses_valid") is True, "holdout B evaluation: 20/20 exact, witnesses valid")

    print(f"\n{'ALL R44 TESTS PASSED' if not FAIL else f'{len(FAIL)} FAILURE(S)'}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
