#!/usr/bin/env python3
"""R71 run (ciphertext-only; no decryption of K4, no published letters). Deterministic seeds.
  1. Reference: 100,000 shuffles of K4 (seed 710001) fix m_w, s_w for T2.
  2. K4: T1, T2 (and descriptive D, A_7, R_21, IC).
  3. SHUF: 1,000,000 fresh K4 shuffles (seed 710002).
  4. Each family (seed 710010 + index): batches of 20,000 until 100,000 IC-matched ciphertexts or 3,000,000 attempts.
     Matched = |IC - IC(K4)| <= 0.004 and >= 25 distinct letters (as R67). The first 200,000 attempts are also kept,
     unmatched, as a secondary analysis.
  5. Joint event J: T1 >= T1(K4) and T2 >= T2(K4). Descriptive fixed-width event F: A_7 >= 5 and R_21 >= 11.
  6. Decision (pre-registered in r71/PREREGISTRATION.md), written to OUT/SUMMARY.json.
Usage: python3 -I r71/run.py SRC_DIR OUT_DIR"""
import hashlib
import json
import sys
import time
from math import exp, lgamma, log, log1p
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "r71"))
import features as F  # noqa: E402
import generators as G  # noqa: E402

K4_FILE = ROOT / "r39/ic_gate/k4_ciphertext.txt"
K4_SHA256 = "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
SOURCES = {"2360.txt": "cf90331a7e235cb117742f8aef111aa28ce76be458e9ce2bc09db55344431edd",
           "974.txt": "a84841ca18ea01ca11ca2ea2bc38d312758ed1570cc91b5447a9356166c13cae",
           "558.txt": "3311ea0e2c85065d81299be5246c186696362aaa0cd4fa314166888cfed3857c"}
N_REF, N_SHUF, BATCH, TARGET, MAX_ATTEMPTS, N_UNMATCHED = 100_000, 1_000_000, 20_000, 100_000, 3_000_000, 200_000
IC_TOL, MIN_DIST = 0.004, 25
CANDIDATES = ("PERIODIC", "HOMOPHONIC", "GROMARK", "CTAK", "PTAK")
BASELINES = ("SHUF", "OTP", "RUNKEY")
ALPHA = 0.01   # family-wise 0.05 over 5 candidate families; two-sided bounds at ALPHA / 2 each


def letters(path):
    t = path.read_text(encoding="utf-8", errors="ignore").upper()
    return np.frombuffer("".join(c for c in t if "A" <= c <= "Z").encode(), dtype=np.uint8).astype(np.int16) - 65


def _pmf_sum(n, p, lo, hi):
    """sum_{i=lo..hi} Binomial(n, p) pmf, in log space (exact enough for i <= a few hundred)."""
    if p <= 0:
        return 1.0 if lo == 0 else 0.0
    if p >= 1:
        return 1.0 if hi == n else 0.0
    lp, lq, ln = log(p), log1p(-p), lgamma(n + 1)
    return sum(exp(ln - lgamma(i + 1) - lgamma(n - i + 1) + i * lp + (n - i) * lq) for i in range(lo, hi + 1))


def cp_bounds(k, n, a):
    """Exact Clopper-Pearson one-sided bounds at level a each: lower bound solves P(X >= k) = a, upper solves
    P(X <= k) = a (bisection). Counts above 300 use the normal approximation."""
    ph = k / n
    if k > 300:
        z = 2.5758293035489  # a = 0.005
        se = (ph * (1 - ph) / n) ** 0.5
        return max(0.0, ph - z * se), min(1.0, ph + z * se)
    lo = 0.0
    if k > 0:
        a_, b_ = 0.0, ph
        for _ in range(80):
            m = (a_ + b_) / 2
            a_, b_ = (m, b_) if 1 - _pmf_sum(n, m, 0, k - 1) < a else (a_, m)
        lo = a_
    a_, b_ = ph, 1.0
    for _ in range(80):
        m = (a_ + b_) / 2
        a_, b_ = (m, b_) if _pmf_sum(n, m, 0, k) > a else (a_, m)
    return lo, b_


def evaluate(f, k4):
    J = (f["T1"] >= k4["T1"] - 1e-9) & (f["T2"] >= k4["T2"] - 1e-9)
    Fx = (f["A7"] >= 5) & (f["R21"] >= 11)
    return J, Fx


