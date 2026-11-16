#!/usr/bin/env python3
"""T1 pass condition (audit/NEXT_STEPS.md): every exact WPX drop-one survivor on K4 must be among the conservative
necessary-only survivors of r83/audit/plaintext_drop.py (260 on K4). POST-FREEZE, CRIB-ASSISTED; structural settings
only. Recomputes the full conservative set (plaintext_drop.py --k4 lists only 20 examples) with its own function,
unchanged, and compares it with r83/audit/EXACT_DROP.json. Usage: python3 -I r83/audit/t1_passcheck.py OUT.json"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "r83" / "audit"), str(ROOT / "r83"), str(ROOT / "r75"), str(ROOT / "r73" / "sealed")]
import plaintext_drop as PD  # noqa: E402
import exact83 as X  # noqa: E402
from reveal_k4 import CLUES  # noqa: E402

cts = dict(l.split("\t") for l in (ROOT / "r83/k4/TARGET.tsv").read_text().splitlines()[1:] if l)
c = np.array([ord(ch) - 65 for ch in cts["K4"]])
pos = np.array([o + j for o, t in CLUES for j in range(len(t))])
pk = np.array([ord(ch) - 65 for _, t in CLUES for ch in t])
cons = set()
by_pos = {}
for bad in pos:
    for conv in X.CONV1:
        for alpha in X.A4:
            for e in (0, 1):
                for d in (1, -1):
                    for m in range(2, 27):
                        if PD.wpx_necessary_after_unknown_plaintext(c, pos, pk, conv, alpha, e, d, m, int(bad)):
                            cons.add((tuple(conv), alpha, e, d, m))
                            by_pos[(tuple(conv), alpha, e, d, m, int(bad))] = True
ex = json.loads((ROOT / "r83/audit/EXACT_DROP.json").read_text())
exact_union = {(tuple(s[0]), s[1], s[2], s[3], s[4]) for s in ex["WPX_drop_excl_union_settings"]["K4"]}
pairs_ok = all(by_pos.get((tuple(s["conv"]), s["alpha"], s["e"], s["d"], s["m"], b), False)
               for s in ex["results"]["K4"]["WPX"]["settings_ge3_list"] for b in s["freed_by"])
out = {"conservative_unique_settings": len(cons), "exact_unique_settings": len(exact_union),
       "exact_subset_of_conservative": exact_union <= cons,
       "every_exact_survivor_position_pair_inside_conservative": pairs_ok,
       "PASS": exact_union <= cons and pairs_ok and len(cons) == 260}
Path(sys.argv[1]).write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps(out))
