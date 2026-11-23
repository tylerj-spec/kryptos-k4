#!/usr/bin/env python3
"""R96 forward witness (standard library; separate code from r96core): every saved state's decode, enciphered with
the searched and supplied inverse wirings (inverted here to forward wirings), must equal the ciphertext.
Usage: witness96.py CONDITIONS.tsv RESULTS.jsonl OUT.json"""
import json
import sys
from pathlib import Path

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def alph(word):
    s = ""
    for ch in word + AZ:
        if ch not in s:
            s += ch
    return s


AL = {"AZ": AZ, "KRY": alph("KRYPTOS"), "PAL": alph("PALIMPSEST"), "ABS": alph("ABSCISSA")}


def enc(pt, W1, W2, ein, eout, n, r, h, d1, d2):
    out = []
    for i, ch in enumerate(pt):
        tau = (i + r) // n
        a, b = (d1 * tau) % 26, (d2 * ((tau + h) // 26)) % 26
        m = (W1[(AL[ein].find(ch) + a) % 26] - a) % 26
        out.append(AL[eout][(W2[(m + b) % 26] - b) % 26])
    return "".join(out)


def forward(inv):
    W = [None] * 26
    for x, y in enumerate(inv):
        W[y] = x
    return W


def main():
    conds = {}
    for line in Path(sys.argv[1]).read_text().splitlines()[1:]:
        rid, cond, lab, ct, sup = line.split("\t")
        conds[(rid, cond)] = (ct, [int(x) for x in sup.split(",")])
    n = bad = 0
    for line in Path(sys.argv[2]).read_text().splitlines():
        r = json.loads(line)
        ct, sup = conds[(r["id"], r["condition"])]
        lab = r["label"]
        for s in r["starts"]:
            Wsearch = s["searched_inverse_wiring"]
            U, V = (Wsearch, sup) if r["searched"] == "U" else (sup, Wsearch)
            assert sorted(U) == list(range(26)) and sorted(V) == list(range(26))
            n += 1
            bad += enc(s["text"], forward(U), forward(V), *lab) != ct
    rep = {"states": n, "failures": bad, "passed": n == 96 * 16 and bad == 0}
    Path(sys.argv[3]).write_text(json.dumps(rep, indent=1) + "\n")
    print("witness", "PASSED" if rep["passed"] else "FAILED", n, bad)
    sys.exit(0 if rep["passed"] else 1)


if __name__ == "__main__":
    main()
