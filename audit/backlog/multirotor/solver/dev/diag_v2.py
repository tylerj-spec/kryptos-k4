#!/usr/bin/env python3
"""Version-2 diagnosis (development truth; spent data): for every plant, the quadgram score of the TRUE plaintext
against the best restart's score, and the found top-1's letter-model score against the true text's. If the search
finds decodes that score above the truth, the failure is identifiability under the score, not search effort.
Usage: diag_v2.py PANEL_TRUTH.json OUTDIR(with ANNEAL.jsonl, RESULTS.jsonl) OUT.json"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path[:0] = [str(HERE), str(ROOT / "r87")]
import rotor87  # noqa: E402


def main():
    truth = json.loads(Path(sys.argv[1]).read_text())
    out = Path(sys.argv[2])
    Q = rotor87.Quad()
    res = {json.loads(l)["id"]: json.loads(l) for l in (out / "RESULTS.jsonl").read_text().splitlines()}
    rows = []
    for line in (out / "ANNEAL.jsonl").read_text().splitlines():
        a = json.loads(line)
        t = truth[a["id"]]
        q_true = Q.score(t["pt"])
        q_best = max(z["quad"] for z in a["restarts"])
        rows.append({"id": a["id"], "cell": t["cell"], "quad_true": round(q_true, 2), "quad_best_found": round(q_best, 2),
                     "found_above_true": q_best > q_true, "top1_lm": round(res[a["id"]]["best"]["lm_per_letter"], 3)})
    import os
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    import run_v2
    import numpy as np
    import core
    sc = run_v2.lean_scorer(sys.argv[4]) if len(sys.argv) > 4 else None
    if sc is not None:
        for r in rows:
            r["true_lm"] = round(float(sc.lm_score(core.codes(truth[r["id"]]["pt"])[None])[0]), 3)
    rep = {"plants": len(rows), "found_above_true_quad": sum(r["found_above_true"] for r in rows),
           "median_gap_quad": sorted(r["quad_best_found"] - r["quad_true"] for r in rows)[len(rows) // 2], "rows": rows}
    Path(sys.argv[3]).write_text(json.dumps(rep, indent=1) + "\n")
    print({k: v for k, v in rep.items() if k != "rows"})
    for r in rows[::6]:
        print(r)


if __name__ == "__main__":
    main()
