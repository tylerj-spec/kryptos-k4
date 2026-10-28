#!/usr/bin/env python3
"""SEALED / POSTFREEZE ONLY. Rank the already-frozen R39 100k scores, then apply published clue constraints.
This program is NOT a blind K4 solver and must not run before the R39 freeze has been committed.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "r39" / "ic_gate"
assert (EXP / "FROZEN.sha256").is_file(), "R39 must have a committed freeze"
for line in (EXP / "FROZEN.sha256").read_text().splitlines():
    digest, relative_path = line.split(maxsplit=1)
    path = EXP / relative_path
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, str(path)
sys.path.insert(0, str(ROOT / "k4kit" / "tools"))
from k4common import gromark_key  # noqa
from key_oracle import possible  # noqa

data = (EXP / "out" / "K4.scores.f64").read_bytes()
assert len(data) == 800000
scores = struct.unpack("<100000d", data)
assert abs(scores[27641] - 0.07510729613733906) < 1e-14
feasible = [p for p in range(100000) if possible(gromark_key(p))]
assert len(feasible) == 39, f"expected 39; found {len(feasible)}"
ranked = sorted(
    (1 + sum(s > scores[p] for s in scores) +
     sum(s == scores[p] for s in scores[:p]), p, scores[p]) for p in feasible
)
out = {
    "model": "POSTFREEZE crib graph, identity route, two unknown alphabets, five-decimal-digit primer",
    "blind_scores_hash_locked": True,
    "total_primers": 100000, "feasible_primers": len(feasible),
    "n_feasible_top100": sum(r <= 100 for r, p, s in ranked),
    "n_feasible_top1000": sum(r <= 1000 for r, p, s in ranked),
    "n_feasible_top5000": sum(r <= 5000 for r, p, s in ranked),
    "ranked_feasible": [{"rank": r, "primer": f"{p:05d}", "IC": s} for r, p, s in ranked],
    "warning": "Not blind recovery; public clues filter feasibility AFTER blind scores froze. No recovered plaintext."
}
(ROOT / "r40" / "POSTFREEZE_ORACLE_RESULT.json").write_text(json.dumps(out, indent=2) + "\n")
print(f"POSTFREEZE 39 feasible; top100={out['n_feasible_top100']}; top1000={out['n_feasible_top1000']}; top5000={out['n_feasible_top5000']}; best={ranked[0]}")
