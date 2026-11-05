#!/usr/bin/env python3
"""R68 contract tests. Run: python3 -I r68/tests/test_contract.py
  1. r68/blind/ holds no K4 plaintext words, clue positions or sealed/truth references;
  2. the published letters appear only in r68/sealed/reveal_k4.py and r68/sealed/exact.py (post-freeze code);
  3. the runner's (path, model) rows plus the sealed decryptor recover synthetic plants exactly, for all families;
  4. the exact checker reports the true setting of planted ciphertexts (with the clue words planted) as feasible."""
import json
import random
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r68/sealed"))
sys.path.insert(0, str(ROOT / "r68/blind"))
import common as C  # noqa: E402
import run as R  # noqa: E402

bad = []
for f in sorted((ROOT / "r68/blind").iterdir()):
    if f.suffix in (".py", ".cpp"):
        t = f.read_text()
        for w in ("EASTNORTHEAST", "NORTHEAST", "BERLINCLOCK", "BERLIN"):
            if w in t:
                bad.append(f"blind/{f.name}: {w}")
        for w in ("sealed", "truth"):
            if re.search(w, t, re.I):
                bad.append(f"blind/{f.name}: {w}")
for f in sorted(list(ROOT.glob("r68/**/*.py")) + list(ROOT.glob("r68/**/*.cpp"))):
    if f.name in ("reveal_k4.py", "exact.py", "test_contract.py"):
        continue
    for w in ("EASTNORTHEAST", "BERLINCLOCK"):
        if w in f.read_text():
            bad.append(f"{f.relative_to(ROOT)}: {w}")

with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    rng = random.Random(3)
    (td / "pt.txt").write_text("".join(rng.choice("ETAOINSHRDLUCMWFGYPB") for _ in range(5000)) + "\n")
    subprocess.run([sys.executable, "-I", str(ROOT / "r68/sealed/make_plants.py"), str(td / "pt.txt"), "8", "9", "T",
                    str(td / "out")], check=True, capture_output=True)
    cts = dict(l.split("\t") for l in (td / "out/blind.tsv").read_text().splitlines()[1:])
    paths = R.load_paths()
    names = [n for n, _ in paths]
    for k, v in json.loads((td / "out/sealed_truth.json").read_text()).items():
        rows = {r[0]: r for r in R.rows_for(k, cts[k], paths)}
        _, Y, Rs = rows[f"{k}__{names.index(v['path'])}__{v['model']}"]
        Q = C.decrypt_path(Y, v["family"], v["convention"], v["param"], v["key"])
        P = Q if Rs == "I" else "".join(Q[int(x)] for x in Rs.split(","))
        if P != v["plaintext"]:
            bad.append(f"runner row / sealed decryption mismatch {k}")

import exact as E  # noqa: E402
D = E.digit_streams()
P = C.paths()
rng = random.Random(5)
for fam, path, model, conv, param, key in (("PER", "SNAKE_L", "M2", "KRY/AZ_VIG", "7", "QWERTYU"),
                                           ("GRO", "SNAKE_L", "M1", "AZ/AZ_BEAU", "31415", "31415"),
                                           ("CTAK", "COL_LT", "M2", "KRY/KRY_VARB", "9", "ABCDEFGHI"),
                                           ("PTAK", "SNAKE_R", "M1", "AZ/KRY_VIG", "5", "KEYAB")):
    p = [rng.choice(C.AZ) for _ in range(97)]
    for o, t in E.CLUES:
        for i, ch in enumerate(t):
            p[o + i] = ch
    p = "".join(p)
    perm = P[path]
    ct = C.to_carved(C.encrypt_path(C.unlayout(p, perm, model), fam, conv, param, key), perm)
    r = E.check(ct, D, P)
    want = [path, model, conv, param if fam == "GRO" else int(param)]
    if not any(e[:4] == want for e in r[fam]):
        bad.append(f"exact checker missed planted {fam}")

if bad:
    print("R68 CONTRACT FAIL:", bad)
    sys.exit(1)
print("R68 CONTRACT OK: blind code clue-free; runner rows and sealed decryption agree; exact checker finds plants")
