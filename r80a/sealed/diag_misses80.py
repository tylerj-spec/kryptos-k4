#!/usr/bin/env python3
"""R80a post-reveal diagnostic (not part of the gate; does not change any verdict). For every holdout positive or
STRETCH plant that was not recovered and confident, with the truth open:
  pass0_rank   the true setting's rank in pass 0 among all settings of its family at its free-key length (the runner
               keeps the K0 = 4,000 best per length, so a rank above 4,000 means the filter lost it). An equivalent
               setting with another listed key or convention could still have survived; this rank is for the planted
               setting only;
  solver_exact R79's solver with 6 starts on the true listed key and convention: does it decode the plaintext exactly?
  quad_truth / quad_best  quadgram score per letter of the plaintext and of the frozen best decode.
Usage: python3 -I r80a/sealed/diag_misses80.py GATE.json sealed_truth.json blind.tsv RESULTS.jsonl OUT.json"""
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r79"))
sys.path.insert(0, str(ROOT / "r80a"))
import solver as SV  # noqa: E402
import two80 as T  # noqa: E402

K0 = 4000


def quad(t):
    c = [T.AZ.index(x) for x in t]
    return float(SV.QUAD[[((c[j] * 26 + c[j + 1]) * 26 + c[j + 2]) * 26 + c[j + 3] for j in range(len(c) - 3)]].mean())


def one(job):
    rid, st, ct, pt, best = job
    fam = st["fam"]
    ci = T.CONVS.index(tuple(st["conv"]))
    wi = T.keys_for(fam).index(st["word"])
    m = len(st["free"])
    S = np.stack([T.scan(ct, fam, c)[:, m - 1] for c in range(len(T.CONVS))])
    rank = int((S > S[ci, wi]).sum()) + 1
    z, out = T.build(ct, fam, ci, wi)
    R = np.array([[i % m for i in range(T.N)]], dtype=np.uint8)
    sc, de = SV.slot_batch(z[None], R, np.array([m], dtype=np.int32), np.zeros(1, dtype=np.int32), out[None], 6,
                           800950, 0)
    got = T.decode_with(z, out, m, de[0])
    return {"id": rid, "fam": fam, "lw": len(st["word"]), "m": m, "pass0_rank": rank, "filter_lost": rank > K0,
            "solver_exact": got == pt, "solver_letters_right": sum(a == b for a, b in zip(got, pt)),
            "quad_truth": quad(pt), "quad_solver": float(sc[0]), "quad_best": quad(best)}


def main():
    gate, truth_p, tsv, res_p, out = sys.argv[1:6]
    rows = json.loads(Path(gate).read_text())["rows"]
    truth = json.loads(Path(truth_p).read_text())
    cts = dict(l.split("\t") for l in Path(tsv).read_text().splitlines()[1:] if l)
    res = {json.loads(l)["id"]: json.loads(l) for l in Path(res_p).read_text().splitlines() if l}
    miss = [r["id"] for r in rows if (r["kind"].startswith("POS") or r["kind"] == "STRETCH") and not r["ok"]]
    jobs = [(i, truth[i]["setting"], cts[i], truth[i]["pt"], res[i]["best"]["text"]) for i in miss]
    with Pool(4) as p:
        d = p.map(one, jobs, chunksize=1)
    for x, i in zip(d, miss):
        x["kind"] = truth[i]["kind"]
    Path(out).write_text(json.dumps(d, indent=1) + "\n")
    for x in d:
        print(x)


if __name__ == "__main__":
    main()
