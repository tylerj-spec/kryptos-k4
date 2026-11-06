#!/usr/bin/env python3
"""R70 contract tests. Run: python3 -I r70/tests/test_contract.py SCANNER EXACT_BINARY LM NORM_DIR
  1. r70/blind/ holds no K4 plaintext words, clue positions or sealed/truth references (source labels such as
     BERLIN_1912 are book names, allowed); the published letters appear only in r70/sealed/reveal_k4.py and
     r70/sealed/exact_scan.cpp;
  2. the Python reference (sealed/common.py) and the C++ scanner agree: a plant made with common.encrypt from a source
     window is returned by the scanner at rank 0 with its exact setting, and every returned decode is a witness;
  3. the exact scanner finds a planted setting's full blocks when the clue words are planted in the plaintext."""
import json
import random
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r70/sealed"))
import common as C  # noqa: E402

scanner, exact_bin, lm, norm = sys.argv[1:5]
bad = []
for f in sorted((ROOT / "r70/blind").iterdir()):
    if f.suffix in (".py", ".cpp"):
        t = f.read_text()
        for w in ("EASTNORTHEAST", "NORTHEAST", "BERLINCLOCK", "CLOCK"):
            if w in t:
                bad.append(f"blind/{f.name}: {w}")
        if re.search(r"BERLIN(?!_1912)", t):
            bad.append(f"blind/{f.name}: BERLIN outside the source label")
        for w in ("sealed", "truth"):
            if re.search(w, t, re.I):
                bad.append(f"blind/{f.name}: {w}")
for f in sorted(list(ROOT.glob("r70/**/*.py")) + list(ROOT.glob("r70/**/*.cpp"))):
    if f.name in ("reveal_k4.py", "exact_scan.cpp", "test_contract.py"):
        continue
    for w in ("EASTNORTHEAST", "BERLINCLOCK"):
        if w in f.read_text():
            bad.append(f"{f.relative_to(ROOT)}: {w}")

SRC = ("BERLIN_1912", "EGYPT_1908", "MURRAY_1907", "COOK_1876", "BUDGE_1898")
srcs = {k: (Path(norm) / f"{k}.txt").read_text().strip() for k in SRC}
rng = random.Random(7)
english = "THEROADRANALONGTHERIVERFORMANYMILESANDTHETRAVELLERSAWTHETEMPLESOFTHEOLDKINGSUPONTHEHILLABOVETHEWATERANDTHEPALMS"
with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    for path, model, conv in (("SNAKE_R", "M1", "AZ_VARB"), ("ID", "M1", "KRY_VIG"), ("COL_RB", "M2", "AZ_BEAU")):
        s = rng.choice(SRC)
        o = rng.randrange(len(srcs[s]) - 97)
        P = english[:97]
        ct = C.encrypt(P, srcs[s][o:o + 97], path, model, conv)
        assert C.decrypt(ct, srcs[s][o:o + 97], path, model, conv) == P
        out = td / "o.jsonl"
        subprocess.run([scanner, lm, str(ROOT / "k4kit/data/word_model_orth.tsv"), str(ROOT / "r61/routes.txt"), ct,
                        str(out), "4", "200", "5"] + [f"{k}={Path(norm) / (k + '.txt')}" for k in SRC], check=True,
                       capture_output=True)
        top = [json.loads(l) for l in out.read_text().splitlines() if l.strip()]
        d = top[0]
        if [d["source"], d["offset"], d["path"], d["model"], d["convention"], d["plaintext"]] != [s, o, path, model, conv, P]:
            bad.append(f"scanner did not return the plant at rank 0: {path} {model} {conv}")
        if not all(C.witness_ok(ct, srcs[x["source"]], x) for x in top):
            bad.append("scanner output is not a witness")
        p = list(english[:97])
        for off, w in ((21, "EASTNORTHEAST"), (63, "BERLINCLOCK")):
            p[off:off + len(w)] = w
        ct2 = C.encrypt("".join(p), srcs[s][o:o + 97], path, model, conv)
        subprocess.run([exact_bin, str(ROOT / "r61/routes.txt"), ct2, str(td / "e.json")] +
                       [f"{k}={Path(norm) / (k + '.txt')}" for k in SRC], check=True)
        e = json.loads((td / "e.json").read_text())["sources"][s]
        if [s, o, path, model, conv, 13, 11] not in e["full_block_settings"]:
            bad.append(f"exact scanner missed the planted setting {path} {model} {conv}")

if bad:
    print("R70 CONTRACT FAIL:", bad)
    sys.exit(1)
print("R70 CONTRACT OK: blind code clue-free; scanner and sealed reference agree; exact scanner finds plants")
