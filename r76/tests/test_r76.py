#!/usr/bin/env python3
"""R76 tests (no letter model, no K4 data). Run: python3 -I r76/tests/test_r76.py
  1. no R76 file holds K4 plaintext words; only files under r76/sealed/ may import the published letters or the K4
     ciphertext;
  2. alphabet tiers, route sets and family sizes are as pre-registered;
  3. for 3 random settings of each blind sub-family, the explicit encryptor and the vectorised enumeration agree;
  4. every alphabet is a permutation of A-Z and every route a permutation of 0..96."""
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r75"))
sys.path.insert(0, str(ROOT / "r76"))
import core  # noqa: E402
import alphabets as AL  # noqa: E402
import families as F  # noqa: E402
import routes76 as RT  # noqa: E402

bad = []
WORDS = ("EASTNORTHEAST", "NORTHEAST", "BERLINCLOCK", "BERLIN", "CLOCK")
for f in sorted((ROOT / "r76").rglob("*.py")):
    if f.name == "test_r76.py":
        continue
    t = f.read_text()
    bad += [f"{f.name}: holds {w}" for w in WORDS if w in t]
    if "sealed" not in f.parts and ("reveal_k4" in t or "k4_ciphertext" in t or "prepare_k4" in t):
        bad.append(f"{f.name}: blind-side file touches K4 material")
small, large = AL.small_tier(), AL.large_tier()
if (len(small), len(large)) != (241, 77229):
    bad.append(f"tiers {len(small)} {len(large)}")
for _, a in small + large:
    if sorted(a) != list(core.AZ):
        bad.append(f"bad alphabet {a}")
        break
sizes = {s: len(RT.merged([s])) for s in ("sheet36", "rot2", "rot1", "colall", "r61")}
if sizes != {"sheet36": 33, "rot2": 17341, "rot1": 188, "colall": 47296, "r61": 14}:
    bad.append(f"route sets {sizes}")
if len(RT.merged(["sheet36", "rot2", "rot1", "colall", "r61"])) != 64782:
    bad.append("merged route count")
for _, p in RT.merged(["sheet36", "rot2", "rot1", "colall", "r61"]):
    if sorted(p) != list(range(core.N)):
        bad.append("bad route")
        break
if F.count() != {"B1": 3149280, "B2": 10514400, "B3": 36960}:
    bad.append(f"family sizes {F.count()}")
rng = random.Random(7601)
pt = "".join(rng.choice(core.AZ) for _ in range(core.N))
gens = {"B1": F.batches_B1, "B2": F.batches_B2, "B3": F.batches_B3}
for which in F.SUBS:
    for _ in range(3):
        st = F.random_setting(rng, which)
        ct = F.encrypt(pt, st)
        hit = False
        for P, meta in gens[which](core.codes(ct)):
            rows = (P == core.codes(pt)[None, :]).all(axis=1).nonzero()[0]
            if any(F.setting(meta, int(r)) == st or F.encrypt(pt, F.setting(meta, int(r))) == ct for r in rows):
                hit = True
                break
        if not hit:
            bad.append(f"round trip {which} {st}")
if bad:
    print("R76 TEST FAIL:", bad[:10])
    sys.exit(1)
print("R76 TESTS OK: no K4 words; blind side clean; tiers 241/77,229; 64,782 routes; 13,700,640 methods; "
      "9 enumeration round trips exact")
