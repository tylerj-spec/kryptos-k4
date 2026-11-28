#!/usr/bin/env python3
"""R117 decision (PREREGISTRATION section 4), from the frozen aggregates only, with the comparison against R108's
frozen K4 verdicts. Usage: python3 -I r117/evaluate117.py OUT.json"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
R108_MAP = {"EXCLUDED_DROP": "EXCL_DROP", "EXCLUDED_EXACT": "EXCL", "OPEN": "OPEN"}


def main():
    out = Path(sys.argv[1])
    frozen = {}
    for line in (HERE / "k4/FROZEN.sha256").read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        frozen[name] = digest
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise SystemExit(f"REFUSED: frozen file changed: {name}")
    if "r117/k4/AGGREGATES.json" not in frozen:
        raise SystemExit("REFUSED: aggregates are not frozen")
    agg = json.loads((HERE / "k4/AGGREGATES.json").read_text())
    k4, shuf = agg["inputs"][0], agg["inputs"][1:]
    assert k4["id"] == "K4" and len(shuf) == 200
    k4_open = k4["totals"]["OPEN"]
    sh_open = [s["totals"]["OPEN"] for s in shuf]
    cells = agg["K4_cells"]
    by_p = {}
    for c, v in cells.items():
        d = by_p.setdefault(c.split("|p=")[1], dict.fromkeys(("EXCL_DROP", "EXCL", "OPEN"), 0))
        d[v] += 1
    sh_share = {p: {v: round(sum(s["by_key_structure"][p][v] for s in shuf) / (16 * len(shuf)), 4)
                    for v in ("EXCL_DROP", "EXCL", "OPEN")} for p in by_p}
    r108 = json.loads((ROOT / "r108/k4/AGGREGATES.json").read_text())["K4_cells"]
    trans = {}
    for c, v in cells.items():
        key = f"R108 {R108_MAP[r108[c]]} -> R117 {v}"
        trans[key] = trans.get(key, 0) + 1
    fam = ("EXCLUDED_DROP" if all(v == "EXCL_DROP" for v in cells.values()) else
           "EXCLUDED_EXACT" if all(v != "OPEN" for v in cells.values()) else "PARTIAL")
    res = {"family_verdict": fam, "lead_flag": k4_open > max(sh_open), "K4_totals": k4["totals"],
           "shuffle_open": {"min": min(sh_open), "median": sorted(sh_open)[len(sh_open) // 2], "max": max(sh_open),
                            "at_or_above_K4": sum(x >= k4_open for x in sh_open)},
           "K4_by_key_structure": by_p, "shuffle_mean_share_by_key_structure": sh_share,
           "R108_to_R117_transitions": dict(sorted(trans.items())),
           "R108_excluded_now_open": sorted(c for c, v in cells.items() if v == "OPEN" and r108[c] != "OPEN"),
           "K4_EXCL_EXACT_ONLY_cells": sorted(c for c, v in cells.items() if v == "EXCL"),
           "K4_OPEN_cells": sorted(c for c, v in cells.items() if v == "OPEN"),
           "aggregates_sha256": frozen["r117/k4/AGGREGATES.json"]}
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(fam, "lead", res["lead_flag"], "K4", k4["totals"], "shuffle OPEN", res["shuffle_open"], json.dumps(trans))


if __name__ == "__main__":
    main()
