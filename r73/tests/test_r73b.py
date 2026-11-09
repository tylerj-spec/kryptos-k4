#!/usr/bin/env python3
"""R73b tests. Run: python3 -I r73/tests/test_r73b.py LM.bin   (the R59 order-6 letter model, r59/blind/LM_SHA256)
  1. (r73/tests/test_r73.py already scans every r73/*.py for K4 plaintext words and the K4 ciphertext file.)
  2. for every 5th R26 setting, a planted message containing out-of-vocabulary names encrypts, and the R73b solver
     (POOV -3, as the blind runner) returns that setting (or one that decodes identically), the exact words, and a
     decode that re-encrypts to the ciphertext."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r73"))
import wordkey as W  # noqa: E402
import wordkey2 as W2  # noqa: E402

s = W2.Solver(sys.argv[1], -3.0)
bad = []
msgs = ["THE MAN WHO HAD WALKED ALONG THE ROAD STOPPED AT THE GATE AND LOOKED BACK AT THE HOUSE WHERE LIGHTS BURNED".split(),
        "MISTER HARDCASTLE SAID THAT CAPTAIN TREMAYNE HAD GONE TO BALLINGFORD WITH HIS SISTER AND WOULD COME HOME".split()]
for msg in msgs:
    assert sum(map(len, msg)) >= 60
    for st in W.settings("R26")[::5]:
        ct = W.encrypt(msg, "R26", st)
        b = s.solve(ct)[0]
        if b["words"] != msg or W.encrypt(b["words"], "R26", tuple(b["setting"])) != ct:
            bad.append(f"{st} -> {b['setting']} {' '.join(b['words'])}")
if bad:
    print("R73b TEST FAIL:", bad[:10])
    sys.exit(1)
print("R73b TESTS OK: planted R26 messages (with unknown names) recovered exactly with forward re-encryption")
