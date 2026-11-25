#!/usr/bin/env python3
"""R101 post-freeze cross-check: K4's 20 cells re-decided from the FROZEN inputs by the second solver (dfs101: DFS
over ranks mod 26 with forward checking, no field decomposition or enumeration); compared with the frozen primary
statuses. Counts and statuses only. Usage: python3 -I r101/crosscheck101.py OUT.json"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "r99")]
import dfs101 as DF  # noqa: E402
import run_target101 as RT  # noqa: E402

NODE_CAP = 5_000_000


def main():
    out = Path(sys.argv[1])
    for line in (HERE / "k4/FROZEN.sha256").read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    obs = RT.observations()
    name, ct = (HERE / "k4/INPUTS.tsv").read_text().splitlines()[1].split("\t")
    assert name == "K4"
    frozen = json.loads((HERE / "k4/AGGREGATES.json").read_text())["inputs"][0]
    rows, agree, both = [], True, 0
    for c in frozen["cells"]:
        st = DF.solve(ct, obs, c["L"], c["s1"], c["s2"], node_cap=NODE_CAP)
        dec = st in ("FEASIBLE", "INFEASIBLE") and c["status"] in ("FEASIBLE", "INFEASIBLE")
        both += dec
        agree &= (not dec) or st == c["status"]
        rows.append({"L": c["L"], "s1": c["s1"], "s2": c["s2"], "primary": c["status"], "dfs": st})
    out.write_text(json.dumps({"implementation": "dfs101 (second solver)", "node_cap": NODE_CAP, "input": "K4",
                               "both_decided": both, "agree_where_both_decided": agree, "cells": rows}, indent=1)
                   + "\n")
    print("AGREE" if agree else "DISAGREE", both, [r["dfs"] for r in rows])


if __name__ == "__main__":
    main()
