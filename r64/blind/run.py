#!/usr/bin/env python3
"""R64 BLIND runner. Reads only an "id<TAB>ciphertext" TSV, r61/routes.txt and generic models; no K4 clue data.
Hypothesis family: ordinary English plaintext P, key K from a NON-English model (R63 CLOCK or GERMAN), letterwise
substitution X[i] = S(P[i], K[i]) under one of 6 conventions (AZ/KRY x VIG/BEAU/VARB), THEN one of the 10 frozen R61
routes: CT[j] = X[perm[j]].
For each ciphertext and each key model m (CLOCK, GERMAN), separately:
  stage 1  undo every route (X[perm[j]] = CT[j]) and run the unchanged R63 solver r63/blind/rk2_solve.cpp WITHOUT
           polish (beam B1, TOPN 2000, LAMBDA 1, all 6 conventions, POLISH_M 0, WORDS 20000);
  stage 2  the TOP_ROUTES best routes by stage-1 total (ties: lower route index) are re-solved with the full R63
           parameters (beam 50000, TOPN 2000, LAMBDA 1, all, POLISH_M 2, WORDS 20000);
  answer   the best stage-2 total (ties: lower route index): route, convention, plaintext and key in PLAINTEXT order.
Every raw solver output (stage 1: 10 routes x {best, 6 per-convention bests, top 8}; stage 2 likewise) is kept in
OUTDIR/work/. A finished (ciphertext, model) job is reused after an interruption only if its stored digest matches
sha256 of (ciphertext, model, every model-file hash, routes hash, solver-binary hash, parameters).
Usage: python3 -I r64/blind/run.py IN.tsv OUTDIR ENGLISH_LM KEYDIR SOLVER [PROCS=4]
  KEYDIR holds lm6_clock.bin, clock_words.tsv, lm6_de.bin, de_words.tsv (hashes in r63/blind/MODELS.sha256);
  ENGLISH_LM must match r59/blind/LM_SHA256.
Writes OUTDIR/RESULTS.jsonl, OUTDIR/FROZEN.sha256 (code, models, input, results) and OUTDIR/WORK.sha256 (every raw
work file). Refuses to overwrite RESULTS.jsonl."""
import hashlib
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORDS_EN = ROOT / "k4kit/data/word_model_orth.tsv"
ROUTES = ROOT / "r61/routes.txt"
MODELS = {"CLOCK": ("lm6_clock.bin", "clock_words.tsv"), "GERMAN": ("lm6_de.bin", "de_words.tsv")}
B1 = "15000"          # stage-1 beam: fixed from development (r64/PREREGISTRATION.md), never from K4
TOP_ROUTES = 2
P1 = [B1, "2000", "1", "all", "0", "20000"]
P2 = ["50000", "2000", "1", "all", "2", "20000"]   # unchanged R63 parameters


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def load_routes():
    out = []
    for line in ROUTES.read_text().splitlines():
        name, order, p = line.split()
        perm = [int(x) for x in p.split(",")]
        if order != "S_then_T" or sorted(perm) != list(range(97)):
            raise SystemExit(f"bad route {name}")
        out.append((name, perm))
    if len(out) != 10:
        raise SystemExit("expected the 10 frozen R61 routes")
    return out


def unroute(ct, perm):
    x = [""] * len(ct)
    for j, src in enumerate(perm):
        x[src] = ct[j]
    return "".join(x)


def solve(solver, args, tsv, out, params, log):
    with open(log, "w") as lg:
        r = subprocess.run([str(solver)] + [str(a) for a in args] + [str(tsv), str(out)] + params, stderr=lg)
    if r.returncode != 0:
        raise RuntimeError(f"solver failed: {log}")
    return [json.loads(l) for l in Path(out).read_text().splitlines() if l.strip()]


