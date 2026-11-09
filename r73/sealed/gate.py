#!/usr/bin/env python3
"""R73 Phase B verify + gate (after the blind results are frozen and pushed).
Verify (no truth): every setting's decode in work/ re-encrypts to its ciphertext; RESULTS equal each file's best.
Gate (truth opened after verify; rules fixed in r73/PHASE_B_PREREGISTRATION.md):
  recovered  = best family is the true family AND >= 90 of 97 plaintext letters right;
  confident  = best score >= -2.7 per letter;
  PASS(f)    = >= 90/100 positives of family f recovered AND confident;
  negatives  = 0/300 confident required (each family's PASS also needs this);
  every recovered decode must re-encrypt (checked by verify).
Usage: gate.py BLIND.tsv RUN_DIR SEALED_TRUTH.json REPORT.json"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r73"))
import wordkey as W  # noqa: E402

CUT = -2.7


def verify(tsv, run):
    cts = dict(l.split("\t") for l in Path(tsv).read_text().splitlines()[1:] if l)
    res = {json.loads(l)["id"]: json.loads(l) for l in (Path(run) / "RESULTS.jsonl").read_text().splitlines() if l}
    problems, n = [], 0
    for rid, ct in cts.items():
        w = json.loads((Path(run) / "work" / f"{rid}.json").read_text())
        for s in w["settings"]:
            n += 1
            if W.encrypt(s["words"], s["family"], tuple(s["setting"])) != ct:
                problems.append(f"witness {rid} {s['family']} {s['setting']}")
        b = w["settings"][0]
        if (b["family"], b["setting"], b["words"]) != (res[rid]["family"], res[rid]["setting"], res[rid]["words"]):
            problems.append(f"result not best {rid}")
    return {"witnesses": n, "problems": problems, "passed": not problems}


def main():
    tsv, run, truth_p, rep = sys.argv[1:5]
    ver = verify(tsv, run)
    print("verify:", ver["witnesses"], "witnesses,", "PASSED" if ver["passed"] else f"FAILED {ver['problems'][:5]}")
    truth = json.loads(Path(truth_p).read_text())
    res = {json.loads(l)["id"]: json.loads(l) for l in (Path(run) / "RESULTS.jsonl").read_text().splitlines() if l}
    rows, neg_conf, neg_max = [], 0, -1e9
    for rid, t in sorted(truth.items()):
        r = res[rid]
        conf = r["per_letter"] >= CUT
        if t["kind"].startswith("NEG_"):
            neg_conf += conf
            neg_max = max(neg_max, r["per_letter"])
            rows.append({"id": rid, "kind": t["kind"], "per_letter": r["per_letter"], "confident": conf})
            continue
        right = sum(a == b for a, b in zip("".join(r["words"]), "".join(t["words"])))
        rec = r["family"] == t["kind"] and right >= 90
        rows.append({"id": rid, "kind": t["kind"], "true_setting": t["setting"], "found": [r["family"], r["setting"]],
                     "letters_right": right, "exact": r["words"] == t["words"], "per_letter": r["per_letter"],
                     "recovered": rec, "confident": conf, "ok": rec and conf})
    summ = {}
    for f in ("I", "R26"):
        p = [x for x in rows if x["kind"] == f]
        summ[f] = {"n": len(p), "recovered_and_confident": sum(x["ok"] for x in p), "recovered": sum(x["recovered"] for x in p),
                   "exact": sum(x["exact"] for x in p), "setting_exact": sum(x["found"] == [f, x["true_setting"]] for x in p),
                   "letters_right_sorted_low5": sorted(x["letters_right"] for x in p)[:5],
                   "per_letter_min": min(x["per_letter"] for x in p)}
        summ[f]["passed"] = summ[f]["recovered_and_confident"] >= 90 and neg_conf == 0 and ver["passed"]
    summ["negatives"] = {"n": sum(1 for x in rows if x["kind"].startswith("NEG_")), "confident": neg_conf,
                         "per_letter_max": neg_max}
    Path(rep).write_text(json.dumps({"cut_per_letter": CUT, "verify": ver, "summary": summ, "rows": rows}, indent=1) + "\n")
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
