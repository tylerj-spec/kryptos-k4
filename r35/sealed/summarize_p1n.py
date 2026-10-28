#!/usr/bin/env python3
"""After frozen null search, assess original P1 top score against twelve control maxima."""
import json
import statistics
import sys
from pathlib import Path

exp = Path(sys.argv[1])
ROOT = Path(__file__).resolve().parents[2]
baseline = json.loads((ROOT / "r35/p1_carter_k3_mixed/SUMMARY.json").read_text())["k4_top_score"]
assert abs(baseline - (-579.3495047)) < 1e-9
reveals = json.loads((exp / "REVEAL.json").read_text())
assert len(reveals) == 12 and all(x["kind"] == "NULL" for x in reveals)
scores = [r["top_score"] for r in reveals]
exceed = sum(s >= baseline for s in scores)
out = {
    "status": "posthoc_descriptive_only",
    "p1_original_k4_score": baseline,
    "null_count": len(scores),
    "null_scores_by_seed": [{"seed": 35021 + i, "score": s} for i, s in enumerate(scores)],
    "null_mean": statistics.mean(scores),
    "null_stdev": statistics.stdev(scores),
    "null_min": min(scores), "null_max": max(scores),
    "nulls_at_least_k4": exceed,
    "empirical_p_add_one": (exceed + 1) / (len(scores) + 1),
    "k4_above_all_new_nulls": exceed == 0,
    "caution": "Study was selected after observing P1's single null gap; not a prespecified confirmatory significance test."
}
(exp / "SUMMARY.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
