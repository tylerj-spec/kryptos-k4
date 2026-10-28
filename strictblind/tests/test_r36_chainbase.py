#!/usr/bin/env python3
"""R36 controls: base10-equivalence and arbitrary-base planted recovery (no K4 clues in search)."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SB = ROOT / "strictblind"
PY = [sys.executable, "-I"]
with tempfile.TemporaryDirectory() as td:
    e = Path(td)
    route = e / "routes.txt"
    route.write_text("ID ID " + ",".join(map(str, range(97))) + "\n")
    quad = ROOT / "k4kit/data/quad_log10.f32"
    shutil.copy(ROOT / "k4kit/r32/runs/k4_ciphertext.txt", e / "ct.txt")
    scan = e / "scan"
    subprocess.run(["g++", "-std=c++17", "-O3", str(SB / "blind/scan.cpp"), "-o", str(scan)], check=True)
    for kind, arg, out in [("CHAIN", "3", "old"), ("CHAINBASE", "10,3", "new")]:
        subprocess.run([str(scan), kind, arg, "REG", str(e / "ct.txt"), str(quad), str(route), "0", "1",
                        str(e / (out + ".tsv")), str(e / (out + "_routes.tsv"))],
                       check=True, capture_output=True)
    assert (e / "old.tsv").read_bytes() == (e / "new.tsv").read_bytes(), "base10 top100 diverged"
    assert (e / "old_routes.tsv").read_bytes() == (e / "new_routes.tsv").read_bytes(), "base10 route scores diverged"

    for tag, kind, arg, template, seed in [("P5", "CHAINBASE", "5,3", 2, 36005),
                                            ("P12", "CHAINBASE", "12,3", 3, 36012)]:
        subprocess.run(PY + [str(ROOT / "r35/sealed/make_controls.py"), str(e), tag,
                             "routes.txt", kind, arg, str(template), str(seed)],
                       check=True, capture_output=True)
    man = {"workers": 2, "runs": [
        {"tag": "K4", "ct": "ct.txt", "routes": "routes.txt", "key": ["CHAINBASE", "5,3"], "label": "B5L3"},
        {"tag": "P5", "ct": "P5_ct.txt", "routes": "routes.txt", "key": ["CHAINBASE", "5,3"], "label": "B5L3"},
        {"tag": "P12", "ct": "P12_ct.txt", "routes": "routes.txt", "key": ["CHAINBASE", "12,3"], "label": "B12L3"}
    ]}
    (e / "manifest.json").write_text(json.dumps(man))
    subprocess.run(PY + [str(SB / "blind/experiment.py"), str(e)], check=True, capture_output=True)
    subprocess.run(PY + [str(SB / "sealed/reveal.py"), str(e)], check=True, capture_output=True)
    subprocess.run(PY + [str(SB / "sealed/whole_family.py"), str(e)], check=True, capture_output=True)
    rep = json.loads((e / "REVEAL.json").read_text())
    plants = [x for x in rep if x["kind"] == "PLANT"]
    assert len(plants) == 2 and [x["truth_rank"] for x in plants] == [1, 1], plants
    wf = json.loads((e / "WHOLE_FAMILY.json").read_text())
    assert wf["K4"]["settings"] == 5 ** 3 * 12
    print("R36 CHAINBASE OK: base-10 byte-identical; independent base-5 and base-12 plants rank 1; whole-family exact")
