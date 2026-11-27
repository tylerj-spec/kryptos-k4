#!/usr/bin/env python3
"""R111 decision (PREREGISTRATION section 4), from the frozen outputs only; reads no published plaintext.
Usage: python3 -I r111/evaluate111.py OUT.json"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BAR = -440.0


def main():
    out = Path(sys.argv[1])
    for line in (HERE / "k4/FROZEN.sha256").read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise SystemExit(f"REFUSED: frozen file changed: {name}")
    cand = json.loads((HERE / "k4/CANDIDATES.json").read_text())["K4"]
    nulls = json.loads((HERE / "k4/NULLS.json").read_text())["nulls"]
    T, nT = cand["T"], [n["T"] for n in nulls]
    above_all = T > max(nT)
    decision = "CANDIDATE" if (above_all and T >= BAR) else "NO_SIGNAL"
    top = max(cand["cells"], key=lambda r: r["score"])
    res = {"decision": decision, "K4_T": T, "bar": BAR, "null_T": sorted(nT), "null_max_T": max(nT),
           "nulls_at_or_above_K4": sum(t >= T for t in nT), "K4_above_every_null": above_all,
           "K4_top_cell": [top["B"], top["L"], top["sigma"]],
           "K4_cell_scores": {f"{r['B']}_L{r['L']}_sig{r['sigma']:+d}": r["score"] for r in cand["cells"]},
           "reencryption_all": all(r["reencrypts"] for r in cand["cells"]) and all(n["reencrypt_all"] for n in nulls)}
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(decision, "K4 T", T, "null max", max(nT), "top cell", res["K4_top_cell"])


if __name__ == "__main__":
    main()
