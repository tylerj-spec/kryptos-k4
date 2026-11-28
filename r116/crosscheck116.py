#!/usr/bin/env python3
"""R116 post-freeze cross-check (PREREGISTRATION section 4): the reference r115/ref115.py recomputes all 702 K4
verdicts at L 1-2 (with drops) and the structured L 3-4 verdicts from the frozen inputs and the published letters, and
checks 300 random L 3 vectors on K4 against a fresh X115 call.
Usage: python3 -I r116/crosscheck116.py OUT.json"""
import ast
import hashlib
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(ROOT / "r115")]
import x115 as X  # noqa: E402
import ref115 as RF  # noqa: E402

CLUE_SHA = "63121ceaddaa577427dec10d169975a96b6c21c9e4f344ccc7d4c4064650425b"
SEED = 1160902


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
    agg = json.loads((HERE / "k4/AGGREGATES.json").read_text())
    frozen = dict(agg["K4_cells_L1_L2"])
    frozen.update(agg["K4_structured_L3_L4"])
    dis = []
    for cell, v in frozen.items():
        a = tuple(int(t) for t in cell.split(","))
        ref = RF.verdict(ct, obs, a, allow_drop=True)
        if ref != v:
            dis.append({"vector": cell, "frozen": v, "reference": ref})
    rng = random.Random(SEED)
    C = X.Checker(ct, obs)
    dis3 = []
    for _ in range(300):
        a = tuple(rng.randrange(26) for _ in range(3))
        v1, v2 = C.verdict(a, allow_drop=True), RF.verdict(ct, obs, a, allow_drop=True)
        if v1 != v2:
            dis3.append({"vector": list(a), "x115": v1, "reference": v2})
    res = {"frozen_cells": len(frozen), "disagreements": len(dis), "rows": dis,
           "random_L3_cells": 300, "random_L3_disagreements": len(dis3), "random_L3_rows": dis3,
           "agree": not dis and not dis3}
    out.write_text(json.dumps(res, indent=1) + "\n")
    print("cross-check", "AGREE" if res["agree"] else "DISAGREE", len(frozen), "frozen cells,", len(dis), "+",
          len(dis3), "disagreements")


if __name__ == "__main__":
    main()
