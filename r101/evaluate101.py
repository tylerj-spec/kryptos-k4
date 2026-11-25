#!/usr/bin/env python3
"""R101 decision (PREREGISTRATION section 5), from the frozen aggregates only. Run after k4/FROZEN.sha256 is pushed.
Usage: python3 -I r101/evaluate101.py r101/k4/AGGREGATES.json OUT.json"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    for line in (HERE / "k4/FROZEN.sha256").read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise SystemExit(f"REFUSED: frozen file changed: {name}")
    agg = json.loads(src.read_text())
    rows = agg["inputs"]
    assert rows[0]["id"] == "K4" and len(rows) == 21
    count = lambda r, s: sum(c["status"] == s for c in r["cells"])  # noqa: E731
    k4 = rows[0]
    kf, ku = count(k4, "FEASIBLE"), count(k4, "UNDECIDED")
    sf = [count(r, "FEASIBLE") for r in rows[1:]]
    if kf == 0 and ku == 0:
        decision = "EXCLUDED"
    elif kf == 0:
        decision = "EXCLUDED_WHERE_DECIDED"
    elif all(x < kf for x in sf):
        decision = "LEAD"
    else:
        decision = "CHANCE"
    res = {"decision": decision, "k4_feasible_cells": kf, "k4_undecided_cells": ku,
           "k4_cells": [{k: c[k] for k in ("L", "s1", "s2", "links", "d13", "status")} for c in k4["cells"]],
           "shuffles": {"n": len(sf), "with_feasible": sum(x > 0 for x in sf), "max_feasible_cells": max(sf),
                        "total_feasible_cells": sum(sf),
                        "undecided_cells": sum(count(r, "UNDECIDED") for r in rows[1:])},
           "aggregates_sha256": hashlib.sha256(src.read_bytes()).hexdigest()}
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(decision, json.dumps({k: v for k, v in res.items() if k not in ("k4_cells", "aggregates_sha256")}))


if __name__ == "__main__":
    main()
