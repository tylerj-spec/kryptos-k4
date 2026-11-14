#!/usr/bin/env python3
"""R80a BLIND runner: two keyword stages on different tableaux, one key listed (word list or every 1-3 letter key), the
other free (r80a/two80.py). Reads only an "id<TAB>ciphertext" TSV, the generic English scorers (quadgram table, R59
order-6 letter model sha256-checked against r59/blind/LM_SHA256, R59 word model) and the family module; no truth, no
published K4 letters.
For each ciphertext and each family (L1, L2, X1, X2):
  pass 0  every setting (listed key x 96 conventions x free length 1..12) by r80a/twostage.c: each slot at its best
          single-letter fit, quadgram score, no ascent; the K0 best settings of each free length go on;
  pass 1  those settings, R79's solver (r79/slotsolve.c) with 1 start;
  pass 2  the family's TOP1 best settings again with 6 starts;
  keep    the family's KEEP best distinct decodes, re-derived by the explicit decryptor (two80.decrypt).
All kept decodes are re-scored by the letter model; the 5 best, and the best of each family, are stored with word
scores. Writes OUT/RESULTS.jsonl and OUT/FROZEN.sha256. Each finished ciphertext is kept in OUT/.partial/ until the
run completes, so a restarted run resumes (results are deterministic per ciphertext); .partial is removed at the end.
Usage: python3 -I r80a/blind/run.py LM.bin IN.tsv OUTDIR [PROCS=4] [--fams F1,F2,...]"""
import hashlib
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r75"))
sys.path.insert(0, str(ROOT / "r79"))
sys.path.insert(0, str(ROOT / "r80a"))
import core  # noqa: E402
import solver as SV  # noqa: E402
import two80 as T  # noqa: E402

SEED, K0, R1, R2, TOP1, KEEP = 800001, 4000, 1, 6, 150, 60
SCORER, FAMS = None, T.FAMS
REP = np.array([[i % m for i in range(T.N)] for m in range(1, T.MFREE + 1)], dtype=np.uint8)


def init(lm, fams):
    global SCORER, FAMS
    SCORER, FAMS = core.Scorer(lm), tuple(fams)
    for f in FAMS:
        for ka in T.A2:
            T.packed(f, ka)
    T.lib()


def gidx(fam, ci, wi, m):
    """Global setting index (seeds the solver, so a setting gives the same result in any batch)."""
    return ((T.FAMS.index(fam) * len(T.CONVS) + ci) * len(T.keys_for(fam)) + wi) * T.MFREE + (m - 1)


def pass0(fam, ct):
    """Per free length m: the K0 best (score, ci, wi) over every listed key and convention."""
    best = {m: [] for m in range(1, T.MFREE + 1)}
    for ci in range(len(T.CONVS)):
        S = T.scan(ct, fam, ci)
        for m in range(1, T.MFREE + 1):
            col = S[:, m - 1]
            k = min(K0, len(col))
            idx = np.argpartition(-col, k - 1)[:k]
            best[m].append(np.stack([col[idx].astype(np.float64), np.full(k, ci), idx], axis=1))
    out = {}
    for m, parts in best.items():
        A = np.concatenate(parts)
        A = A[np.lexsort((A[:, 2], A[:, 1], -A[:, 0]))][:K0]
        out[m] = [(float(s), int(c), int(w)) for s, c, w in A]
    return out


