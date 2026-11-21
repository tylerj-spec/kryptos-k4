#!/usr/bin/env python3
"""R89 BLIND joint runner: reads only an "id<TAB>ciphertext" TSV, the generic English scorers (quadgram table; R59
letter model given by path, sha256-checked against r59/blind/LM_SHA256; R59 word model) and the solvers of the
ARMS named on the command line (F26L: r89/blind/f26_solve.py, which also scores the bare F26 sub-family; RCT:
r89/blind/rct_solve.py). No truth, no published K4 letters.
For each ciphertext every named arm is run with the same fixed effort; every candidate is re-scored by the letter
model; the best 5 RCT candidates are polished by greedy wiring swaps on the letter model (as R87/R88); the 5 best
candidates over ALL arms ("top", best first) and the best of each sub-family ("best_by_arm": F26L, F26, RCT) get the
word score. "best" = top[0] is the maximum over every arm run: the family-wise statistic.
Output OUT/RESULTS.jsonl and OUT/RUNNER_FROZEN.sha256.
Usage: python3 -I r89/blind/run89.py LM.bin IN.tsv OUTDIR ARMS(F26L,RCT | F26L | RCT) [PROCS=4]"""
import hashlib
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(HERE.parent), str(ROOT / "r75")]
import core  # noqa: E402
import f26_solve as FS  # noqa: E402
import rct_solve as RS  # noqa: E402

SCORER, ARMS = None, ()


def init(lm, arms):
    global SCORER, ARMS
    SCORER, ARMS = core.Scorer(lm), arms
    if "RCT" in arms:
        RS.lib()


def lm_of(texts):
    return [float(v) for v in SCORER.lm_score(np.stack([core.codes(t) for t in texts]))]


def rct_polish(ct, cand, rounds=40):
    st = cand["setting"]
    key = (st["ein"], st["eout"], st["d"], st["m"], st["q"])
    W = list(st["wiring"])
    cur = lm_of([RS.R.decrypt(ct, W, *key)])[0]
    pairs = [(a, b) for a in range(26) for b in range(a + 1, 26)]
    for _ in range(rounds):
        Ws = []
        for a, b in pairs:
            W2 = list(W)
            W2[a], W2[b] = W2[b], W2[a]
            Ws.append(W2)
        sc = lm_of([RS.R.decrypt(ct, W2, *key) for W2 in Ws])
        k = int(np.argmax(sc))
        if sc[k] <= cur + 1e-9:
            break
        cur, W = sc[k], Ws[k]
    text = RS.R.decrypt(ct, W, *key)
    assert RS.R.encrypt(text, W, *key) == ct
    return {**cand, "text": text, "setting": {**st, "wiring": W}, "lm_per_letter": cur, "polished": True}


def process(row):
    rid, ct = row
    cands, nset = [], {}
    if "F26L" in ARMS:
        c, nset["F26L+F26"] = FS.solve(ct)
        cands += c
    if "RCT" in ARMS:
        c, nset["RCT"] = RS.solve(ct)
        for e, v in zip(c, lm_of([e["text"] for e in c])):
            e["lm_per_letter"] = v
        c.sort(key=lambda e: -e["lm_per_letter"])
        c = [rct_polish(ct, e) for e in c[:5]] + c[5:]
        cands += c
    todo = [e for e in cands if "lm_per_letter" not in e]
    for e, v in zip(todo, lm_of([e["text"] for e in todo]) if todo else []):
        e["lm_per_letter"] = v
    cands.sort(key=lambda e: -e["lm_per_letter"])
    top = cands[:5]
    by_arm = {}
    for e in cands:
        by_arm.setdefault(e["arm"], e)
    for e in top + list(by_arm.values()):
        if "word_per_letter" not in e:
            e["word_per_letter"] = float(SCORER.word_score(e["text"]))
    return {"id": rid, "arms": list(ARMS), "n_settings": nset, "best": top[0], "top": top, "best_by_arm": by_arm}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    lm, tsv, out, arms = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), tuple(sys.argv[4].split(","))
    procs = int(sys.argv[5]) if len(sys.argv) > 5 else 4
    assert arms and set(arms) <= {"F26L", "RCT"}, "ARMS must be F26L and/or RCT"
    want = (ROOT / "r59/blind/LM_SHA256").read_text().split()[0]
    assert sha(lm) == want, "letter model hash mismatch"
    rows = [l.split("\t") for l in tsv.read_text().splitlines()[1:] if l]
    for _, ct in rows:
        assert len(ct) == 97 and ct.isalpha() and ct.isupper()
    out.mkdir(parents=True, exist_ok=False)
    if "RCT" in arms:
        RS.lib()                         # build the kernel once, before the workers fork
    with Pool(procs, initializer=init, initargs=(lm, arms)) as pool:
        res = {r["id"]: r for r in pool.imap_unordered(process, rows, chunksize=1)}
    (out / "RESULTS.jsonl").write_text("".join(json.dumps(res[rid]) + "\n" for rid, _ in rows))
    files = [(tsv, "input"), (out / "RESULTS.jsonl", "results"), (HERE / "run89.py", "runner"),
             (HERE / "f26_solve.py", "solver_f26l"), (HERE / "rct_solve.py", "solver_rct"), (RS.KERNEL, "kernel"),
             (HERE.parent / "f26l.py", "family_f26l"), (HERE.parent / "rct.py", "family_rct"),
             (ROOT / "r75/core.py", "scorer"), (ROOT / "k4kit/data/quad_log10.f32", "quadgrams"),
             (ROOT / "k4kit/data/word_model_orth.tsv", "word_model")]
    (out / "RUNNER_FROZEN.sha256").write_text("".join(f"{sha(p)}  {lab}  {p}\n" for p, lab in files) +
                                              f"{want}  letter_model  {Path(lm).name}\n")
    print("R89 blind:", len(rows), "ciphertexts; arms", ",".join(arms))


if __name__ == "__main__":
    main()
