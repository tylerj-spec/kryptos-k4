#!/usr/bin/env python3
"""R113 registered run (PREREGISTRATION sections 1-3): lag-21-adjacency decimation (mod 97, steps 37 / 60) plus periodic
substitution, IC-matched to K4, against R71's running-key baseline. Synthetic only; reads no K4 file.
Usage: python3 -I r113/run113.py OUT.json"""
import hashlib
import json
import random
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SEED = 1130901
N, LAG, R_BAR = 97, 21, 11
IC_LO, IC_HI = 0.0341, 0.0381
ATTEMPTS = 100_000
CLUE_WORDS = ("EASTNORTHEAST", "NORTHEAST", "BERLIN", "CLOCK")
TEXT = ROOT / "r33/data/source_carter_mace_1923_google_ocr.txt"
ARMS = ("D37_after", "D37_before", "D60_after", "D60_before", "RUNKEY")


def corpus():
    s = "".join(ch for ch in TEXT.read_text(errors="ignore").upper() if "A" <= ch <= "Z")
    h = len(s) // 2
    return [ord(c) - 65 for c in s[:h]], [ord(c) - 65 for c in s[h:]], s[:h], s[h:]


def window(rng, txt, raw, n=N):
    while True:
        s = rng.randrange(0, len(txt) - n)
        if not any(c in raw[s:s + n] for c in CLUE_WORDS):
            return txt[s:s + n]


def decimate(x, a):
    return [x[(a * j) % N] for j in range(N)]


def ic(c):
    cnt = Counter(c)
    return sum(v * (v - 1) for v in cnt.values()) / (N * (N - 1))


