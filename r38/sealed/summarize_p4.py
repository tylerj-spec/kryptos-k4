#!/usr/bin/env python3
"""Post-freeze, independently checked per-base results. Not imported by blind scanner."""
import json
import sys
from pathlib import Path

exp = Path(sys.argv[1])
rows = {r["tag"]: r for r in json.loads((exp / "REVEAL.json").read_text())}
whole = json.loads((exp / "WHOLE_FAMILY.json").read_text())
out = []
for base in (5, 10, 12, 26):
    k4 = rows[f"K4_B{base}"]
    plants = [rows[f"PLANTA_B{base}"], rows[f"PLANTB_B{base}"]]
    null = rows[f"NULL_B{base}"]
    w = whole[f"K4_B{base}"]
    assert w["settings"] == base ** 5 * 48, f"incorrect count for base {base}"
    assert all(r["forward_check"] for r in [k4, null, *plants])
    out.append({
        "base": base, "k4_settings": w["settings"],
        "plant_truth_ranks": [p["truth_rank"] for p in plants],
        "plant_gate": all(p["truth_rank"] == 1 for p in plants),
        "max_clue_matches": w["max"],
        "full24_count": len(w["full24"]),
        "full24_settings": w["full24"],
        "k4_top_english_score": k4["top_score"],
        "null_top_english_score": null["top_score"],
        "k4_minus_null": round(k4["top_score"] - null["top_score"], 4),
        "status": ("UNVERIFIED_CANDIDATE" if w["full24"] else
                   "EXCL_EXACT_FIXED_FAMILY" if all(p["truth_rank"] == 1 for p in plants) else
                   "INCONCLUSIVE_PLANT_FAILURE")
    })
result = {
    "model": "identity direct lagged-addition Gromark, fixed AZ and ACA KRY/PAL/ABS columnar-transposed alphabet pairs",
    "k4_settings": sum(z["k4_settings"] for z in out),
    "expected_k4_settings": 587199984,
    "bases": out,
    "plant_gate_passed": sum(z["plant_gate"] for z in out),
    "plant_gate_total": 4,
    "total_full24_candidates": sum(z["full24_count"] for z in out),
    "limitation": "Cannot eliminate unknown alphabets, alternative key expansion, or any transposition."
}
assert result["k4_settings"] == result["expected_k4_settings"]
(exp / "SUMMARY.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
