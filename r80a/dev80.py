#!/usr/bin/env python3
"""R80a development run (spent R81a gate books only; no K4; not the sealed holdout). Same item builder and the blind
runner's own per-ciphertext function as the gate, at reduced size: per book 3 plants per family (1 misspelled,
1 nonstandard spelling) + 1 STRETCH plant per family; 3 negatives per R79 wrong-family generator, 2 NEG_TWO_RANDOM,
5 shuffles.
Reports recovery (>= 95 of 97 letters, and exact) and the score ranges the confidence cuts must separate (R79's:
letter model -1.30, word model -2.50 per letter), and, for each positive, the true setting's pass-0 rank among all
settings of its family at its free-key length (diagnostic: is a miss the filter's or the solver's?).
Each finished ciphertext is cached in CACHE_DIR (one JSON file per item), so a restarted run resumes.
Usage: python3 -I r80a/dev80.py LM BOOK_A BOOK_B NEG_PT NEG_KEY OUT.json CACHE_DIR"""
import importlib.util
import json
import math
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "r80a"))
import items80 as I  # noqa: E402
import two80 as T  # noqa: E402

_spec = importlib.util.spec_from_file_location("r80a_blind_run", ROOT / "r80a" / "blind" / "run.py")
RUN = importlib.util.module_from_spec(_spec)
sys.modules["r80a_blind_run"] = RUN
_spec.loader.exec_module(RUN)
CUT_LM, CUT_WORD = -1.30, -2.50      # R79 cuts, to be confirmed here


def rank0(it):
    st, ct, fam = it["setting"], it["ct"], it["fam"]
    ci = T.CONVS.index(tuple(st["conv"]))
    wi = T.keys_for(fam).index(st["word"])
    m = len(st["free"])
    S = np.stack([T.scan(ct, fam, c)[:, m - 1] for c in range(len(T.CONVS))])
    return int((S > S[ci, wi]).sum()) + 1


def _cached(job):
    kind, i, payload, cache = job
    p = Path(cache) / f"{kind}_{i:03d}.json"
    if p.exists():
        return json.loads(p.read_text())
    r = RUN.process((str(i), payload)) if kind == "run" else rank0(payload)
    p.write_text(json.dumps(r))
    return r


def main():
    lm, book_a, book_b, neg_pt, neg_key, out, cache = sys.argv[1:8]
    Path(cache).mkdir(parents=True, exist_ok=True)
    rng = random.Random(800201)
    pos = I.positives(book_a, 3, 1, 1, 1, rng) + I.positives(book_b, 3, 1, 1, 1, rng)
    items = pos + I.negatives(neg_pt, neg_key, 3, np.random.default_rng(800202), 2, rng) + I.shuffles(
        [x for x in pos if x["kind"] != "STRETCH"], 5, rng)
    t0 = time.time()
    with Pool(4, initializer=RUN.init, initargs=(lm, T.FAMS)) as pool:
        res = pool.map(_cached, [("run", i, it["ct"], cache) for i, it in enumerate(items)], chunksize=1)
        ranks = pool.map(_cached, [("rank", i, it, cache) for i, it in enumerate(pos)], chunksize=1)
    rows = []
    for it, r in zip(items, res):
        b = r["best"]
        row = {"kind": it["kind"], "best_fam": b["fam"], "lm": b["lm_per_letter"], "word": b["word_per_letter"],
               "confident": b["lm_per_letter"] >= CUT_LM and b["word_per_letter"] >= CUT_WORD,
               "fam_best_lm": {f: e["lm_per_letter"] for f, e in r["best_by_fam"].items()}}
        if it["kind"].startswith("POS") or it["kind"] == "STRETCH":
            lw, m = len(it["setting"]["word"]), len(it["setting"]["free"])
            right = sum(x == y for x, y in zip(b["text"], it["pt"]))
            row.update({"fam": it["fam"], "lw": lw, "m": m, "gcd": math.gcd(lw, m), "lcm": lw * m // math.gcd(lw, m),
                        "letters_right": right, "recovered": right >= 95, "exact": right == 97,
                        "pass0_rank": ranks[pos.index(it)]})
        rows.append(row)
    P = [r for r in rows if r["kind"].startswith("POS")]
    st = [r for r in rows if r["kind"] == "STRETCH"]
    neg = [r for r in rows if r["kind"].startswith("NEG")]
    ok = [p for p in P if p["recovered"] and p["confident"]]
    rep = {"seconds": round(time.time() - t0), "k0": RUN.K0, "n_pos": len(P),
           "recovered_and_confident_by_fam": {f: [sum(p["recovered"] and p["confident"] for p in P if p["fam"] == f),
                                                  sum(p["fam"] == f for p in P)] for f in T.FAMS},
           "exact": sum(p["exact"] for p in P),
           "by_kind": {k: [sum(p["recovered"] and p["confident"] for p in P if p["kind"] == k),
                           sum(p["kind"] == k for p in P)] for k in ("POS", "POS_MISSP", "POS_NONSTD")},
           "stretch": [[p["fam"], p["lw"], p["m"], p["letters_right"], p["confident"], p["pass0_rank"]] for p in st],
           "pass0_rank_max_positives": max(p["pass0_rank"] for p in P),
           "pos_lm_min": min((p["lm"] for p in ok), default=None),
           "pos_word_min": min((p["word"] for p in ok), default=None),
           "neg_confident": sum(n["confident"] for n in neg), "neg_lm_max": max(n["lm"] for n in neg),
           "neg_word_max": max(n["word"] for n in neg),
           "neg_by_kind_lm_max": {k: max(n["lm"] for n in neg if n["kind"] == k) for k in sorted({n["kind"] for n in neg})},
           "neg_fam_lm_max": {f: max(n["fam_best_lm"].get(f, -9) for n in neg) for f in T.FAMS},
           "theorem_k_log10_settings": T.log10_settings()}
    Path(out).write_text(json.dumps({"report": rep, "rows": rows}, indent=1) + "\n")
    print(json.dumps(rep, indent=1))
    for p in P + st:
        if not (p["recovered"] and p["confident"]):
            print("miss:", p)


if __name__ == "__main__":
    main()
