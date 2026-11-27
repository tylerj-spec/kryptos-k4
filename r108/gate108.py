#!/usr/bin/env python3
"""R108 sealed synthetic gate (PREREGISTRATION section 3). Synthetic only: reads no K4 file and no published letter or
position. Usage: python3 -I r108/gate108.py OUT.json"""
import hashlib
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(ROOT / "r107"), str(ROOT / "r98")]
import slidefair98 as SF  # noqa: E402
import x107 as X  # noqa: E402
import ref107 as RF  # noqa: E402

SEED = 1080901
AZ = SF.AZ
CLUE_WORDS = ("EASTNORTHEAST", "NORTHEAST", "BERLIN", "CLOCK")
TEXT = ROOT / "r33/data/source_carter_mace_1923_google_ocr.txt"
P_V2 = list(range(1, 13)) + [16, 24, 36, 47, None]
P_ALL = list(range(1, 48)) + [None]
SOURCES = ("gate108.py", "run_target108.py", "evaluate108.py", "crosscheck108.py")


def corpus():
    return "".join(ch for ch in TEXT.read_text(errors="ignore").upper() if "A" <= ch <= "Z")


def window(rng, txt, n=97):
    while True:
        s = rng.randrange(0, len(txt) - n)
        w = txt[s:s + n]
        if not any(c in w for c in CLUE_WORDS):
            return w


def mask(rng):
    while True:
        a0, b0 = rng.randrange(0, 85), rng.randrange(0, 87)
        pos = set(range(a0, a0 + 13)) | set(range(b0, b0 + 11))
        if len(pos) == 24:
            return pos


def keyseq(rng, p, n=60):
    if p is None:
        return [rng.randrange(26) for _ in range(n)]
    kp = [rng.randrange(26) for _ in range(p)]
    return [kp[j % p] for j in range(n)]


def roles(pt, ct, i, conv):
    t, r, o, a = conv
    u, w = (pt[i], pt[i + 1]) if r == 0 else (pt[i + 1], pt[i])
    cu, cl = (ct[i], ct[i + 1]) if o == 0 else (ct[i + 1], ct[i])
    return u, w, cu, cl


def same_column(PA, CA, t, k, u, w):
    xw = (CA.index(w) - k) % 26 if t == "VIG" else (k - CA.index(w)) % 26
    return PA.index(u) == xw


def main():
    out = Path(sys.argv[1])
    rng = random.Random(SEED)
    txt = corpus()
    t0w, t0c = time.time(), time.process_time()
    rep = {"round": "R108", "gate_type": "EXACT_CHECKER_CORRECTNESS", "seed": SEED}

    f = {"round_trip": 0, "identity": 0, "equation": 0, "pair_map": 0}
    npairs = 0
    for k in range(200):
        PA, CA = "".join(rng.sample(AZ, 26)), "".join(rng.sample(AZ, 26))
        conv = SF.CONVENTIONS[k % 16]
        t, r, o, a = conv
        pt = "".join(rng.choice(AZ) for _ in range(97))
        keys = keyseq(rng, rng.randrange(1, 13))
        ct = SF.encrypt(pt, PA, CA, conv, keys)
        f["round_trip"] += SF.decrypt(ct, PA, CA, conv, keys) != pt
        A = {l: PA.index(l) for l in AZ}
        B = {l: CA.index(l) for l in AZ}
        for j, i in enumerate(SF.pair_starts(97, a)):
            kk = keys[j]
            u, w, cu, cl = roles(pt, ct, i, conv)
            npairs += 1
            f["identity"] += cu == u
            sc = same_column(PA, CA, t, kk, u, w)
            if t == "VIG":
                ok = ((A[cu] - A[u] - 1) % 26 == 0 and (B[cl] - B[w] - 1) % 26 == 0) if sc else \
                     ((A[cu] - B[w] + kk) % 26 == 0 and (B[cl] - A[u] - kk) % 26 == 0)
                sig = {x: PA[(B[x] - kk) % 26] for x in AZ}
            else:
                ok = ((A[cu] - A[u] - 1) % 26 == 0 and (B[cl] - B[w] + 1) % 26 == 0) if sc else \
                     ((A[cu] + B[w] - kk) % 26 == 0 and (B[cl] + A[u] - kk) % 26 == 0)
                sig = {x: PA[(kk - B[x]) % 26] for x in AZ}
            f["equation"] += not ok
            if not sc:
                inv = {v: x for x, v in sig.items()}
                f["pair_map"] += not (cu == sig[w] and cl == inv[u])
    rep["V1_structure"] = {"messages": 200, "pairs": npairs, "failures": f, "pass": not any(f.values())}

    bad, dist, cells = 0, {}, []
    for k in range(400):
        PA, CA = "".join(rng.sample(AZ, 26)), "".join(rng.sample(AZ, 26))
        conv = SF.CONVENTIONS[k % 16]
        t, r, o, a = conv
        p = P_V2[k % len(P_V2)]
        pt = window(rng, txt)
        keys = keyseq(rng, p)
        ct = SF.encrypt(pt, PA, CA, conv, keys)
        pos = mask(rng)
        hyp = [pt[i] if i in pos else None for i in range(97)]
        ns = sum(same_column(PA, CA, t, keys[j], *roles(pt, ct, i, conv)[:2])
                 for j, i in enumerate(SF.pair_starts(97, a)) if i in pos and i + 1 in pos)
        st = X.check(ct, hyp, conv, p)
        key = f"same_col_{min(ns, 2)}{'+' if ns >= 2 else ''}:{st}"
        dist[key] = dist.get(key, 0) + 1
        bad += (st != "OPEN" and ns == 0) or (st == "EXCLUDED_DROP" and ns <= 1)
        cells.append((ct, hyp, conv, p))
    rep["V2_soundness"] = {"plants": 400, "failures": bad, "by_same_column_and_verdict": dict(sorted(dist.items())),
                           "pass": bad == 0}

    for _ in range(4):
        pos = mask(rng)
        ct = "".join(rng.choice(AZ) for _ in range(97))
        hyp = [rng.choice(AZ) if i in pos else None for i in range(97)]
        cells += [(ct, hyp, conv, p) for conv in SF.CONVENTIONS for p in P_ALL]
    dis = sum(X.check(*c) != X.check(*c, collision=RF.collision_rank) for c in cells)
    rep["V3_two_implementations"] = {"cells": len(cells), "disagreements": dis, "pass": dis == 0}

    rep["status"] = "COMPLETE"
    rep["gate_verdict"] = "GO" if all(rep[v]["pass"] for v in ("V1_structure", "V2_soundness", "V3_two_implementations")) \
        else "NO-GO"
    rep["wall_s"], rep["cpu_s"] = round(time.time() - t0w, 2), round(time.process_time() - t0c, 2)
    rep["source_sha256"] = {s: hashlib.sha256((HERE / s).read_bytes()).hexdigest() for s in SOURCES}
    out.write_text(json.dumps(rep, indent=1) + "\n")
    print(rep["gate_verdict"], json.dumps({v: rep[v]["pass"] for v in rep if v[:1] == "V"}))


if __name__ == "__main__":
    main()
