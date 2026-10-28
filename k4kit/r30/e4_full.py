#!/usr/bin/env python3
"""AMENDMENT_R30_3.md: (1) re-search every E4 pass at 64 restarts with new seeds; (2) word-order-shuffle diagnostic
for the pass-count excess.  python3 -I k4kit/r30/e4_full.py BOOK.txt LABEL"""
import json
import random
import re
import sys
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e4_book as eb  # noqa: E402
from r30lib import ANCH, BAR_ORTH, K4, RUNS, assert_protocol, forced_mask, run_solver, seed, solver_line, verify_row  # noqa: E402,E501

if __name__ == "__main__":
    sha = assert_protocol()
    book, label = Path(sys.argv[1]), sys.argv[2]
    raw = book.read_bytes().decode("utf-8", errors="replace")
    text, _ = eb.normalise(raw)
    prev = json.load(open(RUNS / f"e4_{label}.json"))
    ids = [x["id"] for x in prev["ranked"]]
    keys = {}
    for i in ids:
        _, _, d, a, off = i.split("|")
        keys[i] = eb.key_of(text, d, a, int(off))
    L = [solver_line(i, keys[i], K4, ANCH, seed(f"ORTH|{i}|full64"), "-") for i in ids]
    best, _ = run_solver(L, f"e4_{label}_full64", 64)
    ranked = []
    for i in ids:
        assert verify_row(best[i], keys[i], K4), i
        fm = forced_mask(keys[i], K4, ANCH)
        ranked.append({"id": i, "W": best[i]["W"], "plaintext": best[i]["plaintext"], "forced_mask": fm,
                       "forced_beyond_clues": sum(1 for j, c in enumerate(fm) if c != "?" and j not in ANCH),
                       "plaintext_alphabet": best[i]["plaintext_alphabet"],
                       "ciphertext_alphabet": best[i]["ciphertext_alphabet"]})
    ranked.sort(key=lambda x: -x["W"])
    above = [x for x in ranked if x["W"] > BAR_ORTH]
    rep = {}
    if above:
        L2 = [solver_line(x["id"], keys[x["id"]], K4, ANCH, seed(f"ORTH|{x['id']}|full64rep"), "-") for x in above]
        rb, _ = run_solver(L2, f"e4_{label}_full64rep", 64)
        for x in above:
            rep[x["id"]] = {"W": rb[x["id"]]["W"], "plaintext": rb[x["id"]]["plaintext"],
                            "letters_changed_vs_screen": sum(a != b for a, b in zip(rb[x["id"]]["plaintext"],
                                                                                    x["plaintext"]))}
    cands = [i for i, r in rep.items() if r["letters_changed_vs_screen"] <= 5]
    # (2) word-order shuffle null on the pass count
    words = re.findall(r"[A-Za-z]+", "\n".join(ln for ln in raw.splitlines()))
    rng = random.Random(3033)
    wnull = []
    with Pool(4) as pool:
        for _ in range(20):
            w = list(words)
            rng.shuffle(w)
            s = re.sub("[^A-Z]", "", "".join(w).upper())
            wnull.append(len(eb.scan_all(pool, s, False)))
    wnull.sort()
    W = sorted(x["W"] for x in ranked)
    summary = {"protocol": sha, "label": label, "settings": len(ids), "restarts": 64, "bar": BAR_ORTH,
               "best_W": W[-1], "median_W": W[len(W) // 2], "n_above_bar": len(above), "candidates": cands,
               "book_passes": prev["summary"]["passes"], "word_shuffle_null": wnull,
               "word_shuffle_reaching": sum(x >= prev["summary"]["passes"] for x in wnull)}
    json.dump({"summary": summary, "ranked": ranked, "replication": rep},
              open(RUNS / f"e4_{label}_full64.json", "w"), indent=1)
    print(json.dumps(summary, indent=1))
    for x in ranked[:10]:
        print(f"  {x['W']:8.2f} +{x['forced_beyond_clues']:2d} {x['id']:<36} {x['plaintext']}")
