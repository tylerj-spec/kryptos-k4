#!/usr/bin/env python3
"""Synthetic positive control for crosscheck100's second algorithm (development; no K4 file, no published letter):
two full-tier plants on random windows at a lag with >= 14 direct links; the second algorithm's EXACT and DROP must
equal the fast path's for all 12 sign/feedback cases, and the plant must be counted.
Usage: python3 -I r100/dev/crosscheck_control100.py OUT.json"""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"
import json  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

R = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R), str(R.parent / "r76")]
import alphabets as AL  # noqa: E402
import autokey100 as AK  # noqa: E402
import checker100 as CK  # noqa: E402
import crosscheck100 as XC  # noqa: E402

rng = random.Random(1008001)
tier = [a for _, a in AL.large_tier()]
IT = CK.tier_idxt(tier)
rows = []
for k in range(2):
    while True:
        a, b = rng.randrange(0, 85), rng.randrange(0, 87)
        pos = sorted(set(range(a, a + 13)) | set(range(b, b + 11)))
        lags = [L for L in range(1, 97) if len(CK.links({p: 0 for p in pos}, L)) >= 14]
        if len(pos) == 24 and lags:
            break
    L = rng.choice(lags)
    A, B, F = rng.choice(tier), rng.choice(tier), rng.choice(AK.FEEDBACK)
    s1, s2 = rng.choice(AK.SIGNS)
    pt = "".join(rng.choice(AK.AZ) for _ in range(97))
    ct = AK.encrypt(pt, A, B, F, L, s1, s2, rng.randrange(26), [rng.randrange(26) for _ in range(L)])
    obs = {p: pt[p] for p in pos}
    if k == 1:                                   # corrupt one published letter: the plant must survive in DROP
        p = rng.choice(CK.links(obs, L))[1]
        obs[p] = rng.choice([ch for ch in AK.AZ if ch != obs[p]])
    fast = CK.scan(ct, obs, IT, [L], [L])
    lk = CK.links(obs, L)
    for (s1_, s2_), F_ in [(sg, f) for sg in CK.SIGNS for f in CK.FEEDBACK]:
        H, G = CK.side_values(ct, obs, IT, lk, s1_, s2_, F_)
        e = XC.matched(H, G, list(range(len(lk))))[0]
        union = set()
        for q in sorted(obs):
            keep = [i for i, (x, y) in enumerate(lk) if q not in (x, y)]
            if len(keep) < len(lk) and XC.matched(H, G, keep)[0]:
                union |= XC.matched(H, G, keep, True)[1]
        rows.append({"plant": k, "case": [L, s1_, s2_, F_], "planted": (s1_, s2_, F_) == (s1, s2, F),
                     "fast": list(fast[(L, s1_, s2_, F_)][1:]), "second": [e, len(union)]})
ok = all(r["fast"] == r["second"] for r in rows) and all(
    (r["second"][0] if r["plant"] == 0 else r["second"][1]) >= 1 for r in rows if r["planted"])
Path(sys.argv[1]).write_text(json.dumps({"development_only": True, "agree_and_planted_found": ok, "rows": rows},
                                        indent=1) + "\n")
print(ok, [(r["case"], r["fast"], r["second"]) for r in rows if r["planted"] or r["fast"] != [0, 0]])
