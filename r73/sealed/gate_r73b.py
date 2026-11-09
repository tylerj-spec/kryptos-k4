#!/usr/bin/env python3
"""R73b verify + gate (after the blind results are frozen and pushed). Rules fixed in r73/R73B_PREREGISTRATION.md.
Verify (no truth; r73/sealed/gate.py's verify, unchanged): every setting's decode in work/ re-encrypts to its
ciphertext, and RESULTS equal each file's best.
Gate (truth opened after verify):
  recovered  = >= 90 of 97 plaintext letters right (the solver decodes R26 only, so the family is always R26);
  confident  = best score >= CUT per letter;
  PASS       = >= 90/100 positives recovered AND confident, AND 0/300 negatives confident, AND verify passed.
Usage: gate_r73b.py BLIND.tsv RUN_DIR SEALED_TRUTH.json REPORT.json"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r73" / "sealed"))
from gate import verify  # noqa: E402

CUT = -1.4   # fixed in r73/R73B_PREREGISTRATION.md (development rule; r73/results/R73B_DEV_CUT.json)


def main():
    tsv, run, truth_p, rep = sys.argv[1:5]
    ver = verify(tsv, run)
    print("verify:", ver["witnesses"], "witnesses,", "PASSED" if ver["passed"] else f"FAILED {ver['problems'][:5]}")
    if not ver["passed"]:
        raise SystemExit("verify failed: truth not opened")
    truth = json.loads(Path(truth_p).read_text())
    res = {json.loads(l)["id"]: json.loads(l) for l in (Path(run) / "RESULTS.jsonl").read_text().splitlines() if l}
    rows = []
    for rid, t in sorted(truth.items()):
        r = res[rid]
        conf = r["per_letter"] >= CUT
        if t["kind"].startswith("NEG_"):
            rows.append({"id": rid, "kind": t["kind"], "per_letter": r["per_letter"], "confident": conf})
            continue
        right = sum(a == b for a, b in zip("".join(r["words"]), "".join(t["words"])))
        rec = r["family"] == "R26" and right >= 90
        rows.append({"id": rid, "kind": t["kind"], "true_setting": t["setting"], "found": r["setting"],
                     "letters_right": right, "exact": r["words"] == t["words"], "per_letter": r["per_letter"],
                     "recovered": rec, "confident": conf, "ok": rec and conf,
                     "true_words": t["words"], "found_words": r["words"]})
    p = [x for x in rows if x["kind"] == "R26"]
    neg = [x for x in rows if x["kind"].startswith("NEG_")]
    by_kind = {}
    for x in neg:
        by_kind[x["kind"]] = max(by_kind.get(x["kind"], -1e9), x["per_letter"])
    summ = {"R26": {"n": len(p), "recovered_and_confident": sum(x["ok"] for x in p),
                    "recovered": sum(x["recovered"] for x in p), "confident": sum(x["confident"] for x in p),
                    "exact": sum(x["exact"] for x in p), "setting_exact": sum(x["found"] == x["true_setting"] for x in p),
                    "letters_right_sorted_low5": sorted(x["letters_right"] for x in p)[:5],
                    "per_letter_min": min(x["per_letter"] for x in p)},
            "negatives": {"n": len(neg), "confident": sum(x["confident"] for x in neg),
                          "per_letter_max": max(x["per_letter"] for x in neg), "per_letter_max_by_kind": by_kind}}
    summ["passed"] = (summ["R26"]["recovered_and_confident"] >= 90 and summ["negatives"]["confident"] == 0
                      and ver["passed"])
    Path(rep).write_text(json.dumps({"cut_per_letter": CUT, "verify": ver, "summary": summ, "rows": rows}, indent=1) + "\n")
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
