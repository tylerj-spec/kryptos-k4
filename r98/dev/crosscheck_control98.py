#!/usr/bin/env python3
"""Synthetic positive control for crosscheck98.count_conv (development; no K4 file, no published letter):
planted Slidefair inputs on random windows; the pure-Python counts must equal checker98.scan_conv for all 16
conventions, and the planted convention must have EXACT >= 1. Usage: python3 -I r98/dev/crosscheck_control98.py OUT"""
import json
import random
import sys
from pathlib import Path

R98 = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R98), str(R98.parent / "r76")]
import alphabets as AL  # noqa: E402
import checker98 as CK  # noqa: E402
import crosscheck98 as XC  # noqa: E402
import slidefair98 as SF  # noqa: E402

rng = random.Random(988001)
tier = [a for _, a in AL.large_tier()]
IDX = CK.tier_idx(tier)
pos = [{c: k for k, c in enumerate(a)} for a in tier]
rows = []
for k in range(2):
    conv = SF.CONVENTIONS[rng.randrange(16)]
    PA, CA = rng.choice(tier), rng.choice(tier)
    pt = "".join(rng.choice(SF.AZ) for _ in range(97))
    ct = SF.encrypt(pt, PA, CA, conv, [rng.randrange(26) for _ in range(97)])
    s0, s1 = rng.randrange(0, 30), rng.randrange(50, 80)
    obs = {i: pt[i] for i in list(range(s0, s0 + 9)) + list(range(s1, s1 + 7))}
    for c in SF.CONVENTIONS:
        F, G, _ = CK.conv_matrices(ct, obs, IDX, c)
        fast = CK.scan_conv(F, G)
        pure = XC.count_conv(ct, obs, pos, *c)
        rows.append({"plant": k, "convention": c, "planted": c == conv, "fast": fast, "pure": pure})
ok = all(r["fast"] == tuple(r["pure"]) for r in rows) and all(r["fast"][0] >= 1 for r in rows if r["planted"])
Path(sys.argv[1]).write_text(json.dumps({"development_only": True, "agree_and_planted_found": ok,
                                         "rows": rows}, indent=1) + "\n")
print(ok, [(r["convention"], r["fast"]) for r in rows if r["planted"] or r["fast"] != (0, 0)])
