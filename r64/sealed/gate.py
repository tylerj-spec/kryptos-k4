#!/usr/bin/env python3
"""R64 SEALED holdout gate (after the freeze). Plants and nulls in one frozen RESULTS.jsonl (ids HOLD_xx / NULL_xx).
For each plant with key model m (CLOCK or GERMAN, from the sealed truth; kinds CLOCK_RAND, CLOCK_RING, GERMAN_EP,
GERMAN_LIT):
  detected        : its model-m total exceeds the MAXIMUM model-m total over all nulls (nulls ran the same 10-route
                    search, so the route look-elsewhere cost is inside the null distribution);
  pt_correct      : letters of the true plaintext in the model-m output plaintext (plaintext order, position by position);
  route_ok        : the model-m answer route equals the true route;
  route_retained  : the true route is among the 2 routes kept after stage 1;
  conv_ok         : the model-m convention equals the true one.
Every final answer (both models, plants and nulls) is re-encrypted through its route independently.
Usage: gate.py BLIND.tsv NULLS.tsv RESULTS.jsonl SEALED_TRUTH.json REPORT.json DET_CLOCK DET_GERMAN PT_MIN PT_COUNT_CLOCK PT_COUNT_GERMAN
  pass iff, for each model, detected >= DET_m and #plants with pt_correct >= PT_MIN is >= PT_COUNT_m, and all
  witnesses are valid. Per-kind counts are reported; a kind with fewer than half its plants detected is flagged
  "low_power" (its K4 negative is then reported as WEAK, not STAT; r64/PREREGISTRATION.md)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import forward, routes  # noqa: E402


def main():
    blind, nulls, res, truth_p, rep = sys.argv[1:6]
    det_c, det_g, pt_min, cnt_c, cnt_g = map(int, sys.argv[6:11])
    cts = {}
    for f in (blind, nulls):
        cts.update(dict(l.split("\t") for l in Path(f).read_text().splitlines()[1:] if l))
    rows = {json.loads(l)["id"]: json.loads(l) for l in Path(res).read_text().splitlines() if l.strip()}
    assert set(rows) == set(cts)
    truth = json.loads(Path(truth_p).read_text())
    R = routes()
    wit = all(forward(b["plaintext"], b["key"], b["convention"], R[b["route"]]) == cts[i]
              for i, r in rows.items() for b in r["models"].values())
    null_ids = [i for i in rows if i.startswith("NULL_")]
    nmax = {m: max(rows[i]["models"][m]["total"] for i in null_ids) for m in ("CLOCK", "GERMAN")}
    out = []
    for i, t in sorted(truth.items()):
        m = t["key_model"]
        b = rows[i]["models"][m]
        other = "GERMAN" if m == "CLOCK" else "CLOCK"
        out.append({"id": i, "key_kind": t["key_kind"], "key_model": m, "total": b["total"],
                    "detected": b["total"] > nmax[m],
                    "other_model_detected": rows[i]["models"][other]["total"] > nmax[other],
                    "pt_correct": sum(a == x for a, x in zip(b["plaintext"], t["plaintext"])),
                    "key_correct": sum(a == x for a, x in zip(b["key"], t["key"])),
                    "true_route": t["route"], "found_route": b["route"], "route_ok": b["route"] == t["route"],
                    "route_retained": t["route"] in [d["route"] for d in b["stage2"]],
                    "true_convention": t["convention"], "found_convention": b["convention"],
                    "conv_ok": b["convention"] == t["convention"]})

    def summarise(o, m):
        return {"plants": len(o), "detected": sum(x["detected"] for x in o), "conv_ok": sum(x["conv_ok"] for x in o),
                "route_ok": sum(x["route_ok"] for x in o), "route_retained": sum(x["route_retained"] for x in o),
                "pt_ge_min": sum(x["pt_correct"] >= pt_min for x in o),
                "median_pt": sorted(x["pt_correct"] for x in o)[len(o) // 2] if o else None, "null_max": nmax[m]}
    summ, kinds = {}, {}
    for m in ("CLOCK", "GERMAN"):
        summ[m] = summarise([x for x in out if x["key_model"] == m], m)
        summ[m]["null_totals"] = sorted(rows[i]["models"][m]["total"] for i in null_ids)
    for k in ("CLOCK_RAND", "CLOCK_RING", "GERMAN_EP", "GERMAN_LIT"):
        o = [x for x in out if x["key_kind"] == k]
        kinds[k] = summarise(o, k.split("_")[0])
        kinds[k]["low_power"] = kinds[k]["detected"] * 2 < kinds[k]["plants"]
    passed = (summ["CLOCK"]["detected"] >= det_c and summ["GERMAN"]["detected"] >= det_g and
              summ["CLOCK"]["pt_ge_min"] >= cnt_c and summ["GERMAN"]["pt_ge_min"] >= cnt_g and wit)
    rep_d = {"summary": summ, "kinds": kinds, "pt_min": pt_min, "bars": [det_c, det_g, pt_min, cnt_c, cnt_g],
             "all_witnesses_valid": wit, "gate_passed": passed, "rows": out}
    Path(rep).write_text(json.dumps(rep_d, indent=1) + "\n")
    for m, s in summ.items():
        print(m, {k: v for k, v in s.items() if k != "null_totals"})
    for k, s in kinds.items():
        print(" ", k, s)
    print("witnesses", wit, "GATE", "PASSED" if passed else "FAILED")
    for x in out:
        print(x["id"], x["key_kind"], "%.1f" % x["total"], "det" if x["detected"] else "---", x["true_route"],
              x["found_route"], "kept" if x["route_retained"] else "LOST", x["true_convention"], x["found_convention"],
              "pt", x["pt_correct"])


if __name__ == "__main__":
    main()
