#!/usr/bin/env python3
"""R73 BLIND runner. Reads only an "id<TAB>ciphertext" TSV and the generic R59 word model; no truth, no published
K4 letters. For each ciphertext it decodes all 70 settings of both word-boundary families (r73/wordkey.py) and keeps
the best decode of every setting. Writes OUT/RESULTS.jsonl (best decode overall per ciphertext), OUT/work/<id>.json
(all 70 settings' best decodes) and OUT/FROZEN.sha256.
Usage: python3 -I r73/blind/run.py IN.tsv OUTDIR [PROCS=4]"""
import hashlib
import json
import sys
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r73"))
import wordkey as W  # noqa: E402

VOCAB = None


def init():
    global VOCAB
    VOCAB = W.load_words()


def job(row):
    rid, ct = row
    return rid, ct, W.solve_all(ct, VOCAB)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    inp, out = Path(sys.argv[1]), Path(sys.argv[2])
    procs = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    if (out / "RESULTS.jsonl").exists():
        raise SystemExit("refusing to overwrite")
    (out / "work").mkdir(parents=True, exist_ok=True)
    rows = [l.split("\t") for l in inp.read_text().splitlines()[1:] if l]
    for _, ct in rows:
        if len(ct) != 97 or not ct.isalpha() or not ct.isupper():
            raise SystemExit("bad ciphertext")
    res = {}
    with Pool(procs, initializer=init) as pool:
        for rid, ct, all_ in pool.imap(job, rows, chunksize=4):
            (out / "work" / f"{rid}.json").write_text(json.dumps({"id": rid, "ct": ct, "settings": all_}) + "\n")
            b = all_[0]
            res[rid] = {"id": rid, "family": b["family"], "setting": b["setting"], "score": b["score"],
                        "per_letter": b["score"] / 97, "words": b["words"], "oov_words": b["oov"]}
    (out / "RESULTS.jsonl").write_text("".join(json.dumps(res[r[0]]) + "\n" for r in rows))
    man = [(inp, "input"), (out / "RESULTS.jsonl", "results"), (ROOT / "r73/wordkey.py", "solver"),
           (Path(__file__), "runner"), (ROOT / "k4kit/data/word_model_orth.tsv", "word_model")]
    (out / "FROZEN.sha256").write_text("".join(f"{sha(p)}  {lab}  {p.name}\n" for p, lab in man))
    print(f"R73 blind: {len(rows)} ciphertexts decoded")


if __name__ == "__main__":
    main()
