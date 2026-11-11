#!/usr/bin/env python3
"""R75 tests (no letter model, no K4 data). Run: python3 -I r75/tests/test_r75.py
  1. no R75 file holds K4 plaintext words; only files under r75/sealed/ may import the published letters or the K4
     ciphertext, and the blind side (core, families, items, blind/run) never does;
  2. the family sizes are as pre-registered (6,934,560 fixed methods);
  3. for random settings of every sub-family, the explicit encryptor and the vectorised enumeration agree: the row
     that the enumeration assigns to the setting decrypts the ciphertext back to the plaintext;
  4. if ChatGPT's reference cipher (PR #67, r75/reference.py) is present, its 2,880 settings give the same
     ciphertexts as r75/families.py (two independent implementations)."""
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r75"))
import core  # noqa: E402
import families as F  # noqa: E402

bad = []
WORDS = ("EASTNORTHEAST", "NORTHEAST", "BERLINCLOCK", "BERLIN", "CLOCK")
for f in sorted((ROOT / "r75").rglob("*.py")):
    if f.name == "test_r75.py":
        continue
    t = f.read_text()
    bad += [f"{f.name}: holds {w}" for w in WORDS if w in t]
    sealed = "sealed" in f.parts
    if not sealed and ("reveal_k4" in t or "k4_ciphertext" in t or "prepare_k4" in t):
        bad.append(f"{f.name}: blind-side file touches K4 material")
for f in sorted((ROOT / "r75" / "data").glob("*.txt")):
    bad += [f"{f.name}: holds {w}" for w in WORDS if w in f.read_text().split()]

cnt = F.count()
if cnt != {"F1A": 4320000, "F2A": 374400, "F3A": 84000, "F1B": 1843200, "F2B": 299520, "F3B": 13440}:
    bad.append(f"counts {cnt}")

rng = random.Random(7501)
pt = "".join(rng.choice(core.AZ) for _ in range(core.N))
for which in F.SUBS:
    for _ in range(3):
        st = F.random_setting(rng, which)
        ct = F.encrypt(pt, st)
        gen = {"F1": F.batches_F1, "F2": F.batches_F2, "F3": F.batches_F3}[st["family"]]
        hit = False
        for P, meta in gen(core.codes(ct)):
            if meta[1] != st["tier"]:
                continue
            rows = (P == core.codes(pt)[None, :]).all(axis=1).nonzero()[0]
            if any(F.setting(meta, int(r)) == st for r in rows):
                hit = True
                break
        if not hit:
            bad.append(f"round trip {which} {st}")

ref = ROOT / "r75" / "reference.py"
if ref.exists():
    import reference as R  # noqa: E402
    for s in R.settings():
        p = "".join(rng.choice(core.AZ) for _ in range(core.N))
        mine = {"family": "F1", "tier": "A",
                "s1": {"pa": s.a1, "ca": s.a1, "ka": s.a1, "op": s.op1, "word": s.k1, "phase": s.phase1},
                "s2": {"pa": s.a2, "ca": s.a2, "ka": s.a2, "op": s.op2, "word": s.k2, "phase": s.phase2}}
        if F.encrypt(p, mine) != R.encrypt(p, s):
            bad.append(f"reference mismatch {s}")
            break

if bad:
    print("R75 TEST FAIL:", bad[:10])
    sys.exit(1)
print("R75 TESTS OK: no K4 words; blind side clean; 6,934,560 methods; 18 enumeration round trips exact"
      + ("; agrees with PR #67's reference on 2,880 settings" if ref.exists() else ""))
