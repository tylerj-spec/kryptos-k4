#!/usr/bin/env python3
"""R115 registered run (PREREGISTRATION section 3): T1 structure, T2 soundness, T3 two implementations, T4 chance
power. Synthetic only (no K4 input). One random stream (seed 1150901) is used by T1-T4 in that order.
Usage: python3 -I r115/run115.py OUT.json"""
import hashlib
import itertools
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE)]
import x115 as X  # noqa: E402
import ref115 as RF  # noqa: E402

SEED = 1150901
AZ = X.AZ
CLUE_WORDS = ("EASTNORTHEAST", "NORTHEAST", "BERLIN", "CLOCK")
TEXT = ROOT / "r33/data/source_carter_mace_1923_google_ocr.txt"
STRUCTURED = {1: [(1,)], 2: [(1, 1), (0, 1), (2, 25)], 3: [(0, 0, 1), (3, 23, 1), (1, 1, 1)],
              4: [(0, 0, 0, 1), (4, 20, 4, 25), (1, 1, 1, 1)]}
SOURCES = ("x115.py", "ref115.py", "run115.py")


def corpus():
    return "".join(ch for ch in TEXT.read_text(errors="ignore").upper() if "A" <= ch <= "Z")


def window(rng, txt, n=97):
    while True:
        s = rng.randrange(0, len(txt) - n)
        w = txt[s:s + n]
        if not any(c in w for c in CLUE_WORDS):
            return w


def mask(rng, l1=13, l2=11):
    while True:
        a0, b0 = rng.randrange(0, 98 - l1), rng.randrange(0, 98 - l2)
        pos = set(range(a0, a0 + l1)) | set(range(b0, b0 + l2))
        if len(pos) == l1 + l2:
            return sorted(pos)


def perm(rng):
    v = list(range(26))
    rng.shuffle(v)
    return v


def encrypt(pt, x, y, a, seeds, d):
    """Forward from position 0: k_0..k_{L-1} = seeds, then the recurrence; c_n = y^-1(x(p_n) + k_n)."""
    L = len(a)
    k = list(seeds)
    while len(k) < len(pt):
        n = len(k)
        k.append((sum(a[j - 1] * k[n - j] for j in range(1, L + 1)) + d) % 26)
    yinv = [0] * 26
    for letter, v in enumerate(y):
        yinv[v] = letter
    return "".join(AZ[yinv[(x[AZ.index(ch)] + k[n]) % 26]] for n, ch in enumerate(pt)), k


def decrypt(ct, x, y, k):
    xinv = [0] * 26
    for letter, v in enumerate(x):
        xinv[v] = letter
    return "".join(AZ[xinv[(y[AZ.index(ch)] - k[n]) % 26]] for n, ch in enumerate(ct))


def plant(rng, txt, a):
    pt = window(rng, txt)
    x, y = perm(rng), perm(rng)
    ct, k = encrypt(pt, x, y, a, [rng.randrange(26) for _ in a], rng.randrange(26))
    Q = mask(rng)
    return ct, {n: pt[n] for n in Q}, pt, Q


def t1(rng, txt):
    fails = []
    for i in range(300):
        L = 1 + i % 6
        a = tuple(rng.randrange(26) for _ in range(L))
        seeds, d = [rng.randrange(26) for _ in range(L)], rng.randrange(26)
        x, y = perm(rng), perm(rng)
        pt = window(rng, txt)
        ct, k = encrypt(pt, x, y, a, seeds, d)
        ok = decrypt(ct, x, y, k) == pt
        Q = list(range(97)) if i < 150 else mask(rng)
        hyp = {n: pt[n] for n in Q}
        state = k[Q[0]:Q[0] + L] + [d]

        def value(col):
            return x[col] if col < 26 else y[col - 26] if col < 52 else state[col - 52]
        for m in (2, 13):
            for coef, rhs in X.rows(ct, hyp, Q, tuple(v % m for v in a), m):
                ok = ok and (sum(cf * value(c) for c, cf in coef.items()) - rhs) % m == 0
        if not ok:
            fails.append(i)
    return {"messages": 300, "failures": len(fails), "failed": fails}


