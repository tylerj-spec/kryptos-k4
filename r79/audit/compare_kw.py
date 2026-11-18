#!/usr/bin/env python3
"""Compare r79/audit/replay_kw.py outputs with the archived validators (r81a/k4/VALIDATE.json, r79/k4/VALIDATE.json).
Usage: compare_kw.py OUT.json"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
a81 = json.loads((ROOT / "r81a/k4/VALIDATE.json").read_text())["rows"]
a79 = json.loads((ROOT / "r79/k4/VALIDATE.json").read_text())["rows"]
r81 = json.loads((ROOT / "r79/audit/REPLAY_KW_R81A_TARGET.json").read_text())["results"]
r79 = json.loads((ROOT / "r79/audit/REPLAY_KW_R79_TARGET.json").read_text())["results"]
TAG = {"H7CT": "R79", "H7TXT": "R79", "LIB": "R79", "PROG": "R79",
       "H7CT_A": "R81a", "LIB_A": "R81a", "LIB_G4": "R81a", "PROG_A": "R81a"}
rows, ok, min_checks = [], True, 99
for rid, fams in r81.items():
    for fam, r in fams.items():
        a = a81[rid][f"{TAG[fam]}:{fam}"]
        mine = {"settings": r["settings"], "exact_feasible": sum(r["feasible_by_checks"].values()),
                "drop_one_feasible": sum(r["drop_one_by_position"].values()),
                "drop_one_by_position": {str(k): v for k, v in r["drop_one_by_position"].items()}}
        theirs = {"settings": a["settings"], "exact_feasible": a["exact_feasible"],
                  "drop_one_feasible": a["drop_one_feasible"],
                  "drop_one_by_position": {str(k): v for k, v in a["drop_one_by_position"].items()}}
        same = mine == theirs
        ok &= same
        min_checks = min(min_checks, r["min_checks"])
        rows.append({"target": "R81a", "id": rid, "family": fam, "equal": same, "replay": mine, "archive": theirs,
                     "min_checks": r["min_checks"]})
for rid, fams in r79.items():
    for fam, r in fams.items():
        a = a79[rid][fam]
        mine = {str(k): v for k, v in r["feasible_by_checks"].items() if v}
        theirs = {str(k): v for k, v in a["feasible_by_checks"].items() if v}
        same = mine == theirs
        ok &= same
        min_checks = min(min_checks, r["min_checks"])
        rows.append({"target": "R79", "id": rid, "family": fam, "equal": same, "replay_feasible_by_checks": mine,
                     "archive_feasible_by_checks": theirs, "settings": r["settings"], "min_checks": r["min_checks"]})
out = {"all_equal": ok, "comparisons": len(rows), "min_checks_any_setting": min_checks,
       "every_setting_ge_12_checks": min_checks >= 12, "rows": rows}
Path(sys.argv[1]).write_text(json.dumps(out, indent=1) + "\n")
print({k: v for k, v in out.items() if k != "rows"})
print("disagreements:", [(r["target"], r["id"], r["family"]) for r in rows if not r["equal"]])
