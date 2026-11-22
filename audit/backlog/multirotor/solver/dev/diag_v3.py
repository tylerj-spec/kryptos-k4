#!/usr/bin/env python3
"""Version-3 diagnosis (development truth; spent data): the order-5 objective of the TRUE plaintext against the best
restart's, and the order-6 letter-model score of the truth against the found top-1. Usage: diag_v3.py PANEL_TRUTH.json OUTDIR LM.bin OUT.json"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent), str(HERE.parents[4] / "r75")]
import run_v2  # noqa: E402
import core  # noqa: E402


def main():
    truth = json.loads(Path(sys.argv[1]).read_text())
    out = Path(sys.argv[2])
    sc = run_v2.lean_scorer(sys.argv[3])
    res = {json.loads(l)["id"]: json.loads(l) for l in (out / "RESULTS.jsonl").read_text().splitlines()}
    rows = []
    for line in (out / "ANNEAL.jsonl").read_text().splitlines():
        a = json.loads(line)
        pt = truth[a["id"]]["pt"]
        sc.order = 5
        o5 = 97 * float(sc.lm_score(core.codes(pt)[None])[0])
        sc.order = 6
        lm6 = float(sc.lm_score(core.codes(pt)[None])[0])
        best = max(z["quad"] for z in a["restarts"])
        rows.append({"id": a["id"], "cell": truth[a["id"]]["cell"], "o5_true": round(o5, 2), "o5_best_found": round(best, 2),
                     "found_above_true": best > o5, "true_lm6": round(lm6, 3),
                     "top1_lm6": round(res[a["id"]]["best"]["lm_per_letter"], 3)})
    gaps = sorted(r["o5_best_found"] - r["o5_true"] for r in rows)
    rep = {"plants": len(rows), "found_above_true_o5": sum(r["found_above_true"] for r in rows),
           "median_gap_o5": gaps[len(gaps) // 2], "max_gap_o5": gaps[-1], "min_gap_o5": gaps[0], "rows": rows}
    Path(sys.argv[4]).write_text(json.dumps(rep, indent=1) + "\n")
    print({k: v for k, v in rep.items() if k != "rows"})
    for r in rows[::6]:
        print(r)


if __name__ == "__main__":
    main()
