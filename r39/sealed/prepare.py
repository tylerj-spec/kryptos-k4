#!/usr/bin/env python3
"""R39 SEALED: 20 independent unknown-alphabet plants and 10 ciphertext-histogram nulls."""
import json
import random
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "strictblind/sealed"))
from common import AZ, K4, encrypt, make_key  # noqa: E402

exp = ROOT / "r39/ic_gate"
if exp.exists():
    raise RuntimeError("R39 experiment exists; cannot overwrite")
exp.mkdir(parents=True)
orig = ROOT / "k4kit/r32/runs/k4_ciphertext.txt"
(exp / "k4_ciphertext.txt").write_bytes(orig.read_bytes())
rng = random.Random(39000)
source = (ROOT / "k4kit/data/k1k3_plaintext.txt").read_text()
source = "".join(c for c in source.upper() if "A" <= c <= "Z")
assert len(source) >= 1000
passages = json.loads((ROOT / "r35/controls.json").read_text())["texts"]
starts = rng.sample(range(len(source) - 96), 16)
truth, runs = {}, [{"tag": "K4", "ct": "k4_ciphertext.txt"}]
for i in range(20):
    plain = ("".join(c for c in passages[i].upper() if "A" <= c <= "Z")[:97]
             if i < 4 else source[starts[i - 4]:starts[i - 4] + 97])
    assert len(plain) == 97
    assert "EASTNORTHEAST" not in plain and "BERLINCLOCK" not in plain
    pa, ca = list(AZ), list(AZ)
    rng.shuffle(pa)
    rng.shuffle(ca)
    primer = f"primer{rng.randrange(100000):05d}"
    ct = encrypt(plain, list(range(97)), "ID", make_key("CHAIN", "5", primer),
                 "".join(pa), "".join(ca), "VIG")
    tag = f"PLANT_{i:02d}"
    (exp / f"{tag}_ct.txt").write_text(ct + "\n")
    truth[tag] = {"plaintext": plain, "ciphertext": ct, "primer": primer,
                  "PA": "".join(pa), "CA": "".join(ca), "source": "original_r35" if i < 4 else "K1K3_window",
                  "offset": None if i < 4 else starts[i - 4]}
    runs.append({"tag": tag, "ct": f"{tag}_ct.txt"})
for i, seed in enumerate(range(39100, 39110)):
    tag = f"NULL_{i:02d}"
    subprocess.run([sys.executable, "-I", str(ROOT / "r35/sealed/make_null.py"),
                    str(exp / "k4_ciphertext.txt"), str(exp / f"{tag}_ct.txt"), str(seed)], check=True)
    runs.append({"tag": tag, "ct": f"{tag}_ct.txt"})
assert len(runs) == 31 and K4 in orig.read_text()
(exp / "manifest.json").write_text(json.dumps({"runs": runs}, indent=2) + "\n")
(exp / "sealed").mkdir(exist_ok=True)
(exp / "sealed/truth.json").write_text(json.dumps(truth, indent=2) + "\n")
print("R39 planted 20 unknown-alphabet 97-letter English messages and 10 histogram nulls")
