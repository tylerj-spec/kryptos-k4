#!/usr/bin/env python3
"""R116 decision (PREREGISTRATION section 4), from the frozen aggregates only.
Usage: python3 -I r116/evaluate116.py OUT.json"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
NAMED = {"progressive (1)": "1", "Fibonacci (1,1)": "1,1", "period 2 (0,1)": "0,1", "linear progression (2,25)": "2,25"}


def main():
    out = Path(sys.argv[1])
    frozen = {}
    for line in (HERE / "k4/FROZEN.sha256").read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        frozen[name] = digest
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise SystemExit(f"REFUSED: frozen file changed: {name}")
    if "r116/k4/AGGREGATES.json" not in frozen:
        raise SystemExit("REFUSED: aggregates are not frozen")
    agg = json.loads((HERE / "k4/AGGREGATES.json").read_text())
    k4, shuf = agg["inputs"][0], agg["inputs"][1:]
    assert k4["id"] == "K4" and len(shuf) == 200
    per_order = {}
    for L in ("1", "2", "3", "4"):
        kc = k4["by_order"][L]
        sh = [s["by_order"][L]["OPEN"] for s in shuf if L in s["by_order"]]
        total = sum(kc.values())
        fam = ("EXCLUDED_DROP" if kc["EXCL_DROP"] == total else
               "EXCLUDED_EXACT" if kc["OPEN"] == 0 else "PARTIAL")
        per_order[L] = {"vectors": total, "K4": kc, "family_verdict": fam,
                        "K4_excluded_share": round((kc["EXCL"] + kc["EXCL_DROP"]) / total, 4),
                        "shuffles": len(sh),
                        "shuffle_open": {"min": min(sh), "median": sorted(sh)[len(sh) // 2], "max": max(sh),
                                         "at_or_above_K4": sum(x >= kc["OPEN"] for x in sh)},
                        "shuffle_excluded_share_mean": round(1 - sum(sh) / (len(sh) * total), 4),
                        "lead_flag": kc["OPEN"] > max(sh)}
    cells = agg["K4_cells_L1_L2"]
    opens = {L: sorted(a for a, v in cells.items() if v == "OPEN" and len(a.split(",")) == int(L)) for L in ("1", "2")}
    exact_only = {L: sorted(a for a, v in cells.items() if v == "EXCL" and len(a.split(",")) == int(L)) for L in ("1", "2")}
    res = {"per_order": per_order, "lead_flag_any": any(v["lead_flag"] for v in per_order.values()),
           "K4_OPEN_vectors": opens, "K4_EXCL_EXACT_ONLY_vectors": exact_only,
           "named_keys": {n: cells[a] for n, a in NAMED.items()},
           "structured_L3_L4": agg["K4_structured_L3_L4"],
           "aggregates_sha256": frozen["r116/k4/AGGREGATES.json"]}
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({L: (v["family_verdict"], v["K4"], v["lead_flag"]) for L, v in per_order.items()}))


if __name__ == "__main__":
    main()
