#!/usr/bin/env python3
"""R104 registered run (PREREGISTRATION section 3): E1 landscape, E2 reductions, E3 prototype P1 (B known, F = A),
E4 prototype P2 (A known, F = A, L = 1). Synthetic only. Usage: python3 -I r104/run104.py OUT.json"""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(ROOT / "r100")]
import autokey100 as AK  # noqa: E402

SEED = 1040901
AZ = AK.AZ
CLUE_WORDS = ("EASTNORTHEAST", "NORTHEAST", "BERLIN", "CLOCK")
TEXT = ROOT / "r33/data/source_carter_mace_1923_google_ocr.txt"
Q = np.fromfile(ROOT / "k4kit/data/quad_log10.f32", dtype=np.float32).reshape(26, 26, 26, 26)


def corpus():
    return "".join(ch for ch in TEXT.read_text(errors="ignore").upper() if "A" <= ch <= "Z")


def window(rng, txt, n=97):
    while True:
        s = rng.randrange(0, len(txt) - n)
        w = txt[s:s + n]
        if not any(c in w for c in CLUE_WORDS):
            return w


def qs(p):
    p = np.asarray(p)
    return float(Q[p[:-3], p[1:-2], p[2:-1], p[3:]].sum())


def anneal_perm(score, rng, iters=30000, T0=3.5, restarts=6):
    """Maximise score(perm) over permutations of 26 by swap annealing; returns (score, perm)."""
    best = (-1e18, None)
    for _ in range(restarts):
        m = np.array(rng.sample(range(26), 26))
        cur = score(m)
        bl = (cur, m.copy())
        for it in range(iters):
            t = T0 * (1 - it / iters) + 1e-3
            x, y = rng.randrange(26), rng.randrange(26)
            if x == y:
                continue
            m[x], m[y] = m[y], m[x]
            s = score(m)
            if s >= cur or rng.random() < math.exp((s - cur) / t):
                cur = s
            else:
                m[x], m[y] = m[y], m[x]
            if cur > bl[0]:
                bl = (cur, m.copy())
        if bl[0] > best[0]:
            best = bl
    return best


def ic(x):
    n = np.bincount(x, minlength=26)
    return float((n * (n - 1)).sum()) / (len(x) * (len(x) - 1))


def ranks_B_known(y, L, s1, s2, c, offs):
    """Reduction (a): x_i = s1*(y_i - c) + sigma*x_{i-L}, x_r = offs[r] for r < L."""
    sig = -s1 * s2
    x = np.zeros(len(y), dtype=np.int64)
    for r in range(L):
        x[r] = offs[r] % 26
    for i in range(L, len(y)):
        x[i] = (s1 * (y[i] - c) + sig * x[i - L]) % 26
    return x


def P1(ct, B, L, s1, s2, rng):
    y = np.array([B.index(ch) for ch in ct])
    cands = []
    for c in range(26):
        offs = [0] * L
        for _ in range(2):
            for r in range(1, L):
                offs[r] = max(range(26), key=lambda v: ic(ranks_B_known(y, L, s1, s2, c, offs[:r] + [v] + offs[r + 1:])))
        cands.append((ic(ranks_B_known(y, L, s1, s2, c, offs)), c, tuple(offs)))
    cands.sort(reverse=True)
    best = (-1e18, None)
    for _, c, offs in cands[:3]:
        x = ranks_B_known(y, L, s1, s2, c, list(offs))
        sc, perm = anneal_perm(lambda m: qs(m[x]), rng)
        if sc > best[0]:
            best = (sc, "".join(AZ[v] for v in perm[x]))
    return best[1]


def code_model(A, s1, s2):
    """Code-trigram log-probabilities for A known, F = A, L = 1: code g(p, q) = s1*a(q) + s2*a(p)."""
    a = np.array([A.index(ch) for ch in AZ])
    G = (s1 * a[None, :] + s2 * a[:, None]) % 26
    P4 = np.power(10.0, Q.astype(np.float64))
    P4 /= P4.sum()
    T = np.zeros(26 ** 3)
    idx = G[:, :, None, None] * 676 + G[None, :, :, None] * 26 + G[None, None, :, :]
    np.add.at(T, idx.reshape(-1), P4.reshape(-1))
    return np.log10(T.reshape(26, 26, 26) + 1e-12), a


def decode_code(C, m, a, s1, s2, first):
    ainv = np.argsort(a)
    x = [a[first]]
    for i in range(1, len(C)):
        x.append((s1 * (m[C[i]] - s2 * x[-1])) % 26)
    return [int(ainv[v]) for v in x]


def P2(ct, A, s1, s2, rng, B=None, c=None):
    T, a = code_model(A, s1, s2)
    C = np.array([ord(ch) - 65 for ch in ct])
    score = lambda m: float(T[m[C[:-2]], m[C[1:-1]], m[C[2:]]].sum())  # noqa: E731
    sc, m = anneal_perm(score, rng)
    best = max((decode_code(C, m, a, s1, s2, f) for f in range(26)), key=qs)
    diag = None
    if B is not None:
        true_m = np.array([(B.index(AZ[l]) - c) % 26 for l in range(26)])
        diag = {"true_map_score": round(score(true_m), 2), "found_map_score": round(sc, 2)}
    return "".join(AZ[v] for v in best), diag


