#!/usr/bin/env python3
"""R119 post-freeze cross-check (PREREGISTRATION section 4): the brute-force reference r112/ref112.py recomputes 312
K4 route cells drawn at random (seed 1190902; 12 per route), exact verdict plus the drop verdict where excluded, from
the frozen aggregates, the routes and the published letters; 3 worker processes.
Usage: python3 -I r119/crosscheck119.py OUT.json"""
import ast
import hashlib
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "r117"), str(ROOT / "r112"), str(ROOT / "r98")]
import routes119 as RT  # noqa: E402
import crosscheck117 as XC  # noqa: E402

CT_SHA = "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
CLUE_SHA = "63121ceaddaa577427dec10d169975a96b6c21c9e4f344ccc7d4c4064650425b"
SEED, PER_ROUTE, WORKERS = 1190902, 12, 3


def main():
    import multiprocessing as mp
    out = Path(sys.argv[1])
    for line in (HERE / "k4/FROZEN.sha256").read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise SystemExit(f"REFUSED: frozen file changed: {name}")
    raw = (ROOT / "r39/ic_gate/k4_ciphertext.txt").read_bytes()
    if hashlib.sha256(raw).hexdigest() != CT_SHA:
        raise SystemExit("REFUSED: ciphertext changed")
    ct = raw.decode("ascii").strip()
    path = ROOT / "r73/sealed/reveal_k4.py"
    if hashlib.sha256(path.read_bytes()).hexdigest() != CLUE_SHA:
        raise SystemExit("REFUSED: clue source changed")
    clues = [ast.literal_eval(n.value) for n in ast.parse(path.read_text()).body
             if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "CLUES" for t in n.targets)][0]
    obs = {s + i: ch for s, text in clues for i, ch in enumerate(text)}
    hyp = [obs.get(i) for i in range(97)]
    agg = json.loads((HERE / "k4/AGGREGATES.json").read_text())
    perms = {r["name"]: r["perm"] for r in RT.routes()}
    rng = random.Random(SEED)
    jobs, want = [], {}
    for r in agg["routes"]:
        xs = RT.unroute(ct, perms[r["route"]])
        for cell in rng.sample(sorted(r["cells"]), PER_ROUTE):
            jobs.append((cell, xs, hyp))
            want[(r["route"], cell)] = r["cells"][cell]
    keys = list(want)
    with mp.get_context("fork").Pool(WORKERS) as pool:
        got = [v for _, v in pool.imap(XC.ref_verdict, jobs)]
    dis = [{"route": k[0], "cell": k[1], "frozen": want[k], "reference": g} for k, g in zip(keys, got) if want[k] != g]
    res = {"cells": len(jobs), "disagreements": len(dis), "rows": dis, "agree": not dis}
    out.write_text(json.dumps(res, indent=1) + "\n")
    print("cross-check", "AGREE" if not dis else "DISAGREE", len(jobs), "cells", len(dis), "disagreements")


if __name__ == "__main__":
    main()
