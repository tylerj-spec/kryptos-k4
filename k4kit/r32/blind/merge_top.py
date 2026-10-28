#!/usr/bin/env python3
"""Blind side: merge the 4 partial top-100 files (sort by score, then setting) and the per-route best scores."""
import csv
import glob
import sys

out = sys.argv[1]
rows = []
for f in sorted(glob.glob(f"part_{out}_[0-9].tsv")):
    rows += list(csv.DictReader(open(f), delimiter="\t"))
rows.sort(key=lambda r: (-float(r["score"]), r["setting"]))
with open(f"{out}.tsv", "w") as fh:
    fh.write("rank\tscore\tsetting\tplaintext\n")
    for i, r in enumerate(rows[:100]):
        fh.write(f"{i + 1}\t{r['score']}\t{r['setting']}\t{r['plaintext']}\n")
rr = []
for f in sorted(glob.glob(f"part_{out}_routes_[0-9].tsv")):
    rr += list(csv.DictReader(open(f), delimiter="\t"))
with open(f"{out}_routes.tsv", "w") as fh:
    fh.write("route\torder\tbest_score\n")
    for r in rr:
        fh.write(f"{r['route']}\t{r['order']}\t{r['best_score']}\n")
print(out, "merged", len(rows), "partial rows; top", rows[0]["score"] if rows else None)
