#!/usr/bin/env python3
"""R79 development run (spent R76 holdout books only; no K4; not the sealed holdout). Same item builder and the blind
runner's own per-ciphertext function as the gate, at reduced size: per book 3 plants per family (1 misspelled, 1
nonstandard spelling) + 1 STRETCH plant per keyword family; 3 negatives per wrong-family generator; 5 shuffles.
Reports recovery and the score ranges the confidence cuts (letter model -1.45, word model -2.50 per letter) must
separate.
Usage: python3 -I r79/dev.py LM BOOK_A BOOK_B NEG_PT NEG_KEY OUT.json"""
import importlib.util
import json
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "r79"))
import families as F  # noqa: E402
import items as I  # noqa: E402

_spec = importlib.util.spec_from_file_location("r79_blind_run", ROOT / "r79" / "blind" / "run.py")
RUN = importlib.util.module_from_spec(_spec)
sys.modules["r79_blind_run"] = RUN
_spec.loader.exec_module(RUN)
CUT_LM, CUT_WORD = -1.45, -2.50


def main():
    lm, book_a, book_b, neg_pt, neg_key, out = sys.argv[1:7]
    rng = random.Random(790201)
    pos = I.positives(book_a, 3, 1, 1, 1, rng) + I.positives(book_b, 3, 1, 1, 1, rng)
    items = pos + I.negatives(neg_pt, neg_key, 3, np.random.default_rng(790202)) + I.shuffles(pos, 5, rng)
    t0 = time.time()
    with Pool(4, initializer=RUN.init, initargs=(lm, [], F.FAMS)) as pool:
        res = pool.map(RUN.process, [(str(i), it["ct"]) for i, it in enumerate(items)], chunksize=1)
    rows = []
    for it, r in zip(items, res):
        b = r["best"]
        row = {"kind": it["kind"], "best_fam": b["fam"], "lm": b["lm_per_letter"], "word": b["word_per_letter"],
               "confident": b["lm_per_letter"] >= CUT_LM and b["word_per_letter"] >= CUT_WORD,
               "fam_best_lm": {f: e["lm_per_letter"] for f, e in r["best_by_fam"].items()}}
        if it["kind"].startswith("POS") or it["kind"] == "STRETCH":
            row.update({"fam": it["fam"], "letters_right": sum(x == y for x, y in zip(b["text"], it["pt"])),
                        "m": it["setting"].get("m")})
            row["recovered"] = row["letters_right"] >= 95
        rows.append(row)
    pos = [r for r in rows if r["kind"].startswith("POS")]
    st = [r for r in rows if r["kind"] == "STRETCH"]
    neg = [r for r in rows if r["kind"].startswith("NEG")]
    rec = [p for p in pos if p["recovered"]]
    rep = {"seconds": round(time.time() - t0), "n_pos": len(pos),
           "recovered_and_confident_by_fam": {f: [sum(p["recovered"] and p["confident"] for p in pos if p["fam"] == f),
                                                  sum(p["fam"] == f for p in pos)] for f in F.FAMS},
           "by_kind": {k: [sum(p["recovered"] and p["confident"] for p in pos if p["kind"] == k),
                           sum(p["kind"] == k for p in pos)] for k in ("POS", "POS_MISSP", "POS_NONSTD")},
           "stretch": [[p["fam"], p["m"], p["recovered"], p["confident"]] for p in st],
           "pos_lm_min": min(p["lm"] for p in rec), "pos_word_min": min(p["word"] for p in rec),
           "n_neg": len(neg), "neg_confident": sum(n["confident"] for n in neg),
           "neg_lm_max": max(n["lm"] for n in neg), "neg_word_max": max(n["word"] for n in neg),
           "neg_lm_top5": sorted(n["lm"] for n in neg)[-5:],
           "neg_fam_lm_max": {f: max(n["fam_best_lm"].get(f, -9) for n in neg) for f in F.FAMS},
           "theorem_k": F.log10_settings(), "cut_lm": CUT_LM, "cut_word": CUT_WORD,
           "misses": [p for p in pos if not (p["recovered"] and p["confident"])], "rows": rows}
    Path(out).write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps({k: v for k, v in rep.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
