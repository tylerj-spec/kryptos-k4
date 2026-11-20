#!/usr/bin/env python3
"""R88 SEALED K4 evaluation: the first step that reads the published letters. Run ONLY after the K4 + 100 shuffles
results, the independent witness check (WITNESS.json, passed) and r88/k4/FROZEN.sha256 are committed and PUSHED.
Rules fixed in r88/PREREGISTRATION.md (R84's rules; one family, so "best" is already the maximum over all 512
settings, for K4 and every shuffle alike):
  CONFIDENT     K4's best decode clears both cuts (letter model >= -1.30, word model >= -2.50 per letter) AND its
                letter-model score is above every shuffle's best;
  SIGNAL        CONFIDENT and the decode matches >= 10/24 published letters; SCORE_ANOMALY: CONFIDENT without it;
                otherwise NO_SIGNAL.
  p_family      (1 + shuffles whose best letter-model score >= K4's) / (1 + shuffles).
  Contenders    every frozen K4 decode (top 5) matching >= 12/24 published letters, raw, with the most any shuffle's
                frozen decode matches.
The published letters come from r73/sealed/reveal_k4.py (0-based positions 21-33 and 63-73; RQ decodes are in place).
Usage: evaluate87.py TARGET.tsv RESULTS.jsonl WITNESS.json FROZEN.sha256 REPORT.json"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CUT_LM, CUT_WORD, SIG, CONT = -1.30, -2.50, 10, 12


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def check_frozen(frozen, paths):
    listed = {}
    for line in Path(frozen).read_text().splitlines():
        if line.strip():
            h, path = line.split()[0], line.split()[-1]
            listed[path] = h
            if (ROOT / path).exists():
                assert sha(ROOT / path) == h, f"freeze mismatch {path}"
    for p in paths:
        rel = str(Path(p).resolve().relative_to(ROOT))
        assert listed.get(rel) == sha(p), f"{rel} is not frozen"


def main():
    tsv, results, witness, frozen, rep = (Path(a) for a in sys.argv[1:6])
    check_frozen(frozen, (tsv, results, witness))
    w = json.loads(witness.read_text())
    assert w["passed"], "independent witness check did not pass: do not evaluate"
    sys.path.insert(0, str(ROOT / "r73" / "sealed"))
    from reveal_k4 import CLUES  # the published letters; read only after the freeze
    pos = [o + i for o, t in CLUES for i in range(len(t))]
    want = [c for _, t in CLUES for c in t]

    def hits(t):
        return sum(t[p] == x for p, x in zip(pos, want))

    cts = dict(l.split("\t") for l in tsv.read_text().splitlines()[1:] if l)
    res = {json.loads(l)["id"]: json.loads(l) for l in results.read_text().splitlines() if l}
    assert set(res) == set(cts) and "K4" in res
    nulls = sorted(i for i in cts if i != "K4")
    k4 = res["K4"]["best"]
    null_lm = sorted(res[i]["best"]["lm_per_letter"] for i in nulls)
    at_or_above = sum(v >= k4["lm_per_letter"] for v in null_lm)
    clears = k4["lm_per_letter"] >= CUT_LM and k4["word_per_letter"] >= CUT_WORD
    confident = clears and k4["lm_per_letter"] > null_lm[-1]
    h = hits(k4["text"])
    outcome = ("SIGNAL" if h >= SIG else "SCORE_ANOMALY") if confident else "NO_SIGNAL"
    null_hits = [max(hits(e["text"]) for e in res[i]["top"]) for i in nulls]
    k4_max = max(hits(e["text"]) for e in res["K4"]["top"])
    out = {"outcome": outcome, "cut_lm": CUT_LM, "cut_word": CUT_WORD, "k4_best": k4, "k4_best_hits": h,
           "k4_best_clears_cuts": clears, "k4_top": [{**e, "hits": hits(e["text"])} for e in res["K4"]["top"]],
           "n_nulls": len(nulls), "null_best_lm_max": null_lm[-1], "null_best_lm_median": null_lm[len(null_lm) // 2],
           "nulls_at_or_above_k4": at_or_above, "p_family": (1 + at_or_above) / (1 + len(nulls)),
           "nulls_clearing_both_cuts": sum(res[i]["best"]["lm_per_letter"] >= CUT_LM and
                                           res[i]["best"]["word_per_letter"] >= CUT_WORD for i in nulls),
           "k4_max_hits_any_frozen_decode": k4_max, "null_max_hits_any_frozen_decode": max(null_hits),
           "nulls_reaching_k4_max_hits": sum(x >= k4_max for x in null_hits),
           "contenders": [{**e, "hits": hits(e["text"])} for e in res["K4"]["top"] if hits(e["text"]) >= CONT],
           "witnesses_checked": w["witnesses"]}
    rep.write_text(json.dumps(out, indent=1) + "\n")
    st = k4["setting"]
    print(outcome, "| K4 best %.3f/letter (cut %.2f), word %.2f (cut %.2f), setting %s free, %s fixed, n %d d %+d" % (
        k4["lm_per_letter"], CUT_LM, k4["word_per_letter"], CUT_WORD, st["side"], st["alph"], st["n"], st["d"]),
        "| shuffles >= K4: %d of %d (p_family %.3f)" % (at_or_above, len(nulls), out["p_family"]),
        "| published letters matched %d/24 | K4 max over frozen decodes %d, shuffles max %d | contenders %d" % (
        h, k4_max, out["null_max_hits_any_frozen_decode"], len(out["contenders"])))
    print("raw decode (unedited):", k4["text"])


if __name__ == "__main__":
    main()
