#!/usr/bin/env python3
"""R102 registered run (PREREGISTRATION section 3): checks C1-C6 on synthetic data only (no K4 input).
Usage: python3 -I r102/run102.py OUT.json"""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"
import hashlib  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "r100")]
import autokey100 as AK  # noqa: E402
import s3b102 as S  # noqa: E402
import dfs102 as D  # noqa: E402

SEED = 1020902                       # AMENDMENT_2 (approved): run v2 with a new seed; v1 was INCOMPLETE
AZ = AK.AZ
CLUE_WORDS = ("EASTNORTHEAST", "NORTHEAST", "BERLIN", "CLOCK")
SOURCES = ("s3b102.py", "dfs102.py", "run102.py", "AMENDMENT_1.md", "AMENDMENT_2.md")
TEXT = ROOT / "r33/data/source_carter_mace_1923_google_ocr.txt"


def corpus():
    return "".join(ch for ch in TEXT.read_text(errors="ignore").upper() if "A" <= ch <= "Z")


def window(rng, txt, n=97):
    while True:
        s = rng.randrange(0, len(txt) - n)
        w = txt[s:s + n]
        if not any(c in w for c in CLUE_WORDS):
            return w


def ralpha(rng):
    return "".join(rng.sample(AZ, 26))


def maps(A, B, F, s1, s2, c):
    """alpha, beta (letter -> Z26) and gamma (Z26 -> letter) of T1."""
    alpha = {l: (s1 * A.index(l)) % 26 for l in AZ}
    fr = A if F == "A" else B if F == "B" else AZ
    beta = {l: (s2 * fr.index(l)) % 26 for l in AZ}
    gamma = {z: B[(z + c) % 26] for z in range(26)}
    return alpha, beta, gamma


def plant(rng, txt, L):
    A, B = ralpha(rng), ralpha(rng)
    F = rng.choice(AK.FEEDBACK)
    s1, s2 = rng.choice(AK.SIGNS)
    pt = window(rng, txt)
    ct = AK.encrypt(pt, A, B, F, L, s1, s2, rng.randrange(26), [rng.randrange(26) for _ in range(L)])
    return pt, ct, F, s1, s2


def witness_ok(ct, pt, L, s1, s2, F, wit):
    A, B, c = wit
    return all(AK.enc_letter(pt[i], pt[i - L], A, B, F, s1, s2, c) == ct[i]
               for i in range(L, len(ct)) if pt[i] is not None and pt[i - L] is not None)


