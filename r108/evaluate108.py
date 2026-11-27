#!/usr/bin/env python3
"""R108 decision (PREREGISTRATION section 4), from the frozen aggregates only.
Usage: python3 -I r108/evaluate108.py OUT.json"""
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
    if "r108/k4/AGGREGATES.json" not in frozen:
        raise SystemExit("REFUSED: aggregates are not frozen")
    agg = json.loads((HERE / "k4/AGGREGATES.json").read_text())
    k4, shuf = agg["inputs"][0], agg["inputs"][1:]
    assert k4["id"] == "K4" and len(shuf) == 200
    k4_open = k4["totals"]["OPEN"]
    sh_open = [s["totals"]["OPEN"] for s in shuf]
    lead = k4_open > max(sh_open)
    cells = agg["K4_cells"]
    excl = sorted(c for c, v in cells.items() if v == "EXCLUDED_DROP")
    exact_only = sorted(c for c, v in cells.items() if v == "EXCLUDED_EXACT")
    open_ = sorted(c for c, v in cells.items() if v == "OPEN")
    by_p = {}
    for c, v in cells.items():
        p = c.split("|p=")[1]
        d = by_p.setdefault(p, {"EXCL": 0, "EXCL_EXACT_ONLY": 0, "OPEN": 0})
        d[{"EXCLUDED_DROP": "EXCL", "EXCLUDED_EXACT": "EXCL_EXACT_ONLY", "OPEN": "OPEN"}[v]] += 1
    sh_drop_share = {p: round(sum(s["by_key_structure"][p]["EXCLUDED_DROP"] for s in shuf) / (16 * len(shuf)), 4)
                     for p in by_p}
    res = {"family_verdict": "EXCLUDED" if len(excl) == len(cells) else "PARTIAL",
           "lead_flag": lead, "K4_totals": k4["totals"],
           "shuffle_open": {"min": min(sh_open), "median": sorted(sh_open)[len(sh_open) // 2], "max": max(sh_open),
                            "at_or_above_K4": sum(x >= k4_open for x in sh_open)},
           "K4_by_key_structure": by_p, "shuffle_share_EXCLUDED_DROP_by_key_structure": sh_drop_share,
           "K4_EXCL_cells": excl, "K4_EXCL_EXACT_ONLY_cells": exact_only, "K4_OPEN_cells": open_,
           "aggregates_sha256": frozen["r108/k4/AGGREGATES.json"]}
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(res["family_verdict"], "lead", lead, "K4", k4["totals"], "shuffle OPEN", res["shuffle_open"])


if __name__ == "__main__":
    main()
