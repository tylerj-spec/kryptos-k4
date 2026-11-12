#!/usr/bin/env python3
"""R79 BLIND runner. Reads only an "id<TAB>ciphertext" TSV, the generic English scorers (quadgram table, R59 order-6
letter model sha256-checked against r59/blind/LM_SHA256, R59 word model) and r79/families.py; no truth, no published
K4 letters.
For each ciphertext and each family:
  pass 1  every setting, solver with 1 start (each slot's best single-letter fit), quadgram objective;
  pass 2  the family's 150 best settings again with 6 starts;
  keep    the family's 60 best distinct decodes; keyword decodes are re-derived by the explicit decryptor.
All kept decodes are re-scored by the letter model; the 5 best, and the best of each family, are stored with word
scores. For ids given with --full a 25-decode review packet is also stored. H11 also stores how many settings pass
the cycle conditions (ciphertext only), per convention.
Writes OUT/RESULTS.jsonl, OUT/packet/<id>.json and OUT/FROZEN.sha256.
Usage: python3 -I r79/blind/run.py LM.bin IN.tsv OUTDIR [PROCS=4] [--fams F1,F2,...] [--full ID[,ID...]]"""
import hashlib
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r75"))
sys.path.insert(0, str(ROOT / "r79"))
import core  # noqa: E402
import families as F  # noqa: E402
import solver as SV  # noqa: E402

SEED, R1, R2, TOP1, KEEP = 790001, 1, 6, 150, 60
SCORER, FULL, FAMS = None, set(), F.FAMS


def init(lm, full, fams):
    global SCORER, FULL, FAMS
    SCORER, FULL, FAMS = core.Scorer(lm), set(full), tuple(fams)
    F.bank(), F.streams(), F.routes()


def scan_slot(fam, ct):
    B = F.bank()[0]
    pool, n = [], 0
    for Z, R, M, OI, info in F.chunks(fam, ct):
        sc, _ = SV.slot_batch(Z, R, M, OI, B, R1, SEED, n)
        k = min(TOP1, len(sc))
        for j in np.argpartition(-sc, k - 1)[:k]:
            pool.append((float(sc[j]), n + int(j), info, int(j), Z[j].copy(), R[j].copy(), int(M[j]), int(OI[j])))
        pool.sort(key=lambda e: -e[0])
        del pool[TOP1:]
        n += len(sc)
    out, seen = [], set()
    for _, g, info, j, z, r, m, oi in pool:
        sc, de = SV.slot_batch(z[None], r[None], np.array([m]), np.array([oi]), B, R2, SEED + 1, g)
        st = F.setting(info, j, de[0])
        t = F.decrypt(ct, st)
        if t not in seen:
            seen.add(t)
            out.append({"text": t, "setting": st, "fam": fam, "quad": float(sc[0])})
    out.sort(key=lambda e: -e["quad"])
    return out[:KEEP], n, None


def scan_h11(ct):
    names, P = F.routes()
    steps, lets = F.h11_tables()
    c = core.codes(ct).astype(np.int64)
    Y = np.stack([F.IDX[ca][c] for _, _, ca, _ in F.H11_CONV]).astype(np.uint8)
    sc, lc = SV.cyc_batch(P, Y, steps, lets, R1, SEED, 0)
    feas = {"/".join(cv): int((sc[:, k] > -1e8).sum()) for k, cv in enumerate(F.H11_CONV)}
    flat = sc.ravel()
    k = min(TOP1, int((flat > -1e8).sum()))
    out, seen = [], set()
    if k:
        for g in np.argpartition(-flat, k - 1)[:k]:
            r, cv = divmod(int(g), len(F.H11_CONV))
            txt, s2 = SV.cyc_text(Y[cv], P[r], steps[cv], lets[cv], R2, SEED + 1, int(g))
            t = core.text(txt)
            if t not in seen:
                seen.add(t)
                pa, ka, ca, op = F.H11_CONV[cv]
                out.append({"text": t, "fam": "H11", "quad": s2, "log10_candidates": float(lc[r, cv]),
                            "setting": {"fam": "H11", "route": names[r], "pa": pa, "ka": ka, "ca": ca, "op": op}})
    out.sort(key=lambda e: -e["quad"])
    return out[:KEEP], int(sc.size), feas


def process(row):
    rid, ct = row
    cands, nset, feas = [], {}, None
    for fam in FAMS:
        res, n, f = scan_h11(ct) if fam == "H11" else scan_slot(fam, ct)
        cands += res
        nset[fam] = n
        feas = f if fam == "H11" else feas
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
    res = {"id": rid, "n_settings": nset, "h11_feasible": feas, "best": top[0], "top": top, "best_by_fam": best_fam}
    if rid in FULL:
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
            if "packet" in r:
                (out / "packet").mkdir(exist_ok=True)
                pp = out / "packet" / f"{r['id']}.json"
                pp.write_text(json.dumps(r.pop("packet"), indent=1) + "\n")
                extra.append((pp, "packet"))
            res[r["id"]] = r
            print(f"{k + 1}/{len(rows)} done", flush=True)
    (out / "RESULTS.jsonl").write_text("".join(json.dumps(res[r[0]]) + "\n" for r in rows))
    man = [(inp, "input"), (out / "RESULTS.jsonl", "results")] + sorted(extra) + [
        (ROOT / "r75/core.py", "core"), (ROOT / "r79/families.py", "families"), (ROOT / "r79/solver.py", "solver"),
        (ROOT / "r79/slotsolve.c", "solver_c"), (Path(__file__), "runner"), (ROOT / "r76/routes76.py", "routes"),
        (ROOT / "r75/data/kryptos_words.txt", "keywords"), (ROOT / "k4kit/data/k1k3_plaintext.txt", "k1k3_pt"),
        (ROOT / "archive/2026-10-26_allinone_extras/source_key_extensions/r27_sources.py", "k1k3_ct"),
        (ROOT / "k4kit/data/quad_log10.f32", "quadgrams"), (ROOT / "k4kit/data/word_model_orth.tsv", "word_model"),
        (lm, "letter_model")]
    (out / "FROZEN.sha256").write_text("".join(f"{sha(p)}  {lab}  {p.name}\n" for p, lab in man))
    print(f"R79 blind: {len(rows)} ciphertexts; families {','.join(fams)}; settings {res[rows[0][0]]['n_settings']}")


if __name__ == "__main__":
    main()
