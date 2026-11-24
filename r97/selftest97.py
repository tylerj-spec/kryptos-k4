#!/usr/bin/env python3
"""R97 self-tests and the I_c speed rule (synthetic only; reads no panel file). Usage: selftest97.py MODEL.bin"""
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r97core as C  # noqa: E402
import witness97 as WIT  # noqa: E402


def case(rng):
    n = rng.randint(1, 4)
    lab = (rng.choice(list(C.ALPH)), rng.choice(list(C.ALPH)), n, rng.randrange(n), rng.randrange(26),
           rng.choice((1, -1)), rng.choice((1, -1)))
    W1, W2 = list(range(26)), list(range(26))
    rng.shuffle(W1)
    rng.shuffle(W2)
    pt = "".join(rng.choice(C.AZ) for _ in range(97))
    return lab, W1, W2, pt, WIT.encipher(pt, W1, W2, lab)


def main():
    model = C.Model(sys.argv[1])
    rng = random.Random(970901)
    rep = {}
    bad_rt = bad_sc = bad_gauge = 0
    for _ in range(40):
        lab, W1, W2, pt, ct = case(rng)
        U, V = WIT.invert(W1), WIT.invert(W2)
        bad_rt += C.decrypt(ct, U, V, lab) != pt
        keep = C.bind(ct, lab, model)
        g = rng.randrange(1, 26)
        Ug, Vg = [U[(y - g) % 26] for y in range(26)], [(V[x] + g) % 26 for x in range(26)]
        bad_gauge += C.decrypt(ct, Ug, Vg, lab) != pt
        for _ in range(5):
            Ur, Vr = list(range(26)), list(range(26))
            rng.shuffle(Ur)
            rng.shuffle(Vr)
            bad_sc += abs(C.joint(Ur, Vr) - model.score(C.decrypt(ct, Ur, Vr, lab))) > 1e-6
        del keep
    rep["T1_round_trip_gauge_and_score"] = {"cases": 40, "round_trip_failures": bad_rt, "gauge_failures": bad_gauge,
                                            "score_mismatches": bad_sc, "pass": bad_rt == bad_sc == bad_gauge == 0}
    bad = 0
    for _ in range(12):
        lab, W1, W2, pt, ct = case(rng)
        keep = C.bind(ct, lab, model)
        U, V = WIT.invert(W1), WIT.invert(W2)
        for side, fixed, start in (("U", V, None), ("U", V, U), ("V", U, None), ("V", U, V)):
            sc, w = C.cond(fixed, side, start, 2000, 2.0, rng.randrange(1, 2 ** 60))
            Uf, Vf = (w, V) if side == "U" else (U, w)
            bad += sorted(w) != list(range(26)) or abs(sc - model.score(C.decrypt(ct, Uf, Vf, lab))) > 1e-6
        del keep
    rep["T2_cond_returns_valid_states"] = {"runs": 48, "failures": bad, "pass": bad == 0}
    speeds = {}
    for side in ("U", "V"):
        lab, W1, W2, pt, ct = case(rng)
        keep = C.bind(ct, lab, model)
        fixed = WIT.invert(W2) if side == "U" else WIT.invert(W1)
        t = time.process_time()
        C.cond(fixed, side, None, 300000, 4.0, 12345)
        speeds[side] = 300000 / (time.process_time() - t)
        del keep
    s = min(speeds.values())
    Ic = int(0.6 * 700 * s / 4608 / 10000) * 10000
    rep["T3_speed"] = {"proposals_per_cpu_s": {k: round(v) for k, v in speeds.items()}, "s": round(s),
                       "rule": "I_c = floor(0.6*700*s/4608/10000)*10000", "pass": Ic >= 50000}
    rep["I_c"] = Ic
    rep["pass"] = all(v["pass"] for k, v in rep.items() if k.startswith("T"))
    (HERE / "selftest").mkdir(exist_ok=True)
    (HERE / "selftest/SELFTEST.json").write_text(json.dumps(rep, indent=1) + "\n")
    print("SELFTEST", "PASS" if rep["pass"] else "FAIL", "I_c =", Ic, rep["T3_speed"])


if __name__ == "__main__":
    main()
