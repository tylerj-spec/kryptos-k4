#!/usr/bin/env python3
"""R63 BLIND runner. Reads only an "id<TAB>ciphertext" TSV and generic models; no K4 clue data.
Runs r63/blind/rk2_solve.cpp (English plaintext model + one non-English key model) for each of the two key models
(CLOCK = World Clock city-name sequences, GERMAN = German prose), sharded over PROCS processes, and merges:
  {"id", "models": {"CLOCK": best, "GERMAN": best}}  (each best: convention, plaintext, key, lm, word, total).
Usage: python3 -I r63/blind/run.py IN.tsv OUTDIR ENGLISH_LM KEYDIR SOLVER [PROCS=4]
  KEYDIR holds lm6_clock.bin, clock_words.tsv, lm6_de.bin, de_words.tsv (r63/corpus/build_keys.py + lm_build);
  every model file's sha256 must match r63/blind/MODELS.sha256 (English LM: r59/blind/LM_SHA256).
Parameters fixed (R63 pre-registration): BEAM 50000, TOPN 2000, LAMBDA 1, all 6 conventions, POLISH_M 2, WORDS 20000.
Work is split into chunks of CHUNK ciphertexts per model; finished chunks are reused after an interruption
(the solver is deterministic)."""
import hashlib
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORDS_EN = ROOT / "k4kit/data/word_model_orth.tsv"
PARAMS = ["50000", "2000", "1", "all", "2", "20000"]
CHUNK = 3   # ciphertexts per solver call: small chunks make an interrupted run cheap to resume
MODELS = {"CLOCK": ("lm6_clock.bin", "clock_words.tsv"), "GERMAN": ("lm6_de.bin", "de_words.tsv")}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    inp, out, lm_en, keydir, solver = (Path(a) for a in sys.argv[1:6])
    procs = int(sys.argv[6]) if len(sys.argv) > 6 else 4
    if sha(lm_en) != (ROOT / "r59/blind/LM_SHA256").read_text().split()[0]:
        raise SystemExit("English LM sha256 mismatch")
    reg = dict(l.split()[::-1][:2] for l in (ROOT / "r63/blind/MODELS.sha256").read_text().splitlines() if l.strip())
    for f in [x for pair in MODELS.values() for x in pair]:
        if sha(keydir / f) != reg[f]:
            raise SystemExit(f"key model sha256 mismatch: {f}")
    out.mkdir(parents=True, exist_ok=True)
    if (out / "RESULTS.jsonl").exists():
        raise SystemExit("refusing to overwrite")
    work = out / "work"
    work.mkdir(exist_ok=True)
    rows = [l for l in inp.read_text().splitlines() if l and not l.startswith("id\t")]
    ids = [r.split("\t")[0] for r in rows]
    if len(set(ids)) != len(ids):
        raise SystemExit("duplicate ids")
    chunks = [rows[i:i + CHUNK] for i in range(0, len(rows), CHUNK)]
    res = {i: {"id": i, "models": {}} for i in ids}
    jobs = []
    for m, (lmf, wf) in MODELS.items():
        for c, ch in enumerate(chunks):
            tsv, js = work / f"{m}_{c:03d}.tsv", work / f"{m}_{c:03d}.jsonl"
            tsv.write_text("\n".join(ch) + "\n")
            jobs.append((m, lmf, wf, tsv, js, len(ch)))

    def run(job):
        m, lmf, wf, tsv, js, n = job
        have = [l for l in js.read_text().splitlines() if l.strip()] if js.exists() else []
        if len(have) == n:
            return js   # finished chunk from an interrupted run (the solver is deterministic)
        with open(js.with_suffix(".log"), "w") as lg:
            r = subprocess.run([str(solver), str(lm_en), str(WORDS_EN), str(keydir / lmf), str(keydir / wf),
                                str(tsv), str(js)] + PARAMS, stderr=lg)
        if r.returncode != 0:
            raise RuntimeError(f"solver failed: {js}")
        return js

    with ThreadPoolExecutor(procs) as ex:
        for js in ex.map(run, jobs):
            m = js.name.split("_")[0]
            for line in js.read_text().splitlines():
                if line.strip():
                    r = json.loads(line)
                    res[r["id"]]["models"][m] = r["best"]
    if any(len(r["models"]) != len(MODELS) for r in res.values()):
        raise SystemExit("missing results")
    (out / "RESULTS.jsonl").write_text("".join(json.dumps(res[i], separators=(",", ":")) + "\n" for i in ids))
    man = [(inp, "input"), (out / "RESULTS.jsonl", "results"), (ROOT / "r63/blind/rk2_solve.cpp", "solver_source"),
           (solver, "solver_binary"), (lm_en, "english_lm"), (WORDS_EN, "english_words")] + \
          [(keydir / f, "key_model") for pair in MODELS.values() for f in pair] + \
          [(Path(__file__), "runner"), (ROOT / "r63/PREREGISTRATION.md", "protocol")]
    (out / "FROZEN.sha256").write_text("".join(f"{sha(p)}  {lab}  {p.name}\n" for p, lab in man))
    print(f"R63 froze {len(ids)} results in {out}")


if __name__ == "__main__":
    main()
