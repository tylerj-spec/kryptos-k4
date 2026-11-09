#!/usr/bin/env python3
"""R73 SEALED K4 reveal (run ONLY after the K4 + nulls results are frozen, pushed and verified). Family I only.
Holds the published letters: EASTNORTHEAST at 0-based plaintext positions 21-33 and BERLINCLOCK at 63-73 (Family I
enciphers in place, so the decoded letters are in carved order).
  CONFIDENT     K4's best Family I score >= -2.7 per letter AND above every null's best Family I score;
  SIGNAL        CONFIDENT and the decode matches >= 10/24; SCORE_ANOMALY: CONFIDENT without it; else NO_SIGNAL.
  Contenders    any of K4's 18 Family I decodes matching >= 12/24, with the nulls' maximum.
Usage: reveal_k4.py TARGET.tsv RUN_DIR REPORT.json"""
import hashlib
import json
import sys
from pathlib import Path

CLUES = ((21, "EASTNORTHEAST"), (63, "BERLINCLOCK"))
POS = [(o + i, c) for o, t in CLUES for i, c in enumerate(t)]
CUT = -2.7


def hits(pt):
    return sum(pt[i] == c for i, c in POS)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    tsv, run, rep = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    for line in (run / "FROZEN.sha256").read_text().splitlines():
        h, lab, _ = line.split("  ")
        if lab in ("input", "results"):
            assert sha(tsv if lab == "input" else run / "RESULTS.jsonl") == h, f"freeze mismatch {lab}"
    ids = [l.split("\t")[0] for l in tsv.read_text().splitlines()[1:] if l]
    fam = {}
    for rid in ids:
        w = json.loads((run / "work" / f"{rid}.json").read_text())
        fam[rid] = sorted([s for s in w["settings"] if s["family"] == "I"], key=lambda s: -s["score"])
        assert len(fam[rid]) == 18
    nulls = [i for i in ids if i != "K4"]
    k4 = fam["K4"][0]
    k4_pl = k4["score"] / 97
    null_best = sorted(fam[i][0]["score"] / 97 for i in nulls)
    confident = k4_pl >= CUT and k4_pl > null_best[-1]
    h = hits("".join(k4["words"]))
    outcome = ("SIGNAL" if h >= 10 else "SCORE_ANOMALY") if confident else "NO_SIGNAL"
    k4max = max(hits("".join(s["words"])) for s in fam["K4"])
    null_max = sorted(max(hits("".join(s["words"])) for s in fam[i]) for i in nulls)
    contenders = [s for s in fam["K4"] if hits("".join(s["words"])) >= 12]
    out = {"outcome": outcome, "k4_best": k4, "k4_best_per_letter": k4_pl, "k4_best_hits": h,
           "nulls_best_per_letter_sorted": null_best, "nulls_at_or_above": sum(v >= k4_pl for v in null_best),
           "contender_screen": {"k4_max_hits_18_settings": k4max, "null_max_hits_sorted": null_max,
                                "contenders_ge_12": contenders}}
    rep.write_text(json.dumps(out, indent=1) + "\n")
    print(outcome, "| K4 best Family I %.3f/letter (cut -2.7)" % k4_pl, k4["setting"], "| nulls >= K4:",
          out["nulls_at_or_above"], "of", len(nulls), "| null best max %.3f" % null_best[-1], "| hits", h)
    print("raw decode:", " ".join(k4["words"]))
    print("contender screen: K4 max hits over 18 settings", k4max, "| nulls median/max", null_max[len(null_max) // 2],
          null_max[-1], "| contenders >= 12:", len(contenders))


if __name__ == "__main__":
    main()
