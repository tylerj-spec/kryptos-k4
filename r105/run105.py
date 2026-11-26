#!/usr/bin/env python3
"""R105 registered run (PREREGISTRATION section 3): gates G1a, G1b, G2, G3; M1 plants; M2 nulls; E1 sigma unknown.
Synthetic only (no K4 input). Usage: python3 -I r105/run105.py OUT.json"""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"
import hashlib  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "r100")]
import autokey100 as AK  # noqa: E402
import solve105 as S  # noqa: E402

SEED_PLANTS, SEED_SOLVER = 1050901, 1050902
AZ = AK.AZ
CLUE_WORDS = ("EASTNORTHEAST", "NORTHEAST", "BERLIN", "CLOCK")
TEXT = ROOT / "r33/data/source_carter_mace_1923_google_ocr.txt"
GUARD_CPU = 1300.0
REC, REC2 = 90, 80
SOURCES = ("solve105.py", "run105.py")


def corpus():
    return "".join(ch for ch in TEXT.read_text(errors="ignore").upper() if "A" <= ch <= "Z")


def window(rng, txt, n=97):
    while True:
        s = rng.randrange(0, len(txt) - n)
        w = txt[s:s + n]
        if not any(c in w for c in CLUE_WORDS):
            return w


def make_plant(rng, txt, L, s1, s2):
    A, B = "".join(rng.sample(AZ, 26)), "".join(rng.sample(AZ, 26))
    c = rng.randrange(26)
    pt = window(rng, txt)
    ct = AK.encrypt(pt, A, B, "A", L, s1, s2, c, [rng.randrange(26) for _ in range(L)])
    return {"A": A, "B": B, "c": c, "pt": pt, "ct": ct, "L": L, "s1": s1, "s2": s2}


def reencrypts(out, ct, B, L, s1, s2):
    """G3: the output (A, c') with the supplied B, L and signs reproduces the ciphertext at positions L..96."""
    P, A, c = out["plaintext"], out["A"], out["c"]
    return all(AK.enc_letter(P[i], P[i - L], A, B, "A", s1, s2, c) == ct[i] for i in range(L, len(ct)))


def letters(a, b):
    return sum(x == y for x, y in zip(a, b))


