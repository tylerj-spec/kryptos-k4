#!/usr/bin/env python3
"""R70 SEALED exhaustive block check (after the K4 freeze). Runs exact_scan on K4 and on the same 50 nulls.
EXCL(source): no (offset, row, convention) reproduces either published block exactly (13/13 or 11/11) on K4.
Null ciphertexts show how often a full block appears by chance (expected ~0: 26^-11 x 2.5e8 settings ~ 7e-8).
Usage: exact.py TARGET.tsv NORM_DIR EXACT_BINARY REPORT.json"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ("BERLIN_1912", "EGYPT_1908", "MURRAY_1907", "COOK_1876", "BUDGE_1898")


def main():
    tsv, norm, binary, rep = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
    cts = dict(l.split("\t") for l in tsv.read_text().splitlines()[1:] if l)
    res = {}
    with tempfile.TemporaryDirectory() as td:
        for rid, ct in cts.items():
            o = Path(td) / f"{rid}.json"
            subprocess.run([str(binary), str(ROOT / "r61/routes.txt"), ct, str(o)] +
                           [f"{k}={norm / (k + '.txt')}" for k in SOURCES], check=True)
            res[rid] = json.loads(o.read_text())["sources"]
    k4 = res["K4"]
    nulls = [i for i in res if i != "K4"]
    out = {"K4": k4,
           "EXCL": {s: k4[s]["full_block1"] == 0 and k4[s]["full_block2"] == 0 for s in SOURCES},
           "nulls": {s: {"max_hits_sorted": sorted(res[i][s]["max_hits"] for i in nulls),
                         "with_any_full_block": sum(res[i][s]["full_block1"] + res[i][s]["full_block2"] > 0 for i in nulls)}
                     for s in SOURCES}}
    rep.write_text(json.dumps(out, indent=1) + "\n")
    for s in SOURCES:
        print(s, "K4 max hits", k4[s]["max_hits"], "full blocks", k4[s]["full_block1"], k4[s]["full_block2"],
              "EXCL" if out["EXCL"][s] else "FEASIBLE BLOCK", "| nulls max hits median/max",
              out["nulls"][s]["max_hits_sorted"][len(nulls) // 2], out["nulls"][s]["max_hits_sorted"][-1],
              "| nulls with a full block", out["nulls"][s]["with_any_full_block"])


if __name__ == "__main__":
    main()
