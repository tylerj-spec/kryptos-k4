#!/usr/bin/env python3
"""R74 tests (no letter model needed). Run: python3 -I r74/tests/test_r74.py
  1. no R74 code holds K4 plaintext words or reads the K4 ciphertext;
  2. 14 distinct directed routes, 20,160 raw settings, 15,680 distinct transforms;
  3. for 500 random raw settings, the explicit three-stage encryption equals the composite and decrypt() inverts it;
  4. the operation-pair collapse: BEAU/BEAU = VARB/VIG and BEAU/VIG = VARB/BEAU give identical transforms."""
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r74"))
import sandwich as S  # noqa: E402

bad = []
for f in sorted((ROOT / "r74").rglob("*.py")):
    if f.name == "test_r74.py":
        continue
    t = f.read_text()
    for w in ("EASTNORTHEAST", "NORTHEAST", "BERLINCLOCK", "BERLIN", "CLOCK", "k4_ciphertext"):
        if w in t:
            bad.append(f"{f.name}: {w}")
routes = S.load_routes()
raw = list(S.configs(routes))
cls = S.classes(routes)
if (len(routes), len(raw), len(cls)) != (14, 20160, 15680):
    bad.append(f"counts {len(routes)} {len(raw)} {len(cls)}")
rng = random.Random(7401)
for cfg, r in rng.sample(raw, 500):
    p = "".join(rng.choice(S.A) for _ in range(S.N))
    c = S.encrypt(p, cfg["ka"], cfg["kb"], cfg["a"], cfg["b"], cfg["op_a"], cfg["op_b"], r)
    key = S.transform(cfg["ka"], cfg["kb"], cfg["a"], cfg["b"], cfg["op_a"], cfg["op_b"], r)
    if S.decrypt(c, *key) != p or "".join(S.A[(key[1] * S.IDX[p[r[j]]] + key[2][j]) % 26] for j in range(S.N)) != c:
        bad.append(f"round trip {cfg}")
r0 = next(iter(routes.values()))
for (o1, o2), (o3, o4) in ((("BEAU", "BEAU"), ("VARB", "VIG")), (("BEAU", "VIG"), ("VARB", "BEAU"))):
    if S.transform("PALIMPSEST", "ABSCISSA", 3, 5, o1, o2, r0) != S.transform("PALIMPSEST", "ABSCISSA", 3, 5, o3, o4, r0):
        bad.append(f"collapse {o1}/{o2}")
if bad:
    print("R74 TEST FAIL:", bad[:10])
    sys.exit(1)
print("R74 TESTS OK: no K4 data; 14 routes, 20,160 settings, 15,680 transforms; 500 explicit round trips exact")
