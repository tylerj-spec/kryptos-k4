#!/usr/bin/env python3
"""R112 registered run (PREREGISTRATION section 3): T1 structure, T2 soundness, T3 two implementations, T4 chance
power. Synthetic only (no K4 input). Usage: python3 -I r112/run112.py OUT.json"""
import hashlib
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "r98")]
import slidefair98 as SF  # noqa: E402
import x112 as X  # noqa: E402
import ref112 as RF  # noqa: E402

SEED = 1120901
AZ = SF.AZ
CLUE_WORDS = ("EASTNORTHEAST", "NORTHEAST", "BERLIN", "CLOCK")
TEXT = ROOT / "r33/data/source_carter_mace_1923_google_ocr.txt"
P_NAT = list(range(1, 13)) + [16, 24, 36, None]
P_T4 = list(range(1, 13)) + [16, 24, 36, None]
SOURCES = ("x112.py", "ref112.py", "run112.py")


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
            return pos


def roles(pt, i, conv):
    t, r, o, a = conv
    return (pt[i], pt[i + 1]) if r == 0 else (pt[i + 1], pt[i])


def make_keys(rng, PA, CA, conv, pt, p, force_pos=None):
    """Periodic (p) or any-key (p None) keys; with force_pos, crib pairs are made same-column with prob. 0.4."""
    t = conv[0]
    starts = SF.pair_starts(97, conv[3])
    if p is not None:
        kp = [rng.randrange(26) for _ in range(p)]
        return [kp[j % p] for j in range(len(starts) + 10)]
    keys = []
    for i in starts:
        u, w = roles(pt, i, conv)
        if force_pos is not None and i in force_pos and i + 1 in force_pos and rng.random() < 0.4:
            keys.append((CA.index(w) - PA.index(u)) % 26 if t == "VIG" else (PA.index(u) + CA.index(w)) % 26)
        else:
            keys.append(rng.randrange(26))
    return keys + [rng.randrange(26) for _ in range(10)]


def same_col(PA, CA, t, k, u, w):
    xw = (CA.index(w) - k) % 26 if t == "VIG" else (k - CA.index(w)) % 26
    return PA.index(u) == xw


def eq_ok(d_rhs, A, B, kk, s_of):
    d, rhs = d_rhs
    val = 0
    for c, v in d.items():
        val += v * (A[c] if c < 26 else B[c - 26] if c < 52 else kk)
    return (val - rhs) % 26 == 0


