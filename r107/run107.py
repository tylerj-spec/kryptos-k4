#!/usr/bin/env python3
"""R107 registered run (PREREGISTRATION section 4): T1 structure, T2 soundness, T3 two implementations, T4 chance
power, T5 ciphertext-only invariant. Synthetic only (no K4 input). Usage: python3 -I r107/run107.py OUT.json"""
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
import x107 as X  # noqa: E402
import ref107 as RF  # noqa: E402

SEED = 1070901
AZ = SF.AZ
CLUE_WORDS = ("EASTNORTHEAST", "NORTHEAST", "BERLIN", "CLOCK")
TEXT = ROOT / "r33/data/source_carter_mace_1923_google_ocr.txt"
P_T2 = list(range(1, 13)) + [16, 24, None]
P_T4 = list(range(1, 13)) + [16, 24, 36, None]
SOURCES = ("x107.py", "ref107.py", "run107.py")


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


def T_m(s, m):
    tot = 0
    for c in range(m):
        cnt = {}
        for ch in s[c::m]:
            cnt[ch] = cnt.get(ch, 0) + 1
        tot += sum(n * (n - 1) // 2 for n in cnt.values())
    return tot


def aligned(pt, conv):
    """The plaintext as seen by the ciphertext positions: swapped inside each pair when o == r, in place otherwise."""
    t, r, o, a = conv
    s = list(pt)
    if o == r:
        for i in SF.pair_starts(len(pt), a):
            s[i], s[i + 1] = s[i + 1], s[i]
    return "".join(s)


def main():
    out = Path(sys.argv[1])
    rng = random.Random(SEED)
    txt = corpus()
    t0w, t0c = time.time(), time.process_time()
    rep = {"round": "R107", "seed": SEED}

    # T1 structure
    f_round = f_id = f_eq = f_map = f_align = npairs = nsame = 0
    for k in range(400):
        PA, CA = "".join(rng.sample(AZ, 26)), "".join(rng.sample(AZ, 26))
        conv = SF.CONVENTIONS[k % 16]
        t, r, o, a = conv
        pt = "".join(rng.choice(AZ) for _ in range(97))
        keys = keyseq(rng, rng.randrange(1, 13))
        ct = SF.encrypt(pt, PA, CA, conv, keys)
        f_round += SF.decrypt(ct, PA, CA, conv, keys) != pt
        al = aligned(pt, conv)
        A = {l: PA.index(l) for l in AZ}
        B = {l: CA.index(l) for l in AZ}
        for j, i in enumerate(SF.pair_starts(97, a)):
            kk = keys[j]
            u, w, cu, cl = roles(pt, ct, i, conv)
            npairs += 1
            f_id += cu == u
            sc = same_column(PA, CA, t, kk, u, w)
            nsame += sc
            if t == "VIG":
                ok = ((A[cu] - A[u] - 1) % 26 == 0 and (B[cl] - B[w] - 1) % 26 == 0) if sc else \
                     ((A[cu] - B[w] + kk) % 26 == 0 and (B[cl] - A[u] - kk) % 26 == 0)
                sig = {x: PA[(B[x] - kk) % 26] for x in AZ}
            else:
                ok = ((A[cu] - A[u] - 1) % 26 == 0 and (B[cl] - B[w] + 1) % 26 == 0) if sc else \
                     ((A[cu] + B[w] - kk) % 26 == 0 and (B[cl] + A[u] - kk) % 26 == 0)
                sig = {x: PA[(kk - B[x]) % 26] for x in AZ}
            f_eq += not ok
            if not sc:
                inv = {v: x for x, v in sig.items()}
                f_map += not (cu == sig[w] and cl == inv[u])
                # alignment: each ciphertext letter is sigma or sigma^-1 of the aligned plaintext letter there
                f_align += not (ct[i + o] == sig[al[i + o]] and ct[i + 1 - o] == inv[al[i + 1 - o]])
    rep["T1_structure"] = {"messages": 400, "pairs": npairs, "same_column_pairs": nsame, "round_trip_failures": f_round,
                           "identity_failures": f_id, "equation_failures": f_eq, "pair_map_failures": f_map,
                           "alignment_failures": f_align,
                           "pass": f_round == f_id == f_eq == f_map == f_align == 0}

    # T2 soundness
    bad, dist, t2cells = 0, {}, []
    for k in range(400):
        PA, CA = "".join(rng.sample(AZ, 26)), "".join(rng.sample(AZ, 26))
        conv = SF.CONVENTIONS[k % 16]
        t, r, o, a = conv
        p = P_T2[k % len(P_T2)]
        pt = window(rng, txt)
        keys = keyseq(rng, p)
        ct = SF.encrypt(pt, PA, CA, conv, keys)
        pos = mask(rng)
        hyp = [pt[i] if i in pos else None for i in range(97)]
        ns = 0
        for j, i in enumerate(SF.pair_starts(97, a)):
            if i in pos and i + 1 in pos:
                u, w, _, _ = roles(pt, ct, i, conv)
                ns += same_column(PA, CA, t, keys[j], u, w)
        st = X.check(ct, hyp, conv, p)
        key = f"same_col_{min(ns, 2)}{'+' if ns >= 2 else ''}:{st}"
        dist[key] = dist.get(key, 0) + 1
        bad += (st != "OPEN" and ns == 0) or (st == "EXCLUDED_DROP" and ns <= 1)
        t2cells.append((ct, hyp, conv, p))
    rep["T2_soundness"] = {"plants": 400, "failures": bad, "by_same_column_and_verdict": dict(sorted(dist.items())),
                           "pass": bad == 0}

    # T4 chance power (messages drawn before T3 so that T3 can reuse the first 10)
    t4msgs = []
    for _ in range(60):
        pos = mask(rng)
        ct = "".join(rng.choice(AZ) for _ in range(97))
        hyp = [rng.choice(AZ) if i in pos else None for i in range(97)]
        t4msgs.append((ct, hyp))
    power = {}
    for ct, hyp in t4msgs:
        for conv in SF.CONVENTIONS:
            for p in P_T4:
                st = X.check(ct, hyp, conv, p)
                d = power.setdefault("any" if p is None else str(p), {"EXCLUDED_DROP": 0, "EXCLUDED_EXACT": 0, "OPEN": 0})
                d[st] += 1
    labels = {}
    for p, d in power.items():
        n = sum(d.values())
        d["share_drop"] = round(d["EXCLUDED_DROP"] / n, 4)
        d["share_exact_or_drop"] = round((d["EXCLUDED_DROP"] + d["EXCLUDED_EXACT"]) / n, 4)
        labels[p] = "TESTABLE" if d["share_drop"] >= 0.50 else "WEAK" if d["share_exact_or_drop"] >= 0.50 else \
            "NOT_TESTABLE"
    rep["T4_chance_power"] = {"messages": len(t4msgs), "cells_per_period": len(t4msgs) * 16, "by_period": power}

    # T3 two implementations
    cells = list(t2cells) + [(ct, hyp, conv, p) for ct, hyp in t4msgs[:10] for conv in SF.CONVENTIONS for p in P_T4]
    dis = sum(X.check(*c) != X.check(*c, collision=RF.collision_rank) for c in cells)
    rep["T3_two_implementations"] = {"cells": len(cells), "disagreements": dis, "pass": dis == 0}

    # T5 ciphertext-only invariant (exploratory)
    eq = diff = 0
    rows = []
    for k in range(120):
        PA, CA = "".join(rng.sample(AZ, 26)), "".join(rng.sample(AZ, 26))
        conv = SF.CONVENTIONS[k % 16]
        p = k % 6 + 1
        pt = window(rng, txt)
        ct = SF.encrypt(pt, PA, CA, conv, keyseq(rng, p))
        tc, tp = T_m(ct, 2 * p), T_m(aligned(pt, conv), 2 * p)
        eq += tc == tp
        diff += abs(tc - tp)
        rows.append({"p": p, "T_ct": tc, "T_aligned_pt": tp})
    rep["T5_invariant"] = {"plants": 120, "equal": eq, "mean_abs_diff": round(diff / 120, 3), "rows": rows}

    gates = all(rep[g]["pass"] for g in ("T1_structure", "T2_soundness", "T3_two_implementations"))
    rep["labels_by_period"] = labels if gates else None
    rep["verdict"] = "GATE_FAILED" if not gates else ("TESTABLE_AT_SOME_PERIOD" if "TESTABLE" in labels.values()
                                                       else "NOT_TESTABLE")
    rep["wall_s"], rep["cpu_s"] = round(time.time() - t0w, 2), round(time.process_time() - t0c, 2)
    rep["source_sha256"] = {f: hashlib.sha256((HERE / f).read_bytes()).hexdigest() for f in SOURCES}
    out.write_text(json.dumps(rep, indent=1) + "\n")
    print(rep["verdict"], json.dumps({k: {a: b for a, b in v.items() if a not in ("rows", "by_period")}
                                      if isinstance(v, dict) else v for k, v in rep.items() if k[:1] in "Tl"}))


if __name__ == "__main__":
    main()
