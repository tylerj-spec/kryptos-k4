#!/usr/bin/env python3
"""R68 SEALED exact family check (run ONLY after the K4 freeze; holds the published letters).
For every path (ID + 10 R61 routes) x model (M1, M2) x convention (12), which settings of each family can produce the 24
published letters at their plaintext positions (M1: path order, the R61/R64 convention; M2: carved order, Sanborn's
literal statement)? Exact necessary-and-sufficient conditions on the key shift k_t at the clue steps t:
  PER  p = 1..48: all clue steps with equal t mod p need equal k.
  GRO  each of the 100,000 primers: d_t = k_t at every clue step (so each k_t must be a digit 0-9).
  CTAK lag L = 1..96: k_t = Ac^-1(Y[t-L]) at every clue step t >= L (earlier steps use the free primer).
  PTAK lag L = 1..96: k_t = Ap^-1(Q[t-L]) wherever step t-L also carries a published letter (other positions free).
Run on K4 and on the same 100 nulls, so feasible counts can be compared with chance.
Usage: exact.py TARGET.tsv REPORT.json"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import CONVS, from_carved, parse, paths  # noqa: E402

CLUES = ((21, "EASTNORTHEAST"), (63, "BERLINCLOCK"))
POS = [(o + i, c) for o, t in CLUES for i, c in enumerate(t)]


def digit_streams():
    pr = np.arange(100000)
    d = np.zeros((100000, 97), dtype=np.int8)
    for i in range(5):
        d[:, i] = (pr // 10 ** (4 - i)) % 10
    for t in range(5, 97):
        d[:, t] = (d[:, t - 5] + d[:, t - 4]) % 10
    return d


def implied(conv, ych, pch):
    Ap, Ac, op = parse(conv)
    y, x = Ac.index(ych), Ap.index(pch)
    return ((y - x) if op == "VIG" else (y + x) if op == "BEAU" else (x - y)) % 26


def check(ct, D, P):
    res = {"PER": [], "GRO": [], "CTAK": [], "PTAK": []}
    for path, perm in P.items():
        Y = from_carved(ct, perm)
        inv = [0] * 97
        for j, t in enumerate(perm):
            inv[t] = j
        for model in (("M1",) if path == "ID" else ("M1", "M2")):
            steps = [(i if model == "M1" else perm[i], c) for i, c in POS]   # (path step, published letter)
            known_q = {t: c for t, c in steps}                               # Q[t] known at these steps
            for conv in CONVS:
                Ap, Ac, _ = parse(conv)
                ks = [(t, implied(conv, Y[t], c)) for t, c in steps]
                for p in range(1, 49):
                    seen, ok = {}, True
                    for t, k in ks:
                        if seen.setdefault(t % p, k) != k:
                            ok = False
                            break
                    if ok:
                        res["PER"].append([path, model, conv, p, len(ks) - len(seen)])   # constraints = repeats
                if all(k <= 9 for _, k in ks):
                    m = np.ones(100000, dtype=bool)
                    for t, k in ks:
                        m &= D[:, t] == k
                    for pr in np.nonzero(m)[0]:
                        res["GRO"].append([path, model, conv, f"{pr:05d}", len(ks)])
                for L in range(1, 97):
                    if all(t < L or k == Ac.index(Y[t - L]) for t, k in ks):
                        res["CTAK"].append([path, model, conv, L, sum(t >= L for t, _ in ks)])
                    if all((t - L) not in known_q or k == Ap.index(known_q[t - L]) for t, k in ks):
                        n_con = sum((t - L) in known_q for t, _ in ks)
                        res["PTAK"].append([path, model, conv, L, n_con])
    return res


def main():
    tsv, rep = Path(sys.argv[1]), Path(sys.argv[2])
    cts = dict(l.split("\t") for l in tsv.read_text().splitlines()[1:] if l)
    P = paths()
    D = digit_streams()
    out = {"note": "Each entry ends with the number of constraints actually checked; 0 = vacuous (unconstrained). "
                   "Counts below are non-vacuous entries (>= 1 constraint) and strong entries (>= 8 constraints)."}
    counts = {}
    for rid in ["K4"] + sorted(i for i in cts if i != "K4"):
        r = check(cts[rid], D, P)
        counts[rid] = {f: sum(1 for e in v if e[-1] > 0) for f, v in r.items()}
        counts[rid].update({f + "_strong": sum(1 for e in v if e[-1] >= 8) for f, v in r.items()})
        if rid == "K4":
            out["k4_feasible"] = {f: [e for e in v if e[-1] > 0] for f, v in r.items()}
    out["k4_counts"] = counts["K4"]
    nul = [c for k, c in counts.items() if k != "K4"]
    out["null_counts"] = {f: {"median": sorted(c[f] for c in nul)[len(nul) // 2], "max": max(c[f] for c in nul),
                              "ge_k4": sum(c[f] >= counts["K4"][f] for c in nul)} for f in counts["K4"]}
    rep.write_text(json.dumps(out, indent=1) + "\n")
    print("K4 feasible (non-vacuous) counts:", out["k4_counts"])
    print("nulls:", out["null_counts"])


if __name__ == "__main__":
    main()
