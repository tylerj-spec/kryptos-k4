#!/usr/bin/env python3
"""R69 BLIND runner: R64/R65's stage 1 under the GERMAN key model, unchanged (R63 two-model solver, beam 15000,
TOPN 2000, LAMBDA 1, all 6 conventions, POLISH_M 0, WORDS 20000), applied to the R69 readings (r69/data/patterns.txt).
Input TSV columns: id, ciphertext, set. set F = the 16 F readings only; set A = all 78 (F + B). Identical permutations
(F_0101 = B_c27_q0, F_1010 = B_c27_q1) are solved once and reported under both names.
For each ciphertext it records every requested reading's stage-1 best total and convention.
Reads only the TSV and generic models; no K4 clue data.
Usage: python3 -I r69/blind/run.py IN.tsv OUTDIR ENGLISH_LM KEYDIR SOLVER [PROCS=4]
Writes OUTDIR/RESULTS.jsonl, OUTDIR/FROZEN.sha256 and OUTDIR/WORK.sha256 (raw solver outputs in OUTDIR/work/).
A finished ciphertext is reused after an interruption only if its stored digest matches."""
import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r64/blind"))
import run as r64  # noqa: E402  (unroute, solve, sha, MODELS, P1, WORDS_EN: unchanged R64 code)

MODEL = "GERMAN"
PATTERNS = ROOT / "r69/data/patterns.txt"


def load_patterns():
    out = []
    for line in PATTERNS.read_text().splitlines():
        name, order, p = line.split()
        perm = [int(x) for x in p.split(",")]
        if order != "S_then_T" or sorted(perm) != list(range(97)):
            raise SystemExit(f"bad reading {name}")
        out.append((name, perm))
    if len(out) != 78 or sum(n.startswith("F_") for n, _ in out) != 16:
        raise SystemExit("expected 16 F + 62 B readings")
    return out


def job(a):
    rid, ct, sset, work, solver, margs, digest, pats = a
    base = work / rid
    done = Path(f"{base}.result.json")
    if done.exists():
        r = json.loads(done.read_text())
        if r.get("digest") == digest:
            return rid, r["result"]
        done.unlink()
    want = [(n, p) for n, p in pats if sset == "A" or n.startswith("F_")]
    uniq, alias = [], {}
    for n, p in want:
        key = tuple(p)
        if key not in alias:
            alias[key] = len(uniq)
            uniq.append(p)
    s1 = Path(f"{base}.s1.tsv")
    s1.write_text("".join(f"{rid}__{i}\t{r64.unroute(ct, p)}\n" for i, p in enumerate(uniq)))
    r1 = r64.solve(solver, margs, s1, f"{base}.s1.jsonl", r64.P1, f"{base}.s1.log")
    got = {int(r["id"].rsplit("__", 1)[1]): r["best"] for r in r1}
    if sorted(got) != list(range(len(uniq))):
        raise RuntimeError(f"stage 1 incomplete: {base}")
    res = {"set": sset, "readings": {n: {"convention": got[alias[tuple(p)]]["convention"],
                                         "total": got[alias[tuple(p)]]["total"]} for n, p in want}}
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
    hashes = {"english_lm": h_en, "patterns": r64.sha(PATTERNS), "solver": r64.sha(solver), "words_en": r64.sha(r64.WORDS_EN)}
    for f in (lmf, wf):
        if (h := r64.sha(keydir / f)) != reg[f]:
            raise SystemExit(f"key model sha256 mismatch: {f}")
        hashes[f] = h
    pats = load_patterns()
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
    for rid, ct, sset in rows:
        if len(ct) != 97 or not ct.isalpha() or not ct.isupper() or sset not in ("A", "F"):
            raise SystemExit(f"bad row {rid}")
        dig = hashlib.sha256(json.dumps({"ct": ct, "set": sset, "model": MODEL, "hashes": hashes, "P1": r64.P1},
                                        sort_keys=True).encode()).hexdigest()
        jobs.append((rid, ct, sset, work, solver, margs, dig, pats))
    res = {}
    with ThreadPoolExecutor(procs) as ex:
        for rid, r in ex.map(job, jobs):
            res[rid] = r
            best = max(r["readings"].items(), key=lambda kv: kv[1]["total"])
            print(f"R69 {rid} set {r['set']} best {best[0]} {best[1]['total']:.4f}", flush=True)
    (out / "RESULTS.jsonl").write_text("".join(json.dumps({"id": i, **res[i]}, separators=(",", ":")) + "\n" for i in ids))
    man = [(inp, "input"), (out / "RESULTS.jsonl", "results"), (ROOT / "r63/blind/rk2_solve.cpp", "solver_source"),
           (solver, "solver_binary"), (lm_en, "english_lm"), (r64.WORDS_EN, "english_words"), (PATTERNS, "patterns"),
           (keydir / lmf, "key_model"), (keydir / wf, "key_model"), (Path(__file__), "runner"),
           (ROOT / "r64/blind/run.py", "r64_runner"), (ROOT / "r69/PREREGISTRATION.md", "protocol")]
    (out / "FROZEN.sha256").write_text("".join(f"{r64.sha(p)}  {lab}  {p.name}\n" for p, lab in man))
    (out / "WORK.sha256").write_text("".join(f"{r64.sha(p)}  {p.name}\n" for p in sorted(work.iterdir())))
    print(f"R69 froze {len(ids)} results in {out}")


if __name__ == "__main__":
    main()
