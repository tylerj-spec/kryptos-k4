#!/usr/bin/env python3
"""R73b BLIND runner. Reads only an "id<TAB>ciphertext" TSV, the generic R59 word model and the generic R59 order-6
letter model (sha256-checked against r59/blind/LM_SHA256); no truth, no published K4 letters. For each ciphertext it
decodes all 52 R26 settings with r73/wordkey2.py (unknown word = letter-model log10 + POOV, POOV = -3 fixed in
r73/R73B_PREREGISTRATION.md) and keeps every setting's best decode. Writes OUT/RESULTS.jsonl (best decode per
ciphertext), OUT/work/<id>.json (all 52 settings' best decodes) and OUT/FROZEN.sha256.
Usage: python3 -I r73/blind/run_r73b.py LM.bin IN.tsv OUTDIR [PROCS=4]"""
import hashlib
import json
import sys
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r73"))
import wordkey2 as W2  # noqa: E402

POOV = -3.0
SOLVER = None


def init(lm):
    global SOLVER
    SOLVER = W2.Solver(lm, POOV)


def job(row):
    rid, ct = row
    return rid, ct, SOLVER.solve(ct)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def main():
    lm, inp, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    procs = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    if sha(lm) != (ROOT / "r59/blind/LM_SHA256").read_text().split()[0]:
        raise SystemExit("letter model sha256 does not match r59/blind/LM_SHA256")
    if (out / "RESULTS.jsonl").exists():
        raise SystemExit("refusing to overwrite")
    (out / "work").mkdir(parents=True, exist_ok=True)
    rows = [l.split("\t") for l in inp.read_text().splitlines()[1:] if l]
    for _, ct in rows:
        if len(ct) != 97 or not ct.isalpha() or not ct.isupper():
            raise SystemExit("bad ciphertext")
    res = {}
    with Pool(procs, initializer=init, initargs=(str(lm),)) as pool:
        for rid, ct, all_ in pool.imap(job, rows, chunksize=4):
            (out / "work" / f"{rid}.json").write_text(json.dumps({"id": rid, "ct": ct, "settings": all_}) + "\n")
            b = all_[0]
            res[rid] = {"id": rid, "family": b["family"], "setting": b["setting"], "score": b["score"],
                        "per_letter": b["score"] / 97, "words": b["words"], "oov_words": b["oov"]}
    (out / "RESULTS.jsonl").write_text("".join(json.dumps(res[r[0]]) + "\n" for r in rows))
    man = [(inp, "input"), (out / "RESULTS.jsonl", "results"), (ROOT / "r73/wordkey2.py", "solver"),
           (ROOT / "r73/wordkey.py", "cipher"), (Path(__file__), "runner"),
           (ROOT / "k4kit/data/word_model_orth.tsv", "word_model"), (lm, "letter_model")]
    (out / "FROZEN.sha256").write_text("".join(f"{sha(p)}  {lab}  {p.name}\n" for p, lab in man))
    print(f"R73b blind: {len(rows)} ciphertexts decoded")


if __name__ == "__main__":
    main()
