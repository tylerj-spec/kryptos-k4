#!/usr/bin/env python3
"""R117 post-freeze cross-check (PREREGISTRATION section 4): the brute-force reference r112/ref112.py recomputes every
K4 cell's exact verdict, and the DROP verdict of every cell it finds excluded, from the frozen inputs and the published
letters; 3 worker processes. Usage: python3 -I r117/crosscheck117.py OUT.json"""
import ast
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(ROOT / "r112"), str(ROOT / "r98")]
import ref112 as RF  # noqa: E402

CLUE_SHA = "63121ceaddaa577427dec10d169975a96b6c21c9e4f344ccc7d4c4064650425b"
WORKERS = 3


def ref_verdict(job):
    cell, ct, hyp = job
    conv_s, p_s = cell.split("|p=")
    t, r, o, a = conv_s.split("_")
    conv = (t, int(r), int(o), int(a))
    p = None if p_s == "any" else int(p_s)
    if RF.check(ct, hyp, conv, p) == "OPEN":
        return cell, "OPEN"
    return cell, "EXCL_DROP" if RF.check(ct, hyp, conv, p, allow_drop=True) == "EXCL" else "EXCL"


def main():
    import multiprocessing as mp
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
    jobs = [(cell, ct, hyp) for cell in sorted(frozen)]
    with mp.get_context("fork").Pool(WORKERS) as pool:
        ref = dict(pool.imap(ref_verdict, jobs))
    dis = [{"cell": c, "frozen": frozen[c], "reference": ref[c]} for c in sorted(frozen) if ref[c] != frozen[c]]
    res = {"cells": len(frozen), "disagreements": len(dis), "rows": dis, "agree": not dis}
    out.write_text(json.dumps(res, indent=1) + "\n")
    print("cross-check", "AGREE" if not dis else "DISAGREE", len(frozen), "cells", len(dis), "disagreements")


if __name__ == "__main__":
    main()
