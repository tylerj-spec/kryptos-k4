#!/usr/bin/env python3
"""R64 SEALED holdout gate (after the freeze). Plants and nulls in one frozen RESULTS.jsonl (ids HOLD_xx / NULL_xx).
For each plant with key model m (CLOCK or GERMAN, from the sealed truth; kinds CLOCK_RAND, CLOCK_RING, GERMAN_EP,
GERMAN_LIT):
  detected        : its model-m total exceeds the MAXIMUM model-m total over all nulls (nulls ran the same 10-route
                    search, so the route look-elsewhere cost is inside the null distribution);
  pt_correct      : letters of the true plaintext in the model-m output plaintext (plaintext order, position by position);
  route_ok        : the model-m answer route equals the true route;
  route_retained  : the true route is among the 2 routes kept after stage 1;
  conv_ok         : the model-m convention equals the true one;
  recovered       : detected AND pt_correct >= PT_MIN (what a K4 SIGNAL needs: a score above all nulls together with
                    correct plaintext, not a high score on a wrong decomposition).
Every final answer (both models, plants and nulls) is re-encrypted through its route independently.
Usage: gate.py BLIND.tsv NULLS.tsv RESULTS.jsonl SEALED_TRUTH.json REPORT.json PT_MIN BAR_CLOCK_RAND BAR_GERMAN_EP
  Each model is gated separately on its IN-DISTRIBUTION kind (CLOCK_RAND for CLOCK, GERMAN_EP for GERMAN):
  model m passes iff recovered >= BAR for that kind and all witnesses are valid. The out-of-distribution kinds
  (CLOCK_RING, GERMAN_LIT) are reported, not gated. Any kind with fewer than half its plants recovered is flagged
  "low_power": a K4 negative for that kind is then reported as WEAK, not STAT (r64/PREREGISTRATION.md). K4 runs if
  at least one model passes; a model that fails is INCONCLUSIVE for K4."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import forward, routes  # noqa: E402


def main():
    blind, nulls, res, truth_p, rep = sys.argv[1:6]
    pt_min, bar_c, bar_g = map(int, sys.argv[6:9])
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
        out[-1]["recovered"] = out[-1]["detected"] and out[-1]["pt_correct"] >= pt_min

    def summarise(o, m):
        return {"plants": len(o), "detected": sum(x["detected"] for x in o), "conv_ok": sum(x["conv_ok"] for x in o),
                "route_ok": sum(x["route_ok"] for x in o), "route_retained": sum(x["route_retained"] for x in o),
                "pt_ge_min": sum(x["pt_correct"] >= pt_min for x in o), "recovered": sum(x["recovered"] for x in o),
                "median_pt": sorted(x["pt_correct"] for x in o)[len(o) // 2] if o else None, "null_max": nmax[m]}
    summ, kinds = {}, {}
    for m in ("CLOCK", "GERMAN"):
        summ[m] = summarise([x for x in out if x["key_model"] == m], m)
        summ[m]["null_totals"] = sorted(rows[i]["models"][m]["total"] for i in null_ids)
    for k in ("CLOCK_RAND", "CLOCK_RING", "GERMAN_EP", "GERMAN_LIT"):
        o = [x for x in out if x["key_kind"] == k]
        kinds[k] = summarise(o, k.split("_")[0])
        kinds[k]["low_power"] = kinds[k]["recovered"] * 2 < kinds[k]["plants"]
    model_pass = {"CLOCK": kinds["CLOCK_RAND"]["recovered"] >= bar_c and wit,
                  "GERMAN": kinds["GERMAN_EP"]["recovered"] >= bar_g and wit}
    passed = any(model_pass.values())
    rep_d = {"summary": summ, "kinds": kinds, "pt_min": pt_min,
             "bars": {"CLOCK_RAND_recovered": bar_c, "GERMAN_EP_recovered": bar_g}, "all_witnesses_valid": wit,
             "model_passed": model_pass, "gate_passed_any_model": passed, "rows": out}
    Path(rep).write_text(json.dumps(rep_d, indent=1) + "\n")
    for m, s in summ.items():
        print(m, {k: v for k, v in s.items() if k != "null_totals"})
    for k, s in kinds.items():
        print(" ", k, s)
    print("witnesses", wit, "model gates", model_pass, "K4 RUN" if passed else "GATE FAILED: INCONCLUSIVE, no K4 run")
    for x in out:
        print(x["id"], x["key_kind"], "%.1f" % x["total"], "det" if x["detected"] else "---", x["true_route"],
              x["found_route"], "kept" if x["route_retained"] else "LOST", x["true_convention"], x["found_convention"],
              "pt", x["pt_correct"])


if __name__ == "__main__":
    main()
