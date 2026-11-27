#!/usr/bin/env python3
"""R109 decision (PREREGISTRATION section 4), from the frozen verdicts only.
Usage: python3 -I r109/evaluate109.py OUT.json"""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def main():
    out = Path(sys.argv[1])
    for line in (HERE / "k4/FROZEN.sha256").read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise SystemExit(f"REFUSED: frozen file changed: {name}")
    v = json.loads((HERE / "k4/VERDICTS.json").read_text())
    cells = v["K4_cells"]
    label = {}
    for k, r in cells.items():
        if r["exact"] == "INCONSISTENT":
            label[k] = "EXCL" if r["drop"] else "EXCL_EXACT_ONLY"
        elif r["exact"] == "CONSISTENT":
            label[k] = "OPEN"
        else:
            label[k] = r["exact"]
    dis = sorted(k for k, r in cells.items() if r.get("dfs_crosscheck") == "CONSISTENT")
    k4_inc = v["primary_only_counts"][0]["primary_counts"].get("INCONSISTENT", 0)
    sh_inc = [r["primary_counts"].get("INCONSISTENT", 0) for r in v["primary_only_counts"][1:]]
    by_lag = {}
    for k, lab in label.items():
        L = int(k.split("_")[0][1:])
        by_lag.setdefault(L, Counter())[lab] += 1
    res = {"counts": dict(Counter(label.values())), "dfs_disagreements": dis,
           "dfs_crosscheck_counts": dict(Counter(r["dfs_crosscheck"] for r in cells.values() if "dfs_crosscheck" in r)),
           "lead_flag": k4_inc < min(sh_inc), "K4_primary_inconsistent": k4_inc,
           "shuffle_primary_inconsistent": {"min": min(sh_inc), "median": sorted(sh_inc)[len(sh_inc) // 2],
                                            "max": max(sh_inc), "values": sh_inc},
           "by_lag": {str(L): dict(c) for L, c in sorted(by_lag.items()) if set(c) != {"NO_EQUATIONS"}},
           "EXCL_cells": sorted(k for k, lab in label.items() if lab == "EXCL"),
           "EXCL_EXACT_ONLY_cells": sorted(k for k, lab in label.items() if lab == "EXCL_EXACT_ONLY"),
           "OPEN_cells": sorted(k for k, lab in label.items() if lab == "OPEN"),
           "UNDECIDED_cells": sorted(k for k, lab in label.items() if lab == "UNDECIDED")}
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(res["counts"], "dfs disagreements", len(dis), "lead", res["lead_flag"], "K4 prim INC", k4_inc,
          "shuffles", res["shuffle_primary_inconsistent"]["min"], res["shuffle_primary_inconsistent"]["median"])


if __name__ == "__main__":
    main()
