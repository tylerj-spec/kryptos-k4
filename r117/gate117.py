#!/usr/bin/env python3
"""R117 sealed synthetic gate (PREREGISTRATION section 3). Synthetic only: reads no K4 file and no published letter or
position. Usage: python3 -I r117/gate117.py OUT.json"""
import hashlib
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(ROOT / "r112"), str(ROOT / "r98")]
import slidefair98 as SF  # noqa: E402
import x112 as X  # noqa: E402
import ref112 as RF  # noqa: E402

SEED = 1170901
AZ = SF.AZ
CLUE_WORDS = ("EASTNORTHEAST", "NORTHEAST", "BERLIN", "CLOCK")
TEXT = ROOT / "r33/data/source_carter_mace_1923_google_ocr.txt"
P_NAT = list(range(1, 13)) + [16, 24, 36, 47, None]
SOURCES = ("gate117.py", "run_target117.py", "evaluate117.py", "crosscheck117.py")


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
    return (pt[i], pt[i + 1]) if conv[1] == 0 else (pt[i + 1], pt[i])


def same_col(PA, CA, t, k, u, w):
    xw = (CA.index(w) - k) % 26 if t == "VIG" else (k - CA.index(w)) % 26
    return PA.index(u) == xw


def make_keys(rng, PA, CA, conv, pt, p, force_pos=None):
    """Periodic (p) or any-key (p None) pair keys; with force_pos, pairs inside it are made same-column w.p. 0.4."""
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


def eq_ok(e, A, B, kk):
    d, rhs = e
    val = sum(v * (A[c] if c < 26 else B[c - 26] if c < 52 else kk) for c, v in d.items())
    return (val - rhs) % 26 == 0


def main():
    out = Path(sys.argv[1])
    rng = random.Random(SEED)
    txt = corpus()
    t0w, t0c = time.time(), time.process_time()
    rep = {"round": "R117", "gate_type": "EXACT_CHECKER_CORRECTNESS", "seed": SEED}

    f_rt = f_eq = npairs = nsc = 0
    for k in range(150):
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
            f_eq += not all(eq_ok(e, A, B, keys[j]) for e in X.eqs((0, u, w, cu, cl), t, "S" if sc else "N"))
    rep["G1_structure"] = {"messages": 150, "pairs": npairs, "same_column_pairs": nsc, "round_trip_failures": f_rt,
                           "equation_failures": f_eq, "pass": f_rt == f_eq == 0}

    bad = bad_drop = 0
    sc_hist = {}
    for k in range(200):
        PA, CA = "".join(rng.sample(AZ, 26)), "".join(rng.sample(AZ, 26))
        conv = SF.CONVENTIONS[k % 16]
        pt = window(rng, txt)
        pos = mask(rng)
        p = P_NAT[k % len(P_NAT)] if k < 100 else None
        keys = make_keys(rng, PA, CA, conv, pt, p, force_pos=pos if k >= 100 else None)
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
    rep["G2_soundness"] = {"plants": 200,
                           "same_column_crib_pairs_histogram": dict(sorted(sc_hist.items(), key=lambda x: int(x[0]))),
                           "excluded_true": bad, "excluded_drop_with_one_error": bad_drop,
                           "pass": bad == 0 and bad_drop == 0}

    dis = cells = 0
    for _ in range(10):
        pos = mask(rng, 7, 5)
        ct = "".join(rng.choice(AZ) for _ in range(97))
        hyp = [rng.choice(AZ) if i in pos else None for i in range(97)]
        for conv in SF.CONVENTIONS:
            for p in (1, 2, 4, None):
                for dr in (False, True):
                    cells += 1
                    dis += X.check(ct, hyp, conv, p, allow_drop=dr) != RF.check(ct, hyp, conv, p, allow_drop=dr)
    full = 0
    for _ in range(30):
        pos = mask(rng)
        ct = "".join(rng.choice(AZ) for _ in range(97))
        hyp = [rng.choice(AZ) if i in pos else None for i in range(97)]
        conv = rng.choice(SF.CONVENTIONS)
        p = rng.choice(P_NAT)
        full += 1
        dis += X.check(ct, hyp, conv, p) != RF.check(ct, hyp, conv, p)
    rep["G3_two_implementations"] = {"small_mask_cells": cells, "full_mask_cells": full, "disagreements": dis,
                                     "pass": dis == 0}

    rep["status"] = "COMPLETE"
    rep["gate_verdict"] = "GO" if all(rep[g]["pass"] for g in ("G1_structure", "G2_soundness",
                                                                 "G3_two_implementations")) else "NO-GO"
    rep["wall_s"], rep["cpu_s"] = round(time.time() - t0w, 2), round(time.process_time() - t0c, 2)
    rep["source_sha256"] = {s: hashlib.sha256((HERE / s).read_bytes()).hexdigest() for s in SOURCES}
    out.write_text(json.dumps(rep, indent=1) + "\n")
    print(rep["gate_verdict"], json.dumps({g: rep[g]["pass"] for g in rep if g[:1] == "G" and g != "gate_type"
                                           and g != "gate_verdict"}))


if __name__ == "__main__":
    main()
