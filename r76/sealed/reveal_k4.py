#!/usr/bin/env python3
"""R76 SEALED K4 reveal (run ONLY after the K4 + 100 shuffles results are frozen, pushed and verified).
The published letters come from r73/sealed/reveal_k4.py (0-based plaintext positions; every R76 decode is in
plaintext order). Rules fixed in r76/PREREGISTRATION.md:
  CONFIDENT     K4's best decode clears both cuts AND its letter-model score is above every shuffle's best;
  SIGNAL        CONFIDENT and the decode matches >= 10/24; SCORE_ANOMALY: CONFIDENT without it; else NO_SIGNAL.
  Whole family  (crib-assisted, post-freeze; not part of the blind outcome) every fixed method is re-run on K4 and
                its decode compared with the published letters: the histogram of matches, every method with >= 14/24
                listed raw, and the same maximum for the first 10 shuffles.
  Packet        the frozen review decodes, each with its letter count added.
Usage: reveal_k4.py TARGET.tsv RUN_DIR REPORT.json"""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r75"))
sys.path.insert(0, str(ROOT / "r76"))
sys.path.insert(0, str(ROOT / "r73" / "sealed"))
import core  # noqa: E402
import families as F  # noqa: E402
from reveal_k4 import CLUES  # noqa: E402

CUT_LM, CUT_WORD = -1.45, -2.50
POS = np.array([o + i for o, t in CLUES for i in range(len(t))])
WANT = np.array([ord(c) - 65 for _, t in CLUES for c in t])
LIST_AT = 14


def hits(t):
    return int(sum(t[int(p)] == chr(65 + int(w)) for p, w in zip(POS, WANT)))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def family_hits(ct, collect):
    hist, listed, n = Counter(), [], 0
    for P, meta in F.batches(core.codes(ct)):
        h = (P[:, POS] == WANT).sum(axis=1)
        n += len(h)
        for v, k in zip(*np.unique(h, return_counts=True)):
            hist[int(v)] += int(k)
        if collect:
            for r in np.where(h >= LIST_AT)[0]:
                listed.append({"hits": int(h[r]), "text": core.text(P[int(r)]), "setting": F.setting(meta, int(r))})
    return hist, listed, n


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
    hist, listed, n = family_hits(cts["K4"], True)
    null_max = sorted(max(family_hits(cts[i], False)[0]) for i in nulls[:10])
    packet = json.loads(files["packet"].read_text())
    for e in packet:
        e["hits"] = hits(e["text"])
    out = {"outcome": outcome, "cut_lm": CUT_LM, "cut_word": CUT_WORD, "k4_best": k4, "k4_best_hits": h,
           "k4_best_by_sub": {s: {**e, "hits": hits(e["text"])} for s, e in res["K4"]["best_by_sub"].items()},
           "null_best_lm_median": null_lm[len(null_lm) // 2], "null_best_lm_max": null_lm[-1],
           "nulls_at_or_above_k4": sum(v >= k4["lm_per_letter"] for v in null_lm), "n_nulls": len(nulls),
           "whole_family_crib_assisted": {"methods": n, "k4_hits_histogram": dict(sorted(hist.items())),
                                          "k4_max_hits": max(hist), "listed_ge_%d" % LIST_AT: listed,
                                          "null_max_hits_first10": null_max},
           "packet": packet}
    rep.write_text(json.dumps(out, indent=1) + "\n")
    print(outcome, "| K4 best %.3f/letter (cut %.2f), word %.2f (cut %.2f)" % (k4["lm_per_letter"], CUT_LM,
          k4["word_per_letter"], CUT_WORD), k4["sub"], "| shuffles >= K4:", out["nulls_at_or_above_k4"], "of",
          len(nulls), "| hits", h)
    print("raw decode:", k4["text"])
    print("whole family (crib-assisted):", f"{n:,}", "methods | K4 max hits", max(hist), "| listed >=", LIST_AT, ":",
          len(listed), "| first 10 shuffles' max", null_max)
    print("packet hits:", [e["hits"] for e in packet])


if __name__ == "__main__":
    main()
