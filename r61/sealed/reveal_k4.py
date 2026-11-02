#!/usr/bin/env python3
"""R61 SEALED K4 reveal. Run ONLY after the K4 + nulls results are frozen and pushed. The only R61 code holding the
published letters (EASTNORTHEAST at 0-based plaintext positions 21-33, BERLINCLOCK at 63-73). Outputs are already in
plaintext order (the route has been undone), so the letters are compared position by position in each text.
Usage: reveal_k4.py TARGET.tsv FROZEN_DIR REPORT.json"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import encrypt  # noqa: E402

CLUES = ((21, "EASTNORTHEAST"), (63, "BERLINCLOCK"))


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
    for rid, r in rows.items():
        for c in r["stage2"]:
            assert encrypt(c["plaintext"], c["key"], c["convention"], c["route"]) == cts[rid], f"witness {rid}"
            nw += 1
    k4 = rows["K4"]
    nulls = [rows[i] for i in rows if i != "K4"]
    s = k4["best"]["total"]
    ge = sum(n["best"]["total"] >= s for n in nulls)
    h = lambda c: {"text_A": hits(c["plaintext"]), "text_B": hits(c["key"]), "route": c["route"], "convention": c["convention"], "total": c["total"]}
    out = {"witnesses_checked": nw, "k4_best": k4["best"], "k4_best_total": s, "k4_stage1": k4["stage1"],
           "nulls": len(nulls), "nulls_at_or_above_k4": ge, "empirical_rank_p": (ge + 1) / (len(nulls) + 1),
           "null_totals_sorted": sorted(n["best"]["total"] for n in nulls),
           "k4_best_clue_hits": h(k4["best"]), "k4_stage2_clue_hits": [h(c) for c in k4["stage2"]],
           "null_best_max_text_clue_hits_sorted": sorted(max(hits(n["best"]["plaintext"]), hits(n["best"]["key"])) for n in nulls)}
    rep.write_text(json.dumps(out, indent=1) + "\n")
    print({k: v for k, v in out.items() if k not in ("null_totals_sorted", "null_best_max_text_clue_hits_sorted", "k4_stage1")})


if __name__ == "__main__":
    main()
