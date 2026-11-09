#!/usr/bin/env python3
"""R74 BLIND runner. Reads only an "id<TAB>ciphertext" TSV, the generic R59 order-6 letter model (sha256-checked
against r59/blind/LM_SHA256) and the generic R59 word model; no truth, no published K4 letters.
For each ciphertext: decrypt under all 15,680 distinct transforms (r74/scan.py), rank by the letter model, and keep
the 5 best distinct decodes with both scores (letter model per letter; word model per letter).
For ids given with --full (e.g. the real target), also write the complete scan (all 15,680 decodes with setting and
letter-model score) as OUT/full/<id>.tsv.gz and the 25-decode review packet OUT/packet/<id>.json: the best decode of
each (route, keyword order) pair, the 25 best of those 28 by letter model.
Writes OUT/RESULTS.jsonl and OUT/FROZEN.sha256.
Usage: python3 -I r74/blind/run.py LM.bin IN.tsv OUTDIR [PROCS=4] [--full ID[,ID...]]"""
import gzip
import hashlib
import json
import sys
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r74"))
sys.path.insert(0, str(ROOT / "r73"))
import scan as SC  # noqa: E402
import wordkey as W  # noqa: E402

SCANNER, VOCAB, FULL = None, None, set()


def init(lm, full):
    global SCANNER, VOCAB, FULL
    SCANNER, VOCAB, FULL = SC.Scanner(lm), W.load_words(), set(full)


def process(row):
    rid, ct = row
    P, s, order = SCANNER.scan(ct)
    out = {"id": rid, "top": SC.top_distinct(SCANNER, P, s, order, 5, VOCAB)}
    out["best"] = out["top"][0]
    if rid in FULL:
        lines = []
        for k in range(len(s)):
            e = SC.entry(SCANNER, P, s, k)
            st = e["setting"]
            lines.append("\t".join([str(k), e["route"], st["ka"], st["kb"], str(st["a"]), str(st["b"]), st["op_a"],
                                    st["op_b"], f"{e['lm_per_letter']:.6f}", e["text"]]))
        pair_best = {}
        for k in order:
            k = int(k)
            pair = (SCANNER.route_name[k], SCANNER.labels[k][0]["ka"])
            if pair not in pair_best:
                pair_best[pair] = SC.entry(SCANNER, P, s, k, VOCAB)
        out["full"] = "\n".join(lines) + "\n"
        out["packet"] = sorted(pair_best.values(), key=lambda e: -e["lm_per_letter"])[:25]
    return out


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def main():
    args = sys.argv[1:]
    full = []
    if "--full" in args:
        i = args.index("--full")
        full = args[i + 1].split(",")
        args = args[:i] + args[i + 2:]
    lm, inp, out = Path(args[0]), Path(args[1]), Path(args[2])
    procs = int(args[3]) if len(args) > 3 else 4
    if sha(lm) != (ROOT / "r59/blind/LM_SHA256").read_text().split()[0]:
        raise SystemExit("letter model sha256 does not match r59/blind/LM_SHA256")
    if (out / "RESULTS.jsonl").exists():
        raise SystemExit("refusing to overwrite")
    out.mkdir(parents=True, exist_ok=True)
    rows = [l.split("\t") for l in inp.read_text().splitlines()[1:] if l]
    for _, ct in rows:
        if len(ct) != 97 or not ct.isalpha() or not ct.isupper():
            raise SystemExit("bad ciphertext")
    res, extra = {}, []
    with Pool(procs, initializer=init, initargs=(str(lm), full)) as pool:
        for r in pool.imap(process, rows, chunksize=2):
            if "full" in r:
                (out / "full").mkdir(exist_ok=True)
                (out / "packet").mkdir(exist_ok=True)
                fp = out / "full" / f"{r['id']}.tsv.gz"
                with gzip.GzipFile(fp, "wb", mtime=0) as g:
                    g.write(r.pop("full").encode())
                pp = out / "packet" / f"{r['id']}.json"
                pp.write_text(json.dumps(r.pop("packet"), indent=1) + "\n")
                extra += [(fp, "full"), (pp, "packet")]
            res[r["id"]] = r
    (out / "RESULTS.jsonl").write_text("".join(json.dumps(res[r[0]]) + "\n" for r in rows))
    man = [(inp, "input"), (out / "RESULTS.jsonl", "results")] + extra + [
        (ROOT / "r74/sandwich.py", "cipher"), (ROOT / "r74/scan.py", "scanner"), (Path(__file__), "runner"),
        (ROOT / "r61/routes.txt", "routes"), (ROOT / "k4kit/data/word_model_orth.tsv", "word_model"),
        (lm, "letter_model")]
    (out / "FROZEN.sha256").write_text("".join(f"{sha(p)}  {lab}  {p.name}\n" for p, lab in man))
    print(f"R74 blind: {len(rows)} ciphertexts scanned under 15,680 transforms each")


if __name__ == "__main__":
    main()