def main():
    out = Path(sys.argv[1])
    rng = random.Random(SEED)
    txt = corpus()
    t0w, t0c = time.time(), time.process_time()
    rep = {"round": "R104", "seed": SEED}
    rand_alpha = lambda: "".join(rng.sample(AZ, 26))  # noqa: E731

    land = {}
    for k in range(120):
        A, B = rand_alpha(), rand_alpha()
        F = AK.FEEDBACK[k % 3]
        L = (1, 2, 3, 5)[k % 4]
        s1, s2 = rng.choice(AK.SIGNS)
        c = rng.randrange(26)
        pr = [rng.randrange(26) for _ in range(L)]
        pt = window(rng, txt)
        ct = AK.encrypt(pt, A, B, F, L, s1, s2, c, pr)
        for which in ("A", "B"):
            for nsw in (1, 2):
                X = list(A if which == "A" else B)
                for _ in range(nsw):
                    i, j = rng.sample(range(26), 2)
                    X[i], X[j] = X[j], X[i]
                X = "".join(X)
                d = AK.decrypt(ct, X if which == "A" else A, X if which == "B" else B, F, L, s1, s2, c, pr)
                land.setdefault(f"F={F} swap_{which} x{nsw}", []).append(sum(a == b for a, b in zip(d, pt)) / 97)
    E1 = {k: round(sum(v) / len(v), 3) for k, v in sorted(land.items())}
    pred = all((E1[k] >= 0.80) if k.startswith("F=A swap_A") else (E1[k] <= 0.60) for k in E1)
    rep["E1_landscape"] = {"mean_fraction_correct": E1, "prediction_holds": pred}

    fa = fb = fz = 0
    for _ in range(100):
        A, B = rand_alpha(), rand_alpha()
        L = rng.choice([1, 2, 3, 5, 8])
        s1, s2 = rng.choice(AK.SIGNS)
        c = rng.randrange(26)
        pt = window(rng, txt)
        ct = AK.encrypt(pt, A, B, "A", L, s1, s2, c, [rng.randrange(26) for _ in range(L)])
        x = ranks_B_known(np.array([B.index(ch) for ch in ct]), L, s1, s2, c, [A.index(pt[r]) for r in range(L)])
        fa += "".join(A[v] for v in x) != pt
        fb += any((B.index(ct[i]) - c) % 26 != (s1 * A.index(pt[i]) + s2 * A.index(pt[i - L])) % 26 for i in range(L, 97))
        ct2 = AK.encrypt(pt, A, B, "AZ", L, s1, s2, c, [rng.randrange(26) for _ in range(L)])
        fz += any((B.index(ct2[i]) - c) % 26 != (s1 * A.index(pt[i]) + s2 * AZ.index(pt[i - L])) % 26 for i in range(L, 97))
    rep["E2_identities"] = {"cases": 100, "a_B_known_FA_failures": fa, "b_A_known_FA_failures": fb,
                            "b_A_known_FAZ_failures": fz, "pass": fa == fb == fz == 0}

    rec, rows = 0, []
    for k in range(24):
        L = (1, 2, 3)[k % 3]
        A, B = rand_alpha(), rand_alpha()
        s1, s2 = rng.choice(AK.SIGNS)
        c = rng.randrange(26)
        pt = window(rng, txt)
        ct = AK.encrypt(pt, A, B, "A", L, s1, s2, c, [rng.randrange(26) for _ in range(L)])
        dec = P1(ct, B, L, s1, s2, rng)
        n = sum(a == b for a, b in zip(dec, pt))
        rec += n >= 90
        rows.append({"L": L, "sigma": -s1 * s2, "letters": n})
    rep["E3_P1_B_known"] = {"plants": 24, "recovered": rec, "rows": rows, "gate_for_R105": rec >= 12}

    rec, rows, gaps, counter = 0, [], 0, 0
    for k in range(24):
        A, B = rand_alpha(), rand_alpha()
        s1, s2 = rng.choice(AK.SIGNS)
        c = rng.randrange(26)
        pt = window(rng, txt)
        ct = AK.encrypt(pt, A, B, "A", 1, s1, s2, c, [rng.randrange(26)])
        dec, diag = P2(ct, A, s1, s2, rng, B=B, c=c)
        n = sum(a == b for a, b in zip(dec, pt))
        rec += n >= 90
        gaps += diag["true_map_score"] > diag["found_map_score"]
        counter += diag["true_map_score"] < diag["found_map_score"]
        rows.append({"letters": n, **diag})
    rep["E4_P2_A_known"] = {"plants": 24, "recovered": rec, "search_gaps": gaps, "objective_counterexamples": counter,
                            "rows": rows, "gate_for_R105": rec >= 12}

    rep["R105_entry"] = {"B_known_F_A": rep["E2_identities"]["pass"] and rep["E3_P1_B_known"]["gate_for_R105"],
                         "A_known_F_A_L1": rep["E2_identities"]["pass"] and rep["E4_P2_A_known"]["gate_for_R105"]}
    rep["wall_s"], rep["cpu_s"] = round(time.time() - t0w, 2), round(time.process_time() - t0c, 2)
    rep["source_sha256"] = {"run104.py": hashlib.sha256((HERE / "run104.py").read_bytes()).hexdigest()}
    out.write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps({k: (v if not isinstance(v, dict) else {a: b for a, b in v.items() if a != "rows"})
                      for k, v in rep.items() if k[:1] in "ER"}))


if __name__ == "__main__":
    main()
