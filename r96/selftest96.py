#!/usr/bin/env python3
"""R96 self-tests and speed rule (synthetic only; reads no panel file). Fixes I (PREREGISTRATION section 3).
Usage: python3 -I r96/selftest96.py MODEL.bin      -> r96/selftest/SELFTEST.json"""
import ctypes
import itertools
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r96core as C  # noqa: E402
import witness96 as WIT  # noqa: E402


def rand_case(rng):
    lab = (rng.choice(list(C.ALPH)), rng.choice(list(C.ALPH)), rng.randint(1, 4), 0, rng.randrange(26),
           rng.choice((1, -1)), rng.choice((1, -1)))
    lab = (lab[0], lab[1], lab[2], rng.randrange(lab[2]), lab[4], lab[5], lab[6])
    W1, W2 = list(range(26)), list(range(26))
    rng.shuffle(W1)
    rng.shuffle(W2)
    pt = "".join(rng.choice(C.AZ) for _ in range(97))
    return lab, W1, W2, pt, WIT.enc(pt, W1, W2, *lab)


def inv(W):
    return WIT.forward(W)


def main():
    model = C.Model(sys.argv[1])
    L = C.lib()
    rng = random.Random(960901)
    rep = {}
    # 1 decrypt equals the witness's encipherment inverse; kernel score equals the reference scorer
    bad_rt = bad_sc = 0
    for _ in range(40):
        lab, W1, W2, pt, ct = rand_case(rng)
        U, V = inv(W1), inv(W2)
        bad_rt += C.decrypt(ct, U, V, lab) != pt
        case = C.Case(ct, lab, model)
        case.bind()
        for _ in range(5):
            Ur, Vr = list(range(26)), list(range(26))
            rng.shuffle(Ur)
            rng.shuffle(Vr)
            k = L.score_pair((ctypes.c_int * 26)(*Ur), (ctypes.c_int * 26)(*Vr))
            bad_sc += abs(k - model.score(C.decrypt(ct, Ur, Vr, lab))) > 1e-6
    rep["T1_round_trip_and_kernel_score"] = {"cases": 40, "round_trip_failures": bad_rt, "score_mismatches": bad_sc,
                                             "pass": bad_rt == 0 and bad_sc == 0}
    # 2 run_v1 / run_v2 return permutations and scores equal to the reference score of their decode
    bad = 0
    for mode in (0, 1):
        for _ in range(6):
            lab, W1, W2, pt, ct = rand_case(rng)
            U, V = inv(W1), inv(W2)
            sup = V if mode == 0 else U
            case = C.Case(ct, lab, model)
            case.bind()
            for v in (1, 2):
                w = (ctypes.c_int * 26)()
                seed = rng.randrange(1, 2 ** 60)
                if v == 1:
                    sc = L.run_v1((ctypes.c_int * 26)(*sup), mode, 3000, 4.0, seed, w)
                else:
                    st = C.assignment_start(ct, lab, mode, sup, model, seed)
                    case.bind()
                    sc = L.run_v2((ctypes.c_int * 26)(*sup), mode, 3000, 4.0, 1.0, seed, (ctypes.c_int * 26)(*st), w)
                W = list(w)
                Uf, Vf = (W, sup) if mode == 0 else (sup, W)
                bad += sorted(W) != list(range(26)) or abs(sc - model.score(C.decrypt(ct, Uf, Vf, lab))) > 1e-6
    rep["T2_runs_return_valid_states"] = {"runs": 24, "failures": bad, "pass": bad == 0}
    # 3 Hungarian equals brute force on 200 random 6x6 instances
    bad = 0
    for _ in range(200):
        M = [[rng.uniform(-5, 0) for _ in range(6)] for _ in range(6)]
        h = C.hungarian_max(M)
        best = max(sum(M[i][p[i]] for i in range(6)) for p in itertools.permutations(range(6)))
        bad += abs(sum(M[i][h[i]] for i in range(6)) - best) > 1e-9 or sorted(h) != list(range(6))
    rep["T3_hungarian_vs_brute_force"] = {"instances": 200, "failures": bad, "pass": bad == 0}
    # 4 speed (synthetic random inputs, both modes) -> I by the registered rule
    speeds = {}
    for mode in (0, 1):
        lab, W1, W2, pt, ct = rand_case(rng)
        sup = inv(W2) if mode == 0 else inv(W1)
        case = C.Case(ct, lab, model)
        case.bind()
        w = (ctypes.c_int * 26)()
        t = time.process_time()
        L.run_v1((ctypes.c_int * 26)(*sup), mode, 300000, 4.0, 12345, w)
        speeds[mode] = 300000 / (time.process_time() - t)
    s = min(speeds.values())
    I = int(0.6 * 450 * s / (96 * 16) / 10000) * 10000
    rep["T4_speed"] = {"proposals_per_cpu_s": {"U_searched": round(speeds[0]), "V_searched": round(speeds[1])},
                       "s": round(s), "rule": "I = floor(0.6*450*s/(96*16)/10000)*10000", "pass": I >= 100000}
    rep["I"] = I
    rep["pass"] = all(v["pass"] for k, v in rep.items() if k.startswith("T"))
    (HERE / "selftest").mkdir(exist_ok=True)
    (HERE / "selftest/SELFTEST.json").write_text(json.dumps(rep, indent=1) + "\n")
    print("SELFTEST", "PASS" if rep["pass"] else "FAIL", "I =", I, rep["T4_speed"])


if __name__ == "__main__":
    main()
