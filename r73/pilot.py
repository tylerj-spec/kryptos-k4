#!/usr/bin/env python3
"""R73 Phase A pilot (synthetic only; no K4 input). Measures whether the word-boundary families of PR #62 can be
recovered blind, and how wrong-family ciphertexts score.
  Positives: 12 Family I + 12 Family R26 messages; each is consecutive whole words of an English novel totalling
             exactly 97 letters, enciphered with a hidden random setting (seeded).
  Negatives: 30 ciphertexts from R71's generators (OTP, running key, periodic, homophonic + route, Gromark, CTAK,
             PTAK; 4-5 each) built from other English text.
The solver sees only the ciphertext and runs every setting of both families. Reported per ciphertext: best decode,
whether family + plaintext are exact, the score per letter, the margin over the best decode of the other family,
and IC. Usage: python3 -I r73/pilot.py PT_BOOK OTHER_BOOK KEY_BOOK OUT.json"""
import json
import random
import re
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "r73"))
sys.path.insert(0, str(ROOT / "r71"))
import wordkey as W  # noqa: E402
import generators as G  # noqa: E402

N = 97


def word_stream(path):
    return re.findall(r"[A-Z]+", Path(path).read_text(encoding="utf-8", errors="ignore").upper())


def message(rng, words, vocab):
    while True:
        i = rng.randrange(len(words) - 60)
        out, n = [], 0
        while n < N:
            out.append(words[i])
            n += len(words[i])
            i += 1
        if n == N:
            return out


def ic(s):
    c = Counter(s)
    return sum(v * (v - 1) for v in c.values()) / (len(s) * (len(s) - 1))


def main():
    pt_book, other_book, key_book, out = sys.argv[1:5]
    vocab = W.load_words()
    words = word_stream(pt_book)
    rng = random.Random(730001)
    items = []
    for fam in ("I", "R26"):
        sts = W.settings(fam)
        for _ in range(12):
            msg = message(rng, words, vocab)
            st = sts[rng.randrange(len(sts))]
            items.append({"kind": fam, "setting": list(st), "words": msg, "ct": W.encrypt(msg, fam, st)})
    letters = lambda p: np.frombuffer("".join(re.findall(r"[A-Z]", Path(p).read_text(  # noqa: E731
        encoding="utf-8", errors="ignore").upper())).encode(), dtype=np.uint8).astype(np.int16) - 65
    pt, kt = letters(other_book), letters(key_book)
    routes = [[int(x) for x in l.split()[2].split(",")] for l in (ROOT / "r61/routes.txt").read_text().splitlines()]
    nrng = np.random.default_rng(730002)
    arms = ["OTP", "RUNKEY", "PERIODIC", "HOMOPHONIC", "GROMARK", "CTAK", "PTAK"]
    for j in range(30):
        arm = arms[j % len(arms)]
        C, _ = G.gen(arm, nrng, 1, pt, kt, routes)
        items.append({"kind": "NEG_" + arm, "ct": "".join(chr(65 + int(v)) for v in C[0])})
    t0 = time.time()
    for it in items:
        res = W.solve_all(it["ct"], vocab)
        b = res[0]
        other = next(r for r in res if r["family"] != b["family"])
        it.update({"best_family": b["family"], "best_setting": b["setting"], "best_score": b["score"],
                   "best_per_letter": b["score"] / N, "best_words": b["words"], "best_oov": b["oov"],
                   "margin_other_family": b["score"] - other["score"], "ic": ic(it["ct"])})
        if it["kind"] in ("I", "R26"):
            it["family_ok"] = b["family"] == it["kind"]
            it["plaintext_ok"] = "".join(b["words"]) == "".join(it["words"])
            it["segmentation_ok"] = b["words"] == it["words"]
            it["setting_ok"] = b["setting"] == it["setting"]
    dt = time.time() - t0
    pos = [i for i in items if i["kind"] in ("I", "R26")]
    neg = [i for i in items if i["kind"].startswith("NEG_")]
    summ = {"seconds": dt, "per_ciphertext_s": dt / len(items)}
    for fam in ("I", "R26"):
        p = [i for i in pos if i["kind"] == fam]
        summ[fam] = {k: sum(i[k] for i in p) for k in ("family_ok", "plaintext_ok", "segmentation_ok", "setting_ok")}
        summ[fam]["n"] = len(p)
        summ[fam]["per_letter_min"] = min(i["best_per_letter"] for i in p)
        summ[fam]["ic_median"] = sorted(i["ic"] for i in p)[len(p) // 2]
    summ["negatives"] = {"n": len(neg), "per_letter_max": max(i["best_per_letter"] for i in neg),
                         "per_letter_median": sorted(i["best_per_letter"] for i in neg)[len(neg) // 2],
                         "max_known_word_letters": max(N - i["best_oov"] for i in neg)}
    Path(out).write_text(json.dumps({"summary": summ, "items": items}, indent=1) + "\n")
    print(json.dumps(summ, indent=1))
    for i in items:
        print(i["kind"], i.get("setting", ""), "->", i["best_family"], i["best_setting"], "%.2f" % i["best_per_letter"],
              "oovw", i["best_oov"], "ok" if i.get("plaintext_ok") else "", " ".join(i["best_words"])[:70])


if __name__ == "__main__":
    main()