def R_stat(ct, L):
    pairs = {}
    for i in range(len(ct) - L):
        pairs[(ct[i], ct[i + L])] = pairs.get((ct[i], ct[i + L]), 0) + 1
    return sum(n * (n - 1) // 2 for n in pairs.values())


def main():
    out = Path(sys.argv[1])
    rng = random.Random(SEED)
    txt = corpus()
    t0w, t0c = time.time(), time.process_time()
    rep = {"round": "R102", "seed": SEED, "corpus_letters": len(txt)}

    bad = 0
    for _ in range(400):
        A, B = ralpha(rng), ralpha(rng)
        F = rng.choice(AK.FEEDBACK)
        L = rng.randrange(1, 97)
        s1, s2 = rng.choice(AK.SIGNS)
        c = rng.randrange(26)
        pt = "".join(rng.choice(AZ) for _ in range(97))
        ct = AK.encrypt(pt, A, B, F, L, s1, s2, c, [rng.randrange(26) for _ in range(L)])
        al, be, ga = maps(A, B, F, s1, s2, c)
        bad += any(ct[i] != ga[(al[pt[i]] + be[pt[i - L]]) % 26] for i in range(L, 97))
    rep["C1_reduction"] = {"cases": 400, "failures": bad, "pass": bad == 0}

    bad = 0
    units = [k for k in range(26) if k % 2 and k != 13]
    for _ in range(200):
        al = dict(zip(AZ, rng.sample(range(26), 26)))
        be = dict(zip(AZ, rng.sample(range(26), 26)))
        gperm = rng.sample(AZ, 26)
        ga = {z: gperm[z] for z in range(26)}
        t, u, k = rng.randrange(26), rng.randrange(26), rng.choice(units)
        kinv = pow(k, -1, 26)
        al2 = {l: (k * (v + t)) % 26 for l, v in al.items()}
        be2 = {l: (k * (v + u)) % 26 for l, v in be.items()}
        ga2 = {z: ga[(kinv * z - t - u) % 26] for z in range(26)}
        bad += any(ga[(al[b] + be[a]) % 26] != ga2[(al2[b] + be2[a]) % 26] for a in AZ for b in AZ)
    rep["C2_gauge"] = {"cases": 200, "failures": bad, "pass": bad == 0}

    lags = [1, 2, 3, 5, 8, 13, 21, 40]
    inc = badw = und = und_unconfirmed = 0
    for k in range(120):                                  # AMENDMENT_1 (approved): soundness over both solvers
        L = lags[k % len(lags)]
        pt, ct, F, s1, s2 = plant(rng, txt, L)
        for n in (97, 60):
            hyp = list(pt[:n]) + [None] * (97 - n)
            st, d, wit = S.solve(ct, hyp, L, s1, s2, F)
            if st == "UNDECIDED":
                und += 1
                dst = D.solve(ct, hyp, L, s1, s2, F, node_cap=2_000_000)
                und_unconfirmed += dst != "CONSISTENT"
            else:
                dst = D.solve(ct, hyp, L, s1, s2, F)
            inc += st == "INCONSISTENT" or dst == "INCONSISTENT"
            badw += st == "CONSISTENT" and not witness_ok(ct, hyp, L, s1, s2, F, wit)
    rep["C3_soundness"] = {"hypotheses": 240, "inconsistent_by_either": inc, "primary_undecided": und,
                           "undecided_not_confirmed_by_dfs": und_unconfirmed, "bad_witnesses": badw,
                           "amendment": "AMENDMENT_1 (approved)",
                           "pass": inc == 0 and und_unconfirmed == 0 and badw == 0}

    both = dis = 0
    rows = []
    for k in range(60):
        L = rng.choice([1, 2, 3, 5, 8])
        pt, ct, F, s1, s2 = plant(rng, txt, L)
        n = 97 if k % 2 else 60
        src = pt if k < 30 else window(rng, txt)
        hyp = list(src[:n]) + [None] * (97 - n)
        a = S.solve(ct, hyp, L, s1, s2, F)[0]
        b = D.solve(ct, hyp, L, s1, s2, F)
        dec = a in ("CONSISTENT", "INCONSISTENT") and b in ("CONSISTENT", "INCONSISTENT")
        both += dec
        dis += dec and a != b
        rows.append({"true": k < 30, "n": n, "L": L, "F": F, "primary": a, "dfs": b})
    rep["C4_two_solvers"] = {"cases": 60, "both_decided": both, "disagreements": dis, "rows": rows,
                             "pass": dis == 0 and both >= 40}

    cons = und = n_ = 0
    dims, eqs = [], []
    for _ in range(40):
        while True:
            a0, b0 = rng.randrange(0, 85), rng.randrange(0, 87)
            pos = set(range(a0, a0 + 13)) | set(range(b0, b0 + 11))
            if len(pos) == 24:
                break
        ct = "".join(rng.choice(AZ) for _ in range(97))
        hyp = [rng.choice(AZ) if i in pos else None for i in range(97)]
        for L in range(1, 11):
            for F in AK.FEEDBACK:
                s1, s2 = rng.choice(AK.SIGNS)
                R = S.rows(ct, hyp, L, s1, s2, F)
                if not R:
                    continue
                used = sorted({c for r in R for c in range(S.NV) if r[c] % 26})     # AMENDMENT_2: dimension by
                sp = S.affine_space(R, used, 13)                                    # elimination only; the DFS
                d = len(sp[1]) if sp is not None else None                          # alone decides the cell
                st = D.solve(ct, hyp, L, s1, s2, F, node_cap=50_000)
                n_ += 1
                cons += st == "CONSISTENT"
                und += st == "UNDECIDED"
                eqs.append(len(R))
                if d is not None:
                    dims.append(d)
    rep["C5_crib_shape"] = {"cells": n_, "consistent": cons, "undecided": und,
                            "share_consistent": round(cons / max(1, n_ - und), 4),
                            "max_equations": max(eqs), "min_d13": min(dims) if dims else None,
                            "prediction_ge_90pct": cons / max(1, n_ - und) >= 0.90}

    c6 = {}
    for L in (1, 2, 3):
        pl, sh = [], []
        for _ in range(200):
            pt, ct, F, s1, s2 = plant(rng, txt, L)
            pl.append(R_stat(ct, L))
            lst = list(ct)
            rng.shuffle(lst)
            sh.append(R_stat("".join(lst), L))
        q95 = sorted(sh)[int(0.95 * len(sh))]
        c6[str(L)] = {"plant_mean": round(sum(pl) / len(pl), 3), "shuffle_mean": round(sum(sh) / len(sh), 3),
                      "shuffle_q95": q95, "power_gt_q95": round(sum(x > q95 for x in pl) / len(pl), 3)}
    rep["C6_lag_pairs"] = c6

    rep["verdict"] = "VERIFIED" if all(rep[k]["pass"] for k in ("C1_reduction", "C2_gauge", "C3_soundness",
                                                                  "C4_two_solvers")) else "FAILED"
    rep["wall_s"], rep["cpu_s"] = round(time.time() - t0w, 2), round(time.process_time() - t0c, 2)
    rep["source_sha256"] = {f: hashlib.sha256((HERE / f).read_bytes()).hexdigest() for f in SOURCES}
    out.write_text(json.dumps(rep, indent=1) + "\n")
    print(rep["verdict"], json.dumps({k: v.get("pass", v) if isinstance(v, dict) and "pass" in v else None
                                      for k, v in rep.items() if k[:1] == "C"}))


if __name__ == "__main__":
    main()
