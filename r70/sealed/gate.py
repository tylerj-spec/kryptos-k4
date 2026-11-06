#!/usr/bin/env python3
"""R70 SEALED holdout gate (after freeze and verify). Plants HOLD_xx and nulls NULL_xx in one frozen run.
  detected   : the plant's rank-0 total exceeds the MAXIMUM rank-0 total over the 20 nulls;
  pt_correct : letters of the true plaintext in the rank-0 plaintext;
  recovered  : detected AND pt_correct >= 60;
  setting_ok : source, offset, path, model and convention of rank 0 equal the truth (CLEAN plants).
PASS iff >= 18 of the 20 CLEAN plants are recovered and the verifier passed. NOISY plants are reported only.
Usage: gate.py BLIND.tsv RESULTS.jsonl SEALED_TRUTH.json VERIFY.json REPORT.json"""
import json
import sys
from pathlib import Path


def main():
    blind, res, truth_p, ver, rep = sys.argv[1:6]
    rows = {json.loads(l)["id"]: json.loads(l) for l in Path(res).read_text().splitlines() if l.strip()}
    truth = json.loads(Path(truth_p).read_text())
    assert set(rows) == set(truth) == {l.split("\t")[0] for l in Path(blind).read_text().splitlines()[1:] if l}
    vok = json.loads(Path(ver).read_text())["passed"]
    nmax = max(rows[i]["total"] for i, t in truth.items() if t["kind"] == "NULL")
    out = []
    for i, t in sorted(truth.items()):
        if t["kind"] == "NULL":
            continue
        b = rows[i]
        ptc = sum(a == c for a, c in zip(b["plaintext"], t["plaintext"]))
        det = b["total"] > nmax
        out.append({"id": i, "kind": t["kind"], "true": [t["source"], t["offset"], t["path"], t["model"], t["convention"]],
                    "found": [b["source"], b["offset"], b["path"], b["model"], b["convention"]], "total": b["total"],
                    "detected": det, "pt_correct": ptc, "recovered": det and ptc >= 60,
                    "setting_ok": [b["source"], b["offset"], b["path"], b["model"], b["convention"]] ==
                                  [t["source"], t["offset"], t["path"], t["model"], t["convention"]]})
    summ = {}
    for k in ("CLEAN", "NOISY_SUB", "NOISY_DEL"):
        o = [x for x in out if x["kind"] == k]
        summ[k] = {"plants": len(o), "recovered": sum(x["recovered"] for x in o), "setting_ok": sum(x["setting_ok"] for x in o),
                   "median_pt": sorted(x["pt_correct"] for x in o)[len(o) // 2]}
    passed = summ["CLEAN"]["recovered"] >= 18 and vok
    Path(rep).write_text(json.dumps({"null_max": nmax, "summary": summ, "verify_passed": vok, "gate_passed": passed,
                                     "rows": out}, indent=1) + "\n")
    print("null max", round(nmax, 2), summ, "verify", vok, "K4 RUN" if passed else "GATE FAILED: INCONCLUSIVE, no K4 run")
    for x in out:
        print(x["id"], x["kind"], "%.1f" % x["total"], "det" if x["detected"] else "---", "pt", x["pt_correct"],
              "true", x["true"], "found", x["found"])


if __name__ == "__main__":
    main()
