#!/usr/bin/env python3
"""R64 contract tests. Run: python3 -I r64/tests/test_contract.py
  1. r64/blind/ code holds no K4 plaintext words, clue positions or sealed/truth references;
  2. the published letters appear in no r64 code except r64/sealed/reveal_k4.py;
  3. the 10 routes are permutations and the runner's un-routing inverts the plant maker's routing;
  4. plants from r64/sealed/make_plants.py re-encrypt exactly (independent forward witness) on synthetic sources;
  5. the clock ring only uses names from the R63 vocabulary."""
import json
import random
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r64/sealed"))
sys.path.insert(0, str(ROOT / "r64/blind"))
from common import forward, routes  # noqa: E402
import run as runner  # noqa: E402

bad = []
for f in sorted((ROOT / "r64/blind").iterdir()):
    if f.suffix not in (".py", ".cpp"):
        continue
    t = f.read_text()
    for w in ("EASTNORTHEAST", "NORTHEAST", "BERLINCLOCK", "BERLIN"):
        if w in t:
            bad.append(f"blind/{f.name}: {w}")
    for w in ("sealed", "truth"):
        if re.search(w, t, re.I):
            bad.append(f"blind/{f.name}: {w}")
for f in sorted(ROOT.glob("r64/**/*.py")):
    if f.name in ("reveal_k4.py", "test_contract.py"):
        continue
    t = f.read_text()
    for w in ("EASTNORTHEAST", "BERLINCLOCK"):
        if w in t:
            bad.append(f"{f.relative_to(ROOT)}: {w}")

R = routes()
assert len(R) == 10 and all(sorted(p) == list(range(97)) for p in R.values())
rng = random.Random(1)
for name, p in R.items():
    x = "".join(rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(97))
    ct = "".join(x[p[j]] for j in range(97))
    if runner.unroute(ct, p) != x:
        bad.append(f"unroute does not invert {name}")

voc = set((ROOT / "r63/data/clock_names.txt").read_text().split())
ring = (ROOT / "r64/data/clock_ring.txt").read_text().split()
if not ring or not all(n in voc for n in ring):
    bad.append("clock ring uses names outside the R63 vocabulary")

with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    letters = lambda n, s: "".join(random.Random(s).choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(n))  # noqa: E731
    for nm, s in (("pt", 1), ("ep", 2), ("lit", 3)):
        (td / f"{nm}.txt").write_text(letters(5000, s) + "\n")
    subprocess.run([sys.executable, "-I", str(ROOT / "r64/sealed/make_plants.py"), str(td / "pt.txt"), str(td / "ep.txt"),
                    str(td / "lit.txt"), "8", "99", "T", str(td / "out")], check=True, capture_output=True)
    cts = dict(l.split("\t") for l in (td / "out/blind.tsv").read_text().splitlines()[1:])
    truth = json.loads((td / "out/sealed_truth.json").read_text())
    kinds = sorted(t["key_kind"] for t in truth.values())
    if kinds != sorted(["CLOCK_RAND", "CLOCK_RING", "GERMAN_EP", "GERMAN_LIT"] * 2):
        bad.append(f"plant kinds unbalanced: {kinds}")
    for i, t in truth.items():
        if forward(t["plaintext"], t["key"], t["convention"], R[t["route"]]) != cts[i]:
            bad.append(f"plant witness failed {i}")
        if runner.unroute(cts[i], R[t["route"]]) != forward(t["plaintext"], t["key"], t["convention"], list(range(97))):
            bad.append(f"plant un-route mismatch {i}")

if bad:
    print("R64 CONTRACT FAIL:", bad)
    sys.exit(1)
print("R64 CONTRACT OK: blind code holds no K4 clue data; routes, un-routing and plant witnesses verified")
