#!/usr/bin/env python3
"""R66 SEALED holdout gate (after the freeze and verify). Plants HOLD_xx and nulls NULL_xx in one frozen RESULTS.jsonl.
  detected  : the plant's total exceeds the MAXIMUM total over all nulls (nulls ran the same 10-route search);
  pt_correct: letters of the true plaintext in the output (plaintext order);
  recovered : detected AND pt_correct >= PT_MIN;
  route_ok  : the answer route equals the true route.
Usage: gate.py BLIND.tsv NULLS.tsv RESULTS.jsonl SEALED_TRUTH.json REPORT.json PT_MIN BAR_RECOVERED
  pass iff recovered >= BAR_RECOVERED and every final answer is a valid witness."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import routes, witness_ok  # noqa: E402


def main():
    blind, nulls, res, truth_p, rep = sys.argv[1:6]
    pt_min, bar = int(sys.argv[6]), int(sys.argv[7])
    cts = {}
    for f in (blind, nulls):
        cts.update(dict(l.split("\t") for l in Path(f).read_text().splitlines()[1:] if l))
    rows = {json.loads(l)["id"]: json.loads(l) for l in Path(res).read_text().splitlines() if l.strip()}
    assert set(rows) == set(cts)
    truth = json.loads(Path(truth_p).read_text())
    R = routes()
    wit = all(witness_ok(cts[i], R[r["route"]], r["plaintext"], r["map"]) for i, r in rows.items())
    null_ids = [i for i in rows if i.startswith("NULL_")]
    nmax = max(rows[i]["total"] for i in null_ids)
    out = []
    for i, t in sorted(truth.items()):
        r = rows[i]
        ptc = sum(a == b for a, b in zip(r["plaintext"], t["plaintext"]))
        out.append({"id": i, "total": r["total"], "detected": r["total"] > nmax, "pt_correct": ptc,
                    "recovered": r["total"] > nmax and ptc >= pt_min, "true_route": t["route"],
                    "found_route": r["route"], "route_ok": r["route"] == t["route"], "ic": t["ic"]})
    summ = {"plants": len(out), "detected": sum(x["detected"] for x in out),
            "recovered": sum(x["recovered"] for x in out), "route_ok": sum(x["route_ok"] for x in out),
            "median_pt": sorted(x["pt_correct"] for x in out)[len(out) // 2], "null_max": nmax,
            "null_totals": sorted(rows[i]["total"] for i in null_ids),
            "plant_ic_range": [min(x["ic"] for x in out), max(x["ic"] for x in out)]}
    passed = summ["recovered"] >= bar and wit
    Path(rep).write_text(json.dumps({"summary": summ, "pt_min": pt_min, "bar_recovered": bar,
                                     "all_witnesses_valid": wit, "gate_passed": passed, "rows": out}, indent=1) + "\n")
    print({k: v for k, v in summ.items() if k != "null_totals"})
    print("witnesses", wit, "GATE", "PASSED" if passed else "FAILED")
    for x in out:
        print(x["id"], "%.1f" % x["total"], "det" if x["detected"] else "---", x["true_route"], x["found_route"],
              "pt", x["pt_correct"], "ic", x["ic"])


if __name__ == "__main__":
    main()
