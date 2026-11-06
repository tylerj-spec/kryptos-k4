#!/usr/bin/env python3
"""R70 SEALED K4 reveal. Run ONLY after the K4 + nulls results are frozen, pushed and verified. Holds the published
letters (EASTNORTHEAST at 0-based plaintext positions 21-33, BERLINCLOCK at 63-73; plaintext order as R68: path order
for M1, carved order for M2 and ID), compared with the frozen decodes.
  SIGNAL      : K4's rank-0 total exceeds all 50 nulls' rank-0 totals AND its plaintext matches >= 10/24;
  SCORE_ANOMALY: the first condition without the second; otherwise NO_SIGNAL.
  Contenders  : ANY of K4's 200 frozen decodes matching >= 12/24 is listed raw, with the nulls' maximum over their 200.
Usage: reveal_k4.py TARGET.tsv FROZEN_DIR NORM_DIR REPORT.json"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import sha, witness_ok  # noqa: E402

CLUES = ((21, "EASTNORTHEAST"), (63, "BERLINCLOCK"))
POS = [(o + i, c) for o, t in CLUES for i, c in enumerate(t)]


def hits(pt):
    return sum(pt[i] == c for i, c in POS)


def main():
    tsv, fz, norm, rep = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
    for line in (fz / "FROZEN.sha256").read_text().splitlines():
        h, lab, _ = line.split("  ")
        if lab in ("input", "results"):
            assert sha(tsv if lab == "input" else fz / "RESULTS.jsonl") == h, f"freeze mismatch {lab}"
    src = {p.stem: p.read_text().strip() for p in norm.glob("*.txt")}
    cts = dict(l.split("\t") for l in tsv.read_text().splitlines()[1:] if l)
    top = {i: [json.loads(l) for l in (fz / "work" / f"{i}.jsonl").read_text().splitlines() if l.strip()] for i in cts}
    for i, ds in top.items():
        assert all(witness_ok(cts[i], src[d["source"]], d) for d in ds), f"witness {i}"
    nulls = [i for i in cts if i != "K4"]
    k4 = top["K4"][0]
    ge = sum(top[i][0]["total"] >= k4["total"] for i in nulls)
    h0 = hits(k4["plaintext"])
    outcome = "SIGNAL" if ge == 0 and h0 >= 10 else "SCORE_ANOMALY" if ge == 0 else "NO_SIGNAL"
    k4max = max(hits(d["plaintext"]) for d in top["K4"])
    null_max = sorted(max(hits(d["plaintext"]) for d in top[i]) for i in nulls)
    contenders = [{**d, "hits": hits(d["plaintext"])} for d in top["K4"] if hits(d["plaintext"]) >= 12]
    out = {"outcome": outcome, "k4_best": k4, "k4_best_hits": h0, "nulls_at_or_above": ge,
           "empirical_rank_p": (ge + 1) / (len(nulls) + 1),
           "null_best_totals_sorted": sorted(top[i][0]["total"] for i in nulls),
           "null_best_hits_sorted": sorted(hits(top[i][0]["plaintext"]) for i in nulls),
           "contender_screen": {"k4_max_hits_top200": k4max, "null_max_hits_top200_sorted": null_max,
                                "nulls_reaching_k4_max": sum(v >= k4max for v in null_max), "contenders_ge_12": contenders}}
    rep.write_text(json.dumps(out, indent=1) + "\n")
    print(outcome, "K4 best", round(k4["total"], 2), k4["source"], k4["offset"], k4["path"], k4["model"],
          k4["convention"], "hits", h0, "| nulls >= K4:", ge, "| null best totals max",
          round(out["null_best_totals_sorted"][-1], 2))
    print("contender screen: K4 max hits over 200 frozen decodes", k4max, "| nulls median/max",
          null_max[len(null_max) // 2], null_max[-1], "| contenders >= 12:", len(contenders))
    for d in contenders:
        print("  CONTENDER", d["source"], d["offset"], d["path"], d["model"], d["convention"], d["hits"], d["plaintext"])


if __name__ == "__main__":
    main()
