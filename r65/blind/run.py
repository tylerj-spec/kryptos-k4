#!/usr/bin/env python3
"""R65 BLIND runner: R64's stage 1 under the GERMAN key model only, unchanged (r64/blind/run.py: the 10 R61 routes,
R63 two-model solver, beam 15000, TOPN 2000, LAMBDA 1, all 6 conventions, POLISH_M 0, WORDS 20000).
For each ciphertext it records every route's stage-1 best and the statistic
    G = (best stage-1 route total) - (second-best stage-1 route total)   [ties: lower route index first]
Reads only an "id<TAB>ciphertext" TSV and generic models; no K4 clue data.
Usage: python3 -I r65/blind/run.py IN.tsv OUTDIR ENGLISH_LM KEYDIR SOLVER [PROCS=4]
Writes OUTDIR/RESULTS.jsonl, OUTDIR/FROZEN.sha256 and OUTDIR/WORK.sha256 (raw solver outputs in OUTDIR/work/).
A finished ciphertext is reused after an interruption only if its stored digest matches."""
import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r64/blind"))
import run as r64  # noqa: E402  (load_routes, unroute, solve, sha, MODELS, P1, WORDS_EN: unchanged R64 code)

MODEL = "GERMAN"


def job(a):
    rid, ct, work, solver, margs, digest, routes = a
    base = work / rid
    done = Path(f"{base}.result.json")
    if done.exists():
        r = json.loads(done.read_text())
        if r.get("digest") == digest:
            return rid, r["result"]
        done.unlink()
    s1 = Path(f"{base}.s1.tsv")
    s1.write_text("".join(f"{rid}__{i}\t{r64.unroute(ct, p)}\n" for i, (_, p) in enumerate(routes)))
    r1 = r64.solve(solver, margs, s1, f"{base}.s1.jsonl", r64.P1, f"{base}.s1.log")
    st = []
    for r in r1:
        i = int(r["id"].rsplit("__", 1)[1])
        st.append({"route": routes[i][0], "idx": i, "convention": r["best"]["convention"], "total": r["best"]["total"]})
    if sorted(d["idx"] for d in st) != list(range(10)):
        raise RuntimeError(f"stage 1 incomplete: {base}")
    st.sort(key=lambda d: (-d["total"], d["idx"]))
    res = {"best_route": st[0]["route"], "gap": st[0]["total"] - st[1]["total"],
           "stage1": [{k: v for k, v in d.items() if k != "idx"} for d in st]}
    done.write_text(json.dumps({"id": rid, "ct": ct, "digest": digest, "result": res}))
    return rid, res


def main():
    inp, out, lm_en, keydir, solver = (Path(a) for a in sys.argv[1:6])
    procs = int(sys.argv[6]) if len(sys.argv) > 6 else 4
    h_en = r64.sha(lm_en)
    if h_en != (ROOT / "r59/blind/LM_SHA256").read_text().split()[0]:
        raise SystemExit("English LM sha256 mismatch")
    reg = dict(l.split()[::-1][:2] for l in (ROOT / "r63/blind/MODELS.sha256").read_text().splitlines() if l.strip())
    lmf, wf = r64.MODELS[MODEL]
    hashes = {"english_lm": h_en, "routes": r64.sha(r64.ROUTES), "solver": r64.sha(solver), "words_en": r64.sha(r64.WORDS_EN)}
    for f in (lmf, wf):
        if (h := r64.sha(keydir / f)) != reg[f]:
            raise SystemExit(f"key model sha256 mismatch: {f}")
        hashes[f] = h
    routes = r64.load_routes()
    out.mkdir(parents=True, exist_ok=True)
    if (out / "RESULTS.jsonl").exists():
        raise SystemExit("refusing to overwrite")
    work = out / "work"
    work.mkdir(exist_ok=True)
    rows = [l.split("\t") for l in inp.read_text().splitlines() if l and not l.startswith("id\t")]
    ids = [r[0] for r in rows]
    if len(set(ids)) != len(ids):
        raise SystemExit("duplicate ids")
    margs = [lm_en, r64.WORDS_EN, keydir / lmf, keydir / wf]
    jobs = []
    for rid, ct in rows:
        if len(ct) != 97 or not ct.isalpha() or not ct.isupper():
            raise SystemExit(f"bad ciphertext {rid}")
        dig = hashlib.sha256(json.dumps({"ct": ct, "model": MODEL, "hashes": hashes, "P1": r64.P1},
                                        sort_keys=True).encode()).hexdigest()
        jobs.append((rid, ct, work, solver, margs, dig, routes))
    res = {}
    with ThreadPoolExecutor(procs) as ex:
        for rid, r in ex.map(job, jobs):
            res[rid] = r
            print(f"R65 {rid} gap {r['gap']:.4f} best {r['best_route']}", flush=True)
    (out / "RESULTS.jsonl").write_text("".join(json.dumps({"id": i, **res[i]}, separators=(",", ":")) + "\n" for i in ids))
    man = [(inp, "input"), (out / "RESULTS.jsonl", "results"), (ROOT / "r63/blind/rk2_solve.cpp", "solver_source"),
           (solver, "solver_binary"), (lm_en, "english_lm"), (r64.WORDS_EN, "english_words"), (r64.ROUTES, "routes"),
           (keydir / lmf, "key_model"), (keydir / wf, "key_model"), (Path(__file__), "runner"),
           (ROOT / "r64/blind/run.py", "r64_runner"), (ROOT / "r65/PREREGISTRATION.md", "protocol")]
    (out / "FROZEN.sha256").write_text("".join(f"{r64.sha(p)}  {lab}  {p.name}\n" for p, lab in man))
    (out / "WORK.sha256").write_text("".join(f"{r64.sha(p)}  {p.name}\n" for p in sorted(work.iterdir())))
    print(f"R65 froze {len(ids)} results in {out}")


if __name__ == "__main__":
    main()
