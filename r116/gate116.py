#!/usr/bin/env python3
"""R116 sealed synthetic gate (PREREGISTRATION section 3). Synthetic only: reads no K4 file and no published letter or
position. Usage: python3 -I r116/gate116.py OUT.json"""
import hashlib
import itertools
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(ROOT / "r115")]
import x115 as X  # noqa: E402
import ref115 as RF  # noqa: E402

SEED = 1160901
AZ = X.AZ
CLUE_WORDS = ("EASTNORTHEAST", "NORTHEAST", "BERLIN", "CLOCK")
TEXT = ROOT / "r33/data/source_carter_mace_1923_google_ocr.txt"
STRUCTURED = {1: [(1,)], 2: [(1, 1), (0, 1), (2, 25)], 3: [(0, 0, 1), (3, 23, 1), (1, 1, 1)],
              4: [(0, 0, 0, 1), (4, 20, 4, 25), (1, 1, 1, 1)]}
SOURCES = ("gate116.py", "run_target116.py", "evaluate116.py", "crosscheck116.py")


def corpus():
    return "".join(ch for ch in TEXT.read_text(errors="ignore").upper() if "A" <= ch <= "Z")


def window(rng, txt, n=97):
    while True:
        s = rng.randrange(0, len(txt) - n)
        w = txt[s:s + n]
        if not any(c in w for c in CLUE_WORDS):
            return w


def mask(rng):
    while True:
        a0, b0 = rng.randrange(0, 85), rng.randrange(0, 87)
        pos = set(range(a0, a0 + 13)) | set(range(b0, b0 + 11))
        if len(pos) == 24:
            return sorted(pos)


def keystream(a, seeds, d, n=97):
    k = list(seeds)
    while len(k) < n:
        k.append((sum(c * k[-j] for j, c in enumerate(a, start=1)) + d) % 26)
    return k


def encipher(pt, PA, CA, k):
    """c_n = CA[PA.index(p_n) + k_n]: PA, CA are 26-letter strings, so x = PA.index and y = CA.index."""
    return "".join(CA[(PA.index(ch) + k[n]) % 26] for n, ch in enumerate(pt))


def decipher(ct, PA, CA, k):
    return "".join(PA[(CA.index(ch) - k[n]) % 26] for n, ch in enumerate(ct))


def plant(rng, txt, a):
    pt = window(rng, txt)
    PA, CA = "".join(rng.sample(AZ, 26)), "".join(rng.sample(AZ, 26))
    k = keystream(a, [rng.randrange(26) for _ in a], rng.randrange(26))
    ct = encipher(pt, PA, CA, k)
    Q = mask(rng)
    return ct, {n: pt[n] for n in Q}, pt, Q


def main():
    out = Path(sys.argv[1])
    rng = random.Random(SEED)
    txt = corpus()
    t0w, t0c = time.time(), time.process_time()
    rep = {"round": "R116", "gate_type": "EXACT_CHECKER_CORRECTNESS", "seed": SEED}

    fails = 0
    for i in range(100):
        L = 1 + i % 6
        a = tuple(rng.randrange(26) for _ in range(L))
        d = rng.randrange(26)
        k = keystream(a, [rng.randrange(26) for _ in range(L)], d)
        PA, CA = "".join(rng.sample(AZ, 26)), "".join(rng.sample(AZ, 26))
        pt = window(rng, txt)
        ct = encipher(pt, PA, CA, k)
        ok = decipher(ct, PA, CA, k) == pt
        Q = list(range(97)) if i < 50 else mask(rng)
        hyp = {n: pt[n] for n in Q}
        state = k[Q[0]:Q[0] + L] + [d]

        def value(col):
            return PA.index(AZ[col]) if col < 26 else CA.index(AZ[col - 26]) if col < 52 else state[col - 52]
        for m in (2, 13):
            for coef, rhs in X.rows(ct, hyp, Q, tuple(v % m for v in a), m):
                ok = ok and (sum(cf * value(c) for c, cf in coef.items()) - rhs) % m == 0
        fails += not ok
    rep["V1_structure"] = {"messages": 100, "failures": fails, "pass": fails == 0}

    unsound = drop_unsound = 0
    for L in (1, 2, 3, 4):
        for i in range(50):
            a = STRUCTURED[L][i % len(STRUCTURED[L])] if i < 12 else tuple(rng.randrange(26) for _ in range(L))
            ct, hyp, pt, Q = plant(rng, txt, a)
            unsound += X.Checker(ct, hyp).verdict(a) != "OPEN"
            q = rng.choice(Q)
            hyp2 = dict(hyp)
            hyp2[q] = rng.choice([c for c in AZ if c != pt[q]])
            drop_unsound += X.Checker(ct, hyp2).verdict(a, allow_drop=True) == "EXCL_DROP"
    rep["V2_soundness"] = {"plants": 200, "true_vector_excluded": unsound, "wrong_letter_excl_drop": drop_unsound,
                           "pass": unsound == 0 and drop_unsound == 0}

    cells, dis = 0, 0
    for m in range(12):
        L = 1 + m % 3
        if m % 2 == 0:
            a0 = tuple(rng.randrange(26) for _ in range(L))
            ct, hyp, _, _ = plant(rng, txt, a0)
        else:
            a0 = None
            pt = window(rng, txt)
            ct = "".join(rng.choice(AZ) for _ in range(97))
            hyp = {n: pt[n] for n in mask(rng)}
        C = X.Checker(ct, hyp)
        vecs = (list(itertools.product(range(26), repeat=L)) if L <= 2
                else [tuple(rng.randrange(26) for _ in range(L)) for _ in range(100)])
        if a0 is not None:
            vecs.append(a0)
        for a in vecs:
            drop = L <= 2 and rng.random() < 0.3
            cells += 1
            dis += C.verdict(a, drop) != RF.verdict(ct, hyp, a, drop)
    rep["V3_two_implementations"] = {"messages": 12, "cells": cells, "disagreements": dis, "pass": dis == 0}

    rep["status"] = "COMPLETE"
    rep["gate_verdict"] = "GO" if all(rep[v]["pass"] for v in ("V1_structure", "V2_soundness", "V3_two_implementations")) \
        else "NO-GO"
    rep["wall_s"], rep["cpu_s"] = round(time.time() - t0w, 2), round(time.process_time() - t0c, 2)
    rep["source_sha256"] = {s: hashlib.sha256((HERE / s).read_bytes()).hexdigest() for s in SOURCES}
    out.write_text(json.dumps(rep, indent=1) + "\n")
    print(rep["gate_verdict"], json.dumps({v: rep[v]["pass"] for v in rep if v[:1] == "V"}))


if __name__ == "__main__":
    main()
