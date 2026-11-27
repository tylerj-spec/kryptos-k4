#!/usr/bin/env python3
"""R111 post-freeze clue check (PREREGISTRATION section 5). Runs only after k4/FROZEN.sha256 and k4/EVALUATION.json are
committed. Counts agreement of each frozen K4 cell output with the 24 published letters; changes nothing upstream.
Usage: python3 -I r111/cluecheck111.py OUT.json"""
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CLUE_SHA = "63121ceaddaa577427dec10d169975a96b6c21c9e4f344ccc7d4c4064650425b"


def need(cond, msg):
    if not cond:
        raise SystemExit("REFUSED: " + msg)


def main():
    out = Path(sys.argv[1])
    for rel in ("r111/k4/FROZEN.sha256", "r111/k4/EVALUATION.json"):
        got = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT, capture_output=True)
        need(got.returncode == 0 and got.stdout == (ROOT / rel).read_bytes(), f"{rel} is not committed as on disk")
    for line in (HERE / "k4/FROZEN.sha256").read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        need(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, f"frozen file changed: {name}")
    path = ROOT / "r73/sealed/reveal_k4.py"
    need(hashlib.sha256(path.read_bytes()).hexdigest() == CLUE_SHA, "published observation source changed")
    found = [ast.literal_eval(n.value) for n in ast.parse(path.read_text()).body
             if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "CLUES" for t in n.targets)]
    need(len(found) == 1, "expected one CLUES literal")
    obs = {s + i: ch for s, text in found[0] for i, ch in enumerate(text)}
    need(len(obs) == 24, "expected 24 published letters")
    ev = json.loads((HERE / "k4/EVALUATION.json").read_text())
    cand = json.loads((HERE / "k4/CANDIDATES.json").read_text())["K4"]
    rows = []
    for r in cand["cells"]:
        rows.append({"cell": [r["B"], r["L"], r["sigma"]], "score": r["score"],
                     "agreement": sum(r["plaintext"][p] == ch for p, ch in obs.items())})
    top = max(rows, key=lambda r: r["score"])
    label = None
    if ev["decision"] == "CANDIDATE":
        label = "VERIFIED_CANDIDATE" if top["agreement"] >= 18 else "FALSE_CANDIDATE"
    res = {"decision": ev["decision"], "label": label, "top_cell": top, "max_agreement_any_cell": max(r["agreement"] for r in rows),
           "expected_by_chance_per_cell": round(24 / 26, 3), "cells": rows}
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(ev["decision"], label, "top-cell agreement", top["agreement"], "/24; max any cell", res["max_agreement_any_cell"])


if __name__ == "__main__":
    main()