def scan_fam(fam, ct):
    p0 = pass0(fam, ct)
    pool = []
    for m, lst in p0.items():
        Z = np.zeros((len(lst), T.N), dtype=np.uint8)
        B = np.zeros((len(lst), T.N, 26), dtype=np.uint8)
        for j, (_, ci, wi) in enumerate(lst):
            Z[j], B[j] = T.build(ct, fam, ci, wi)
        R = np.repeat(REP[m - 1][None], len(lst), axis=0)
        M = np.full(len(lst), m, dtype=np.int32)
        OI = np.arange(len(lst), dtype=np.int32)
        for j, (_, ci, wi) in enumerate(lst):
            sc, _ = SV.slot_batch(Z[j:j + 1], R[j:j + 1], M[j:j + 1], np.zeros(1, dtype=np.int32), B[j:j + 1], R1,
                                  SEED, gidx(fam, ci, wi, m))
            pool.append((float(sc[0]), ci, wi, m, Z[j].copy(), B[j].copy()))
        pool.sort(key=lambda e: -e[0])
        del pool[TOP1:]
    out, seen = [], set()
    for _, ci, wi, m, z, b in pool[:TOP1]:
        sc, de = SV.slot_batch(z[None], REP[m - 1][None], np.array([m], dtype=np.int32), np.zeros(1, dtype=np.int32),
                               b[None], R2, SEED + 1, gidx(fam, ci, wi, m))
        st = T.setting(fam, ci, wi, m, de[0])
        t = T.decrypt(ct, st)
        assert t == T.decode_with(z, b, m, de[0])
        if t not in seen:
            seen.add(t)
            out.append({"text": t, "setting": st, "fam": fam, "quad": float(sc[0])})
    out.sort(key=lambda e: -e["quad"])
    n = len(T.keys_for(fam)) * len(T.CONVS) * T.MFREE
    return out[:KEEP], n


def process(row):
    rid, ct = row
    cands, nset = [], {}
    for fam in FAMS:
        res, n = scan_fam(fam, ct)
        cands += res
        nset[fam] = n
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
    return {"id": rid, "n_settings": nset, "best": top[0], "top": top, "best_by_fam": best_fam}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def main():
    args = sys.argv[1:]
    fams = list(T.FAMS)
    if "--fams" in args:
        i = args.index("--fams")
        fams = args[i + 1].split(",")
        args = args[:i] + args[i + 2:]
    assert all(f in T.FAMS for f in fams)
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
    part = out / ".partial"
    part.mkdir(exist_ok=True)
    res = {}
    for p in part.glob("*.json"):
        r = json.loads(p.read_text())
        if r.get("families") == fams:
            res[r["id"]] = r
    todo = [r for r in rows if r[0] not in res]
    print(f"resuming: {len(res)} already done, {len(todo)} to run", flush=True)
    with Pool(procs, initializer=init, initargs=(str(lm), fams)) as pool:
        for k, r in enumerate(pool.imap_unordered(process, todo, chunksize=1)):
            r["families"] = fams
            (part / f"{r['id']}.json.tmp").write_text(json.dumps(r))
            (part / f"{r['id']}.json.tmp").replace(part / f"{r['id']}.json")
            res[r["id"]] = r
            print(f"{len(res)}/{len(rows)} done", flush=True)
    for r in res.values():
        r.pop("families", None)
    (out / "RESULTS.jsonl").write_text("".join(json.dumps(res[r[0]]) + "\n" for r in rows))
    for p in part.glob("*"):
        p.unlink()
    part.rmdir()
    man = [(inp, "input"), (out / "RESULTS.jsonl", "results"),
           (ROOT / "r75/core.py", "core"), (ROOT / "r80a/two80.py", "families"), (ROOT / "r80a/twostage.c", "pass0_c"),
           (ROOT / "r79/solver.py", "solver"), (ROOT / "r79/slotsolve.c", "solver_c"), (Path(__file__), "runner"),
           (ROOT / "r75/data/kryptos_words.txt", "keywords"), (ROOT / "k4kit/data/quad_log10.f32", "quadgrams"),
           (ROOT / "k4kit/data/word_model_orth.tsv", "word_model"), (lm, "letter_model")]
    (out / "FROZEN.sha256").write_text("".join(f"{sha(p)}  {lab}  {p.name}\n" for p, lab in man))
    print(f"R80a blind: {len(rows)} ciphertexts; families {','.join(fams)}")


if __name__ == "__main__":
    main()
