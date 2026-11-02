#!/usr/bin/env python3
"""R59 SEALED evaluator (after freeze only). For each plant: letters of the true plaintext recovered by the solver's
best answer. VIG is symmetric in (p, k) and BEAU == VARB with p and k swapped, so the plaintext counts as recovered in
whichever output stream matches it best; the convention counts as identified when it is the true one up to these two
symmetries (VARB is reported as BEAU). Every output pair is re-encrypted to its ciphertext independently.

Usage: evaluate.py BLIND.tsv RESULTS.jsonl SEALED_TRUTH.json REPORT.json [READABLE_MAX_WRONG=10]"""
import json
import sys
from pathlib import Path

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"


def enc(p, k, X, op):
    return "".join(X[(X.index(a) + X.index(b)) % 26 if op == "VIG" else (X.index(b) - X.index(a)) % 26 if op == "BEAU"
                     else (X.index(a) - X.index(b)) % 26] for a, b in zip(p, k))


def canon(conv):
    return conv.replace("VARB", "BEAU")


def main():
    blind, res, truth_p, rep = map(Path, sys.argv[1:5])
    readable = int(sys.argv[5]) if len(sys.argv) > 5 else 10
    cts = dict(l.split("\t") for l in blind.read_text().splitlines()[1:] if l)
    truth = json.loads(truth_p.read_text())
    rows = []
    for line in res.read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        t = truth[r["id"]]
        b = r["best"]
        xn, op = b["convention"].split("_")
        ok_witness = enc(b["plaintext"], b["key"], AZ if xn == "AZ" else KRY, op) == cts[r["id"]]
        tp = t["plaintext"]
        m_p = sum(a == c for a, c in zip(b["plaintext"], tp))
        m_k = sum(a == c for a, c in zip(b["key"], tp))
        stream = "plaintext" if m_p >= m_k else "key"
        m = max(m_p, m_k)
        other = b["key"] if stream == "plaintext" else b["plaintext"]
        rows.append({"id": r["id"], "true_convention": t["convention"], "found_convention": b["convention"],
                     "convention_ok": canon(b["convention"]) == canon(t["convention"]),
                     "plaintext_letters_correct": m, "wrong": 97 - m, "plaintext_in_stream": stream,
                     "key_letters_correct": sum(a == c for a, c in zip(other, t["key"])),
                     "exact": m == 97, "readable": 97 - m <= readable, "witness_ok": ok_witness,
                     "total": b["total"]})
    n = len(rows)
    out = {"total": n, "exact": sum(r["exact"] for r in rows), "readable": sum(r["readable"] for r in rows),
           "readable_max_wrong": readable, "convention_ok": sum(r["convention_ok"] for r in rows),
           "readable_and_convention": sum(r["readable"] and r["convention_ok"] for r in rows),
           "median_wrong": sorted(r["wrong"] for r in rows)[n // 2] if n else None,
           "all_witnesses_valid": all(r["witness_ok"] for r in rows), "rows": rows}
    rep.write_text(json.dumps(out, indent=1) + "\n")
    print({k: v for k, v in out.items() if k != "rows"})
    for r in rows:
        print(r["id"], r["true_convention"], r["found_convention"], "wrong", r["wrong"], "keyok", r["key_letters_correct"])


if __name__ == "__main__":
    main()
