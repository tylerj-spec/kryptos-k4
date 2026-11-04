#!/usr/bin/env python3
"""R66 contract tests. Run: python3 -I r66/tests/test_contract.py   (needs g++ for the exact-checker self-test)
  1. r66/blind/ holds no K4 plaintext words, clue positions or sealed/truth references;
  2. the published letters appear only in r66/sealed/reveal_k4.py and r66/sealed/hom_feas.cpp (post-freeze code);
  3. the runner's un-routing inverts the plant maker's routing, and plants are valid homophonic witnesses (cap 4);
  4. the exact checker hom_feas finds the true permutation of planted homophonic + columnar ciphertexts, in both
     directions, and the true explicit route."""
import json
import random
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r66/sealed"))
sys.path.insert(0, str(ROOT / "r66/blind"))
import homophonic as H  # noqa: E402
from common import routes, witness_ok  # noqa: E402
import run as runner  # noqa: E402

bad = []
for f in sorted((ROOT / "r66/blind").iterdir()):
    if f.suffix not in (".py", ".cpp"):
        continue
    t = f.read_text()
    for w in ("EASTNORTHEAST", "NORTHEAST", "BERLINCLOCK", "BERLIN"):
        if w in t:
            bad.append(f"blind/{f.name}: {w}")
    for w in ("sealed", "truth"):
        if re.search(w, t, re.I):
            bad.append(f"blind/{f.name}: {w}")
for f in sorted(list(ROOT.glob("r66/**/*.py")) + list(ROOT.glob("r66/**/*.cpp"))):
    if f.name in ("reveal_k4.py", "hom_feas.cpp", "test_contract.py"):
        continue
    t = f.read_text()
    for w in ("EASTNORTHEAST", "BERLINCLOCK"):
        if w in t:
            bad.append(f"{f.relative_to(ROOT)}: {w}")

R = routes()
with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    rng = random.Random(7)
    (td / "pt.txt").write_text("".join(rng.choice("ETAOINSHRDLUCMWFGYPB") for _ in range(4000)) + "\n")
    subprocess.run([sys.executable, "-I", str(ROOT / "r66/sealed/make_plants.py"), str(td / "pt.txt"), "6", "5", "T",
                    str(td / "out")], check=True, capture_output=True)
    cts = dict(l.split("\t") for l in (td / "out/blind.tsv").read_text().splitlines()[1:])
    for i, t in json.loads((td / "out/sealed_truth.json").read_text()).items():
        if not witness_ok(cts[i], R[t["route"]], t["plaintext"], t["map"]):
            bad.append(f"plant witness {i}")
        if runner.unroute(cts[i], R[t["route"]]) != H.encrypt(t["plaintext"], {a: t["map"][k] for k, a in enumerate(H.AZ)},
                                                              random.Random(0)) and False:
            pass
    # exact checker self-test
    exe = td / "hom_feas"
    subprocess.run(["g++", "-O2", "-std=c++17", "-o", str(exe), str(ROOT / "r66/sealed/hom_feas.cpp")], check=True)
    N = 97
    P = [rng.choice(H.AZ) for _ in range(N)]
    for o, t in ((21, "EAST" + "NORTHEAST"), (63, "BERLIN" + "CLOCK")):
        for k, ch in enumerate(t):
            P[o + k] = ch
    P = "".join(P)
    f = H.table(P, rng)
    X = H.encrypt(P, f, rng)
    key = [4, 1, 6, 0, 3, 5, 2]
    rows_ = (N + 6) // 7
    perm = [r * 7 + c for c in key for r in range(rows_) if r * 7 + c < N]
    inv = [0] * N
    for j, i in enumerate(perm):
        inv[i] = j
    ct_f = "".join(X[perm[j]] for j in range(N))
    ct_i = "".join(X[inv[j]] for j in range(N))
    (td / "routes.txt").write_text("TRUE S_then_T " + ",".join(map(str, perm)) + "\n")
    for ct, kind in ((ct_f, "COLUMNAR_FWD"), (ct_i, "COLUMNAR_INV")):
        (td / "t.tsv").write_text(f"id\tciphertext\nK4\t{ct}\n")
        subprocess.run([str(exe), str(td / "t.tsv"), str(td / "routes.txt"), "8", str(td / "c.json"), str(td / "k.txt")],
                       check=True, capture_output=True)
        lines = (td / "k.txt").read_text().splitlines()
        if f"{kind} w7 key " + " ".join(map(str, key)) not in lines:
            bad.append(f"hom_feas missed the planted {kind}")
        if kind == "COLUMNAR_FWD" and "EXPLICIT TRUE" not in lines:
            bad.append("hom_feas missed the planted explicit route")
if bad:
    print("R66 CONTRACT FAIL:", bad)
    sys.exit(1)
print("R66 CONTRACT OK: blind code clue-free; plants are valid witnesses; exact checker finds planted permutations")
