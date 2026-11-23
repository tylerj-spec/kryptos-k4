#!/usr/bin/env python3
"""R96: write r96/inputs/CONDITIONS.tsv from the spent R94 panel. One row per (case, condition): id, condition
(trueV = V supplied, U searched; trueU = U supplied, V searched), label, ciphertext, the supplied INVERSE wiring.
No plaintext and no searched wiring is written. Run before any solver code. Usage: python3 -I r96/make_conditions.py"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def inverse(W):
    inv = [0] * 26
    for x, y in enumerate(W):
        inv[y] = x
    return inv


def main():
    panel = (ROOT / "r94/inputs/PANEL.tsv").read_bytes()
    truth_raw = (ROOT / "r94/inputs/PANEL_TRUTH.json").read_bytes()
    assert hashlib.sha256(panel).hexdigest() == "9b3ed6b49d437d4289f2a1126dd79b61ed7158b0e35b408bb39b1409aab8786c"
    assert hashlib.sha256(truth_raw).hexdigest() == "27aecaf0aa2050e12d0d05e6c2ccc84b0598acd170e3e47f8667718732cf6ebf"
    truth = json.loads(truth_raw)
    rows = ["id\tcondition\tlabel\tciphertext\tsupplied_inverse_wiring"]
    for line in panel.decode().splitlines()[1:]:
        rid, lab, ct = line.split("\t")
        t = truth[rid]
        assert t["ct"] == ct and ",".join(map(str, t["label"])) == lab
        rows.append(f"{rid}\ttrueV\t{lab}\t{ct}\t{','.join(map(str, inverse(t['W2'])))}")
        rows.append(f"{rid}\ttrueU\t{lab}\t{ct}\t{','.join(map(str, inverse(t['W1'])))}")
    (ROOT / "r96/inputs/CONDITIONS.tsv").write_text("\n".join(rows) + "\n")
    print(len(rows) - 1, "conditions")


if __name__ == "__main__":
    main()
