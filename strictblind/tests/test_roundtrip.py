#!/usr/bin/env python3
"""Round-trip test (about 1 minute): plants hidden messages under random settings of two key kinds, runs the full
blind experiment, freezes, reveals; every plant must come back rank 1 and every frozen row must re-encrypt. Also runs
the whole-family counter on a small K4 run and checks its setting count."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SB = Path(__file__).resolve().parents[1]
REPO = SB.parent
py = [sys.executable, "-I"]
with tempfile.TemporaryDirectory() as td:
    exp = Path(td)
    subprocess.run(py + [str(SB / "blind/routes.py"), "r27", str(exp / "routes.txt")], check=True, capture_output=True)
    shutil.copy(REPO / "k4kit/data/k1k3_plaintext.txt", exp / "k1k3.txt")
    (exp / "k4.txt").write_text("OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR\n")
    runs = [{"tag": "K4_CHAIN3", "ct": "k4.txt", "routes": "routes.txt", "key": ["CHAIN", "3"], "label": "CHAIN3"}]
    for i in range(6):
        key = ["CHAIN", "3"] if i % 2 else ["TEXT", "k1k3.txt"]
        tag = f"PLANT_{i}"
        subprocess.run(py + [str(SB / "sealed/make_plants.py"), str(exp), tag, "routes.txt", key[0], key[1], str(i), str(900 + i)],
                       check=True, capture_output=True)
        runs.append({"tag": tag, "ct": f"{tag}_ct.txt", "routes": "routes.txt", "key": key, "label": key[0]})
    (exp / "manifest.json").write_text(json.dumps({"runs": runs}, indent=1))
    subprocess.run(py + [str(SB / "blind/experiment.py"), str(exp)], check=True, capture_output=True)
    subprocess.run(py + [str(SB / "sealed/reveal.py"), str(exp)], check=True, capture_output=True)
    rep = json.loads((exp / "REVEAL.json").read_text())
    ranks = [e["truth_rank"] for e in rep if e["kind"] == "PLANT"]
    wf = subprocess.run(py + [str(SB / "sealed/whole_family.py"), str(exp)], check=True, capture_output=True, text=True)
    tot = json.loads((exp / "WHOLE_FAMILY.json").read_text())["K4_CHAIN3"]["settings"]
    ok = ranks == [1] * 6 and tot == 41 * 1000 * 12
    print(f"plants ranked {ranks}; K4 whole-family settings {tot:,} (expected 492,000)")
    print("ROUNDTRIP OK" if ok else "ROUNDTRIP FAILED")
    sys.exit(0 if ok else 1)
