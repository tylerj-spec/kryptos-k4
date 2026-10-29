#!/usr/bin/env python3
"""R38 ACA-Gromark construction: published ENIGMA vector + two independent 97-letter plant gates."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SB = ROOT / "strictblind"
PY = [sys.executable, "-I"]
sys.path.insert(0, str(ROOT / "r38"))
from aca_alphabet import aca_alphabet  # noqa: E402
sys.path.insert(0, str(SB / "sealed"))
from common import ALPHABETS_ACA, encrypt, make_key  # noqa: E402

assert aca_alphabet("ENIGMA") == "AJRXEBKSYGFPVIDOUMHQWNCLTZ"
for name, keyword in {"KRY": "KRYPTOS", "PAL": "PALIMPSEST", "ABS": "ABSCISSA"}.items():
    assert aca_alphabet(keyword) == ALPHABETS_ACA[name], name
# Independent published ACA 35-letter encryption vector, not a K4 excerpt.
plain = "THEREAREUPTOTENSUBSTITUTESPERLETTER"
expected = "NFYCKBTIJCNWZYCACJNAYNLQPWWSTWPJQFL"
key = [2, 3, 4, 5, 2]
for i in range(5, len(plain)):
    key.append((key[i - 5] + key[i - 4]) % 10)
ct = "".join(aca_alphabet("ENIGMA")[("ABCDEFGHIJKLMNOPQRSTUVWXYZ".index(ch) + key[i]) % 26]
             for i, ch in enumerate(plain))
assert ct == expected, f"ACA example failed: {ct}"
with tempfile.TemporaryDirectory() as td:
    exp = Path(td)
    (exp / "routes.txt").write_text("ID ID " + ",".join(map(str, range(97))) + "\n")
    (exp / "ct.txt").write_bytes((ROOT / "k4kit/r32/runs/k4_ciphertext.txt").read_bytes())
    passages = json.loads((ROOT / "r35/controls.json").read_text())["texts"]
    runs = [{"tag": "K4", "ct": "ct.txt", "routes": "routes.txt",
             "key": ["CHAINACA", "5,3"], "label": "ACA5"}]
    for name, idx, base, primer, pa, ca, op in [
        ("PLANT_A", 0, "5,3", "primer123", "PAL", "ABS", "VARB"),
        ("PLANT_B", 1, "12,3", "primerA72", "ABS", "KRY", "BEAU")
    ]:
        msg = "".join(c for c in passages[idx].upper() if "A" <= c <= "Z")[:97]
        assert len(msg) == 97 and "EASTNORTHEAST" not in msg and "BERLINCLOCK" not in msg
        out = encrypt(msg, list(range(97)), "ID", make_key("CHAINACA", base, primer),
                      ALPHABETS_ACA[pa], ALPHABETS_ACA[ca], op)
        (exp / f"{name}_ct.txt").write_text(out + "\n")
        (exp / "sealed").mkdir(exist_ok=True)
        truth_file = exp / "sealed/truth.json"
        truth = json.loads(truth_file.read_text()) if truth_file.exists() else {}
        truth[name] = {"plaintext": msg, "route": "ID", "order": "ID", "key": primer,
                       "PA": pa, "CA": ca, "OP": op, "ciphertext": out}
        truth_file.write_text(json.dumps(truth) + "\n")
        runs.append({"tag": name, "ct": f"{name}_ct.txt", "routes": "routes.txt",
                     "key": ["CHAINACA", base], "label": name})
    (exp / "manifest.json").write_text(json.dumps({"workers": 2, "runs": runs}))
    subprocess.run(PY + [str(SB / "blind/experiment.py"), str(exp)], check=True, capture_output=True)
    subprocess.run(PY + [str(SB / "sealed/reveal.py"), str(exp)], check=True, capture_output=True)
    subprocess.run(PY + [str(SB / "sealed/whole_family.py"), str(exp)], check=True, capture_output=True)
    rows = {r["tag"]: r for r in json.loads((exp / "REVEAL.json").read_text())}
    assert rows["PLANT_A"]["truth_rank"] == rows["PLANT_B"]["truth_rank"] == 1
    settings = json.loads((exp / "WHOLE_FAMILY.json").read_text())["K4"]["settings"]
    assert settings == 5 ** 3 * 48
    print("R38 ACA OK: ENIGMA published vector exact; PAL/ABS plants #1; 48-convention family complete")
