#!/usr/bin/env python3
"""R119 decision (PREREGISTRATION section 4), from the frozen aggregates and R117's frozen shuffle null.
Usage: python3 -I r119/evaluate119.py OUT.json"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def main():
    out = Path(sys.argv[1])
    frozen = {}
    for line in (HERE / "k4/FROZEN.sha256").read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        frozen[name] = digest
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise SystemExit(f"REFUSED: frozen file changed: {name}")
    if "r119/k4/AGGREGATES.json" not in frozen:
        raise SystemExit("REFUSED: aggregates are not frozen")
    agg = json.loads((HERE / "k4/AGGREGATES.json").read_text())
    null = [s["totals"]["OPEN"] for s in json.loads((ROOT / "r117/k4/AGGREGATES.json").read_text())["inputs"][1:]]
    assert len(null) == 200
    nmax = max(null)
    per = {}
    for r in agg["routes"]:
        t, cells = r["totals"], r["cells"]
        fam = ("EXCLUDED_DROP" if t["OPEN"] == 0 and t["EXCL"] == 0 else
               "EXCLUDED_EXACT" if t["OPEN"] == 0 else "PARTIAL")
        per[r["route"]] = {"status": r["status"], "totals": t, "family_verdict": fam,
                           "null_at_or_above": sum(x >= t["OPEN"] for x in null),
                           "lead": t["OPEN"] > nmax,
                           "OPEN_cells": sorted(c for c, v in cells.items() if v == "OPEN")}
    overall = ("EXCLUDED_EXACT" if all(v["family_verdict"] != "PARTIAL" for v in per.values()) else "PARTIAL")
    res = {"overall_verdict": overall, "lead_flag": any(v["lead"] for v in per.values()), "null_max_open": nmax,
           "null_median_open": sorted(null)[100],
           "totals_all_routes": {k: sum(v["totals"][k] for v in per.values()) for k in ("EXCL_DROP", "EXCL", "OPEN")},
           "per_route": per, "aggregates_sha256": frozen["r119/k4/AGGREGATES.json"]}
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(overall, "lead", res["lead_flag"], json.dumps(res["totals_all_routes"]),
          {k: v["totals"]["OPEN"] for k, v in per.items()})


if __name__ == "__main__":
    main()
