#!/usr/bin/env python3
"""Sealed-only diagnostic: read after-the-fact beam prefixes and secret D0 truth.
Never pass true plaintext to the blind solver; report which lengths survived.
"""
import csv
import json
import sys
from pathlib import Path

trace = Path(sys.argv[1])
truth = json.loads(Path(sys.argv[2]).read_text())
out = Path(sys.argv[3])
rec = {}
with trace.open() as fp:
    for row in csv.DictReader(fp, delimiter="\t"):
        key = row["id"]
        if key not in truth:
            raise ValueError("unknown D0 case")
        pos = int(row["position"])
        rank = int(row["rank"])
        prefix = row["plaintext_prefix"]
        assert len(prefix) == pos
        target = truth[key]["plaintext"]
        assert len(target) == 97
        x = rec.setdefault(key, {"max_exact_pos": 0, "exact_positions": {},
                                 "highest_common_prefix": 0, "traced": 0})
        x["traced"] += 1
        if prefix == target[:pos]:
            x["max_exact_pos"] = max(x["max_exact_pos"], pos)
            x["exact_positions"][str(pos)] = min(rank, x["exact_positions"].get(str(pos), 999999))
        common = 0
        for a, b in zip(prefix, target):
            if a != b:
                break
            common += 1
        x["highest_common_prefix"] = max(x["highest_common_prefix"], common)
for key, v in rec.items():
    v["notable_exact_positions"] = list(v["exact_positions"].items())[-20:]
    v.pop("exact_positions")
out.write_text(json.dumps(rec, indent=2) + "\n")
for k, v in rec.items():
    print(k, "max_surviving_true_prefix", v["max_exact_pos"],
          "max_partial_match", v["highest_common_prefix"],
          "tracked_states", v["traced"],
          "last_matched_ranks", v["notable_exact_positions"])
