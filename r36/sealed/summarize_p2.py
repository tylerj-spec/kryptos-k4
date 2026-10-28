#!/usr/bin/env python3
"""R36 post-freeze evaluation per preregistered base. Does not influence ranking."""
import json
import sys
from pathlib import Path

exp = Path(sys.argv[1])
entries = {e["tag"]: e for e in json.loads((exp / "REVEAL.json").read_text())}
family = json.loads((exp / "WHOLE_FAMILY.json").read_text())
bases = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 16, 20, 26]
results = []
for base in bases:
    k4 = entries[f"K4_B{base}"]
    a, b = entries[f"PLANTA_B{base}"], entries[f"PLANTB_B{base}"]
    null = entries[f"NULL_B{base}"]
    whole = family[f"K4_B{base}"]
    assert whole["settings"] == base ** 5 * 12, "incomplete family: base " + str(base)
    passed = a["truth_rank"] == 1 and b["truth_rank"] == 1
    results.append({
        "base": base, "primer_length": 5, "settings": whole["settings"],
        "max_clue_matches": whole["max"], "all24": len(whole["full24"]),
        "top_english_score": k4["top_score"], "null_english_score": null["top_score"],
        "difference_from_null": round(k4["top_score"] - null["top_score"], 4),
        "plant_ranks": [a["truth_rank"], b["truth_rank"]], "plant_gate": passed,
        "status": ("CANDIDATE_UNVERIFIED" if whole["full24"] else
                   "EXCL_FIXED_FAMILY" if passed else "INCONCLUSIVE_PLANT_FAILURE")
    })
total = sum(e["settings"] for e in results)
assert total == 201127524
summary = {
    "analysis": "strict-blind, post-freeze, fixed-alphabet no-transposition five-primer nondecimal Gromark",
    "total_k4_settings": total, "models": results,
    "overall_candidates_with_all_24": sum(r["all24"] for r in results),
    "plant_gates_passed": sum(r["plant_gate"] for r in results), "plant_gates_total": len(results),
    "limitation": "No inference about arbitrary alphabets, other key lengths or other stream generator rules."
}
(exp / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
