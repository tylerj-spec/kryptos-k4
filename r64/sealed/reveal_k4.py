#!/usr/bin/env python3
"""R64 SEALED K4 reveal. Run ONLY after the K4 + nulls results are frozen, pushed and verified (verify.py). The only
R64 code holding the published letters (EASTNORTHEAST at 0-based 21-33, BERLINCLOCK at 63-73). In the S-then-T model
the published positions are plaintext positions, i.e. positions of the un-routed stream, so they are compared with the
frozen PLAINTEXT-order output of each model (and, as a reference, the key stream).
Primary (pre-registered): per model m, K4's frozen model-m total vs the 100 nulls' model-m totals, and K4's frozen
model-m plaintext vs the 24 published letters.
Secondary (exploratory, labelled so): best published-letter match over ALL frozen raw alternatives of K4 (both stages,
all routes, all conventions, top lists), with the same statistic for every null.
Usage: reveal_k4.py TARGET.tsv FROZEN_DIR REPORT.json"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import forward, routes, sha  # noqa: E402

CLUES = ((21, "EASTNORTHEAST"), (63, "BERLINCLOCK"))


def hits(s):
    return sum(s[o + i] == c for o, t in CLUES for i, c in enumerate(t))


def alt_best(work, rid, m):
    best = 0
    for st in ("s1", "s2"):
        for line in (work / f"{rid}.{m}.{st}.jsonl").read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                for w in [r["best"]] + r["per_convention"] + r["top"]:
                    best = max(best, hits(w["plaintext"]))
    return best


def main():
    tsv, fz, rep = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    for line in (fz / "FROZEN.sha256").read_text().splitlines():
        h, lab, _ = line.split("  ")
        if lab in ("input", "results"):
            p = tsv if lab == "input" else fz / "RESULTS.jsonl"
            assert sha(p) == h, f"freeze mismatch {lab}"
    R = routes()
    cts = dict(l.split("\t") for l in tsv.read_text().splitlines()[1:] if l)
    rows = {json.loads(l)["id"]: json.loads(l) for l in (fz / "RESULTS.jsonl").read_text().splitlines() if l.strip()}
    assert set(rows) == set(cts)
    nw = 0
    for i, r in rows.items():
        for b in r["models"].values():
            assert forward(b["plaintext"], b["key"], b["convention"], R[b["route"]]) == cts[i], f"witness {i}"
            nw += 1
    out = {"witnesses_checked": nw, "models": {}}
    for m in ("CLOCK", "GERMAN"):
        k4 = rows["K4"]["models"][m]
        null_ids = [i for i in rows if i != "K4"]
        nulls = [rows[i]["models"][m] for i in null_ids]
        ge = sum(n["total"] >= k4["total"] for n in nulls)
        nh = [hits(n["plaintext"]) for n in nulls]
        signal = ge == 0 and hits(k4["plaintext"]) >= 10
        out["models"][m] = {
            "k4_best": {k: v for k, v in k4.items() if k not in ("stage1", "stage2")},
            "k4_stage1": k4["stage1"], "k4_total": k4["total"], "nulls": len(nulls), "nulls_at_or_above_k4": ge,
            "empirical_rank_p": (ge + 1) / (len(nulls) + 1), "null_totals_sorted": sorted(n["total"] for n in nulls),
            "k4_clue_hits_plaintext": hits(k4["plaintext"]), "k4_clue_hits_key": hits(k4["key"]),
            "null_clue_hits_plaintext_sorted": sorted(nh),
            "outcome": "SIGNAL" if signal else "SCORE_ANOMALY" if ge == 0 else "NO_SIGNAL",
            "secondary_exploratory": {
                "k4_best_hits_any_frozen_alternative": alt_best(fz / "work", "K4", m),
                "null_best_hits_any_frozen_alternative_sorted": sorted(alt_best(fz / "work", i, m) for i in null_ids)}}
    rep.write_text(json.dumps(out, indent=1) + "\n")
    for m, d in out["models"].items():
        print(m, d["outcome"], {k: v for k, v in d.items() if k in ("k4_total", "nulls_at_or_above_k4", "empirical_rank_p",
                                                                  "k4_clue_hits_plaintext", "k4_clue_hits_key")},
              d["k4_best"]["route"], d["k4_best"]["convention"])
        print("   secondary", d["secondary_exploratory"]["k4_best_hits_any_frozen_alternative"],
              "nulls median/max", sorted(d["secondary_exploratory"]["null_best_hits_any_frozen_alternative_sorted"])[50],
              max(d["secondary_exploratory"]["null_best_hits_any_frozen_alternative_sorted"]))


if __name__ == "__main__":
    main()
