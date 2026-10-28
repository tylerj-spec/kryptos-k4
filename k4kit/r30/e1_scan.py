#!/usr/bin/env python3
"""E1 oracle scan (PREREGISTRATION_R30.md): chain-addition primers b = 6 (all 1e6, K4 + 5 shuffled-K4 nulls) and
b = 7 (all 1e7, K4 only). Writes runs/e1_passes.csv and runs/e1_scan.json."""
import csv
import json
import random
import time
from multiprocessing import Pool

from r30lib import ANCH, K4, RUNS, assert_protocol, chain_key, possible

SHUF = []
for s in range(3001, 3006):
    x = list(K4)
    random.Random(s).shuffle(x)
    SHUF.append("".join(x))


def work(args):
    b, lo, hi, nulls = args
    hits, null_hits = [], [0] * len(SHUF)
    for p in range(lo, hi):
        k = chain_key(p, b)
        if possible(k):
            hits.append(p)
        if nulls:
            for j, ct in enumerate(SHUF):
                null_hits[j] += possible(k, ct=ct)
    return b, hits, null_hits


if __name__ == "__main__":
    sha = assert_protocol()
    t0 = time.time()
    jobs = [(6, lo, lo + 10000, True) for lo in range(0, 10 ** 6, 10000)]
    jobs += [(7, lo, lo + 50000, False) for lo in range(0, 10 ** 7, 50000)]
    res = {6: [], 7: []}
    nulls = [0] * len(SHUF)
    with Pool(3) as pool:
        for b, hits, nh in pool.imap_unordered(work, jobs):
            res[b] += hits
            nulls = [a + c for a, c in zip(nulls, nh)]
    with open(RUNS / "e1_passes.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["b", "primer"])
        for b in (6, 7):
            for p in sorted(res[b]):
                w.writerow([b, f"{p:0{b}d}"])
    out = {"protocol": sha, "b6_passes": len(res[6]), "b7_passes": len(res[7]),
           "b6_null_passes_5_shuffles": nulls, "expected_b6": 1e6 * 3.9e-4, "expected_b7": 1e7 * 3.9e-4,
           "seconds": round(time.time() - t0, 1)}
    json.dump(out, open(RUNS / "e1_scan.json", "w"), indent=1)
    print(json.dumps(out, indent=1))
