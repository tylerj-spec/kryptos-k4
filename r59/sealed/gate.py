#!/usr/bin/env python3
"""R59 SEALED holdout gate (after both freezes). Inputs: plant TSV + frozen plant results + sealed truth, and the
frozen results for the shuffled-plant nulls.
Per plant:
  detected      : its best total exceeds the MAXIMUM best total over all null ciphertexts;
  convention_ok : identified up to the two symmetries (VIG p<->k; BEAU == VARB with p<->k);
  pair_correct  : positions where the output letter pair {p_i, k_i} equals the true pair (reading order ignored);
  witness_ok    : the output pair re-encrypts exactly to the ciphertext (independent encryptor).
Gate (fixed in r59/PREREGISTRATION.md): detected >= 16/20, convention_ok >= 16/20, pair_correct >= 60 in >= 12/20,
all witnesses valid (plants and nulls).
Usage: gate.py PLANTS.tsv PLANT_RESULTS.jsonl SEALED_TRUTH.json NULLS.tsv NULL_RESULTS.jsonl REPORT.json"""
import json
import sys
from pathlib import Path

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"


def enc(p, k, conv):
    xn, op = conv.split("_")
    X = AZ if xn == "AZ" else KRY
    return "".join(X[(X.index(a) + X.index(b)) % 26 if op == "VIG" else (X.index(b) - X.index(a)) % 26 if op == "BEAU"
                     else (X.index(a) - X.index(b)) % 26] for a, b in zip(p, k))


def load(tsv, res):
    cts = dict(l.split("\t") for l in Path(tsv).read_text().splitlines()[1:] if l)
    rows = [json.loads(l) for l in Path(res).read_text().splitlines() if l.strip()]
    assert set(r["id"] for r in rows) == set(cts), "result ids differ from input ids"
    return cts, rows


def main():
    pt_tsv, pt_res, truth_p, nl_tsv, nl_res, rep = sys.argv[1:7]
    truth = json.loads(Path(truth_p).read_text())
    pcts, prows = load(pt_tsv, pt_res)
    ncts, nrows = load(nl_tsv, nl_res)
    wit = all(enc(r["best"]["plaintext"], r["best"]["key"], r["best"]["convention"]) == pcts[r["id"]] for r in prows) and \
        all(enc(r["best"]["plaintext"], r["best"]["key"], r["best"]["convention"]) == ncts[r["id"]] for r in nrows)
    nmax = max(r["best"]["total"] for r in nrows)
    out = []
    for r in prows:
        b, t = r["best"], truth[r["id"]]
        pair = sum({a, c} == {x, y} for a, c, x, y in zip(b["plaintext"], b["key"], t["plaintext"], t["key"]))
        stream = max(sum(a == x for a, x in zip(b["plaintext"], t["plaintext"])), sum(a == x for a, x in zip(b["key"], t["plaintext"])))
        out.append({"id": r["id"], "total": b["total"], "detected": b["total"] > nmax,
                    "true_convention": t["convention"], "found_convention": b["convention"],
                    "convention_ok": b["convention"].replace("VARB", "BEAU") == t["convention"].replace("VARB", "BEAU"),
                    "pair_correct": pair, "plaintext_stream_correct": stream, "exact_plaintext": stream == 97})
    det = sum(o["detected"] for o in out)
    conv = sum(o["convention_ok"] for o in out)
    p60 = sum(o["pair_correct"] >= 60 for o in out)
    res = {"plants": len(out), "nulls": len(nrows), "null_max_total": nmax,
           "null_totals": sorted(r["best"]["total"] for r in nrows),
           "detected": det, "convention_ok": conv, "pair_correct_ge_60": p60,
           "exact_plaintext": sum(o["exact_plaintext"] for o in out),
           "median_pair_correct": sorted(o["pair_correct"] for o in out)[len(out) // 2],
           "all_witnesses_valid": wit,
           "gate_passed": det >= 16 and conv >= 16 and p60 >= 12 and wit and len(out) == 20,
           "rows": out}
    Path(rep).write_text(json.dumps(res, indent=1) + "\n")
    print({k: v for k, v in res.items() if k not in ("rows", "null_totals")})


if __name__ == "__main__":
    main()
