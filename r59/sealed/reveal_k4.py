#!/usr/bin/env python3
"""R59 SEALED K4 reveal. Run ONLY after the K4 + nulls results are frozen and pushed. The only R59 code that holds
the published K4 letters (EASTNORTHEAST at 0-based 21-33, BERLINCLOCK at 63-73).
Steps: (1) check the freeze manifest; (2) re-encrypt every frozen output (K4 and all nulls) independently;
(3) empirical rank of K4's best total among the null totals; (4) published-letter agreement of K4's frozen outputs in
each stream, with the same count computed for every null's outputs as a chance reference.
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


def clue_hits(s):
    return sum(s[o + i] == c for o, t in CLUES for i, c in enumerate(t))


def main():
    tsv, fz, rep = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    for line in (fz / "FROZEN.sha256").read_text().splitlines():
        h, lab, name = line.split("  ")
        if lab in ("input", "results"):
            p = tsv if lab == "input" else fz / "RESULTS.jsonl"
            assert hashlib.sha256(p.read_bytes()).hexdigest() == h, f"freeze mismatch: {lab}"
    cts = dict(l.split("\t") for l in tsv.read_text().splitlines()[1:] if l)
    rows = {json.loads(l)["id"]: json.loads(l) for l in (fz / "RESULTS.jsonl").read_text().splitlines() if l.strip()}
    assert set(rows) == set(cts)
    nw = 0
    for rid, r in rows.items():
        for c in [r["best"]] + r["per_convention"] + r["top"]:
            assert enc(c["plaintext"], c["key"], c["convention"]) == cts[rid], f"witness {rid}"
            nw += 1
    k4 = rows["K4"]
    nulls = [rows[i] for i in rows if i != "K4"]
    s = k4["best"]["total"]
    ge = sum(n["best"]["total"] >= s for n in nulls)
    hits = lambda c: {"plaintext_stream": clue_hits(c["plaintext"]), "key_stream": clue_hits(c["key"])}
    null_best_hits = sorted(max(clue_hits(n["best"]["plaintext"]), clue_hits(n["best"]["key"])) for n in nulls)
    out = {"witnesses_checked": nw, "k4_best": k4["best"], "k4_best_total": s,
           "nulls": len(nulls), "nulls_at_or_above_k4": ge, "empirical_rank_p": (ge + 1) / (len(nulls) + 1),
           "null_totals_sorted": sorted(n["best"]["total"] for n in nulls),
           "k4_best_clue_hits": hits(k4["best"]),
           "k4_per_convention_clue_hits": [{**hits(c), "convention": c["convention"], "total": c["total"]} for c in k4["per_convention"]],
           "k4_top_clue_hits": [{**hits(c), "convention": c["convention"], "total": c["total"]} for c in k4["top"]],
           "null_best_max_stream_clue_hits_sorted": null_best_hits}
    rep.write_text(json.dumps(out, indent=1) + "\n")
    print({k: v for k, v in out.items() if k not in ("null_totals_sorted", "k4_top_clue_hits", "null_best_max_stream_clue_hits_sorted")})


if __name__ == "__main__":
    main()
