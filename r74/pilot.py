#!/usr/bin/env python3
"""R74 step B: synthetic-only feasibility pilot (development books only; no K4 data; not a sealed holdout).
  Positives: 12 97-letter English passages (6 each from BOOK_A, BOOK_B; consecutive letters from a word start),
             each enciphered by r74/sandwich.py's explicit three-stage encrypt under a hidden raw setting drawn
             uniformly from the 20,160.
  Controls:  21 wrong-family ciphertexts (3 from each of R71's seven generators on NEG_PT/NEG_KEY) and 12
             frequency-preserving shuffles of the positives' ciphertexts.
Each ciphertext is scanned under all 15,680 transforms (r74/scan.py). Reported: whether the best decode is the exact
plaintext and the true transform, its letter-model score per letter, the gap to the best decode with different text,
the word-model score of the best decode (second, independent scorer: R59 word model segmentation, -7 per unknown
letter), and the time per ciphertext.
Usage: python3 -I r74/pilot.py LM BOOK_A BOOK_B NEG_PT NEG_KEY OUT.json"""
import json
import random
import re
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "r74"))
sys.path.insert(0, str(ROOT / "r73"))
sys.path.insert(0, str(ROOT / "r71"))
import sandwich as S  # noqa: E402
from scan import Scanner  # noqa: E402
import wordkey as W  # noqa: E402
import generators as G  # noqa: E402

N = 97


def passages(path, n, rng):
    text = Path(path).read_text(encoding="utf-8", errors="ignore").upper()
    words = re.findall(r"[A-Z]+", text)
    out = []
    while len(out) < n:
        i = rng.randrange(len(words) - 60)
        s = "".join(words[i:i + 60])
        out.append(s[:N])
    return out


def word_score(pt, vocab):
    best = [0.0] + [-1e18] * len(pt)
    for i in range(len(pt)):
        for L in range(1, min(W.MAXLEN, len(pt) - i) + 1):
            w = pt[i:i + L]
            v = max(vocab.get(w, -1e18), -W.OOV * L)
            if best[i] + v > best[i + L]:
                best[i + L] = best[i] + v
    return best[-1] / len(pt)


def main():
    lm, book_a, book_b, neg_pt, neg_key, out = sys.argv[1:7]
    rng = random.Random(740101)
    t0 = time.time()
    sc = Scanner(lm)
    t_init = time.time() - t0
    vocab = W.load_words()
    raw = list(S.configs(sc.routes))
    items = []
    for book in (book_a, book_b):
        for p in passages(book, 6, rng):
            cfg, r = raw[rng.randrange(len(raw))]
            ct = S.encrypt(p, cfg["ka"], cfg["kb"], cfg["a"], cfg["b"], cfg["op_a"], cfg["op_b"], r)
            items.append({"kind": "POS", "pt": p, "cfg": cfg,
                          "key": S.transform(cfg["ka"], cfg["kb"], cfg["a"], cfg["b"], cfg["op_a"], cfg["op_b"], r),
                          "ct": ct})
    letters = lambda p: np.frombuffer("".join(re.findall(r"[A-Z]", Path(p).read_text(  # noqa: E731
        encoding="utf-8", errors="ignore").upper())).encode(), dtype=np.uint8).astype(np.int16) - 65
    pt, kt = letters(neg_pt), letters(neg_key)
    routes = [[int(x) for x in l.split()[2].split(",")] for l in (ROOT / "r61/routes.txt").read_text().splitlines()]
    nrng = np.random.default_rng(740102)
    for arm in ("OTP", "RUNKEY", "PERIODIC", "HOMOPHONIC", "GROMARK", "CTAK", "PTAK"):
        C, _ = G.gen(arm, nrng, 3, pt, kt, routes)
        items += [{"kind": "NEG_" + arm, "ct": "".join(chr(65 + int(v)) for v in r)} for r in C]
    for it in [x for x in items if x["kind"] == "POS"]:
        c = list(it["ct"])
        rng.shuffle(c)
        items.append({"kind": "NEG_SHUFFLE", "ct": "".join(c)})
    rows, times = [], []
    for it in items:
        t1 = time.time()
        P, s, order = sc.scan(it["ct"])
        times.append(time.time() - t1)
        b = int(order[0])
        best_txt = sc.text(P[b])
        second = next(int(k) for k in order[1:] if sc.text(P[int(k)]) != best_txt)
        row = {"kind": it["kind"], "best_per_letter": float(s[b]) / N, "gap_to_next_text": float(s[b] - s[second]) / N,
               "best_route": sc.route_name[b], "best_labels": sc.labels[b][:2], "best_text": best_txt,
               "best_word_per_letter": word_score(best_txt, vocab)}
        if it["kind"] == "POS":
            row.update({"exact_plaintext": best_txt == it["pt"], "true_transform": sc.keys[b] == it["key"],
                        "true_setting": it["cfg"]})
        rows.append(row)
    pos = [r for r in rows if r["kind"] == "POS"]
    neg = [r for r in rows if r["kind"] != "POS"]
    rep = {"n_pos": len(pos), "exact_plaintext": sum(r["exact_plaintext"] for r in pos),
           "true_transform": sum(r["true_transform"] for r in pos),
           "pos_best_per_letter_min": min(r["best_per_letter"] for r in pos),
           "pos_gap_min": min(r["gap_to_next_text"] for r in pos),
           "pos_word_per_letter_min": min(r["best_word_per_letter"] for r in pos),
           "n_neg": len(neg), "neg_best_per_letter_max": max(r["best_per_letter"] for r in neg),
           "neg_word_per_letter_max": max(r["best_word_per_letter"] for r in neg),
           "seconds_model_and_transform_setup": t_init, "seconds_per_ciphertext_mean": sum(times) / len(times),
           "rows": rows}
    Path(out).write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps({k: v for k, v in rep.items() if k != "rows"}, indent=1))
    for r in rows:
        print(r["kind"], round(r["best_per_letter"], 3), round(r["gap_to_next_text"], 3),
              round(r["best_word_per_letter"], 2), r.get("exact_plaintext", ""), r["best_text"][:50])


if __name__ == "__main__":
    main()
