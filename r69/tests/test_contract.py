#!/usr/bin/env python3
"""R69 contract tests. Run: python3 -I r69/tests/test_contract.py
  1. r69/blind/ holds no K4 plaintext words, clue positions or sealed/truth references, and no R69 code holds the
     published letters (R69 never uses them);
  2. r69/data/patterns.txt is exactly what make_patterns.py writes (16 F + 62 B; SNAKE_L/R identities asserted there);
  3. plants re-encrypt: every planted ciphertext un-reads (through its reading) to S(P, K) under its convention;
  4. the contrast code recovers the planted bits on a synthetic additive table."""
import json
import random
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r64/sealed"))
sys.path.insert(0, str(ROOT / "r69/sealed"))
from common import enc  # noqa: E402
import attribute as A  # noqa: E402

bad = []
for f in sorted((ROOT / "r69/blind").iterdir()):
    if f.suffix in (".py", ".cpp"):
        t = f.read_text()
        for w in ("EASTNORTHEAST", "NORTHEAST", "BERLINCLOCK", "BERLIN", "CLOCK"):
            if w in t:
                bad.append(f"blind/{f.name}: {w}")
        for w in ("sealed", "truth"):
            if re.search(w, t, re.I):
                bad.append(f"blind/{f.name}: {w}")
for f in sorted(list(ROOT.glob("r69/**/*.py"))):
    if f.name == "test_contract.py":
        continue
    for w in ("EASTNORTHEAST", "BERLINCLOCK"):
        if w in f.read_text():
            bad.append(f"{f.relative_to(ROOT)}: {w}")

with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    subprocess.run([sys.executable, "-I", str(ROOT / "r69/blind/make_patterns.py"), str(td / "p.txt")], check=True,
                   capture_output=True)
    if (td / "p.txt").read_text() != (ROOT / "r69/data/patterns.txt").read_text():
        bad.append("patterns.txt differs from make_patterns.py output")
    rng = random.Random(3)
    (td / "pt.txt").write_text("".join(rng.choice("ETAOINSHRDLUCMWFGYPB") for _ in range(9000)) + "\n")
    (td / "de.txt").write_text("".join(rng.choice("ENISRATDHULCGMOBWFKZ") for _ in range(9000)) + "\n")
    subprocess.run([sys.executable, "-I", str(ROOT / "r69/sealed/make_plants.py"), str(td / "pt.txt"),
                    str(td / "de.txt"), "9", str(td / "out")], check=True, capture_output=True)
    pats = {l.split()[0]: [int(x) for x in l.split()[2].split(",")]
            for l in (ROOT / "r69/data/patterns.txt").read_text().splitlines()}
    cts = {l.split("\t")[0]: l.split("\t")[1] for l in (td / "out/blind.tsv").read_text().splitlines()[1:]}
    truth = json.loads((td / "out/sealed_truth.json").read_text())
    if len(truth) != 40 or sum(v["reading"].startswith("F_") for v in truth.values()) != 32:
        bad.append("plant counts")
    for k, v in truth.items():
        perm = pats[v["reading"]]
        x = [""] * 97
        for j, src in enumerate(perm):
            x[src] = cts[k][j]
        if "".join(x) != enc(v["plaintext"], v["key"], v["convention"]):
            bad.append(f"plant does not re-encrypt: {k}")

for b in range(16):
    bits = f"{b:04b}"
    read = {f"F_{c:04b}": {"total": -300.0 + sum(10.0 * (1 if f"{c:04b}"[r] == bits[r] else -1) for r in range(4))}
            for c in range(16)}
    c = A.contrasts(read)
    if not all((c[f"E{r}"] > 0) == (bits[r - 1] == "1") for r in range(1, 5)) or c["S_argmax"] != f"F_{bits}":
        bad.append(f"contrast check failed for {bits}")

if bad:
    print("R69 CONTRACT FAIL:", bad)
    sys.exit(1)
print("R69 CONTRACT OK: blind code clue-free; patterns reproducible; plants re-encrypt; contrasts recover planted bits")
