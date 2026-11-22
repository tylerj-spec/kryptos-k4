#!/usr/bin/env python3
"""R92 BLIND runner: reads only an "id<TAB>ciphertext" TSV, the generic English scorers (quadgram table; R59
letter model given by path, sha256-checked against r59/blind/LM_SHA256; R59 word model) and the RXP solver. No truth,
no published K4 letters. For each ciphertext: solve92.solve (pass 1 over all 192 settings, pass 2 on the best TOP = 48),
then every final candidate is re-scored by the letter model, the best 5 are polished by greedy wiring swaps on the
letter model (pass 3) and get the word score. Output
OUT/RESULTS.jsonl (best first) and OUT/RUNNER_FROZEN.sha256.
Usage: python3 -I r92/blind/run92.py LM.bin IN.tsv OUTDIR [PROCS=4]"""
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
import solve92 as S  # noqa: E402

SCORER = None


def init(lm):
    global SCORER
    SCORER = core.Scorer(lm)
    S.lib()


def lm_polish(ct, cand, rounds=40):
    """Pass 3: greedy swaps of the wiring that raise the order-6 letter-model score of the decode (re-derived by
    the explicit decryptor); stops when no swap helps."""
    st = cand["setting"]
    key = (st["ein"], st["eout"], st["n"], st["r"], st["d"])
    W = list(st["wiring"])
    cur = float(SCORER.lm_score(core.codes(S.R.decrypt(ct, W, *key))[None])[0])
    pairs = [(a, b) for a in range(26) for b in range(a + 1, 26)]
    for _ in range(rounds):
        texts, Ws = [], []
        for a, b in pairs:
            W2 = list(W)
            W2[a], W2[b] = W2[b], W2[a]
            Ws.append(W2)
            texts.append(core.codes(S.R.decrypt(ct, W2, *key)))
        sc = SCORER.lm_score(np.stack(texts))
        k = int(np.argmax(sc))
        if sc[k] <= cur + 1e-9:
            break
        cur, W = float(sc[k]), Ws[k]
    text = S.R.decrypt(ct, W, *key)
    assert S.R.encrypt(text, W, *key) == ct
    return {**cand, "text": text, "setting": {**st, "wiring": W}, "lm_per_letter": cur, "polished": True}


def process(row):
    rid, ct = row
    cands, rank1, nset = S.solve(ct)
    lm = SCORER.lm_score(np.stack([core.codes(c["text"]) for c in cands]))
    for c, v in zip(cands, lm):
        c["lm_per_letter"] = float(v)
    cands.sort(key=lambda c: -c["lm_per_letter"])
    cands = [lm_polish(ct, c) for c in cands[:5]] + cands[5:]
    cands.sort(key=lambda c: -c["lm_per_letter"])
    top = cands[:5]
    for c in top:
        c["word_per_letter"] = float(SCORER.word_score(c["text"]))
    return {"id": rid, "n_settings": nset, "best": top[0], "top": top}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    lm, tsv, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    procs = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    want = (ROOT / "r59/blind/LM_SHA256").read_text().split()[0]
    assert sha(lm) == want, "letter model hash mismatch"
    rows = [l.split("\t") for l in tsv.read_text().splitlines()[1:] if l]
    for _, ct in rows:
        assert len(ct) == 97 and ct.isalpha() and ct.isupper()
    out.mkdir(parents=True, exist_ok=False)
    S.lib()                               # build the kernel once, before the workers fork
    with Pool(procs, initializer=init, initargs=(lm,)) as pool:
        res = {r["id"]: r for r in pool.imap_unordered(process, rows, chunksize=1)}
    (out / "RESULTS.jsonl").write_text("".join(json.dumps(res[rid]) + "\n" for rid, _ in rows))
    files = [(tsv, "input"), (out / "RESULTS.jsonl", "results"), (HERE / "run92.py", "runner"),
             (HERE / "solve92.py", "solver"), (S.KERNEL, "kernel"), (HERE.parent / "rotor92.py", "family"),
             (ROOT / "r75/core.py", "scorer"), (ROOT / "k4kit/data/quad_log10.f32", "quadgrams"),
             (ROOT / "k4kit/data/word_model_orth.tsv", "word_model")]
    (out / "RUNNER_FROZEN.sha256").write_text("".join(f"{sha(p)}  {lab}  {p}\n" for p, lab in files) +
                                              f"{want}  letter_model  {Path(lm).name}\n")
    print("R92 blind:", len(rows), "ciphertexts")


if __name__ == "__main__":
    main()
