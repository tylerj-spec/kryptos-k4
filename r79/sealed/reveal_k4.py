#!/usr/bin/env python3
"""R79 SEALED K4 reveal (run ONLY after the K4 + 100 shuffles results are frozen, pushed and verified).
The published letters come from r73/sealed/reveal_k4.py (0-based plaintext positions; every R79 decode is in
plaintext order). Rules fixed in r79/PREREGISTRATION.md:
  CONFIDENT     K4's best decode clears both cuts AND its letter-model score is above every shuffle's best;
  SIGNAL        CONFIDENT and the decode matches >= 10/24; SCORE_ANOMALY: CONFIDENT without it; else NO_SIGNAL.
  Theorem K     reported: the cut for the families run (10^-6 expected false alarms, uniform null and K4-shuffle
                null) and whether K4's best clears it. Not part of the outcome.
  Packet        the frozen review decodes, each with its letter count added; each family's best likewise.
Usage: reveal_k4.py TARGET.tsv RUN_DIR REPORT.json"""
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r79"))
sys.path.insert(0, str(ROOT / "r73" / "sealed"))
import families as F  # noqa: E402
from reveal_k4 import CLUES  # noqa: E402

CUT_LM, CUT_WORD = -1.45, -2.50
POS = [o + i for o, t in CLUES for i in range(len(t))]
WANT = [c for _, t in CLUES for c in t]


def hits(t):
    return sum(t[p] == w for p, w in zip(POS, WANT))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    tsv, run, rep = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    files = {"input": tsv, "results": run / "RESULTS.jsonl", "packet": run / "packet" / "K4.json"}
    for line in (run / "FROZEN.sha256").read_text().splitlines():
        h, lab, _ = line.split("  ")
        if lab in files:
            assert sha(files[lab]) == h, f"freeze mismatch {lab}"
    cts = dict(l.split("\t") for l in tsv.read_text().splitlines()[1:] if l)
    res = {json.loads(l)["id"]: json.loads(l) for l in (run / "RESULTS.jsonl").read_text().splitlines() if l}
    nulls = [i for i in cts if i != "K4"]
    k4 = res["K4"]["best"]
    null_lm = sorted(res[i]["best"]["lm_per_letter"] for i in nulls)
    confident = k4["lm_per_letter"] >= CUT_LM and k4["word_per_letter"] >= CUT_WORD and k4["lm_per_letter"] > null_lm[-1]
    h = hits(k4["text"])
    outcome = ("SIGNAL" if h >= 10 else "SCORE_ANOMALY") if confident else "NO_SIGNAL"
    fams = list(res["K4"]["n_settings"])
    lk = F.log10_settings()
    top = max(lk[f] for f in fams)
    logn = top + math.log10(sum(10 ** (lk[f] - top) for f in fams))
    cut_uni, cut_shuf = (logn - (97 * math.log10(26) - 6)) / 97, (logn - (116.909 - 6)) / 97
    packet = json.loads(files["packet"].read_text())
    for e in packet:
        e["hits"] = hits(e["text"])
    out = {"outcome": outcome, "cut_lm": CUT_LM, "cut_word": CUT_WORD, "families": fams, "k4_best": k4,
           "k4_best_hits": h,
           "k4_best_by_fam": {f: {**e, "hits": hits(e["text"])} for f, e in res["K4"]["best_by_fam"].items()},
           "k4_h11_feasible": res["K4"]["h11_feasible"],
           "null_h11_feasible_total": sorted(sum(res[i]["h11_feasible"].values()) for i in nulls)
           if res["K4"]["h11_feasible"] else None,
           "null_best_lm_median": null_lm[len(null_lm) // 2], "null_best_lm_max": null_lm[-1],
           "nulls_at_or_above_k4": sum(v >= k4["lm_per_letter"] for v in null_lm), "n_nulls": len(nulls),
           "null_best_hits_max": max(hits(res[i]["best"]["text"]) for i in nulls),
           "theorem_k": {"log10_settings": logn, "cut_uniform_null": cut_uni, "cut_shuffle_null": cut_shuf,
                         "k4_clears_uniform_cut": k4["lm_per_letter"] >= cut_uni},
           "packet": packet}
    rep.write_text(json.dumps(out, indent=1) + "\n")
    print(outcome, "| K4 best %.3f/letter (cut %.2f), word %.2f (cut %.2f)" % (k4["lm_per_letter"], CUT_LM,
          k4["word_per_letter"], CUT_WORD), k4["fam"], "| shuffles >= K4:", out["nulls_at_or_above_k4"], "of",
          len(nulls), "| hits", h, "| shuffles' best hits max", out["null_best_hits_max"])
    print("raw decode:", k4["text"])
    print("by family:", {f: (round(e["lm_per_letter"], 3), e["hits"]) for f, e in out["k4_best_by_fam"].items()})
    print("Theorem K: log10 settings %.2f, cut %.3f (uniform) / %.3f (shuffles)" % (logn, cut_uni, cut_shuf))
    print("packet hits:", [e["hits"] for e in packet])


if __name__ == "__main__":
    main()
