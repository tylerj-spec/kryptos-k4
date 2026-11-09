#!/usr/bin/env python3
"""R73b development check of the confidence cut (development books only; no K4; not the sealed holdout).
POOV is fixed at -3 from r73/dev_r73b.py (the largest positive/negative gap among the POOVs that keep the most exact
plaintexts and the highest lowest-letters-right). This run mirrors the holdout's make-up on development books that are
NOT in the R59 letter model's training text: 100 R26 positives (50 from each of BOOK_A, BOOK_B), 280 negatives (40 from
each of R71's seven generators on NEG_PT/NEG_KEY) and 20 frequency-preserving shuffles of positives. It reports the
score-per-letter ranges and the cut rule's value: the midpoint of the lowest recovered positive and the highest
negative, rounded down to 0.05.
Usage: python3 -I r73/dev_r73b_cut.py LM BOOK_A BOOK_B NEG_PT NEG_KEY OUT.json"""
import json
import math
import random
import re
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "r73"))
sys.path.insert(0, str(ROOT / "r71"))
import wordkey as W  # noqa: E402
import wordkey2 as W2  # noqa: E402
import generators as G  # noqa: E402
from dev_r73b import messages  # noqa: E402

N = 97
POOV = -3.0
SOLVER = None


def init(lm):
    global SOLVER
    SOLVER = W2.Solver(lm, POOV)


def job(it):
    b = SOLVER.solve(it["ct"])[0]
    return {**it, "found": b["setting"], "words_found": b["words"], "per_letter": b["score"] / N}


def main():
    lm, book_a, book_b, neg_pt, neg_key, out = sys.argv[1:7]
    rng = random.Random(731101)
    sts = W.settings("R26")
    items = []
    for book in (book_a, book_b):
        for msg in messages(book, 50, rng):
            st = sts[rng.randrange(len(sts))]
            items.append({"kind": "R26", "setting": list(st), "words": msg, "ct": W.encrypt(msg, "R26", st)})
    letters = lambda p: np.frombuffer("".join(re.findall(r"[A-Z]", Path(p).read_text(  # noqa: E731
        encoding="utf-8", errors="ignore").upper())).encode(), dtype=np.uint8).astype(np.int16) - 65
    pt, kt = letters(neg_pt), letters(neg_key)
    routes = [[int(x) for x in l.split()[2].split(",")] for l in (ROOT / "r61/routes.txt").read_text().splitlines()]
    nrng = np.random.default_rng(731102)
    for arm in ("OTP", "RUNKEY", "PERIODIC", "HOMOPHONIC", "GROMARK", "CTAK", "PTAK"):
        C, _ = G.gen(arm, nrng, 40, pt, kt, routes)
        items += [{"kind": "NEG_" + arm, "ct": "".join(chr(65 + int(v)) for v in r)} for r in C]
    for p in rng.sample([x for x in items if x["kind"] == "R26"], 20):
        c = list(p["ct"])
        rng.shuffle(c)
        items.append({"kind": "NEG_SHUFFLE", "ct": "".join(c)})
    with Pool(4, initializer=init, initargs=(lm,)) as pool:
        res = pool.map(job, items)
    pos = [r for r in res if r["kind"] == "R26"]
    neg = [r for r in res if r["kind"].startswith("NEG_")]
    for r in pos:
        r["right"] = sum(a == b for a, b in zip("".join(r["words_found"]), "".join(r["words"])))
    rec = [r for r in pos if r["right"] >= 90]
    lo, hi = min(r["per_letter"] for r in rec), max(r["per_letter"] for r in neg)
    by_arm = {}
    for r in neg:
        by_arm[r["kind"]] = max(by_arm.get(r["kind"], -1e9), r["per_letter"])
    report = {"poov": POOV, "n_pos": len(pos), "recovered": len(rec),
              "setting_exact": sum(r["found"] == r["setting"] for r in pos),
              "exact": sum(r["words_found"] == r["words"] for r in pos),
              "letters_right_low5": sorted(r["right"] for r in pos)[:5],
              "pos_recovered_per_letter_min": lo,
              "pos_per_letter_low5": sorted(r["per_letter"] for r in pos)[:5],
              "n_neg": len(neg), "neg_per_letter_max": hi, "neg_per_letter_top5": sorted(r["per_letter"] for r in neg)[-5:],
              "neg_max_by_kind": by_arm,
              "cut_rule_value": math.floor(((lo + hi) / 2) * 20) / 20,
              "misses": [{"setting": r["setting"], "found": r["found"], "right": r["right"], "per_letter": r["per_letter"],
                          "words": r["words"], "words_found": r["words_found"]} for r in pos if r["right"] < 97]}
    print(json.dumps({k: v for k, v in report.items() if k != "misses"}, indent=1), flush=True)
    Path(out).write_text(json.dumps(report, indent=1) + "\n")


if __name__ == "__main__":
    main()
