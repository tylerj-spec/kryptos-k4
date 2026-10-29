#!/usr/bin/env python3
"""R43 sealed after-the-fact development evaluator; never invoked by blind solver."""
import json
import sys
from pathlib import Path

source, results, truth_path, report_path = map(Path, sys.argv[1:5])
data = {}
for line in source.read_text().splitlines()[1:]:
    label, ct, digits = line.split("\t")
    data[label] = (ct, list(map(int, digits.split(","))))
truth = json.loads(truth_path.read_text())
rows = [json.loads(line) for line in results.read_text().splitlines() if line.strip()]
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
assert len(data) >= len(rows)
assert set(row["id"] for row in rows) <= set(data)
assert len(rows) == len({row["id"] for row in rows})
report = []
for row in rows:
    label = row["id"]
    ct, key = data[label]
    expected = truth[label]
    p, pa, ca = row["plaintext"], row["plaintext_alphabet"], row["ciphertext_alphabet"]
    if p:
        assert len(p) == len(ct) == len(key) == 97
        assert sorted(pa) == sorted(ca) == list(AZ)
        rec = "".join(ca[(pa.index(char) + key[i]) % 26] for i, char in enumerate(p))
        assert rec == ct, f"{label}: forward witness invalid"
    target = expected["plaintext"]
    errors = sum(a != b for a, b in zip(p, target)) if p else 97
    report.append({"id": label, "errors": errors, "exact": errors == 0,
                   "within3": errors <= 3, "word_score": row["score"],
                   "proposals": row["proposals"], "compatible": row["compatible"],
                   "candidate": p, "truth": target})
count = len(report)
summary = {"total": count, "exact": sum(r["exact"] for r in report),
           "within3": sum(r["within3"] for r in report),
           "no_witness": sum(not r["candidate"] for r in report),
           "median_errors": sorted(r["errors"] for r in report)[count // 2] if count else 0,
           "all_forward_witnesses_valid": True, "rows": report,
           "notes": "DEVELOPMENT ONLY, true key supplied; not a K4 decryption or holdout."}
report_path.write_text(json.dumps(summary, indent=2)+"\n")
print("R43 D0 plants", count, "exact", summary["exact"], "within3",
      summary["within3"], "no valid witness", summary["no_witness"],
      "median errors", summary["median_errors"])
for row in report:
    print(row["id"], "err", row["errors"], "score", row["word_score"],
          "tested", row["proposals"], "compatible", row["compatible"])
