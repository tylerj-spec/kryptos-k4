#!/usr/bin/env python3
"""R61 SEALED holdout gate (after both freezes). Like r59/sealed/gate.py, plus the route.
Per plant: detected (best total > max over all null totals), route_ok, convention_ok (VARB == BEAU), pair_correct
(positions, in plaintext order, where the output pair {p_i, k_i} equals the true pair), witness (re-encrypt through the
chosen route). Thresholds are read from the command line exactly as fixed in r61/PREREGISTRATION.md.
Usage: gate.py PLANTS.tsv PLANT_RESULTS.jsonl SEALED_TRUTH.json NULLS.tsv NULL_RESULTS.jsonl REPORT.json DET ROUTE CONV PAIRN"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import encrypt  # noqa: E402


def load(tsv, res):
    cts = dict(l.split("\t") for l in Path(tsv).read_text().splitlines()[1:] if l)
    rows = [json.loads(l) for l in Path(res).read_text().splitlines() if l.strip()]
    assert set(r["id"] for r in rows) == set(cts)
    return cts, rows


def main():
    pt_tsv, pt_res, truth_p, nl_tsv, nl_res, rep = sys.argv[1:7]
    det_bar, route_bar, conv_bar, pair_bar = map(int, sys.argv[7:11])
    truth = json.loads(Path(truth_p).read_text())
    pcts, prows = load(pt_tsv, pt_res)
    ncts, nrows = load(nl_tsv, nl_res)
    wit = all(encrypt(r["best"]["plaintext"], r["best"]["key"], r["best"]["convention"], r["best"]["route"]) == cts[r["id"]]
              for rows, cts in ((prows, pcts), (nrows, ncts)) for r in rows)
    nmax = max(r["best"]["total"] for r in nrows)
    out = []
    for r in prows:
        b, t = r["best"], truth[r["id"]]
        pair = sum({a, c} == {x, y} for a, c, x, y in zip(b["plaintext"], b["key"], t["plaintext"], t["key"]))
        s1rank = [d["route"] for d in r["stage1"]].index(t["route"]) + 1
        out.append({"id": r["id"], "total": b["total"], "detected": b["total"] > nmax,
                    "true_route": t["route"], "found_route": b["route"], "route_ok": b["route"] == t["route"],
                    "true_route_stage1_rank": s1rank,
                    "true_convention": t["convention"], "found_convention": b["convention"],
                    "convention_ok": b["convention"].replace("VARB", "BEAU") == t["convention"].replace("VARB", "BEAU"),
                    "pair_correct": pair})
    det, rok, cok = (sum(o[k] for o in out) for k in ("detected", "route_ok", "convention_ok"))
    p60 = sum(o["pair_correct"] >= 60 for o in out)
    res = {"plants": len(out), "nulls": len(nrows), "null_max_total": nmax,
           "null_totals": sorted(r["best"]["total"] for r in nrows),
           "detected": det, "route_ok": rok, "convention_ok": cok, "pair_correct_ge_60": p60,
           "median_pair_correct": sorted(o["pair_correct"] for o in out)[len(out) // 2],
           "all_witnesses_valid": wit, "bars": {"detected": det_bar, "route": route_bar, "convention": conv_bar, "pair60": pair_bar},
           "gate_passed": det >= det_bar and rok >= route_bar and cok >= conv_bar and p60 >= pair_bar and wit,
           "rows": out}
    Path(rep).write_text(json.dumps(res, indent=1) + "\n")
    print({k: v for k, v in res.items() if k not in ("rows", "null_totals")})
    for o in out:
        print(o["id"], "%.1f" % o["total"], "det" if o["detected"] else "---", o["true_route"], "->", o["found_route"],
              "s1rank", o["true_route_stage1_rank"], o["true_convention"], o["found_convention"], "pair", o["pair_correct"])


if __name__ == "__main__":
    main()
