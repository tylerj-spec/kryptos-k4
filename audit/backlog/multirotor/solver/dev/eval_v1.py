#!/usr/bin/env python3
"""Evaluate an RX2-O development run against the development panel truth (spent data; not a gate).
Per plant: top-1 (letter-model maximum of the KEEP retained) letters right, recovered (>= 95/97), exact, the
quadgram top-1, any-of-KEEP recovery, the best restart's letters, and how many of the R restarts reached >= 95.
The forward witness (rx2o.encrypt of top-1 under its wirings == ciphertext) is checked for every plant.
Usage: eval_v1.py PANEL_TRUTH.json RESULTS.jsonl OUT.json"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import rx2o as X  # noqa: E402


def right(a, b):
    return sum(x == y for x, y in zip(a, b))


def main():
    truth = json.loads(Path(sys.argv[1]).read_text())
    rows, per = [], {}
    for line in Path(sys.argv[2]).read_text().splitlines():
        r = json.loads(line)
        t = truth[r["id"]]
        b = r["best"]
        assert X.encrypt(b["text"], b["W1"], b["W2"], *r["label"]) == t["ct"], "witness"
        top1 = right(b["text"], t["pt"])
        quad1 = right(r["keep"][0]["text"], t["pt"])
        anyk = max(right(c["text"], t["pt"]) for c in r["keep"])
        rest = [right(x, t["pt"]) for x in r["restart_texts"]]
        row = {"id": r["id"], "cell": t["cell"], "turnovers": t["turnovers"], "label": r["label"], "top1": top1,
               "quad_top1": quad1, "any_keep": anyk, "best_restart": max(rest),
               "restarts_ge95": sum(x >= 95 for x in rest), "restarts": len(rest),
               "lm": round(b["lm_per_letter"], 3), "word": round(b["word_per_letter"], 3),
               "true_quad_above_found": None, "cpu_s": r["cpu_s"]}
        rows.append(row)
        per.setdefault(t["cell"], []).append(row)
    summ = {c: {"plants": len(v), "top1_ge95": sum(x["top1"] >= 95 for x in v),
                "top1_exact": sum(x["top1"] == 97 for x in v), "quad_top1_ge95": sum(x["quad_top1"] >= 95 for x in v),
                "any_keep_ge95": sum(x["any_keep"] >= 95 for x in v),
                "median_top1": sorted(x["top1"] for x in v)[len(v) // 2],
                "restarts_ge95_total": sum(x["restarts_ge95"] for x in v)} for c, v in per.items()}
    tot = {k: sum(s[k] for s in summ.values()) for k in ("plants", "top1_ge95", "top1_exact", "quad_top1_ge95",
                                                        "any_keep_ge95", "restarts_ge95_total")}
    tot["cpu_s"] = round(sum(x["cpu_s"] for x in rows), 1)
    rep = {"total": tot, "by_cell": summ, "rows": rows}
    Path(sys.argv[3]).write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps(tot))
    for c, s in summ.items():
        print(c, s)


if __name__ == "__main__":
    main()