def main():
    out = Path(sys.argv[1])
    rng = random.Random(SEED)
    txt = corpus()
    t0w, t0c = time.time(), time.process_time()
    rep = {"round": "R112", "seed": SEED}

    f_rt = f_eq = npairs = nsc = 0
    for k in range(300):
        PA, CA = "".join(rng.sample(AZ, 26)), "".join(rng.sample(AZ, 26))
        conv = SF.CONVENTIONS[k % 16]
        t, r, o, a = conv
        pt = "".join(rng.choice(AZ) for _ in range(97))
        p = None if k % 2 else rng.randrange(1, 13)
        keys = make_keys(rng, PA, CA, conv, pt, p, force_pos=set(range(97)) if p is None else None)
        ct = SF.encrypt(pt, PA, CA, conv, keys)
        f_rt += SF.decrypt(ct, PA, CA, conv, keys) != pt
        A = [PA.index(x) for x in AZ]
        B = [CA.index(x) for x in AZ]
        for j, i in enumerate(SF.pair_starts(97, a)):
            u, w = roles(pt, i, conv)
            cu, cl = (ct[i], ct[i + 1]) if o == 0 else (ct[i + 1], ct[i])
            sc = same_col(PA, CA, t, keys[j], u, w)
            nsc += sc
            npairs += 1
            f_eq += not all(eq_ok(e, A, B, keys[j], None) for e in X.eqs((0, u, w, cu, cl), t, "S" if sc else "N"))
    rep["T1_structure"] = {"messages": 300, "pairs": npairs, "same_column_pairs": nsc, "round_trip_failures": f_rt,
                           "equation_failures": f_eq, "pass": f_rt == f_eq == 0}

    bad = bad_drop = 0
    sc_hist = {}
    for k in range(400):
        PA, CA = "".join(rng.sample(AZ, 26)), "".join(rng.sample(AZ, 26))
        conv = SF.CONVENTIONS[k % 16]
        pt = window(rng, txt)
        pos = mask(rng)
        p = P_NAT[k % len(P_NAT)] if k < 200 else None
        keys = make_keys(rng, PA, CA, conv, pt, p, force_pos=pos if k >= 200 else None)
        ct = SF.encrypt(pt, PA, CA, conv, keys)
        hyp = [pt[i] if i in pos else None for i in range(97)]
        ns = sum(same_col(PA, CA, conv[0], keys[j], *roles(pt, i, conv))
                 for j, i in enumerate(SF.pair_starts(97, conv[3])) if i in pos and i + 1 in pos)
        sc_hist[str(ns)] = sc_hist.get(str(ns), 0) + 1
        bad += X.check(ct, hyp, conv, p) != "OPEN"
        j = rng.choice(sorted(pos))
        h2 = list(hyp)
        h2[j] = rng.choice([x for x in AZ if x != pt[j]])
        bad_drop += X.check(ct, h2, conv, p, allow_drop=True) != "OPEN"
    rep["T2_soundness"] = {"plants": 400, "same_column_crib_pairs_histogram": dict(sorted(sc_hist.items(), key=lambda x: int(x[0]))),
                           "excluded_true": bad, "excluded_drop_with_one_error": bad_drop,
                           "pass": bad == 0 and bad_drop == 0}

    dis = cells = 0
    for _ in range(15):
        pos = mask(rng, 7, 5)
        ct = "".join(rng.choice(AZ) for _ in range(97))
        hyp = [rng.choice(AZ) if i in pos else None for i in range(97)]
        for conv in SF.CONVENTIONS:
            for p in (1, 2, 4, None):
                for dr in (False, True):
                    cells += 1
                    dis += X.check(ct, hyp, conv, p, allow_drop=dr) != RF.check(ct, hyp, conv, p, allow_drop=dr)
    full = 0
    for _ in range(40):
        pos = mask(rng)
        ct = "".join(rng.choice(AZ) for _ in range(97))
        hyp = [rng.choice(AZ) if i in pos else None for i in range(97)]
        conv = rng.choice(SF.CONVENTIONS)
        p = rng.choice(P_T4)
        full += 1
        dis += X.check(ct, hyp, conv, p) != RF.check(ct, hyp, conv, p)
    rep["T3_two_implementations"] = {"small_mask_cells": cells, "full_mask_cells": full, "disagreements": dis,
                                     "pass": dis == 0}

    power = {}
    for _ in range(40):
        pos = mask(rng)
        ct = "".join(rng.choice(AZ) for _ in range(97))
        hyp = [rng.choice(AZ) if i in pos else None for i in range(97)]
        for conv in SF.CONVENTIONS:
            for p in P_T4:
                d = power.setdefault("any" if p is None else str(p), {"EXCL": 0, "EXCL_DROP": 0, "cells": 0})
                d["cells"] += 1
                if X.check(ct, hyp, conv, p) == "EXCL":
                    d["EXCL"] += 1
                    d["EXCL_DROP"] += X.check(ct, hyp, conv, p, allow_drop=True) == "EXCL"
    labels = {}
    for p, d in power.items():
        d["share_excl"] = round(d["EXCL"] / d["cells"], 4)
        d["share_excl_drop"] = round(d["EXCL_DROP"] / d["cells"], 4)
        labels[p] = "ROBUST" if d["share_excl_drop"] >= 0.5 else "TESTABLE" if d["share_excl"] >= 0.5 else "WEAK"
    rep["T4_chance_power"] = {"messages": 40, "by_period": power}

    gates = all(rep[g]["pass"] for g in ("T1_structure", "T2_soundness", "T3_two_implementations"))
    rep["labels_by_period"] = labels if gates else None
    rep["verdict"] = "GATE_FAILED" if not gates else "COMPLETE"
    rep["wall_s"], rep["cpu_s"] = round(time.time() - t0w, 2), round(time.process_time() - t0c, 2)
    rep["source_sha256"] = {f: hashlib.sha256((HERE / f).read_bytes()).hexdigest() for f in SOURCES}
    out.write_text(json.dumps(rep, indent=1) + "\n")
    print(rep["verdict"], json.dumps({k: {a: b for a, b in v.items() if a != "by_period"} if isinstance(v, dict) else v
                                      for k, v in rep.items() if k[:1] in "Tl"}))


if __name__ == "__main__":
    main()