def t2(rng, txt):
    unsound, drop_unsound, rows = 0, 0, []
    for L in (1, 2, 3, 4):
        for i in range(100):
            a = STRUCTURED[L][i % len(STRUCTURED[L])] if i < 25 else tuple(rng.randrange(26) for _ in range(L))
            ct, hyp, pt, Q = plant(rng, txt, a)
            v = X.Checker(ct, hyp).verdict(a)
            q = rng.choice(Q)
            hyp2 = dict(hyp)
            hyp2[q] = rng.choice([c for c in AZ if c != pt[q]])
            v2 = X.Checker(ct, hyp2).verdict(a, allow_drop=True)
            unsound += v != "OPEN"
            drop_unsound += v2 == "EXCL_DROP"
            rows.append({"L": L, "a": list(a), "verdict": v, "wrong_letter_verdict": v2})
    return {"plants": 400, "true_vector_excluded": unsound, "wrong_letter_excl_drop": drop_unsound, "rows": rows}


def t3(rng, txt):
    cells, dis, tally = 0, [], {}
    for m in range(24):
        L = 1 + m % 3
        planted = m % 2 == 0
        if planted:
            a0 = tuple(rng.randrange(26) for _ in range(L))
            ct, hyp, _, _ = plant(rng, txt, a0)
        else:
            pt = window(rng, txt)
            ct = "".join(rng.choice(AZ) for _ in range(97))
            hyp = {n: pt[n] for n in mask(rng)}
        C = X.Checker(ct, hyp)
        vecs = (list(itertools.product(range(26), repeat=L)) if L <= 2
                else [tuple(rng.randrange(26) for _ in range(L)) for _ in range(150)])
        if planted:
            vecs.append(a0)
        for a in vecs:
            drop = L <= 2 and rng.random() < 0.3
            v1, v2 = C.verdict(a, drop), RF.verdict(ct, hyp, a, drop)
            cells += 1
            tally[v1] = tally.get(v1, 0) + 1
            if v1 != v2:
                dis.append({"message": m, "L": L, "a": list(a), "x115": v1, "ref": v2})
    return {"messages": 24, "cells": cells, "disagreements": len(dis), "tally_x115": tally, "examples": dis[:20]}


def t4(rng, txt):
    out = {}
    for L in (1, 2, 3, 4):
        per = []
        for _ in range(40 if L <= 3 else 20):
            pt = window(rng, txt)
            ct = "".join(rng.choice(AZ) for _ in range(97))
            hyp = {n: pt[n] for n in mask(rng)}
            counts, _ = X.scan(ct, hyp, L, allow_drop=True)
            per.append(counts)
        n = len(per) * 26 ** L
        excl = sum(c["EXCL"] + c["EXCL_DROP"] for c in per) / n
        drop = sum(c["EXCL_DROP"] for c in per) / n
        shares = [(c["EXCL"] + c["EXCL_DROP"]) / 26 ** L for c in per]
        label = "ROBUST" if drop >= 0.50 else "TESTABLE" if excl >= 0.50 else "WEAK"
        out[str(L)] = {"messages": len(per), "vectors_per_message": 26 ** L, "excl_share": round(excl, 4),
                       "excl_drop_share": round(drop, 4), "excl_share_min": round(min(shares), 4),
                       "excl_share_max": round(max(shares), 4), "label": label, "per_message": per}
    return out


def main():
    out = Path(sys.argv[1])
    t0w, t0c = time.time(), time.process_time()
    rng = random.Random(SEED)
    txt = corpus()
    rep = {"round": "R115", "seed": SEED}
    for name, fn in (("T1", t1), ("T2", t2), ("T3", t3), ("T4", t4)):
        s = time.time()
        rep[name] = fn(rng, txt)
        rep[name]["wall_s"] = round(time.time() - s, 2)
        print(name, "done", rep[name]["wall_s"], "s", flush=True)
    passed = (rep["T1"]["failures"] == 0 and rep["T2"]["true_vector_excluded"] == 0
              and rep["T2"]["wrong_letter_excl_drop"] == 0 and rep["T3"]["disagreements"] == 0)
    rep["T1_T3_pass"] = passed
    rep["labels"] = {L: v["label"] for L, v in rep["T4"].items()}
    rep["wall_s"], rep["cpu_s"] = round(time.time() - t0w, 2), round(time.process_time() - t0c, 2)
    rep["source_sha256"] = {s: hashlib.sha256((HERE / s).read_bytes()).hexdigest() for s in SOURCES}
    out.write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps({"T1_T3_pass": passed, "labels": rep["labels"],
                      "T4": {L: {k: v[k] for k in ("excl_share", "excl_drop_share")} for L, v in rep["T4"].items()}}))


if __name__ == "__main__":
    main()
