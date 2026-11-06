#!/usr/bin/env python3
"""R68 SEALED holdout gate (after freeze and verify). Plants HOLD_xx and nulls NULL_xx in one frozen RESULTS.jsonl.
For each plant of family f:
  detected   : its family-f best total exceeds the MAXIMUM family-f best total over all nulls;
  pt_correct : letters of the true plaintext in that family-f answer (plaintext order);
  recovered  : detected AND pt_correct >= PT_MIN;
  setting_ok : path, model, convention and parameter all equal the truth.
Usage: gate.py BLIND.tsv NULLS.tsv RESULTS.jsonl SEALED_TRUTH.json REPORT.json PT_MIN BAR_PER BAR_GRO BAR_CTAK BAR_PTAK
  Each family is gated separately: family f passes iff it reaches its bar of recovered plants and every final answer is
  a valid forward witness. K4 runs if at least one family passes; a family that fails is INCONCLUSIVE for K4.
  Recovery is also reported by parameter range (PER p <= 12 vs > 12; CTAK/PTAK L <= 12 vs > 12)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import witness_ok  # noqa: E402

FAMS = ("PER", "GRO", "CTAK", "PTAK")


def main():
    blind, nulls, res, truth_p, rep = sys.argv[1:6]
    pt_min = int(sys.argv[6])
    bars = dict(zip(FAMS, map(int, sys.argv[7:11])))
    cts = {}
    for f in (blind, nulls):
        cts.update(dict(l.split("\t") for l in Path(f).read_text().splitlines()[1:] if l))
    rows = {json.loads(l)["id"]: json.loads(l) for l in Path(res).read_text().splitlines() if l.strip()}
    assert set(rows) == set(cts)
    truth = json.loads(Path(truth_p).read_text())
    wit = all(witness_ok(cts[i], b["path"], b["model"], b["family"], b["convention"], b["param"], b["key"], b["plaintext"])
              for i, r in rows.items() for b in r["families"].values())
    null_ids = [i for i in rows if i.startswith("NULL_")]
    nmax = {f: max(rows[i]["families"][f]["total"] for i in null_ids) for f in FAMS}
    out = []
    for i, t in sorted(truth.items()):
        b = rows[i]["families"][t["family"]]
        ptc = sum(a == c for a, c in zip(b["plaintext"], t["plaintext"]))
        det = b["total"] > nmax[t["family"]]
        out.append({"id": i, "family": t["family"], "true": [t["path"], t["model"], t["convention"], t["param"]],
                    "found": [b["path"], b["model"], b["convention"], b["param"]], "total": b["total"],
                    "detected": det, "pt_correct": ptc, "recovered": det and ptc >= pt_min,
                    "setting_ok": [b["path"], b["model"], b["convention"], b["param"]] ==
                                  [t["path"], t["model"], t["convention"], t["param"]]})
    summ = {}
    for f in FAMS:
        o = [x for x in out if x["family"] == f]
        summ[f] = {"plants": len(o), "detected": sum(x["detected"] for x in o), "recovered": sum(x["recovered"] for x in o),
                   "setting_ok": sum(x["setting_ok"] for x in o), "null_max": nmax[f],
                   "median_pt": sorted(x["pt_correct"] for x in o)[len(o) // 2] if o else None,
                   "bar": bars[f], "passed": sum(x["recovered"] for x in o) >= bars[f]}
    for f in ("PER", "CTAK", "PTAK"):
        o = [x for x in out if x["family"] == f]
        summ[f]["recovered_param_le_12"] = [sum(x["recovered"] for x in o if int(x["true"][3]) <= 12),
                                            sum(1 for x in o if int(x["true"][3]) <= 12)]
        summ[f]["recovered_param_gt_12"] = [sum(x["recovered"] for x in o if int(x["true"][3]) > 12),
                                            sum(1 for x in o if int(x["true"][3]) > 12)]
    for f in FAMS:
        summ[f]["passed"] = summ[f]["passed"] and wit
    passed = any(s["passed"] for s in summ.values())
    Path(rep).write_text(json.dumps({"summary": summ, "pt_min": pt_min, "all_witnesses_valid": wit,
                                     "gate_passed_any_family": passed, "rows": out}, indent=1) + "\n")
    for f, s in summ.items():
        print(f, s)
    print("witnesses", wit, "families passed", {f: s["passed"] for f, s in summ.items()},
          "K4 RUN" if passed else "GATE FAILED: INCONCLUSIVE, no K4 run")
    for x in out:
        print(x["id"], x["family"], "%.1f" % x["total"], "det" if x["detected"] else "---", "pt", x["pt_correct"],
              "true", x["true"], "found", x["found"])


if __name__ == "__main__":
    main()
