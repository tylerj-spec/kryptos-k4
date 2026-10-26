#!/usr/bin/env python3
"""Validate the toolkit on this machine (about 2 minutes). Run from the toolkit root after building the solver:
    g++ -std=c++17 -O3 -march=native tools/solver_s2kp.cpp -o bin/solver_s2kp
    python3 tools/validate.py
Checks: data hashes; key oracle on Gromark (39/100,000); Trifid planted + K4; book harness smoke test (0 passes on
K1-K3 text); solver reproduction of the R21 S2 rows for K4 primer 88254 (exact only with g++/libstdc++) and a short
planted recovery check (meaningful on any platform)."""
import hashlib
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))
from k4common import ANCH, AZ, BIN, DATA, K4, MASK, gromark_key, solver_line  # noqa: E402
from key_oracle import possible  # noqa: E402

ok = True


def report(name, good, detail=""):
    global ok
    ok &= good
    print(f"[{'PASS' if good else 'FAIL'}] {name} {detail}", flush=True)


H = {"word_model_orth.tsv": "12392e2d463631bbcaafd7aa56eb2bc391325d8964e6f5c19b13786a48676877",
     "quad_log10.f32": "d2a64e70154725a0c0d1901690df47c73086e0bfc112ad419aad2eb069f89a43"}
for f, h in H.items():
    report(f"data {f}", hashlib.sha256((DATA / f).read_bytes()).hexdigest() == h)

n = sum(possible(gromark_key(p)) for p in range(100000))
report("oracle: Gromark primers possible", n == 39, f"({n}, expected 39)")

import trifid_any as tf  # noqa: E402
rng = random.Random(1)
good = True
for p in (3, 11, 40, 97):
    cube = list(tf.SYM)
    rng.shuffle(cube)
    pt = [rng.choice(AZ) for _ in range(97)]
    for i, c in ANCH.items():
        pt[i] = c
    good &= tf.solve(tf.constraints(tf.encrypt("".join(pt), "".join(cube), p), ANCH, p)) == "possible"
k4imp = all(tf.solve(tf.constraints(K4, ANCH, p)) == "impossible" for p in range(1, 98))
report("trifid: planted possible, K4 impossible at every period", good and k4imp)

with tempfile.TemporaryDirectory() as td:
    out = subprocess.run([sys.executable, str(TOOLS / "book_key_test.py"), str(DATA / "k1k3_plaintext.txt")],
                         capture_output=True, text=True, cwd=td).stdout
    report("book harness on K1-K3 text: 0 passes", "oracle: 0 passes" in out, out.splitlines()[1] if out else "")

    exe = BIN / "solver_s2kp"
    if not exe.exists():
        report("solver binary", False, "(build it first)")
    else:
        seed = random.Random("K4-88254").randrange(1, 2 ** 63)
        Path(td, "in.txt").write_text(solver_line("K4@88254", gromark_key(88254), K4, ANCH, seed) + "\n")
        subprocess.run([str(exe), str(DATA / "word_model_orth.tsv"), str(DATA / "quad_log10.f32"), str(Path(td, "in.txt")),
                        str(Path(td, "out.jsonl")), "64", "40000", "0.05", "0"], check=True)
        new = [json.loads(x)["plaintext"] for x in open(Path(td, "out.jsonl"))]
        old = [json.loads(x)["plaintext"] for x in open(ROOT / "fixtures/s2_k4_primer88254_rows.jsonl")]
        same = sum(a == b for a, b in zip(new, old))
        print(f"[INFO] solver reproduces R21 S2 rows for K4 primer 88254: {same}/64 identical "
              "(64 expected with g++/libstdc++; other C++ libraries give different random streams)")
        # planted recovery (platform independent): 6 calibration passages, identity order, random keys
        bases = json.loads((DATA / "reference_messages.json").read_text())["calibration"][:6]
        lines, truth = [], {}
        for i, P in enumerate(bases):
            pa, ca = list(AZ), list(AZ)
            rng.shuffle(pa)
            rng.shuffle(ca)
            k = gromark_key(rng.randrange(100000))
            ct = "".join(ca[(pa.index(P[t]) + k[t]) % 26] for t in range(97))
            lines.append(solver_line(f"P{i}", k, ct, ANCH, rng.randrange(1, 2 ** 63)))
            truth[f"P{i}"] = P
        Path(td, "cal.txt").write_text("\n".join(lines) + "\n")
        subprocess.run([str(exe), str(DATA / "word_model_orth.tsv"), str(DATA / "quad_log10.f32"), str(Path(td, "cal.txt")),
                        str(Path(td, "cal.jsonl")), "64", "40000", "0.05", "0"], check=True)
        best = {}
        for x in open(Path(td, "cal.jsonl")):
            r = json.loads(x)
            if r["id"] not in best or r["W"] > best[r["id"]]["W"]:
                best[r["id"]] = r
        rd = sum(sum(a != b for a, b in zip(best[i]["plaintext"], truth[i])) <= 5 for i in truth)
        report("solver planted recovery (identity order, 64 restarts)", rd >= 2, f"({rd}/6 readable; R21 rate ~70%)")
print("ALL CHECKS PASSED" if ok else "SOME CHECKS FAILED")
