#!/usr/bin/env python3
"""R108 post-freeze cross-check (PREREGISTRATION section 4): the rank reference (r107/ref107.py) recomputes all 768 K4
cells from the frozen inputs and the published letters, and is compared with the frozen verdicts.
Usage: python3 -I r108/crosscheck108.py OUT.json"""
import ast
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(ROOT / "r107"), str(ROOT / "r98")]
import slidefair98 as SF  # noqa: E402
import x107 as X  # noqa: E402
import ref107 as RF  # noqa: E402

CLUE_SHA = "63121ceaddaa577427dec10d169975a96b6c21c9e4f344ccc7d4c4064650425b"


def main():
    out = Path(sys.argv[1])
    for line in (HERE / "k4/FROZEN.sha256").read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise SystemExit(f"REFUSED: frozen file changed: {name}")
    ct = [ln.split("\t")[1] for ln in (HERE / "k4/INPUTS.tsv").read_text().splitlines()[1:] if ln.startswith("K4\t")][0]
    path = ROOT / "r73/sealed/reveal_k4.py"
    if hashlib.sha256(path.read_bytes()).hexdigest() != CLUE_SHA:
        raise SystemExit("REFUSED: clue source changed")
    clues = [ast.literal_eval(n.value) for n in ast.parse(path.read_text()).body
             if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "CLUES" for t in n.targets)][0]
    obs = {s + i: ch for s, text in clues for i, ch in enumerate(text)}
    hyp = [obs.get(i) for i in range(97)]
    frozen = json.loads((HERE / "k4/AGGREGATES.json").read_text())["K4_cells"]
    dis = []
    for cell, v in frozen.items():
        conv_s, p_s = cell.split("|p=")
        t, r, o, a = conv_s.split("_")
        conv = (t, int(r), int(o), int(a))
        p = None if p_s == "any" else int(p_s)
        ref = X.check(ct, hyp, conv, p, collision=RF.collision_rank)
        if ref != v:
            dis.append({"cell": cell, "frozen": v, "reference": ref})
    res = {"cells": len(frozen), "disagreements": len(dis), "rows": dis, "agree": not dis}
    out.write_text(json.dumps(res, indent=1) + "\n")
    print("cross-check", "AGREE" if not dis else "DISAGREE", len(frozen), "cells", len(dis), "disagreements")


if __name__ == "__main__":
    main()
