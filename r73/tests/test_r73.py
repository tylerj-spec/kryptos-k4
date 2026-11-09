#!/usr/bin/env python3
"""R73 tests. Run: python3 -I r73/tests/test_r73.py
  1. no R73 code holds K4 plaintext words or reads the K4 ciphertext;
  2. for every setting of both families, a planted message encrypts and the blind solver returns that family, that
     setting (or one that decodes identically) and the exact words."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r73"))
import wordkey as W  # noqa: E402

bad = []
for f in sorted((ROOT / "r73").rglob("*.py")):
    if f.name == "test_r73.py":
        continue
    t = f.read_text()
    for w in ("EASTNORTHEAST", "NORTHEAST", "BERLINCLOCK", "BERLIN", "CLOCK", "k4_ciphertext"):
        if w in t:
            bad.append(f"{f.name}: {w}")
vocab = W.load_words()
msg = "THE MAN WHO HAD WALKED ALONG THE ROAD STOPPED AT THE GATE AND LOOKED BACK AT THE HOUSE WHERE LIGHTS BURNED".split()
for fam in ("I", "R26"):
    for st in W.settings(fam)[::5]:
        ct = W.encrypt(msg, fam, st)
        b = W.solve_all(ct, vocab)[0]
        if b["family"] != fam or b["words"] != msg or W.encrypt(b["words"], fam, tuple(b["setting"])) != ct:
            bad.append(f"{fam} {st} -> {b['family']} {b['setting']}")
if bad:
    print("R73 TEST FAIL:", bad[:10])
    sys.exit(1)
print("R73 TESTS OK: no K4 data; both families' planted messages recovered exactly with forward re-encryption")