def R_counter(c, L):
    cnt = Counter((c[i], c[i + L]) for i in range(len(c) - L))
    return sum(v * (v - 1) // 2 for v in cnt.values())


def R_sorted(c, L):
    codes = sorted(c[i] * 26 + c[i + L] for i in range(len(c) - L))
    tot, run = 0, 1
    for a, b in zip(codes, codes[1:]):
        if a == b:
            run += 1
        else:
            tot += run * (run - 1) // 2
            run = 1
    return tot + run * (run - 1) // 2


def R71count(c, L):
    cnt = Counter((c[i], c[i + L]) for i in range(len(c) - L))
    return sum(max(v - 1, 0) for v in cnt.values())


def triples(c):
    cnt = Counter((c[i], c[i + LAG], c[i + 2 * LAG]) for i in range(len(c) - 2 * LAG))
    return sum(v * (v - 1) // 2 for v in cnt.values())


def periodic(x, rng, p):
    alph = [rng.sample(range(26), 26) for _ in range(p)]
    return [alph[i % p][v] for i, v in enumerate(x)]


def gen(arm, rng, ptxt, praw, ktxt, kraw):
    pt = window(rng, ptxt, praw)
    if arm == "RUNKEY":
        k = window(rng, ktxt, kraw)
        return [(a + b) % 26 for a, b in zip(pt, k)], None
    a = 37 if arm.startswith("D37") else 60
    p = rng.randrange(2, 31)
    if arm.endswith("after"):
        return periodic(decimate(pt, a), rng, p), p
    return decimate(periodic(pt, rng, p), a), p


def binom_cdf(k, n, q):
    """P(X <= k) for X ~ Binomial(n, q), summing k + 1 terms in log space (standard library)."""
    from math import exp, lgamma, log
    if k < 0:
        return 0.0
    if q <= 0.0:
        return 1.0
    if q >= 1.0:
        return 1.0 if k >= n else 0.0
    lq, l1q, c = log(q), log(1.0 - q), lgamma(n + 1)
    return min(1.0, sum(exp(c - lgamma(i + 1) - lgamma(n - i + 1) + i * lq + (n - i) * l1q) for i in range(k + 1)))


def cp_bounds(k, n, alpha=0.01):
    """Exact Clopper-Pearson interval by bisection; the cdf is decreasing in q."""
    def solve(f, target):
        lo, hi = 0.0, 1.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if f(mid) > target:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    lower = 0.0 if k == 0 else solve(lambda q: binom_cdf(k - 1, n, q), 1 - alpha / 2)
    upper = 1.0 if k == n else solve(lambda q: binom_cdf(k, n, q), alpha / 2)
    return lower, upper


def main():
    out = Path(sys.argv[1])
    rng = random.Random(SEED)
    ptxt, ktxt, praw, kraw = corpus()
    t0w, t0c = time.time(), time.process_time()
    rep = {"round": "R113", "seed": SEED, "attempts_per_arm": ATTEMPTS, "ic_window": [IC_LO, IC_HI], "R_bar": R_BAR}

    x = list(range(N))
    ok = True
    for a, lag in ((37, 21), (60, N - 21)):
        c = decimate(x, a)
        where = {v: j for j, v in enumerate(c)}
        ok &= all((where[m + 1] - where[m]) % N == lag for m in range(N - 1))
        inv = pow(a, -1, N)
        ok &= [c[(inv * m) % N] for m in range(N)] == x
    rep["C1_decimation"] = {"pass": ok}
    dis = 0
    for _ in range(1000):
        s = [rng.randrange(26) for _ in range(N)]
        dis += R_counter(s, LAG) != R_sorted(s, LAG)
    rep["C2_two_implementations"] = {"strings": 1000, "disagreements": dis, "pass": dis == 0}
    s_plain, s_shuf = [], []
    for _ in range(500):
        c = decimate(window(rng, ptxt, praw), 37)
        s_plain.append(R_counter(c, LAG))
        lst = list(c)
        rng.shuffle(lst)
        s_shuf.append(R_counter(lst, LAG))
    m1, m0 = sum(s_plain) / 500, sum(s_shuf) / 500
    v1 = sum((x - m1) ** 2 for x in s_plain) / 499
    v0 = sum((x - m0) ** 2 for x in s_shuf) / 499
    se = ((v1 + v0) / 500) ** 0.5
    # "far above" (PREREGISTRATION section 3) operationalized as a difference of more than 5 combined standard errors
    rep["C3_sanity_no_substitution"] = {"mean_R21_D37": round(m1, 3), "mean_R21_shuffled": round(m0, 3),
                                        "difference_in_se": round((m1 - m0) / se, 2), "pass": m1 - m0 > 5 * se}

    arms = {}
    for arm in ARMS:
        acc = q1 = q2 = 0
        tri = []
        bands = {}
        for _ in range(ATTEMPTS):
            c, p = gen(arm, rng, ptxt, praw, ktxt, kraw)
            if not (IC_LO <= ic(c) <= IC_HI):
                continue
            acc += 1
            r1 = R_counter(c, LAG) >= R_BAR
            q1 += r1
            q2 += R71count(c, LAG) >= R_BAR
            tri.append(triples(c))
            if p is not None:
                b = "2-5" if p <= 5 else "6-10" if p <= 10 else "11-20" if p <= 20 else "21-30"
                d = bands.setdefault(b, [0, 0])
                d[0] += r1
                d[1] += 1
        lo1, hi1 = cp_bounds(q1, acc)
        lo2, hi2 = cp_bounds(q2, acc)
        arms[arm] = {"accepted": acc, "acceptance": round(acc / ATTEMPTS, 4),
                     "q1_hits": q1, "q1": q1 / acc if acc else None, "q1_cp99": [lo1, hi1],
                     "q2_hits": q2, "q2": q2 / acc if acc else None, "q2_cp99": [lo2, hi2],
                     "mean_triple_repeats_21_42": round(sum(tri) / len(tri), 4) if tri else None,
                     "q1_by_period_band": {b: {"hits": d[0], "accepted": d[1]} for b, d in sorted(bands.items())}}
    base = arms["RUNKEY"]
    ratios = {}
    for arm in ARMS[:-1]:
        a = arms[arm]
        ratios[arm] = {"q1_conservative_ratio": (a["q1_cp99"][0] / base["q1_cp99"][1]) if base["q1_cp99"][1] > 0 else None,
                       "q1_point_ratio": (a["q1"] / base["q1"]) if base["q1"] else None,
                       "q2_conservative_ratio": (a["q2_cp99"][0] / base["q2_cp99"][1]) if base["q2_cp99"][1] > 0 else None}
    rep["arms"] = arms
    rep["ratios_vs_RUNKEY"] = ratios
    gates = all(rep[k]["pass"] for k in ("C1_decimation", "C2_two_implementations", "C3_sanity_no_substitution"))
    cont = any((r["q1_conservative_ratio"] or 0) >= 10 for r in ratios.values())
    rep["decision"] = "GATE_FAILED" if not gates else ("CONTINUE" if cont else "CLOSE")
    rep["wall_s"], rep["cpu_s"] = round(time.time() - t0w, 2), round(time.process_time() - t0c, 2)
    rep["source_sha256"] = {"run113.py": hashlib.sha256((HERE / "run113.py").read_bytes()).hexdigest()}
    out.write_text(json.dumps(rep, indent=1) + "\n")
    print(rep["decision"], json.dumps({a: {k: v for k, v in d.items() if k in ("acceptance", "q1_hits", "q1", "q2_hits")}
                                       for a, d in arms.items()}), json.dumps(ratios))


if __name__ == "__main__":
    main()
