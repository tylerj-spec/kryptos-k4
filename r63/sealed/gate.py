#!/usr/bin/env python3
"""R63 SEALED holdout gate (after the freeze). Plants and nulls in one frozen RESULTS.jsonl (ids HOLD_xx / NULL_xx).
For each plant with key model m (CLOCK or GERMAN, from the sealed truth):
  detected  : its model-m total exceeds the MAXIMUM model-m total over all nulls;
  pt_correct: letters of the true plaintext in the model-m output plaintext (position by position);
  conv_ok   : the model-m convention equals the true one (no symmetry: the two streams have different models).
Every output (both models, plants and nulls) is re-encrypted independently.
Usage: gate.py BLIND.tsv NULLS.tsv RESULTS.jsonl SEALED_TRUTH.json REPORT.json DET_CLOCK DET_GERMAN PT_MIN PT_COUNT_CLOCK PT_COUNT_GERMAN
  (pass iff, for each model, detected >= DET_m and #plants with pt_correct >= PT_MIN is >= PT_COUNT_m; all witnesses valid)"""
import json
import sys
from pathlib import Path

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"


def enc(p, k, conv):
    xn, op = conv.split("_")
    X = AZ if xn == "AZ" else KRY
    return "".join(X[(X.index(a) + X.index(b)) % 26 if op == "VIG" else (X.index(b) - X.index(a)) % 26 if op == "BEAU"
                     else (X.index(a) - X.index(b)) % 26] for a, b in zip(p, k))


def main():
    blind, nulls, res, truth_p, rep = sys.argv[1:6]
    det_c, det_g, pt_min, cnt_c, cnt_g = map(int, sys.argv[6:11])
    cts = {}
    for f in (blind, nulls):
        cts.update(dict(l.split("\t") for l in Path(f).read_text().splitlines()[1:] if l))
    rows = {json.loads(l)["id"]: json.loads(l) for l in Path(res).read_text().splitlines() if l.strip()}
    assert set(rows) == set(cts)
    truth = json.loads(Path(truth_p).read_text())
    wit = all(enc(b["plaintext"], b["key"], b["convention"]) == cts[i] for i, r in rows.items() for b in r["models"].values())
    null_ids = [i for i in rows if i.startswith("NULL_")]
    nmax = {m: max(rows[i]["models"][m]["total"] for i in null_ids) for m in ("CLOCK", "GERMAN")}
    out = []
    for i, t in sorted(truth.items()):
        m = t["key_model"]
        b = rows[i]["models"][m]
        other = "GERMAN" if m == "CLOCK" else "CLOCK"
        out.append({"id": i, "key_model": m, "total": b["total"], "detected": b["total"] > nmax[m],
                    "other_model_detected": rows[i]["models"][other]["total"] > nmax[other],
                    "pt_correct": sum(a == x for a, x in zip(b["plaintext"], t["plaintext"])),
                    "key_correct": sum(a == x for a, x in zip(b["key"], t["key"])),
                    "true_convention": t["convention"], "found_convention": b["convention"],
                    "conv_ok": b["convention"] == t["convention"]})
    summ = {}
    for m in ("CLOCK", "GERMAN"):
        o = [x for x in out if x["key_model"] == m]
        summ[m] = {"plants": len(o), "detected": sum(x["detected"] for x in o), "conv_ok": sum(x["conv_ok"] for x in o),
                   "pt_ge_min": sum(x["pt_correct"] >= pt_min for x in o),
                   "median_pt": sorted(x["pt_correct"] for x in o)[len(o) // 2] if o else None, "null_max": nmax[m],
                   "null_totals": sorted(rows[i]["models"][m]["total"] for i in null_ids)}
    passed = (summ["CLOCK"]["detected"] >= det_c and summ["GERMAN"]["detected"] >= det_g and
              summ["CLOCK"]["pt_ge_min"] >= cnt_c and summ["GERMAN"]["pt_ge_min"] >= cnt_g and wit)
    rep_d = {"summary": summ, "pt_min": pt_min, "bars": [det_c, det_g, pt_min, cnt_c, cnt_g],
             "all_witnesses_valid": wit, "gate_passed": passed, "rows": out}
    Path(rep).write_text(json.dumps(rep_d, indent=1) + "\n")
    for m, s in summ.items():
        print(m, {k: v for k, v in s.items() if k != "null_totals"})
    print("witnesses", wit, "GATE", "PASSED" if passed else "FAILED")
    for x in out:
        print(x["id"], x["key_model"], "%.1f" % x["total"], "det" if x["detected"] else "---", x["true_convention"], x["found_convention"], "pt", x["pt_correct"])


if __name__ == "__main__":
    main()
