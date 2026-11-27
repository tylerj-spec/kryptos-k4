#!/usr/bin/env python3
"""R110 decision (PREREGISTRATION section 3), from the frozen statistics only.
Usage: python3 -I r110/evaluate110.py OUT.json"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def main():
    out = Path(sys.argv[1])
    for line in (HERE / "k4/FROZEN.sha256").read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise SystemExit(f"REFUSED: frozen file changed: {name}")
    st = json.loads((HERE / "k4/STATISTICS.json").read_text())
    p = {int(k): v for k, v in st["p_one_sided"].items()}
    explo = {L: v for L, v in p.items() if L >= 2}
    Lmin = min(explo, key=explo.get)
    res = {"decision": "SIGNAL_L1" if p[1] < 0.05 else "NO_SIGNAL", "R1_K4": st["R_K4"]["1"],
           "R1_shuffle_mean": st["shuffle_mean"]["1"], "p1": p[1],
           "exploratory": {"min_p_lag": Lmin, "min_p": explo[Lmin], "bonferroni_23": min(1.0, explo[Lmin] * 23),
                           "bonferroni_24_all_lags": min(1.0, min(p.values()) * 24)},
           "R_K4": st["R_K4"], "shuffle_mean": st["shuffle_mean"], "p_one_sided": st["p_one_sided"]}
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(res["decision"], "p1", p[1], "R1", res["R1_K4"], "vs mean", res["R1_shuffle_mean"], res["exploratory"])


if __name__ == "__main__":
    main()
