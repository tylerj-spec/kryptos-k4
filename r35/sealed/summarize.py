#!/usr/bin/env python3
"""After freeze/reveal: report independent control ranks and null score comparison."""
import json
import sys
from pathlib import Path

exp = Path(sys.argv[1])
results = json.loads((exp / "REVEAL.json").read_text())
whole = json.loads((exp / "WHOLE_FAMILY.json").read_text())
k4 = [e for e in results if e["kind"] == "K4"]
plants = [e for e in results if e["kind"] == "PLANT"]
nulls = [e for e in results if e["kind"] == "NULL"]
if len(k4) != 1 or len(plants) != 2 or len(nulls) != 1:
    raise RuntimeError("unexpected run inventory")
settings = whole[k4[0]["tag"]]["settings"]
controls_pass = all(e["truth_rank"] == 1 for e in plants)
null_delta = k4[0]["top_score"] - nulls[0]["top_score"]
result = {
    "tested_family_settings": settings,
    "k4_top_score": k4[0]["top_score"],
    "null_top_score": nulls[0]["top_score"],
    "k4_minus_null_top_score": round(null_delta, 4),
    "plant_truth_ranks": {e["tag"]: e["truth_rank"] for e in plants},
    "plant_controls_passed": controls_pass,
    "all24_count": len(whole[k4[0]["tag"]]["full24"]),
    "whole_family_max_clue_matches": whole[k4[0]["tag"]]["max"],
    "interpretation": (
        "CANDIDATE_REQUIRES_INDEPENDENT_CHECK" if whole[k4[0]["tag"]]["full24"] else
        "NO_CANDIDATE_TESTED_FAMILY_WITH_CONTROLS_PASSING" if controls_pass else
        "INCONCLUSIVE_CONTROL_FAILURE"
    ),
    "limitation": "Exclusion is only for the pre-registered fixed-alphabet key/route family."
}
(exp / "SUMMARY.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
