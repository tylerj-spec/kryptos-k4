#!/usr/bin/env python3
"""RX2-O development run, VERSION 3 (the last): solve_v3 (order-5 letter-model objective; dev/v2/V2.md says why) with
version 2's stages; the annealing workers read only the model's order-1..5 tables, the scoring stage the full model:
  anneal  LM.bin PANEL.tsv OUT [P=2]  all restarts of every plant -> OUT/ANNEAL.jsonl (order-1..5 tables only);
  score   LM.bin OUT           fresh process: the KEEP best distinct decodes by quadgram, letter and word model,
                               top-1 = letter-model maximum -> OUT/RESULTS.jsonl (run_v1.py's format).
Reads PANEL.tsv only, never the panel truth. The restart field "quad" holds the kernel objective (here the order-5 total), as in version 2's format.
Usage: python3 -I .../dev/run_v3.py STAGE ARGS"""
import json
import os
import resource
import sys
import time
from pathlib import Path

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")   # before numpy: no per-thread buffers in the scoring process
os.environ.setdefault("OMP_NUM_THREADS", "1")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path[:0] = [str(HERE), str(HERE.parent), str(ROOT / "r75")]
import solve_v3 as S  # noqa: E402
from run_v2 import lean_scorer, vm_peak_mb  # noqa: E402,F401

P = S.PARAMS_V3
LM = None




def work(row):
    rid, label, ct = row
    t0 = time.process_time()
    res = S.restarts(ct, label, P["R"], P["I"], P["T0"], S.seed_of(ct, label, P["SEED"]), LM)
    return rid, label, ct, res, time.process_time() - t0


def init(lm):
    global LM
    LM = lm


def anneal(tsv, out, procs, lm):
    import hashlib
    from multiprocessing import Pool
    h = hashlib.sha256()
    with open(lm, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 24), b""):
            h.update(chunk)
    assert h.hexdigest() == (ROOT / "r59/blind/LM_SHA256").read_text().split()[0], "letter model hash mismatch"
    rows = []
    for line in tsv.read_text().splitlines()[1:]:
        rid, lab, ct = line.split("\t")
        f = lab.split(",")
        rows.append((rid, (f[0], f[1], *map(int, f[2:])), ct))
    out.mkdir(parents=True, exist_ok=False)
    S.lib()
    t = time.time()
    with open(out / "ANNEAL.jsonl", "w") as fh, Pool(procs, initializer=init, initargs=(lm,)) as pool:
        for rid, label, ct, res, cpu in pool.imap(work, rows, chunksize=1):     # input order, written as they finish
            fh.write(json.dumps({"id": rid, "label": label, "ct": ct, "cpu_s": round(cpu, 2),
                                 "restarts": [{"quad": sc, "W1": W1, "W2": W2, "text": tx} for sc, W1, W2, tx in res]})
                     + "\n")
            fh.flush()
    (out / "ANNEAL_RUN.json").write_text(json.dumps({"params": P, "procs": procs, "plants": len(rows),
                                                     "anneal_wall_s": round(time.time() - t, 1)}) + "\n")
    print("v3 anneal:", len(rows), "plants,", round(time.time() - t, 1), "s wall")


def score(lm, out):
    import numpy as np
    import core
    scorer = lean_scorer(lm)
    lines = []
    for line in (out / "ANNEAL.jsonl").read_text().splitlines():
        a = json.loads(line)
        seen, keep = set(), []
        for z in sorted(a["restarts"], key=lambda z: -z["quad"]):
            if z["text"] not in seen:
                seen.add(z["text"])
                keep.append({"quad": z["quad"], "W1": z["W1"], "W2": z["W2"], "text": z["text"]})
            if len(keep) == P["KEEP"]:
                break
        lmv = scorer.lm_score(np.stack([core.codes(c["text"]) for c in keep]))
        for c, v in zip(keep, lmv):
            c["lm_per_letter"] = float(v)
            c["word_per_letter"] = float(scorer.word_score(c["text"]))
        best = max(keep, key=lambda c: c["lm_per_letter"])
        lines.append(json.dumps({"id": a["id"], "label": a["label"], "cpu_s": a["cpu_s"], "best": best, "keep": keep,
                                 "restart_quads": [round(z["quad"], 3) for z in a["restarts"]],
                                 "restart_texts": [z["text"] for z in a["restarts"]]}) + "\n")
    (out / "RESULTS.jsonl").write_text("".join(lines))
    print("v3 score:", len(lines), "plants; VmPeak", vm_peak_mb(), "MB")



def main():
    st = sys.argv[1]
    if st == "anneal":
        anneal(Path(sys.argv[3]), Path(sys.argv[4]), int(sys.argv[5]) if len(sys.argv) > 5 else 2, sys.argv[2])
    elif st == "score":
        score(sys.argv[2], Path(sys.argv[3]))
    else:
        raise SystemExit("stage: anneal | score")


if __name__ == "__main__":
    main()
