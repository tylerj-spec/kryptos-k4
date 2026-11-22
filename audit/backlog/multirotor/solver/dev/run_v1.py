#!/usr/bin/env python3
"""RX2-O development run, version 1 (supplied structure; reads PANEL.tsv only, never the panel truth).
Workers (no letter model; created before the main process loads it, so no page is shared or double-counted) run
solve_v1.restarts per plant. The main process then scores the KEEP best distinct decodes (by quadgram) with the
R59 letter model and the word model; top-1 is the letter-model maximum among them. Output OUT/RESULTS.jsonl.
Usage: python3 -I audit/backlog/multirotor/solver/dev/run_v1.py LM.bin PANEL.tsv OUTDIR [PROCS=2]"""
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path[:0] = [str(HERE.parent), str(ROOT / "r75")]
import solve_v1 as S  # noqa: E402

P = S.PARAMS_V1


def work(row):
    rid, label, ct = row
    t0 = time.process_time()
    res = S.restarts(ct, label, P["R"], P["I"], P["T0"], S.seed_of(ct, label, P["SEED"]))
    return rid, label, ct, res, time.process_time() - t0


def main():
    lm, tsv, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    procs = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    rows = []
    for line in tsv.read_text().splitlines()[1:]:
        rid, lab, ct = line.split("\t")
        f = lab.split(",")
        rows.append((rid, (f[0], f[1], *map(int, f[2:])), ct))
    out.mkdir(parents=True, exist_ok=False)
    S.lib()
    t = time.time()
    with Pool(procs) as pool:
        done = pool.map(work, rows, chunksize=1)
    anneal_wall = time.time() - t
    import numpy as np
    import core
    scorer = core.Scorer(lm)
    lines = []
    for rid, label, ct, res, cpu in done:
        seen, keep = set(), []
        for sc, W1, W2, text in sorted(res, key=lambda z: -z[0]):
            if text not in seen:
                seen.add(text)
                keep.append({"quad": sc, "W1": W1, "W2": W2, "text": text})
            if len(keep) == P["KEEP"]:
                break
        lmv = scorer.lm_score(np.stack([core.codes(c["text"]) for c in keep]))
        for c, v in zip(keep, lmv):
            c["lm_per_letter"] = float(v)
            c["word_per_letter"] = float(scorer.word_score(c["text"]))
        best = max(keep, key=lambda c: c["lm_per_letter"])
        lines.append(json.dumps({"id": rid, "label": label, "cpu_s": round(cpu, 2), "best": best, "keep": keep,
                                 "restart_quads": [round(z[0], 3) for z in res],
                                 "restart_texts": [z[3] for z in res]}) + "\n")
    (out / "RESULTS.jsonl").write_text("".join(lines))
    (out / "RUN.json").write_text(json.dumps({"params": P, "procs": procs, "anneal_wall_s": round(anneal_wall, 1),
                                              "plants": len(rows)}) + "\n")
    print("v1:", len(rows), "plants, anneal wall", round(anneal_wall, 1), "s")


if __name__ == "__main__":
    main()
