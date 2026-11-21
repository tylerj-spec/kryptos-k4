#!/usr/bin/env python3
"""R90 BLIND runner: reads only an "id<TAB>ciphertext" TSV, the generic English scorers (quadgram table; R59 letter
model given by path, sha256-checked against r59/blind/LM_SHA256; R59 word model) and the F26C solver. No truth, no
published K4 letters.
For each ciphertext: stage 1 scores all 104,340 settings by quadgrams (f26c_solve.py); the 256 best are kept
(retention rule) and ALL of them are scored by the letter model; "best" = the letter-model maximum over the retained
256; the 5 best ("top") and the best retained decode of each sub-family ("best_by_arm": F26C with the outer tableau,
F26 without) get the word score. Each record also lists the 256 retained settings ("retained", quadgram order), so
the gate can measure whether the true setting survived stage 1.
Output OUT/RESULTS.jsonl and OUT/RUNNER_FROZEN.sha256.
Usage: python3 -I r90/blind/run90.py LM.bin IN.tsv OUTDIR [PROCS=4]"""
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
import f26c_solve as FS  # noqa: E402

SCORER = None


def init(lm):
    global SCORER
    SCORER = core.Scorer(lm)


def process(row):
    rid, ct = row
    cands, nset = FS.solve(ct)
    lm = SCORER.lm_score(np.stack([core.codes(e["text"]) for e in cands]))
    for e, v in zip(cands, lm):
        e["lm_per_letter"] = float(v)
    retained = [e["tag"] for e in cands]
    ranked = sorted(cands, key=lambda e: -e["lm_per_letter"])
    top = ranked[:5]
    by_arm = {}
    for e in ranked:
        by_arm.setdefault(e["arm"], e)
    for e in top + list(by_arm.values()):
        if "word_per_letter" not in e:
            e["word_per_letter"] = float(SCORER.word_score(e["text"]))
    return {"id": rid, "n_settings": nset, "kept": len(cands), "best": top[0], "top": top, "best_by_arm": by_arm,
            "retained": retained}


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
    with Pool(procs, initializer=init, initargs=(lm,)) as pool:
        res = {r["id"]: r for r in pool.imap_unordered(process, rows, chunksize=1)}
    (out / "RESULTS.jsonl").write_text("".join(json.dumps(res[rid]) + "\n" for rid, _ in rows))
    files = [(tsv, "input"), (out / "RESULTS.jsonl", "results"), (HERE / "run90.py", "runner"),
             (HERE / "f26c_solve.py", "solver"), (HERE.parent / "f26c.py", "family"), (ROOT / "r75/core.py", "scorer"),
             (ROOT / "k4kit/data/quad_log10.f32", "quadgrams"), (ROOT / "k4kit/data/word_model_orth.tsv", "word_model")]
    (out / "RUNNER_FROZEN.sha256").write_text("".join(f"{sha(p)}  {lab}  {p}\n" for p, lab in files) +
                                              f"{want}  letter_model  {Path(lm).name}\n")
    print("R90 blind:", len(rows), "ciphertexts")


if __name__ == "__main__":
    main()
