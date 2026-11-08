#!/usr/bin/env python3
"""R72 tests. Run: python3 -I r72/tests/test_r72.py
  1. no R72 code holds K4 plaintext words; 2. K3 is reproduced by the documented 42 -> 14 double turn and its inverse
  (multiply by 192 mod 337) decrypts it; 3. the turn = decimation lemma holds; 4. the 98-cell sheet has exactly 9
  double-turn orderings, k in {4, 14, 25, 28, 46, 49, 92, 97, 98}; 5. the 14 x 31 panel puts K4 at 4 + 31 + 31 + 31."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r72"))
import reconstruct as R  # noqa: E402

bad = []
for f in sorted((ROOT / "r72").rglob("*.py")):
    if f.name == "test_r72.py":
        continue
    for w in ("EASTNORTHEAST", "NORTHEAST", "BERLINCLOCK", "BERLIN", "CLOCK"):
        if w in f.read_text():
            bad.append(f"{f.name}: {w}")
ct3 = R.K123_CT.read_text().strip()[-336:]
pt3 = R.K123_PT.read_text().strip()[-336:]
k3 = R.compose(R.turn(336, 42, True), R.turn(336, 14, True))
if "".join(pt3[i] for i in k3) != ct3:
    bad.append("K3 encryption not reproduced")
if "".join(ct3[(192 * (i + 1)) % 337 - 1] for i in range(336)) != pt3:
    bad.append("K3 decryption by x192 mod 337 failed")
for n in (336, 98):
    for w in [w for w in range(2, n) if n % w == 0]:
        if R.decimation(R.turn(n, w, False)) != w or R.decimation(R.turn(n, w, True)) != n + 1 - w:
            bad.append(f"lemma n={n} w={w}")
ks = set()
for w1 in (2, 7, 14, 49):
    for w2 in (2, 7, 14, 49):
        for cw in (True, False):
            ks.add(R.decimation(R.compose(R.turn(98, w1, cw), R.turn(98, w2, cw))))
if ks != {4, 14, 25, 28, 46, 49, 92, 97, 98}:
    bad.append(f"98-cell orderings {sorted(ks)}")
k4 = R.K4_CT.read_text().strip()
cells = ct3 + "?" + k4
if len(cells) != 434 or divmod(cells.index("?" + k4), 31) != (10, 26):
    bad.append("panel layout")
if bad:
    print("R72 TEST FAIL:", bad)
    sys.exit(1)
print("R72 TESTS OK: K3 reproduced both ways; turn = decimation lemma; 9 orderings on 98 cells; panel 4+31+31+31")
