#!/usr/bin/env python3
"""T6 item 1: compare the EXACT step (all 24 letters) of r83/audit/EXACT_DROP.json (T1, independent full replay of
WPX and PFX) with R83a's archived EXACT record (r83/k4/run/R83A.json): tested and feasible by checks, and the
feasible list (complete when shorter than R83a's cap of 300). Usage: compare_exact_wpx_pfx.py OUT.json"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ed = json.loads((ROOT / "r83/audit/EXACT_DROP.json").read_text())["results"]
arch = json.loads((ROOT / "r83/k4/run/R83A.json").read_text())["EXACT"]["none"]
norm = lambda d: {int(k): v for k, v in d.items() if v}  # noqa: E731
out, ok = {}, True
for rid, res in ed.items():
    for fam in ("WPX", "PFX"):
        a, r = arch[rid][fam], res[fam]
        new = {json.dumps({k: s[k] for k in s if k not in ("checks", "eff", "exact_feasible", "freed_by")}, sort_keys=True)
               for s in r["settings_ge3_list"] if s["exact_feasible"]}
        old = {json.dumps({k: (list(v) if isinstance(v, (list, tuple)) else v) for k, v in s.items()
                           if k not in ("checks", "eff")}, sort_keys=True) for s in a["feasible_list"]}
        row = {"tested_equal": norm(r["tested_by_checks"]) == norm(a["tested_by_checks"]),
               "feasible_equal": norm(r["exact_feasible_by_checks"]) == norm(a["feasible_by_checks"]),
               "list_equal": new == old, "feasible_ge3": r["exact_ge3"], "archive_feasible_ge3": a["feasible_ge_3_checks"]}
        ok &= row["tested_equal"] and row["feasible_equal"] and row["list_equal"]
        out[f"{rid}:{fam}"] = row
Path(sys.argv[1]).write_text(json.dumps({"all_agree": ok, "comparison": out}, indent=1) + "\n")
print("all_agree", ok, {k: v for k, v in out.items() if not (v["tested_equal"] and v["feasible_equal"] and v["list_equal"])})
