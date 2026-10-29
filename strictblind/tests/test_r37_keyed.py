#!/usr/bin/env python3
"""R37: explicit PAL/ABS positive controls + whole-family and compatibility checks."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SB = ROOT / "strictblind"
PY = [sys.executable, "-I"]
sys.path.insert(0, str(SB / "sealed"))
from common import ALPHABETS, encrypt, make_key  # noqa: E402

assert sorted(ALPHABETS["PAL"]) == sorted(ALPHABETS["ABS"]) == list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
assert ALPHABETS["PAL"] == "PALIMSETBCDFGHJKNOQRUVWXYZ"
assert ALPHABETS["ABS"] == "ABSCIDEFGHJKLMNOPQRTUVWXYZ"
with tempfile.TemporaryDirectory() as td:
    exp = Path(td)
    (exp / "routes.txt").write_text("ID ID " + ",".join(map(str, range(97))) + "\n")
    (exp / "ct.txt").write_bytes((ROOT / "k4kit/r32/runs/k4_ciphertext.txt").read_bytes())
    texts = json.loads((ROOT / "r35/controls.json").read_text())["texts"]
    runs = [{"tag": "K4", "ct": "ct.txt", "routes": "routes.txt",
             "key": ["CHAINALPH", "5,3"], "label": "TEST5"}]
    planted = [
        ("P5", 2, "5,3", "primer231", "PAL", "ABS", "BEAU"),
        ("P12", 3, "12,3", "primerA72", "ABS", "PAL", "VARB")
    ]
    for tag, idx, spec, primer, pa, ca, op in planted:
        plain = "".join(c for c in texts[idx].upper() if "A" <= c <= "Z")[:97]
        assert len(plain) == 97 and "EASTNORTHEAST" not in plain and "BERLINCLOCK" not in plain
        key = make_key("CHAINALPH", spec, primer)
        ct = encrypt(plain, list(range(97)), "ID", key, ALPHABETS[pa], ALPHABETS[ca], op)
        (exp / f"{tag}_ct.txt").write_text(ct + "\n")
        runs.append({"tag": tag, "ct": f"{tag}_ct.txt", "routes": "routes.txt",
                     "key": ["CHAINALPH", spec], "label": tag})
        (exp / "sealed").mkdir(exist_ok=True)
        tf = exp / "sealed/truth.json"
        truth = json.loads(tf.read_text()) if tf.exists() else {}
        truth[tag] = {"plaintext": plain, "route": "ID", "order": "ID", "key": primer,
                      "PA": pa, "CA": ca, "OP": op, "ciphertext": ct}
        tf.write_text(json.dumps(truth) + "\n")
    (exp / "manifest.json").write_text(json.dumps({"workers": 2, "runs": runs}))
    subprocess.run(PY + [str(SB / "blind/experiment.py"), str(exp)], check=True, capture_output=True)
    subprocess.run(PY + [str(SB / "sealed/reveal.py"), str(exp)], check=True, capture_output=True)
    subprocess.run(PY + [str(SB / "sealed/whole_family.py"), str(exp)], check=True, capture_output=True)
    rows = {r["tag"]: r for r in json.loads((exp / "REVEAL.json").read_text())}
    for tag, *_ in planted:
        assert rows[tag]["truth_rank"] == 1, rows[tag]
    settings = json.loads((exp / "WHOLE_FAMILY.json").read_text())["K4"]["settings"]
    assert settings == 5 ** 3 * 48, f"expected {5**3*48}, got {settings}"
    print("R37 KEYED OK: PAL/ABS controls rank 1, all 48 conventions independently counted")