def main():
    out_path = Path(sys.argv[1])
    rng = random.Random(SEED_PLANTS)
    srng = random.Random(SEED_SOLVER)
    txt = corpus()
    t0w, t0c = time.time(), time.process_time()
    cpu = lambda: time.process_time() - t0c  # noqa: E731
    rep = {"round": "R105", "seed_plants": SEED_PLANTS, "seed_solver": SEED_SOLVER,
           "solver": {"N_stage1": S.N_STAGE1, "K_stage2": S.K_STAGE2, "K_stage3": S.K_STAGE3, "quick": S.QUICK,
                      "full": S.FULL, "T0": S.T0}}
    g3_total = g3_bad = 0

    # G1a gauge identity
    bad = 0
    for k in range(100):
        L = k % 8 + 1
        s1, s2 = AK.SIGNS[k % 4]
        p = make_plant(rng, txt, L, s1, s2)
        z0 = S.gauge_truth(p["A"], p["c"], s1, s2, L, p["pt"])
        y = np.array([p["B"].index(ch) for ch in p["ct"]])
        x = S.apply_offsets(S.chain_ranks(y, L, s1, s2, z0[0], [0] * L), L, -s1 * s2, (0,) + z0[1:])
        o0 = p["A"].index(p["pt"][0])
        bad += any(int(x[i]) != (p["A"].index(p["pt"][i]) - o0) % 26 for i in range(97))
    rep["G1a_gauge"] = {"plants": 100, "failures": bad, "pass": bad == 0}

    # G1b sign reflection
    bad = 0
    for k in range(100):
        L = k % 8 + 1
        s1, s2 = AK.SIGNS[k % 4]
        p = make_plant(rng, txt, L, s1, s2)
        Aref = "".join(p["A"][(-v) % 26] for v in range(26))
        ct2 = AK.encrypt(p["pt"], Aref, p["B"], "A", L, -s1, -s2, p["c"], [0] * L)
        bad += ct2[L:] != p["ct"][L:]
    rep["G1b_reflection"] = {"plants": 100, "failures": bad, "pass": bad == 0}

    # G2 stage-1 table against a direct count
    bad = pts = 0
    for k in range(20):
        L = k % 5 + 1
        s1, s2 = rng.choice(AK.SIGNS)
        p = make_plant(rng, txt, L, s1, s2)
        sig = -s1 * s2
        y = np.array([p["B"].index(ch) for ch in p["ct"]])
        X0 = [S.chain_ranks(y, L, s1, s2, cc, [0] * L) for cc in range(26)]
        G = np.stack([S.sumsq_grid(X0[cc], L, sig) for cc in range(26)])
        zs = [tuple(rng.randrange(26) for _ in range(L)) for _ in range(50)]
        zs.append(S.gauge_truth(p["A"], p["c"], s1, s2, L, p["pt"]))
        for z in zs:
            n = np.bincount(S.apply_offsets(X0[z[0]], L, sig, (0,) + z[1:]), minlength=26)
            pts += 1
            bad += float(G[z]) != float((n * n).sum())
    rep["G2_stage1_reference"] = {"points": pts, "mismatches": bad, "pass": bad == 0}

    # M1 plants
    rows = []
    for L in range(1, 6):
        for j in range(10):
            sig = 1 if j < 5 else -1
            s1, s2 = rng.choice([sp for sp in AK.SIGNS if -sp[0] * sp[1] == sig])
            p = make_plant(rng, txt, L, s1, s2)
            tr = {"z0": S.gauge_truth(p["A"], p["c"], s1, s2, L, p["pt"])}
            o = S.solve(p["ct"], p["B"], L, s1, s2, srng, trace=tr)
            n = letters(o["plaintext"], p["pt"])
            ok3 = reencrypts(o, p["ct"], p["B"], L, s1, s2)
            g3_total += 1
            g3_bad += not ok3
            true_score = S.qs([AZ.index(ch) for ch in p["pt"]])
            if n >= REC:
                lost = None
            elif tr["stage1_rank"] is None:
                lost = "stage1"
            elif tr["stage2_rank"] >= S.K_STAGE2:
                lost = "stage2"
            elif tr["stage3_rank"] >= S.K_STAGE3:
                lost = "stage3"
            else:
                lost = "scorer" if true_score <= o["score"] else "annealer"
            rows.append({"L": L, "sigma": sig, "signs": [s1, s2], "letters": n, "score": o["score"],
                         "true_plaintext_score": true_score, "stage1_rank": tr["stage1_rank"],
                         "stage2_rank": tr["stage2_rank"], "stage3_rank": tr["stage3_rank"],
                         "selected_is_truth": tr["selected_is_truth"], "lost_at": lost, "reencrypts": ok3})
    rec = [r for r in rows if r["letters"] >= REC]
    by_lag = {str(L): sum(r["letters"] >= REC for r in rows if r["L"] == L) for L in range(1, 6)}
    by_cell = {f"L{L}_sigma{s:+d}": sum(r["letters"] >= REC for r in rows if r["L"] == L and r["sigma"] == s)
               for L in range(1, 6) for s in (1, -1)}
    lost = {}
    for r in rows:
        if r["lost_at"]:
            lost[r["lost_at"]] = lost.get(r["lost_at"], 0) + 1
    rep["M1_plants"] = {"plants": len(rows), "recovered_ge90": len(rec), "recovered_ge80": sum(r["letters"] >= REC2 for r in rows),
                        "recovered_by_lag": by_lag, "recovered_by_lag_sigma": by_cell, "unrecovered_lost_at": lost,
                        "rows": rows, "cpu_after_s": round(cpu(), 1)}

    # M2 nulls
    nulls = []
    for k in range(30):
        kind = ("random_ciphertext", "wrong_B", "wrong_L")[k // 10]
        L = k % 5 + 1
        s1, s2 = rng.choice(AK.SIGNS)
        if kind == "random_ciphertext":
            B = "".join(rng.sample(AZ, 26))
            ct = "".join(rng.choice(AZ) for _ in range(97))
            Ls = L
        else:
            p = make_plant(rng, txt, L, s1, s2)
            ct = p["ct"]
            if kind == "wrong_B":
                B, Ls = "".join(rng.sample(AZ, 26)), L
            else:
                B, Ls = p["B"], rng.choice([v for v in range(1, 6) if v != L])
        o = S.solve(ct, B, Ls, s1, s2, srng)
        ok3 = reencrypts(o, ct, B, Ls, s1, s2)
        g3_total += 1
        g3_bad += not ok3
        nulls.append({"kind": kind, "L_solved": Ls, "signs": [s1, s2], "score": o["score"], "reencrypts": ok3})
    M = max(r["score"] for r in nulls)
    above = sum(r["score"] > M for r in rec)
    rep["M2_nulls"] = {"nulls": len(nulls), "max_score_M": M,
                       "max_by_kind": {kd: max(r["score"] for r in nulls if r["kind"] == kd)
                                       for kd in ("random_ciphertext", "wrong_B", "wrong_L")},
                       "recovered_above_M": above, "recovered": len(rec),
                       "share_recovered_above_M": round(above / len(rec), 4) if rec else None,
                       "unrecovered_above_M": sum(r["score"] > M for r in rows if r["letters"] < REC),
                       "rows": nulls, "cpu_after_s": round(cpu(), 1)}

    # E1 sigma unknown (exploratory; time guard)
    e1, truncated = [], False
    for k in range(10):
        if cpu() >= GUARD_CPU:
            truncated = True
            break
        L = k % 5 + 1
        sig = 1 if k % 2 == 0 else -1
        s1, s2 = rng.choice([sp for sp in AK.SIGNS if -sp[0] * sp[1] == sig])
        p = make_plant(rng, txt, L, s1, s2)
        res = {}
        for cell in ((1, -1), (1, 1)):
            o = S.solve(p["ct"], p["B"], L, *cell, srng)
            ok3 = reencrypts(o, p["ct"], p["B"], L, *cell)
            g3_total += 1
            g3_bad += not ok3
            res[-cell[0] * cell[1]] = (o["score"], letters(o["plaintext"], p["pt"]))
        best_sig = max(res, key=lambda s: res[s][0])
        e1.append({"L": L, "sigma": sig, "score_sigma_plus": res[1][0], "score_sigma_minus": res[-1][0],
                   "best_sigma": best_sig, "best_is_true_sigma": best_sig == sig,
                   "best_letters": res[best_sig][1], "best_recovered": res[best_sig][1] >= REC})
    rep["E1_sigma_unknown"] = {"plants": len(e1), "truncated": truncated,
                               "best_is_true_sigma": sum(r["best_is_true_sigma"] for r in e1),
                               "best_recovered": sum(r["best_recovered"] for r in e1), "rows": e1}

    rep["G3_reencryption"] = {"outputs": g3_total, "failures": g3_bad, "pass": g3_bad == 0}
    gates = all(rep[g]["pass"] for g in ("G1a_gauge", "G1b_reflection", "G2_stage1_reference", "G3_reencryption"))
    bar_m1 = len(rec) >= 35 and all(v >= 5 for v in by_lag.values())
    bar_det = bool(rec) and above / len(rec) >= 0.90
    rep["bars"] = {"M1_ge35_and_ge5_per_lag": bar_m1, "detection_ge90pct_above_M": bar_det}
    rep["verdict"] = "GATE_FAILED" if not gates else "GO" if (bar_m1 and bar_det) else "NO_POWER"
    rep["wall_s"], rep["cpu_s"] = round(time.time() - t0w, 2), round(cpu(), 2)
    rep["source_sha256"] = {f: hashlib.sha256((HERE / f).read_bytes()).hexdigest() for f in SOURCES}
    out_path.write_text(json.dumps(rep, indent=1) + "\n")
    print(rep["verdict"], json.dumps({k: {a: b for a, b in v.items() if a != "rows"} if isinstance(v, dict) else v
                                      for k, v in rep.items() if k[:1] in "GMEb"}))


if __name__ == "__main__":
    main()
