#!/usr/bin/env python3
"""R81a BLIND runner (r79/blind/run.py with the R81a families of r81a/families81.py; no H11). Reads only an
"id<TAB>ciphertext" TSV, the generic English scorers (quadgram table, R59 order-6 letter model sha256-checked against
r59/blind/LM_SHA256, R59 word model) and the family modules; no truth, no published K4 letters.
For each ciphertext and each family:
  pass 1  every setting, solver with 1 start (each slot's best single-letter fit), quadgram objective;
  pass 2  the family's 150 best settings again with 6 starts;
  keep    the family's 60 best distinct decodes, re-derived by the explicit decryptor.
All kept decodes are re-scored by the letter model; the 5 best, and the best of each family, are stored with word
scores. For ids given with --full: a 25-decode review packet, and the pass-1 score of EVERY setting of every R81a
family and of R79's four keyword families (OUT/scores/<id>.npz, in chunk order), so that any setting the post-freeze
validator flags already has a frozen blind score.
Writes OUT/RESULTS.jsonl, OUT/packet/<id>.json, OUT/scores/<id>.npz and OUT/FROZEN.sha256.
Usage: python3 -I r81a/blind/run.py LM.bin IN.tsv OUTDIR [PROCS=4] [--fams F1,F2,...] [--full ID[,ID...]]"""
import hashlib
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r75"))
sys.path.insert(0, str(ROOT / "r79"))
sys.path.insert(0, str(ROOT / "r81a"))
import core  # noqa: E402
import families as F79  # noqa: E402
import families81 as F  # noqa: E402
import solver as SV  # noqa: E402

SEED, R1, R2, TOP1, KEEP = 810001, 1, 6, 150, 60
SCORER, FULL, FAMS, SCORES = None, set(), F.FAMS, {}


def init(lm, full, fams):
    global SCORER, FULL, FAMS
    SCORER, FULL, FAMS = core.Scorer(lm), set(full), tuple(fams)
    F.bank(), F79.bank(), F79.streams()


def scan_slot(fam, ct, dump=None, mod=None):
    """dump: list that receives the pass-1 score of every setting (float16), in chunk order."""
    mod = mod or F
    B = mod.bank()[0]
    pool, n = [], 0
    for Z, R, M, OI, info in mod.chunks(fam, ct):
        sc, _ = SV.slot_batch(Z, R, M, OI, B, R1, SEED, n)
        if dump is not None:
            dump.append(sc.astype(np.float16))
        k = min(TOP1, len(sc))
        for j in np.argpartition(-sc, k - 1)[:k]:
            pool.append((float(sc[j]), n + int(j), info, int(j), Z[j].copy(), R[j].copy(), int(M[j]), int(OI[j])))
        pool.sort(key=lambda e: -e[0])
        del pool[TOP1:]
        n += len(sc)
    out, seen = [], set()
    for _, g, info, j, z, r, m, oi in pool:
        sc, de = SV.slot_batch(z[None], r[None], np.array([m]), np.array([oi]), B, R2, SEED + 1, g)
        st = mod.setting(info, j, de[0])
        t = mod.decrypt(ct, st)
        if t not in seen:
            seen.add(t)
            out.append({"text": t, "setting": st, "fam": fam, "quad": float(sc[0])})
    out.sort(key=lambda e: -e["quad"])
    return out[:KEEP], n, None


def process(row):
    rid, ct = row
    cands, nset, feas = [], {}, None
    for fam in FAMS:
        dump = [] if rid in FULL else None
        res, n, _ = scan_slot(fam, ct, dump)
        cands += res
        nset[fam] = n
        if dump is not None:
            SCORES[f"{rid}__{fam}"] = np.concatenate(dump)
    if rid in FULL:                          # R79's keyword families, pass-1 scores only (for the validator's G6)
        for fam in ("H7CT", "H7TXT", "LIB", "PROG"):
            dump = []
            scan_slot(fam, ct, dump, F79)
            SCORES[f"{rid}__R79_{fam}"] = np.concatenate(dump)
    seen, uniq = set(), []
    for e in cands:
        if e["text"] not in seen:
            seen.add(e["text"])
            uniq.append(e)
    lm = SCORER.lm_score(np.stack([core.codes(e["text"]) for e in uniq]))
    for e, v in zip(uniq, lm):
        e["lm_per_letter"] = float(v)
    uniq.sort(key=lambda e: -e["lm_per_letter"])
    top = uniq[:5]
    best_fam = {}
    for e in uniq:
        best_fam.setdefault(e["fam"], e)
    for e in top + list(best_fam.values()):
        e.setdefault("word_per_letter", SCORER.word_score(e["text"]))
    res = {"id": rid, "n_settings": nset, "best": top[0], "top": top, "best_by_fam": best_fam}
    if rid in FULL:
        res["scores"] = {k: v for k, v in SCORES.items() if k.startswith(rid + "__")}
        packet = list(best_fam.values()) + [e for e in uniq if e not in best_fam.values()]
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
    full, fams = [], list(F.FAMS)
    for flag in ("--full", "--fams"):
        if flag in args:
            i = args.index(flag)
            val = args[i + 1].split(",")
            args = args[:i] + args[i + 2:]
            if flag == "--full":
                full = val
            else:
                fams = val
    assert all(f in F.FAMS for f in fams)
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
    with Pool(procs, initializer=init, initargs=(str(lm), full, fams)) as pool:
        for k, r in enumerate(pool.imap_unordered(process, rows, chunksize=1)):
            if "scores" in r:
                (out / "scores").mkdir(exist_ok=True)
                sp = out / "scores" / f"{r['id']}.npz"
                np.savez_compressed(sp, **r.pop("scores"))
                extra.append((sp, "scores"))
            if "packet" in r:
                (out / "packet").mkdir(exist_ok=True)
                pp = out / "packet" / f"{r['id']}.json"
                pp.write_text(json.dumps(r.pop("packet"), indent=1) + "\n")
                extra.append((pp, "packet"))
            res[r["id"]] = r
            print(f"{k + 1}/{len(rows)} done", flush=True)
    (out / "RESULTS.jsonl").write_text("".join(json.dumps(res[r[0]]) + "\n" for r in rows))
    man = [(inp, "input"), (out / "RESULTS.jsonl", "results")] + sorted(extra) + [
        (ROOT / "r75/core.py", "core"), (ROOT / "r81a/families81.py", "families"), (ROOT / "r79/families.py", "families79"),
        (ROOT / "r79/solver.py", "solver"),
        (ROOT / "r79/slotsolve.c", "solver_c"), (Path(__file__), "runner"),
        (ROOT / "r75/data/kryptos_words.txt", "keywords"), (ROOT / "k4kit/data/k1k3_plaintext.txt", "k1k3_pt"),
        (ROOT / "archive/2026-10-26_allinone_extras/source_key_extensions/r27_sources.py", "k1k3_ct"),
        (ROOT / "k4kit/data/quad_log10.f32", "quadgrams"), (ROOT / "k4kit/data/word_model_orth.tsv", "word_model"),
        (lm, "letter_model")]
    (out / "FROZEN.sha256").write_text("".join(f"{sha(p)}  {lab}  {p.name}\n" for p, lab in man))
    print(f"R81a blind: {len(rows)} ciphertexts; families {','.join(fams)}; settings {res[rows[0][0]]['n_settings']}")


if __name__ == "__main__":
    main()