def summarise(f, par, k4):
    J, Fx = evaluate(f, k4)
    n = len(J)
    out = {"n": int(n), "joint": int(J.sum()), "q_joint": J.sum() / n, "fixed_7_21": int(Fx.sum()),
           "T1_ge_k4": int((f["T1"] >= k4["T1"] - 1e-9).sum()), "T2_ge_k4": int((f["T2"] >= k4["T2"] - 1e-9).sum()),
           "IC_mean": float(f["IC"].mean())}
    lo, hi = cp_bounds(out["joint"], n, ALPHA / 2)
    out["q_lo"], out["q_hi"] = lo, hi
    if par is not None:
        by = {}
        for v in np.unique(par):
            sel = par == v
            by[int(v)] = [int(sel.sum()), int(J[sel].sum())]
        out["by_param"] = by
    return out


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    if (out / "SUMMARY.json").exists():
        raise SystemExit("refusing to overwrite")
    raw = K4_FILE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == K4_SHA256, "K4 ciphertext hash"
    for fn, h in SOURCES.items():
        assert hashlib.sha256((src / fn).read_bytes()).hexdigest() == h, fn
    k4c = F.to_int(raw.decode().strip())
    pt = np.concatenate([letters(src / "2360.txt"), letters(src / "974.txt")])
    kt = letters(src / "558.txt")
    routes = [[int(x) for x in l.split()[2].split(",")] for l in (ROOT / "r61/routes.txt").read_text().splitlines()]
    t0 = time.time()
    rr = np.random.default_rng(710001)
    ref = F.reference(np.array([rr.permutation(k4c) for _ in range(N_REF)]))
    k4f = {k: float(v[0]) for k, v in F.all_features(k4c[None, :], ref).items()}
    print("K4", k4f, flush=True)
    res = {"K4": k4f, "reference_shuffles": N_REF, "families": {}}
    rs = np.random.default_rng(710002)
    shuf_f = []
    for b in range(N_SHUF // BATCH):
        C = np.array([rs.permutation(k4c) for _ in range(BATCH)])
        shuf_f.append(F.all_features(C, ref))
    sf = {k: np.concatenate([x[k] for x in shuf_f]) for k in shuf_f[0]}
    res["families"]["SHUF"] = {"matched": summarise(sf, None, k4f), "attempts": N_SHUF}
    print("SHUF", res["families"]["SHUF"]["matched"], f"{time.time() - t0:.0f}s", flush=True)
    for i, arm in enumerate(G.ARMS):
        rg = np.random.default_rng(710010 + i)
        mf, mp, uf, up, att = [], [], [], [], 0
        nm = 0
        while nm < TARGET and att < MAX_ATTEMPTS:
            C, par = G.gen(arm, rg, BATCH, pt, kt, routes)
            att += BATCH
            I, nd = F.ic(C)
            sel = (np.abs(I - k4f["IC"]) <= IC_TOL) & (nd >= MIN_DIST)
            if att <= N_UNMATCHED:
                uf.append(F.all_features(C, ref))
                up.append(par)
            if sel.any():
                mf.append(F.all_features(C[sel], ref))
                mp.append(par[sel])
                nm += int(sel.sum())
        cat = lambda L: {k: np.concatenate([x[k] for x in L]) for k in L[0]}  # noqa: E731
        res["families"][arm] = {"attempts": att, "acceptance": nm / att,
                                "matched": summarise(cat(mf), np.concatenate(mp), k4f),
                                "unmatched": summarise(cat(uf), np.concatenate(up), k4f)}
        print(arm, att, nm, {k: res["families"][arm]["matched"][k] for k in ("joint", "q_joint", "fixed_7_21")},
              f"{time.time() - t0:.0f}s", flush=True)
    res["decision"] = decide(res)
    (out / "SUMMARY.json").write_text(json.dumps(res, indent=1, default=float) + "\n")
    print("DECISION", json.dumps(res["decision"], indent=1, default=float))


def decide(res):
    fam = res["families"]
    q0 = fam["SHUF"]["matched"]["q_joint"]
    d = {"q_shuf": q0}
    if q0 > 0.01:
        d["outcome"] = "NOT_DISTINCTIVE"
        return d
    base = {b: fam[b]["matched"] for b in BASELINES}
    bmax = max(base, key=lambda b: base[b]["q_joint"])
    d["baseline_max"] = bmax
    rows = {}
    for c in CANDIDATES:
        m = fam[c]["matched"]
        qb = base[bmax]["q_joint"]
        ratio = m["q_joint"] / qb if qb > 0 else float("inf")
        lb = min(m["q_lo"] / base[b]["q_hi"] for b in BASELINES)
        ub = m["q_hi"] / base[bmax]["q_lo"] if base[bmax]["q_lo"] > 0 else float("inf")
        status = "PROMISING" if m["joint"] >= 30 and ratio >= 10 and lb > 3 else "NOT_ENRICHED" if ub < 10 else "LOW_POWER"
        rows[c] = {"joint": m["joint"], "ratio": ratio, "ratio_lower_bound": lb, "ratio_upper_bound": ub, "status": status}
    d["candidates"] = rows
    st = [r["status"] for r in rows.values()]
    d["outcome"] = "PROMISING" if "PROMISING" in st else "LOW_POWER" if "LOW_POWER" in st else "NO_FAMILY"
    d["promising"] = [c for c, r in rows.items() if r["status"] == "PROMISING"]
    return d


if __name__ == "__main__":
    main()
