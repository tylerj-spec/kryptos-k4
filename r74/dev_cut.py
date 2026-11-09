#!/usr/bin/env python3
"""R74 development run for the confidence cuts (development books only; no K4; not the sealed holdout).
Mirrors the holdout's make-up (r74/items.py): 100 positives (50 from each of BOOK_A, BOOK_B, 10 of each misspelled),
280 wrong-family negatives (40 per R71 generator on NEG_PT/NEG_KEY) and 20 shuffles of positives; scanned with the
blind runner's own per-ciphertext function. Cut rule (as R73b): for each scorer, the midpoint of the lowest recovered
positive and the highest negative, rounded down to 0.05.
Usage: python3 -I r74/dev_cut.py LM BOOK_A BOOK_B NEG_PT NEG_KEY OUT.json"""
import importlib.util
import json
import math
import random
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "r74"))
import items as I  # noqa: E402
import sandwich as S  # noqa: E402

_spec = importlib.util.spec_from_file_location("r74_blind_run", ROOT / "r74" / "blind" / "run.py")
RUN = importlib.util.module_from_spec(_spec)
sys.modules["r74_blind_run"] = RUN
_spec.loader.exec_module(RUN)


def main():
    lm, book_a, book_b, neg_pt, neg_key, out = sys.argv[1:7]
    items = I.build((book_a, book_b), 50, 10, neg_pt, neg_key, 40, 20, random.Random(740201),
                    np.random.default_rng(740202))
    with Pool(4, initializer=RUN.init, initargs=(lm, [])) as pool:
        res = pool.map(RUN.process, [(str(i), it["ct"]) for i, it in enumerate(items)], chunksize=2)
    routes = S.load_routes()
    pos, neg = [], []
    for it, r in zip(items, res):
        b = r["best"]
        if it["kind"].startswith("POS"):
            st = b["setting"]
            key = S.transform(st["ka"], st["kb"], st["a"], st["b"], st["op_a"], st["op_b"], routes[st["route"]])
            pos.append({"kind": it["kind"], "exact": b["text"] == it["pt"], "transform": key == I.true_key(it),
                        "lm": b["lm_per_letter"], "word": b["word_per_letter"]})
        else:
            neg.append({"kind": it["kind"], "lm": b["lm_per_letter"], "word": b["word_per_letter"]})
    rec = [p for p in pos if p["exact"] and p["transform"]]
    cut = lambda lo, hi: math.floor((lo + hi) / 2 * 20) / 20  # noqa: E731
    rep = {"n_pos": len(pos), "recovered": len(rec),
           "recovered_misspelled": sum(p["kind"] == "POS_MISSPELLED" for p in rec),
           "pos_lm_min": min(p["lm"] for p in rec), "pos_word_min": min(p["word"] for p in rec),
           "n_neg": len(neg), "neg_lm_max": max(n["lm"] for n in neg), "neg_word_max": max(n["word"] for n in neg),
           "neg_lm_top5": sorted(n["lm"] for n in neg)[-5:], "neg_word_top5": sorted(n["word"] for n in neg)[-5:]}
    rep["cut_lm"] = cut(rep["pos_lm_min"], rep["neg_lm_max"])
    rep["cut_word"] = cut(rep["pos_word_min"], rep["neg_word_max"])
    rep["misses"] = [p for p in pos if not (p["exact"] and p["transform"])]
    Path(out).write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
