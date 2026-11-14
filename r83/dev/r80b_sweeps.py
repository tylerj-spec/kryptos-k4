#!/usr/bin/env python3
"""R80b development measurement (SPENT data only: the nine R80a holdout misses, whose truth was opened in 0d71fcc;
no K4). Question: R80a's misses were all lost by pass 0 (the true setting ranked 7,849 to 1.8 million, outside the
4,000 kept). Would pass 0 with 1 or 2 quadgram coordinate-ascent sweeps per setting rank the true setting inside the
4,000 kept per free length? Reports, per miss, the true setting's rank among all settings of its family at its
free-key length with 1 sweep (the 0-sweep ranks are in DIAG_MISSES.json), and the time per family scan.
Usage: python3 -I r83/dev/r80b_sweeps.py OUT.json [PROCS=3]"""
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r80a"))
import two80 as T  # noqa: E402

K0 = 4000
SWEEPS = (1,)          # the sweeps-0 ranks are in r80a/holdout/DIAG_MISSES.json


def one(job):
    rid, st, ct, sweeps = job
    fam, m = st["fam"], len(st["free"])
    ci, wi = T.CONVS.index(tuple(st["conv"])), T.keys_for(fam).index(st["word"])
    t0 = time.time()
    S = np.stack([T.scan(ct, fam, c, sweeps)[:, m - 1] for c in range(len(T.CONVS))])
    return {"id": rid, "fam": fam, "m": m, "lw": len(st["word"]), "sweeps": sweeps,
            "rank": int((S > S[ci, wi]).sum()) + 1, "kept": int((S > S[ci, wi]).sum()) + 1 <= K0,
            "seconds": round(time.time() - t0, 1)}


def main():
    out = sys.argv[1]
    procs = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    diag = json.loads((ROOT / "r80a/holdout/DIAG_MISSES.json").read_text())
    truth = json.loads((ROOT / "r80a/holdout/sealed_truth.json").read_text())
    cts = dict(l.split("\t") for l in (ROOT / "r80a/holdout/blind.tsv").read_text().splitlines()[1:] if l)
    jobs = [(d["id"], truth[d["id"]]["setting"], cts[d["id"]], s) for s in SWEEPS for d in diag]
    with Pool(procs) as p:
        res = p.map(one, jobs, chunksize=1)
    Path(out).write_text(json.dumps(res, indent=1) + "\n")
    for r in res:
        print(r)


if __name__ == "__main__":
    main()
