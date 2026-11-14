#!/usr/bin/env python3
"""R83a verdicts (rules fixed in r83/PREREGISTRATION.md; applied mechanically to OUT/R83A.json).
For every step (EXACT, DROP, F1XD, and each of the 8 SHIFT position sets) and every family:
  statistic  EXACT and SHIFT: feasible settings by checks; DROP and F1XD: settings infeasible as they stand but feasible
             once one published letter is set aside, by checks (a setting's checks are counted with all 24 letters);
  K(c)       K4's number of such settings with >= c checks;  S(c) the most any shuffle of the same step has (only
             shuffles on which that family ran: LX's DROP and SHIFT steps have 5, every other step 20);
  EXCL       K(3) = 0: no setting of the family with >= 3 checks is feasible on K4 (in that step);
  LEAD       some K4 setting with effective strength e >= 3 (eff: -log26 of its chance of being feasible on a
             random ciphertext; = checks for the slot checks, edges - slots for the graph checks LX and F1X) while no
             shuffle of the step has any at eff >= e;
  CHANCE     otherwise: K4's feasible settings are at levels the shuffles also reach; every other setting with >= 3
             checks is excluded, these stay open and are listed.
A LEAD is a reason for a new blind round of that family and cell (sealed gate, then K4 blind). It is never a
solution, and nothing here decrypts or completes a key.
Usage: verdict83.py R83A.json VERDICT.json"""
import json
import sys
from pathlib import Path

MIN = 3


def stat(rep, step, by="checks"):
    key = ("drop_one_feasible_by_" if step in ("DROP", "F1XD") else "feasible_by_") + by
    lst = "drop_one_list" if step in ("DROP", "F1XD") else "feasible_list"
    return {int(k): v for k, v in rep.get(key, {}).items()}, rep.get(lst, [])


def ge(d, c):
    return sum(v for k, v in d.items() if k >= c)


def verdicts(res):
    out = []
    for step, vs in res.items():
        for var, byid in vs.items():
            ids = list(byid)
            k4 = byid["K4"]
            shuf = [byid[i] for i in ids if i != "K4"]
            for fam in sorted(k4):
                K, lst = stat(k4[fam], step)
                ran = [s[fam] for s in shuf if fam in s]          # only shuffles on which this family ran
                SE = [stat(r, step, "eff")[0] for r in ran]
                kn = ge(K, MIN)
                S = [stat(r, step)[0] for r in ran]
                tested = sum(v for k, v in k4[fam].get("tested_by_checks", {}).items() if int(k) >= MIN)
                row = {"step": step, "variant": var, "family": fam, "settings_ge3": tested, "k4_ge3": kn,
                       "shuffles": len(S), "shuffles_ge3": [ge(s, MIN) for s in S]}
                if kn == 0:
                    row["verdict"] = "EXCL"
                else:
                    leads = [r for r in lst if r["eff"] >= MIN and max(ge(s, r["eff"]) for s in SE) == 0]
                    row["verdict"] = "LEAD" if leads else "CHANCE"
                    row["k4_settings"] = lst[:50]
                    row["leads"] = leads[:50]
                out.append(row)
    return out


def main():
    res = json.loads(Path(sys.argv[1]).read_text())
    v = verdicts(res)
    summary = {}
    for r in v:
        summary.setdefault(r["verdict"], []).append(f'{r["step"]}:{r["variant"]}:{r["family"]}')
    Path(sys.argv[2]).write_text(json.dumps({"label": "CRIB-ASSISTED exclusion-only checks (R83a); no decryption",
                                             "summary": summary, "rows": v}, indent=1) + "\n")
    for r in v:
        print(r["step"], r["variant"], r["family"], r["verdict"], "K4", r["k4_ge3"], "shuffles", r["shuffles_ge3"])
    print({k: len(x) for k, x in summary.items()})


if __name__ == "__main__":
    main()
