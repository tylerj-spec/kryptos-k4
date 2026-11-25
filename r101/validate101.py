#!/usr/bin/env python3
"""R101 checker-correctness gate (PREREGISTRATION section 4; synthetic only; reads no K4 file and no published
plaintext). Usage: python3 -I r101/validate101.py OUT.json [--dev-seed N]
--dev-seed: development smoke run with another seed; its output is DEVELOPMENT_ONLY and is never the gate."""
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
sys.path[:0] = [str(HERE), str(ROOT / "r99")]
import autokey99 as AK  # noqa: E402
import freealpha101 as FA  # noqa: E402
import dfs101 as DF  # noqa: E402

AZ = AK.AZ
SEED = 1010901
LAGS = (1, 2, 3, 4, 5)
SOURCES = ("freealpha101.py", "dfs101.py", "validate101.py", "run_target101.py", "evaluate101.py")


def windows(rng, lengths):
    while True:
        starts = [rng.randrange(0, 98 - L) for L in lengths]
        pos = set()
        for s, L in zip(starts, lengths):
            pos |= set(range(s, s + L))
        if len(pos) == sum(lengths):
            return sorted(pos)


def rand_text(rng, n=97):
    return "".join(rng.choice(AZ) for _ in range(n))


def rand_alpha(rng):
    return "".join(rng.sample(AZ, 26))


def plant(rng, A, L, s1, s2):
    pt = rand_text(rng)
    return pt, AK.encrypt(pt, A, L, s1, s2, rng.randrange(26), [rng.randrange(26) for _ in range(L)])


def main():
    out = Path(sys.argv[1])
    seed = int(sys.argv[3]) if len(sys.argv) == 4 and sys.argv[2] == "--dev-seed" else SEED
    rng = random.Random(seed)
    t0w, t0c = time.time(), time.process_time()
    rep = {"round": "R101", "gate_type": "EXACT_CHECKER_CORRECTNESS", "blind_recovery_certified": False,
           "seed": seed, "development_only": seed != SEED}

    fails = 0
    for _ in range(400):
        A, L = rand_alpha(rng), rng.choice(LAGS)
        s1, s2 = rng.choice(AK.SIGNS)
        c, pr = rng.randrange(26), [rng.randrange(26) for _ in range(L)]
        pt = rand_text(rng)
        fails += AK.decrypt(AK.encrypt(pt, A, L, s1, s2, c, pr), A, L, s1, s2, c, pr) != pt
    rep["V1_round_trip"] = {"cases": 400, "failures": fails, "pass": fails == 0}

    miss = decided = 0
    for _ in range(60):
        A, L = rand_alpha(rng), rng.choice(LAGS)
        s1, s2 = rng.choice(AK.SIGNS)
        pt, ct = plant(rng, A, L, s1, s2)
        st = FA.solve(ct, {p: pt[p] for p in windows(rng, [13, 11])}, L, s1, s2)[0]
        decided += st in ("FEASIBLE", "INFEASIBLE")
        miss += st == "INFEASIBLE"
    rep["V2_plants"] = {"plants": 60, "decided": decided, "missed": miss, "pass": miss == 0 and decided >= 40}   # AMENDMENT_1: bar 40 (registered 50)

    both = disagree = 0
    rows = []
    for k in range(32):
        L = rng.choice(LAGS)
        s1, s2 = rng.choice(AK.SIGNS)
        pos = windows(rng, [13, 11])
        if k % 2 == 0:
            pt, ct = plant(rng, rand_alpha(rng), L, s1, s2)
        else:
            pt, ct = rand_text(rng), rand_text(rng)
        obs = {p: pt[p] for p in pos}
        a = FA.solve(ct, obs, L, s1, s2)[0]
        b = DF.solve(ct, obs, L, s1, s2, node_cap=1_000_000)
        dec = a in ("FEASIBLE", "INFEASIBLE") and b in ("FEASIBLE", "INFEASIBLE")
        both += dec
        disagree += dec and a != b
        rows.append({"planted": k % 2 == 0, "L": L, "primary": a, "dfs": b})
    rep["V3_two_solvers"] = {"cells": 32, "both_decided": both, "disagreements": disagree, "rows": rows,
                             "pass": disagree == 0 and both >= 20}   # AMENDMENT_1: bar 20 (registered 24)

    miss = 0
    for _ in range(16):
        A = rand_alpha(rng)
        pt = rand_text(rng)
        ct = AK.condi_encrypt(pt, A, rng.randrange(1, 27))
        miss += FA.solve(ct, {p: pt[p] for p in windows(rng, [13, 11])}, 1, 1, 1)[0] != "FEASIBLE"
    rep["V4_condi"] = {"plants": 16, "missed": miss, "pass": miss == 0}

    scans, feas, und = [], 0, 0
    for _ in range(6):
        ct = rand_text(rng)
        obs = {p: rng.choice(AZ) for p in windows(rng, [13, 11])}
        w0, c0 = time.time(), time.process_time()
        st = [FA.solve(ct, obs, L, s1, s2)[0] for L in LAGS for s1, s2 in AK.SIGNS]
        scans.append({"wall_s": round(time.time() - w0, 3), "cpu_s": round(time.process_time() - c0, 3)})
        feas += st.count("FEASIBLE")
        und += st.count("UNDECIDED")
    fw = 2 * max(s["wall_s"] for s in scans) * 21 + 10
    fc = 2 * max(s["cpu_s"] for s in scans) * 21 + 10
    rep["V5_chance_and_throughput"] = {"cells": 120, "feasible": feas, "undecided": und, "scans": scans,
                                       "forecast_wall_s": round(fw, 1), "forecast_cpu_s": round(fc, 1),
                                       "limit_wall_s": 0.8 * 1800, "limit_cpu_s": 0.8 * 1200,
                                       "pass": fw < 0.8 * 1800 and fc < 0.8 * 1200}

    checks = [v["pass"] for key, v in rep.items() if key.startswith("V")]
    rep["status"] = "COMPLETE"
    rep["gate_verdict"] = "GO" if all(checks) else "NO-GO"
    if seed != SEED:
        rep["gate_verdict"] = "DEVELOPMENT_ONLY_" + rep["gate_verdict"]
    rep["wall_s"], rep["cpu_s"] = round(time.time() - t0w, 2), round(time.process_time() - t0c, 2)
    rep["source_sha256"] = {f: hashlib.sha256((HERE / f).read_bytes()).hexdigest() for f in SOURCES}
    out.write_text(json.dumps(rep, indent=1) + "\n")
    print(rep["gate_verdict"], json.dumps({key: v["pass"] for key, v in rep.items() if key.startswith("V")}))


if __name__ == "__main__":
    main()
