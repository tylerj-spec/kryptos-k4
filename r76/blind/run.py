#!/usr/bin/env python3
"""R76 BLIND runner (r75/blind/run.py with the R76 families). Reads only an "id<TAB>ciphertext" TSV, the generic
English scorers (quadgram table, R59 order-6 letter model sha256-checked against r59/blind/LM_SHA256, R59 word model)
and r76/families.py; no truth, no published K4 letters. For each ciphertext it decrypts under every member of the R76
fixed-method families (B1 keyed alphabets, B2 scrambled key, B3 sandwich on sheet routes; 13,700,640 fixed methods),
keeps the 400 best by quadgram score, re-scores those with the letter model and the word model, and stores the 5 best
distinct decodes plus the best decode of each sub-family. For ids given with --full it also stores a 25-decode review
packet. Writes OUT/RESULTS.jsonl, OUT/packet/<id>.json and OUT/FROZEN.sha256.
Usage: python3 -I r76/blind/run.py LM.bin IN.tsv OUTDIR [PROCS=4] [--full ID[,ID...]]"""
import hashlib
import heapq
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r75"))
sys.path.insert(0, str(ROOT / "r76"))
import core  # noqa: E402
import families as F  # noqa: E402

KEEP, PER_BATCH = 400, 8
SCORER, FULL = None, set()


def init(lm, full):
    global SCORER, FULL
    SCORER, FULL = core.Scorer(lm), set(full)


def scan(ct):
    """Full scan of one ciphertext. Returns (ranked decodes, number of decodes, best decode per sub-family)."""
    C = core.codes(ct)
    heap, n, tick = [], 0, 0
    best_sub = {}
    for P, meta in F.batches(C):
        q = SCORER.quad_score(P)
        n += len(q)
        k = min(PER_BATCH, len(q))
        top = np.argpartition(-q, k - 1)[:k] if len(q) > k else np.arange(len(q))
        sub = meta[0] + meta[1]
        b = int(top[np.argmax(q[top])])
        if sub not in best_sub or q[b] > best_sub[sub][0]:
            best_sub[sub] = (float(q[b]), core.text(P[b]), F.setting(meta, b))
        for r in top:
            item = (float(q[r]), tick, core.text(P[int(r)]), meta, int(r))
            tick += 1
            if len(heap) < KEEP:
                heapq.heappush(heap, item)
            elif item[0] > heap[0][0]:
                heapq.heapreplace(heap, item)
    cands, seen = [], set()
    for qv, _, t, meta, r in sorted(heap, reverse=True):
        if t not in seen:
            seen.add(t)
            cands.append((qv, t, F.setting(meta, r)))
    for sub, (qv, t, st) in best_sub.items():
        if t not in seen:
            seen.add(t)
            cands.append((qv, t, st))
    lm = SCORER.lm_score(np.stack([core.codes(t) for _, t, _ in cands]))
    out = [{"text": t, "setting": st, "sub": F.sub(st), "quad": qv, "lm_per_letter": float(l)}
           for (qv, t, st), l in zip(cands, lm)]
    out.sort(key=lambda e: -e["lm_per_letter"])
    return out, n, {s: v[1] for s, v in best_sub.items()}


def process(row):
    rid, ct = row
    ranked, n, best_sub = scan(ct)
    top = ranked[:5]
    subs = [next(e for e in ranked if e["text"] == best_sub[s]) for s in sorted(best_sub)]
    keep = top + [e for e in subs if e not in top]
    for e in keep:
        e["word_per_letter"] = SCORER.word_score(e["text"])
    res = {"id": rid, "n_decodes": n, "best": top[0], "top": top, "best_by_sub": {e["sub"]: e for e in subs}}
    if rid in FULL:
        packet = subs + [e for e in ranked if e not in subs]
        packet = packet[:25]
        for e in packet:
            e.setdefault("word_per_letter", SCORER.word_score(e["text"]))
        res["packet"] = packet
    return res


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
        for k, r in enumerate(pool.imap(process, rows, chunksize=1)):
            if "packet" in r:
                (out / "packet").mkdir(exist_ok=True)
                pp = out / "packet" / f"{r['id']}.json"
                pp.write_text(json.dumps(r.pop("packet"), indent=1) + "\n")
                extra.append((pp, "packet"))
            res[r["id"]] = r
            if (k + 1) % 20 == 0:
                print(f"{k + 1}/{len(rows)} done", flush=True)
    (out / "RESULTS.jsonl").write_text("".join(json.dumps(res[r[0]]) + "\n" for r in rows))
    man = [(inp, "input"), (out / "RESULTS.jsonl", "results")] + extra + [
        (ROOT / "r75/core.py", "core"), (ROOT / "r76/families.py", "families"), (ROOT / "r76/routes76.py", "routes"),
        (ROOT / "r76/alphabets.py", "alphabets"), (Path(__file__), "runner"),
        (ROOT / "r75/data/kryptos_words.txt", "keywords"), (ROOT / "k4kit/data/quad_log10.f32", "quadgrams"),
        (ROOT / "k4kit/data/word_model_orth.tsv", "word_model"), (lm, "letter_model")]
    (out / "FROZEN.sha256").write_text("".join(f"{sha(p)}  {lab}  {p.name}\n" for p, lab in man))
    print(f"R76 blind: {len(rows)} ciphertexts, {res[rows[0][0]]['n_decodes']:,} fixed methods each")


if __name__ == "__main__":
    main()
