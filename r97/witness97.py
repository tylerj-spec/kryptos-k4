#!/usr/bin/env python3
"""R97 forward witness (standard library; separately coded): every retained final's text, enciphered with the
forward wirings of its (U, V), must equal the ciphertext of r94/inputs/PANEL.tsv.
Usage: witness97.py PANEL.tsv RESULTS.jsonl OUT.json"""
import json
import sys
from pathlib import Path

LET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def numbering(word):
    out = []
    for ch in word + LET:
        if ch not in out:
            out.append(ch)
    return out


NUM = {"AZ": list(LET), "KRY": numbering("KRYPTOS"), "PAL": numbering("PALIMPSEST"), "ABS": numbering("ABSCISSA")}


def encipher(text, W1, W2, lab):
    ein, eout, n, r, h, d1, d2 = lab
    res = ""
    for i, ch in enumerate(text):
        t = (i + r) // n
        f, s = (d1 * t) % 26, (d2 * ((t + h) // 26)) % 26
        mid = (W1[(NUM[ein].index(ch) + f) % 26] - f) % 26
        res += NUM[eout][(W2[(mid + s) % 26] - s) % 26]
    return res


def invert(p):
    q = [0] * 26
    for x, y in enumerate(p):
        q[y] = x
    return q


def main():
    cts = {l.split("\t")[0]: l.split("\t")[2] for l in Path(sys.argv[1]).read_text().splitlines()[1:]}
    n = bad = 0
    for line in Path(sys.argv[2]).read_text().splitlines():
        r = json.loads(line)
        for f in r["finals"]:
            assert sorted(f["U"]) == list(range(26)) and sorted(f["V"]) == list(range(26))
            n += 1
            bad += encipher(f["text"], invert(f["U"]), invert(f["V"]), r["label"]) != cts[r["id"]]
    rep = {"finals": n, "failures": bad, "passed": bad == 0 and n > 0}
    Path(sys.argv[3]).write_text(json.dumps(rep, indent=1) + "\n")
    print("witness", "PASSED" if rep["passed"] else "FAILED", n, bad)
    sys.exit(0 if rep["passed"] else 1)


if __name__ == "__main__":
    main()
