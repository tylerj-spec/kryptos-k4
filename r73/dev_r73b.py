#!/usr/bin/env python3
"""R73b development (development books only; no K4; not the sealed holdout). Sweeps the per-word unknown-word penalty
POOV of r73/wordkey2.py on R26 messages from development books (The Thirty-Nine Steps; Pride and Prejudice, whose
R73 Phase B holdout is spent) and wrong-family negatives (R71 generators on other development books). Reports, per
POOV, recovery (true setting family + >= 90/97 letters), exact setting, and the score-per-letter ranges of positives
and negatives, to fix POOV and the confidence cut for the R73b pre-registration.
Usage: python3 -I r73/dev_r73b.py LM BOOK_A BOOK_B NEG_PT NEG_KEY OUT.json"""
import json
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

N = 97
SOLVER = None


def init(lm, poov):
    global SOLVER
    SOLVER = W2.Solver(lm, poov)


def job(it):
    b = SOLVER.solve(it["ct"])[0]
    return {**it, "found": b["setting"], "words_found": b["words"], "per_letter": b["score"] / N}


def messages(path, n, rng):
    words = re.findall(r"[A-Z]+", Path(path).read_text(encoding="utf-8", errors="ignore").upper())
    out = []
    while len(out) < n:
        i = rng.randrange(len(words) - 60)
        msg, k = [], 0
        while k < N:
            msg.append(words[i])
            k += len(words[i])
            i += 1
        if k == N:
            out.append(msg)
    return out


def main():
    lm, book_a, book_b, neg_pt, neg_key, out = sys.argv[1:7]
    rng = random.Random(731001)
    sts = W.settings("R26")
    items = []
    for book in (book_a, book_b):
        for msg in messages(book, 20, rng):
            st = sts[rng.randrange(len(sts))]
            items.append({"kind": "R26", "setting": list(st), "words": msg, "ct": W.encrypt(msg, "R26", st)})
    letters = lambda p: np.frombuffer("".join(re.findall(r"[A-Z]", Path(p).read_text(  # noqa: E731
        encoding="utf-8", errors="ignore").upper())).encode(), dtype=np.uint8).astype(np.int16) - 65
    pt, kt = letters(neg_pt), letters(neg_key)
    routes = [[int(x) for x in l.split()[2].split(",")] for l in (ROOT / "r61/routes.txt").read_text().splitlines()]
    nrng = np.random.default_rng(731002)
    for arm in ("OTP", "RUNKEY", "PERIODIC", "HOMOPHONIC", "GROMARK", "CTAK", "PTAK"):
        C, _ = G.gen(arm, nrng, 8, pt, kt, routes)
        items += [{"kind": "NEG_" + arm, "ct": "".join(chr(65 + int(v)) for v in r)} for r in C]
    report = {}
    for poov in (-1.0, -2.0, -3.0, -4.0, -6.0):
        with Pool(4, initializer=init, initargs=(lm, poov)) as pool:
            res = pool.map(job, items)
        pos = [r for r in res if r["kind"] == "R26"]
        neg = [r for r in res if r["kind"].startswith("NEG_")]
        for r in pos:
            r["right"] = sum(a == b for a, b in zip("".join(r["words_found"]), "".join(r["words"])))
        rec = sum(r["right"] >= 90 for r in pos)
        report[poov] = {"recovered": rec, "n": len(pos), "setting_exact": sum(r["found"] == r["setting"] for r in pos),
                        "exact": sum(r["words_found"] == r["words"] for r in pos),
                        "pos_per_letter_min": min(r["per_letter"] for r in pos),
                        "pos_recovered_per_letter_min": min((r["per_letter"] for r in pos if r["right"] >= 90), default=None),
                        "neg_per_letter_max": max(r["per_letter"] for r in neg), "n_neg": len(neg),
                        "letters_right_low5": sorted(r["right"] for r in pos)[:5]}
        print(poov, report[poov], flush=True)
    Path(out).write_text(json.dumps(report, indent=1) + "\n")


if __name__ == "__main__":
    main()
