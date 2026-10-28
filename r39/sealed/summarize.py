#!/usr/bin/env python3
"""Post-freeze fixed-gate calibration of Blackman-style ciphertext-only primer ranking."""
import json
import statistics
import sys
from pathlib import Path

exp = Path(sys.argv[1])
rows = json.loads((exp / "REVEAL.json").read_text())
plants = [r for r in rows if r["type"] == "PLANT"]
nulls = [r for r in rows if r["type"] == "NULL"]
k4 = [r for r in rows if r["type"] == "K4"]
assert len(plants) == 20 and len(nulls) == 10 and len(k4) == 1
ranks = [r["true_primer_rank"] for r in plants]
top_5000 = sum(r <= 5000 for r in ranks)
median = statistics.median(ranks)
gate = top_5000 >= 16 and median <= 1000
nulls_at_least_k4 = sum(r["max_ic"] >= k4[0]["max_ic"] for r in nulls)
out = {
    "model": "Blackman key-conditioned IC, base10 5-digit Gromark, ciphertext only, no alphabets",
    "k4_primers_ranked": 100000,
    "true_ranked_planted_controls": 20,
    "unknown_alphabet_plant_ranks": ranks,
    "plants_top100": sum(r <= 100 for r in ranks),
    "plants_top1000": sum(r <= 1000 for r in ranks),
    "plants_top5000": top_5000,
    "median_true_primer_rank": median,
    "prespecified_gate": ">=16/20 top5000 and median<=1000",
    "development_gate_passed": gate,
    "k4_highest_conditional_ic": k4[0]["max_ic"],
    "k4_top_ranked_primer": f"{k4[0]['top_primer']:05d}",
    "null_max_scores": [r["max_ic"] for r in nulls],
    "nulls_at_least_k4": nulls_at_least_k4,
    "interpretation": ("KEY_RANKING_USEFUL_FOR_FOLLOWUP_NOT_A_SOLUTION" if gate else
                       "IC_RANKING_UNRELIABLE_ON_HIDDEN_PLANTS_DO_NOT_TRUST_K4_TOP_KEYS"),
    "limitation": "Key-only IC score is not a decryption. Null comparison descriptive, not a definitive p-value."
}
(exp / "SUMMARY.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