def job(a):
    rid, ct, m, work, solver, margs, digest, routes = a
    base = work / f"{rid.replace('/', '_')}.{m}"
    done = Path(f"{base}.result.json")
    if done.exists():
        r = json.loads(done.read_text())
        if r.get("digest") == digest:
            return rid, m, r["result"]
        done.unlink()   # stale: different ciphertext, models, routes, binary or parameters
    s1 = Path(f"{base}.s1.tsv")
    s1.write_text("".join(f"{rid}__{i}\t{unroute(ct, p)}\n" for i, (_, p) in enumerate(routes)))
    r1 = solve(solver, margs, s1, f"{base}.s1.jsonl", P1, f"{base}.s1.log")
    st1 = []
    for r in r1:
        i = int(r["id"].rsplit("__", 1)[1])
        st1.append({"route": routes[i][0], "idx": i, "convention": r["best"]["convention"], "total": r["best"]["total"]})
    if sorted(d["idx"] for d in st1) != list(range(10)):
        raise RuntimeError(f"stage 1 incomplete: {base}")
    st1.sort(key=lambda d: (-d["total"], d["idx"]))
    s2 = Path(f"{base}.s2.tsv")
    s2.write_text("".join(f"{rid}__{d['idx']}\t{unroute(ct, routes[d['idx']][1])}\n" for d in st1[:TOP_ROUTES]))
    r2 = solve(solver, margs, s2, f"{base}.s2.jsonl", P2, f"{base}.s2.log")
    st2 = []
    for r in r2:
        i = int(r["id"].rsplit("__", 1)[1])
        st2.append({"route": routes[i][0], "idx": i, **r["best"]})
    st2.sort(key=lambda d: (-d["total"], d["idx"]))
    res = {**{k: v for k, v in st2[0].items() if k != "idx"},
           "stage1": [{k: v for k, v in d.items() if k != "idx"} for d in st1],
           "stage2": [{k: v for k, v in d.items() if k != "idx"} for d in st2]}
    done.write_text(json.dumps({"id": rid, "model": m, "ct": ct, "digest": digest, "result": res}))
    return rid, m, res


def main():
    inp, out, lm_en, keydir, solver = (Path(a) for a in sys.argv[1:6])
    procs = int(sys.argv[6]) if len(sys.argv) > 6 else 4
    h_en = sha(lm_en)
    if h_en != (ROOT / "r59/blind/LM_SHA256").read_text().split()[0]:
        raise SystemExit("English LM sha256 mismatch")
    reg = dict(l.split()[::-1][:2] for l in (ROOT / "r63/blind/MODELS.sha256").read_text().splitlines() if l.strip())
    hashes = {"english_lm": h_en, "routes": sha(ROUTES), "solver": sha(solver), "words_en": sha(WORDS_EN)}
    for f in [x for pair in MODELS.values() for x in pair]:
        if (h := sha(keydir / f)) != reg[f]:
            raise SystemExit(f"key model sha256 mismatch: {f}")
        hashes[f] = h
    routes = load_routes()
    out.mkdir(parents=True, exist_ok=True)
    if (out / "RESULTS.jsonl").exists():
        raise SystemExit("refusing to overwrite")
    work = out / "work"
    work.mkdir(exist_ok=True)
    rows = [l.split("\t") for l in inp.read_text().splitlines() if l and not l.startswith("id\t")]
    ids = [r[0] for r in rows]
    if len(set(ids)) != len(ids):
        raise SystemExit("duplicate ids")
    jobs = []
    for rid, ct in rows:
        if len(ct) != 97 or not ct.isalpha() or not ct.isupper():
            raise SystemExit(f"bad ciphertext {rid}")
        for m, (lmf, wf) in MODELS.items():
            dig = hashlib.sha256(json.dumps({"ct": ct, "model": m, "hashes": hashes, "P1": P1, "P2": P2,
                                             "top": TOP_ROUTES}, sort_keys=True).encode()).hexdigest()
            margs = [lm_en, WORDS_EN, keydir / lmf, keydir / wf]
            jobs.append((rid, ct, m, work, solver, margs, dig, routes))
    res = {i: {"id": i, "models": {}} for i in ids}
    with ThreadPoolExecutor(procs) as ex:
        for rid, m, r in ex.map(job, jobs):
            res[rid]["models"][m] = r
            print(f"R64 {rid} {m} {r['total']:.2f} {r['route']} {r['convention']}", flush=True)
    (out / "RESULTS.jsonl").write_text("".join(json.dumps(res[i], separators=(",", ":")) + "\n" for i in ids))
    man = [(inp, "input"), (out / "RESULTS.jsonl", "results"), (ROOT / "r63/blind/rk2_solve.cpp", "solver_source"),
           (solver, "solver_binary"), (lm_en, "english_lm"), (WORDS_EN, "english_words"), (ROUTES, "routes")] + \
          [(keydir / f, "key_model") for pair in MODELS.values() for f in pair] + \
          [(Path(__file__), "runner"), (ROOT / "r64/PREREGISTRATION.md", "protocol")]
    (out / "FROZEN.sha256").write_text("".join(f"{sha(p)}  {lab}  {p.name}\n" for p, lab in man))
    (out / "WORK.sha256").write_text("".join(f"{sha(p)}  {p.name}\n" for p in sorted(work.iterdir())))
    print(f"R64 froze {len(ids)} results in {out} (B1={B1}, TOP_ROUTES={TOP_ROUTES})")


if __name__ == "__main__":
    main()
