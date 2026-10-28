#!/usr/bin/env python3
"""SEALED reveal (run only after runs/FROZEN.sha256 exists). Checks the freeze, re-encrypts every frozen row forward to
its input ciphertext under its stated setting, ranks the planted truths, and counts K4 clue matches."""
import csv
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE.parent / "runs"
sys.path.insert(0, str(HERE))
from make_plants import AZ, KRY, SRC, chain, encrypt, route  # noqa: E402

ANCH = {21 + i: c for i, c in enumerate("EASTNORTHEAST")} | {63 + i: c for i, c in enumerate("BERLINCLOCK")}
for line in (RUNS / "FROZEN.sha256").read_text().splitlines():
    h, f = line.split()
    assert hashlib.sha256((RUNS / f).read_bytes()).hexdigest() == h, f"{f} changed after freeze"


def key_of(fam, spec):
    if fam in ("CARTER", "K1K3"):
        d, num, off = spec.split("/")
        s = SRC[fam] if d == "fwd" else SRC[fam][::-1]
        al = AZ if num == "AZ" else KRY
        return [al.index(c) for c in s[int(off[3:]):int(off[3:]) + 97]]
    return chain(int(spec[6:]), 5 if fam == "G5" else 6)


def check(row, ct):
    fam, name, order, spec, pa, ca, op = row["setting"].split("|")
    perm = list(range(97)) if order == "ID" else route(name)
    key = key_of(fam, spec)
    return encrypt(row["plaintext"], perm, order, key, AZ if pa == "PA=AZ" else KRY, AZ if ca == "CA=AZ" else KRY,
                   op[3:]) == ct


rep = {"plants": [], "k4": []}
truth = json.loads((HERE / "plants_truth.json").read_text())
for m in truth:
    tag = f"PLANT_F{1 if m['plant'] < 6 else 2}_{m['plant']}"
    rows = list(csv.DictReader(open(RUNS / f"{tag}.tsv"), delimiter="\t"))
    assert all(check(r, m["ciphertext"]) for r in rows), tag
    rank = next((int(r["rank"]) for r in rows if r["plaintext"] == m["plaintext"]), None)
    rep["plants"].append({"plant": tag, "family": m["family"], "route": m["route"], "order": m["order"],
                          "true_rank": rank, "true_in_top100": rank is not None, "top_score": rows[0]["score"],
                          "top_is_truth": rows[0]["plaintext"] == m["plaintext"]})
K4 = (RUNS / "k4_ciphertext.txt").read_text().strip()
for tag in ("K4_F1_CARTER", "K4_F1_K1K3", "K4_F1_G5", "K4_F1_C6", "K4_F2_G5"):
    rows = list(csv.DictReader(open(RUNS / f"{tag}.tsv"), delimiter="\t"))
    assert all(check(r, K4) for r in rows), tag
    m = [sum(r["plaintext"][i] == c for i, c in ANCH.items()) for r in rows]
    rep["k4"].append({"run": tag, "rows": len(rows), "forward_check": "all rows re-encrypt to K4",
                      "top_score": rows[0]["score"], "top_plaintext": rows[0]["plaintext"],
                      "clue_matches_max": max(m), "rows_with_24": sum(x == 24 for x in m),
                      "clue_matches_by_rank_top10": m[:10]})
(RUNS / "REVEAL.json").write_text(json.dumps(rep, indent=1) + "\n")
print(json.dumps(rep, indent=1))
