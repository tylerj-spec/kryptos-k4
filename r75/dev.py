#!/usr/bin/env python3
"""R75 development run (development books only; no K4; not the sealed holdout). Mirrors the holdout at reduced size:
36 positives (3 per sub-family from each of BOOK_A, BOOK_B; 4 of each book misspelled), 56 wrong-family negatives
(8 per R71 generator) and 8 shuffles, all scanned with the blind runner's own per-ciphertext function. Reports
recovery and the score ranges that the confidence cuts (letter model -1.45, word model -2.50 per letter, as R74) must
separate.
Usage: python3 -I r75/dev.py LM BOOK_A BOOK_B NEG_PT NEG_KEY OUT.json"""
import importlib.util
import json
import random
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "r75"))
import items as I  # noqa: E402

_spec = importlib.util.spec_from_file_location("r75_blind_run", ROOT / "r75" / "blind" / "run.py")
RUN = importlib.util.module_from_spec(_spec)
sys.modules["r75_blind_run"] = RUN
_spec.loader.exec_module(RUN)
CUT_LM, CUT_WORD = -1.45, -2.50


def main():
    lm, book_a, book_b, neg_pt, neg_key, out = sys.argv[1:7]
    items = I.build((book_a, book_b), 3, 4, neg_pt, neg_key, 8, 8, random.Random(750201),
                    np.random.default_rng(750202))
    with Pool(4, initializer=RUN.init, initargs=(lm, [])) as pool:
        res = pool.map(RUN.process, [(str(i), it["ct"]) for i, it in enumerate(items)], chunksize=1)
    pos, neg = [], []
    for it, r in zip(items, res):
        b = r["best"]
        row = {"kind": it["kind"], "lm": b["lm_per_letter"], "word": b["word_per_letter"],
               "confident": b["lm_per_letter"] >= CUT_LM and b["word_per_letter"] >= CUT_WORD}
        if it["kind"].startswith("POS"):
            row.update({"sub": it["sub"], "exact": b["text"] == it["pt"], "same_setting": b["setting"] == it["setting"]})
            pos.append(row)
        else:
            neg.append(row)
    rec = [p for p in pos if p["exact"]]
    rep = {"n_pos": len(pos), "recovered": len(rec), "recovered_and_confident": sum(p["confident"] for p in rec),
           "same_setting": sum(p["same_setting"] for p in pos),
           "recovered_by_sub": {s: sum(p["exact"] for p in pos if p["sub"] == s) for s in sorted({p["sub"] for p in pos})},
           "pos_lm_min": min(p["lm"] for p in rec), "pos_word_min": min(p["word"] for p in rec),
           "n_neg": len(neg), "neg_confident": sum(n["confident"] for n in neg),
           "neg_lm_max": max(n["lm"] for n in neg), "neg_word_max": max(n["word"] for n in neg),
           "neg_lm_top5": sorted(n["lm"] for n in neg)[-5:], "cut_lm": CUT_LM, "cut_word": CUT_WORD,
           "misses": [p for p in pos if not p["exact"]]}
    Path(out).write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
