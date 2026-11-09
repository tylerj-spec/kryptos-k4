#!/usr/bin/env python3
"""R74 SEALED K4 reveal (run ONLY after the K4 + 1,000 shuffles results are frozen, pushed and verified).
The published letters come from r73/sealed/reveal_k4.py (0-based plaintext positions 21-33 and 63-73; the R74
decrypt is in plaintext order). Rules fixed in r74/PREREGISTRATION.md:
  CONFIDENT     K4's best decode clears both cuts (letter model >= CUT_LM, word model >= CUT_WORD per letter) AND
                its letter-model score is above every null's best;
  SIGNAL        CONFIDENT and the decode matches >= 10/24; SCORE_ANOMALY: CONFIDENT without it; else NO_SIGNAL.
  R74X          (crib-assisted, post-freeze; not part of the blind outcome) the published letters matched by every one
                of K4's 15,680 frozen decodes; CONSISTENT iff some transform matches >= 20/24 (listed raw), else
                EXCLUDED; the same maximum is computed for each of the 1,000 shuffles.
  Packet        the 25 frozen review decodes, each with its letter count added.
Usage: reveal_k4.py TARGET.tsv RUN_DIR REPORT.json"""
import gzip
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r74"))
sys.path.insert(0, str(ROOT / "r73" / "sealed"))
import sandwich as S  # noqa: E402
from reveal_k4 import CLUES  # noqa: E402

CUT_LM, CUT_WORD = -1.45, -2.5
POS = [(o + i, c) for o, t in CLUES for i, c in enumerate(t)]


def hits(pt):
    return sum(pt[i] == c for i, c in POS)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    tsv, run, rep = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    files = {"input": tsv, "results": run / "RESULTS.jsonl", "full": run / "full" / "K4.tsv.gz",
             "packet": run / "packet" / "K4.json"}
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
    # R74X on the frozen full scan
    full = [l.split("\t") for l in gzip.decompress(files["full"].read_bytes()).decode().splitlines()]
    k4_hits = [hits(r[9]) for r in full]
    hist = {str(v): k4_hits.count(v) for v in sorted(set(k4_hits))}
    consistent = [{"t": int(r[0]), "route": r[1], "ka": r[2], "kb": r[3], "a": int(r[4]), "b": int(r[5]),
                   "op_a": r[6], "op_b": r[7], "lm_per_letter": float(r[8]), "text": r[9], "hits": hk}
                  for r, hk in zip(full, k4_hits) if hk >= 20]
    # same maximum for every null, computed directly from the transforms (vectorised; deterministic decryption)
    cls = list(S.classes(S.load_routes()))
    R = np.array([k[0] for k in cls], dtype=np.int64)
    rinv = np.argsort(R, axis=1)
    sig = np.array([k[1] for k in cls], dtype=np.int64)[:, None]
    V = np.array([k[2] for k in cls], dtype=np.int64)
    pi = np.array([i for i, _ in POS])
    want = np.array([S.IDX[c] for _, c in POS])
    J = rinv[:, pi]
    VJ = np.take_along_axis(V, J, axis=1)

    def max_hits(ct):
        c = np.array([S.IDX[x] for x in ct], dtype=np.int64)
        return ((sig * (c[J] - VJ)) % 26 == want).sum(axis=1)

    k4_check = max_hits(cts["K4"])
    assert sorted(k4_check.tolist()) == sorted(k4_hits), "full-scan hits disagree with direct decryption"
    null_max = sorted(int(max_hits(cts[i]).max()) for i in nulls)
    packet = json.loads(files["packet"].read_text())
    for e in packet:
        e["hits"] = hits(e["text"])
    out = {"outcome": outcome, "cut_lm": CUT_LM, "cut_word": CUT_WORD, "k4_best": k4, "k4_best_hits": h,
           "nulls_best_lm_sorted_top10": null_lm[-10:], "null_best_lm_median": null_lm[len(null_lm) // 2],
           "nulls_at_or_above_k4": sum(v >= k4["lm_per_letter"] for v in null_lm), "n_nulls": len(nulls),
           "r74x_crib_assisted": {"verdict": "CONSISTENT" if consistent else "EXCLUDED", "k4_max_hits": max(k4_hits),
                                  "k4_hits_histogram": hist, "consistent_ge_20": consistent,
                                  "null_max_hits_median": null_max[len(null_max) // 2], "null_max_hits_max": null_max[-1],
                                  "nulls_ge_k4_max": sum(v >= max(k4_hits) for v in null_max)},
           "packet": packet}
    rep.write_text(json.dumps(out, indent=1) + "\n")
    print(outcome, "| K4 best %.3f/letter (cut %.2f), word %.2f (cut %.2f)" % (k4["lm_per_letter"], CUT_LM,
          k4["word_per_letter"], CUT_WORD), k4["route"], k4["setting"]["ka"], "| nulls >= K4:",
          out["nulls_at_or_above_k4"], "of", len(nulls), "| hits", h)
    print("raw decode:", k4["text"])
    x = out["r74x_crib_assisted"]
    print("R74X (crib-assisted):", x["verdict"], "| K4 max hits over 15,680 transforms", x["k4_max_hits"],
          "| nulls median/max", x["null_max_hits_median"], x["null_max_hits_max"], "| nulls >= K4 max",
          x["nulls_ge_k4_max"])
    print("packet hits:", [e["hits"] for e in packet])


if __name__ == "__main__":
    main()
