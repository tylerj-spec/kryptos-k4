#!/usr/bin/env python3
"""R63 SEALED K4 reveal. Run ONLY after the K4 + nulls results are frozen and pushed. The only R63 code holding the
published letters (EASTNORTHEAST at 0-based 21-33, BERLINCLOCK at 63-73), compared in the plaintext stream (and, as a
reference, the key stream) of each model's frozen output.
Usage: reveal_k4.py TARGET.tsv FROZEN_DIR REPORT.json"""
import hashlib
import json
import sys
from pathlib import Path

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
CLUES = ((21, "EASTNORTHEAST"), (63, "BERLINCLOCK"))


def enc(p, k, conv):
    xn, op = conv.split("_")
    X = AZ if xn == "AZ" else KRY
    return "".join(X[(X.index(a) + X.index(b)) % 26 if op == "VIG" else (X.index(b) - X.index(a)) % 26 if op == "BEAU"
                     else (X.index(a) - X.index(b)) % 26] for a, b in zip(p, k))


def hits(s):
    return sum(s[o + i] == c for o, t in CLUES for i, c in enumerate(t))


def main():
    tsv, fz, rep = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    for line in (fz / "FROZEN.sha256").read_text().splitlines():
        h, lab, _ = line.split("  ")
        if lab in ("input", "results"):
            p = tsv if lab == "input" else fz / "RESULTS.jsonl"
            assert hashlib.sha256(p.read_bytes()).hexdigest() == h, f"freeze mismatch {lab}"
    cts = dict(l.split("\t") for l in tsv.read_text().splitlines()[1:] if l)
    rows = {json.loads(l)["id"]: json.loads(l) for l in (fz / "RESULTS.jsonl").read_text().splitlines() if l.strip()}
    assert set(rows) == set(cts)
    nw = 0
    for i, r in rows.items():
        for b in r["models"].values():
            assert enc(b["plaintext"], b["key"], b["convention"]) == cts[i], f"witness {i}"
            nw += 1
    out = {"witnesses_checked": nw, "models": {}}
    for m in ("CLOCK", "GERMAN"):
        k4 = rows["K4"]["models"][m]
        nulls = [rows[i]["models"][m] for i in rows if i != "K4"]
        ge = sum(n["total"] >= k4["total"] for n in nulls)
        out["models"][m] = {"k4_best": k4, "k4_total": k4["total"], "nulls": len(nulls), "nulls_at_or_above_k4": ge,
                            "empirical_rank_p": (ge + 1) / (len(nulls) + 1),
                            "null_totals_sorted": sorted(n["total"] for n in nulls),
                            "k4_clue_hits_plaintext": hits(k4["plaintext"]), "k4_clue_hits_key": hits(k4["key"]),
                            "null_clue_hits_plaintext_sorted": sorted(hits(n["plaintext"]) for n in nulls)}
    rep.write_text(json.dumps(out, indent=1) + "\n")
    for m, d in out["models"].items():
        print(m, {k: v for k, v in d.items() if k not in ("null_totals_sorted", "null_clue_hits_plaintext_sorted", "k4_best")})


if __name__ == "__main__":
    main()
