#!/usr/bin/env python3
"""R66 SEALED K4 reveal (Part A). Run ONLY after the K4 + nulls results are frozen, pushed and verified. Holds the
published letters (EASTNORTHEAST at 0-based 21-33, BERLINCLOCK at 63-73), compared with each frozen plaintext.
Primary: K4's total vs the 100 nulls' totals, and K4's frozen plaintext vs the 24 published letters.
  SIGNAL = K4 above all 100 nulls AND >= 10/24 letters; SCORE_ANOMALY = the first only; NO_SIGNAL otherwise.
Secondary (exploratory): best published-letter match over ALL frozen alternatives (10 routes x best/top 8); and
(Amendment 1) the best match over all 97 cyclic rotations of each frozen answer plaintext, K4 and nulls alike.
Usage: reveal_k4.py TARGET.tsv FROZEN_DIR REPORT.json"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import routes, sha, witness_ok  # noqa: E402

CLUES = ((21, "EASTNORTHEAST"), (63, "BERLINCLOCK"))


def hits(s):
    return sum(s[o + i] == c for o, t in CLUES for i, c in enumerate(t))


def rot_best(s):
    return max(hits(s[k:] + s[:k]) for k in range(len(s)))


def alt_best(work, rid):
    best = 0
    for line in (work / f"{rid}.jsonl").read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            for w in [r["best"]] + r["top"]:
                best = max(best, hits(w["plaintext"]))
    return best


def main():
    tsv, fz, rep = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    for line in (fz / "FROZEN.sha256").read_text().splitlines():
        h, lab, _ = line.split("  ")
        if lab in ("input", "results"):
            assert sha(tsv if lab == "input" else fz / "RESULTS.jsonl") == h, f"freeze mismatch {lab}"
    R = routes()
    cts = dict(l.split("\t") for l in tsv.read_text().splitlines()[1:] if l)
    rows = {json.loads(l)["id"]: json.loads(l) for l in (fz / "RESULTS.jsonl").read_text().splitlines() if l.strip()}
    assert set(rows) == set(cts)
    for i, r in rows.items():
        assert witness_ok(cts[i], R[r["route"]], r["plaintext"], r["map"]), f"witness {i}"
    k4 = rows["K4"]
    nulls = [rows[i] for i in rows if i != "K4"]
    ge = sum(n["total"] >= k4["total"] for n in nulls)
    h = hits(k4["plaintext"])
    out = {"k4": {k: v for k, v in k4.items() if k != "routes"}, "k4_routes": k4["routes"], "k4_total": k4["total"],
           "nulls": len(nulls), "nulls_at_or_above_k4": ge, "empirical_rank_p": (ge + 1) / (len(nulls) + 1),
           "null_totals_sorted": sorted(n["total"] for n in nulls), "k4_clue_hits": h,
           "null_clue_hits_sorted": sorted(hits(n["plaintext"]) for n in nulls),
           "outcome": "SIGNAL" if ge == 0 and h >= 10 else "SCORE_ANOMALY" if ge == 0 else "NO_SIGNAL",
           "secondary_exploratory": {"k4_best_hits_any_rotation": rot_best(k4["plaintext"]),
                                     "null_best_hits_any_rotation_sorted": sorted(rot_best(n["plaintext"]) for n in nulls),
                                     "k4_best_hits_any_frozen_alternative": alt_best(fz / "work", "K4"),
                                     "null_best_hits_sorted": sorted(alt_best(fz / "work", i) for i in rows if i != "K4")}}
    rep.write_text(json.dumps(out, indent=1) + "\n")
    print(out["outcome"], {k: out[k] for k in ("k4_total", "nulls_at_or_above_k4", "empirical_rank_p", "k4_clue_hits")},
          k4["route"])
    print("  K4", k4["plaintext"])
    s = out["secondary_exploratory"]
    print("  secondary: alternatives", s["k4_best_hits_any_frozen_alternative"], "nulls median/max",
          s["null_best_hits_sorted"][len(nulls) // 2], max(s["null_best_hits_sorted"]))
    print("  secondary: rotations", s["k4_best_hits_any_rotation"], "nulls median/max",
          s["null_best_hits_any_rotation_sorted"][len(nulls) // 2], max(s["null_best_hits_any_rotation_sorted"]))


if __name__ == "__main__":
    main()
