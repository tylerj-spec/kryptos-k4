#!/usr/bin/env python3
"""RX2-O development run, VERSION 2: version 1's solver and parameters UNCHANGED (solve_v1.PARAMS_V1; v1 produced no
output, so nothing was learned from it), with v1's infrastructure failure fixed. v1 annealed every plant and then
failed to map the letter model in the same process under the 2,048 MiB per-process address-space limit, losing
everything (dev/v1/V1.md). Here the stages are separate jobs and the annealing output is written first:
  lmcheck LM.bin [REF.jsonl]   load the letter model (lean_scorer) in a fresh process; check scores against REF;
  anneal  PANEL.tsv OUT [P=2]  all restarts of every plant -> OUT/ANNEAL.jsonl (no letter model in any process);
  score   LM.bin OUT           fresh process: the KEEP best distinct decodes by quadgram, letter and word model,
                               top-1 = letter-model maximum -> OUT/RESULTS.jsonl (run_v1.py's format).
Reads PANEL.tsv only, never the panel truth. Usage: python3 -I .../dev/run_v2.py STAGE ARGS"""
import json
import os
import resource
import sys
import time
from pathlib import Path

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")   # before numpy: no per-thread buffers in the scoring process
os.environ.setdefault("OMP_NUM_THREADS", "1")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path[:0] = [str(HERE.parent), str(ROOT / "r75")]
import solve_v1 as S  # noqa: E402

P = S.PARAMS_V1


def lean_scorer(lm):
    """core.Scorer with the same letter-model arrays, built WITHOUT core.Scorer's whole-file uint8 header map. That
    map (1.29 GB) coexists with the per-order maps (another 1.29 GB) during core.Scorer.__init__, which is what
    exceeded the 2,048 MiB address-space limit (v2 lmcheck, first attempt). Same offsets, dtype and shapes; the file's
    sha256 is checked against r59/blind/LM_SHA256."""
    import hashlib
    import numpy as np
    import core
    h = hashlib.sha256()
    with open(lm, "rb") as f:
        head = f.read(8)
        f.seek(0)
        for chunk in iter(lambda: f.read(1 << 24), b""):
            h.update(chunk)
    assert h.hexdigest() == (ROOT / "r59/blind/LM_SHA256").read_text().split()[0], "letter model hash mismatch"
    if head[:5] != b"R59LM":
        raise ValueError("not an R59 letter model")
    sc = core.Scorer(None)
    sc.order = head[5]
    off, sz, sc.lm = 8, 26, {}
    for k in range(1, sc.order + 1):
        sc.lm[k] = np.memmap(lm, dtype=np.float32, mode="r", offset=off, shape=(sz,))
        off += sz * 4
        sz *= 26
    return sc


def vm_peak_mb():
    for line in open("/proc/self/status"):
        if line.startswith("VmPeak:"):
            return round(int(line.split()[1]) / 1024, 1)


def work(row):
    rid, label, ct = row
    t0 = time.process_time()
    res = S.restarts(ct, label, P["R"], P["I"], P["T0"], S.seed_of(ct, label, P["SEED"]))
    return rid, label, ct, res, time.process_time() - t0


def anneal(tsv, out, procs):
    from multiprocessing import Pool
    rows = []
    for line in tsv.read_text().splitlines()[1:]:
        rid, lab, ct = line.split("\t")
        f = lab.split(",")
        rows.append((rid, (f[0], f[1], *map(int, f[2:])), ct))
    out.mkdir(parents=True, exist_ok=False)
    S.lib()
    t = time.time()
    with open(out / "ANNEAL.jsonl", "w") as fh, Pool(procs) as pool:
        for rid, label, ct, res, cpu in pool.imap(work, rows, chunksize=1):     # input order, written as they finish
            fh.write(json.dumps({"id": rid, "label": label, "ct": ct, "cpu_s": round(cpu, 2),
                                 "restarts": [{"quad": sc, "W1": W1, "W2": W2, "text": tx} for sc, W1, W2, tx in res]})
                     + "\n")
            fh.flush()
    (out / "ANNEAL_RUN.json").write_text(json.dumps({"params": P, "procs": procs, "plants": len(rows),
                                                     "anneal_wall_s": round(time.time() - t, 1)}) + "\n")
    print("v2 anneal:", len(rows), "plants,", round(time.time() - t, 1), "s wall")


def score(lm, out):
    import numpy as np
    import core
    scorer = lean_scorer(lm)
    lines = []
    for line in (out / "ANNEAL.jsonl").read_text().splitlines():
        a = json.loads(line)
        seen, keep = set(), []
        for z in sorted(a["restarts"], key=lambda z: -z["quad"]):
            if z["text"] not in seen:
                seen.add(z["text"])
                keep.append({"quad": z["quad"], "W1": z["W1"], "W2": z["W2"], "text": z["text"]})
            if len(keep) == P["KEEP"]:
                break
        lmv = scorer.lm_score(np.stack([core.codes(c["text"]) for c in keep]))
        for c, v in zip(keep, lmv):
            c["lm_per_letter"] = float(v)
            c["word_per_letter"] = float(scorer.word_score(c["text"]))
        best = max(keep, key=lambda c: c["lm_per_letter"])
        lines.append(json.dumps({"id": a["id"], "label": a["label"], "cpu_s": a["cpu_s"], "best": best, "keep": keep,
                                 "restart_quads": [round(z["quad"], 3) for z in a["restarts"]],
                                 "restart_texts": [z["text"] for z in a["restarts"]]}) + "\n")
    (out / "RESULTS.jsonl").write_text("".join(lines))
    print("v2 score:", len(lines), "plants; VmPeak", vm_peak_mb(), "MB")


def lmcheck(lm, ref=None):
    """Load the letter model with lean_scorer and, given REF (a JSONL of decodes whose lm_per_letter core.Scorer
    computed, e.g. a spent R92 development RESULTS.jsonl), require equal scores on its first 20 best decodes."""
    import numpy as np
    import core
    scorer = lean_scorer(lm)
    n = 0
    if ref:
        for line in Path(ref).read_text().splitlines()[:20]:
            b = json.loads(line)["best"]
            v = float(scorer.lm_score(core.codes(b["text"])[None])[0])
            assert abs(v - b["lm_per_letter"]) < 1e-9, (v, b["lm_per_letter"])
            n += 1
    print("lmcheck ok:", n, "reference scores equal; VmPeak", vm_peak_mb(), "MB; RLIMIT_AS",
          resource.getrlimit(resource.RLIMIT_AS)[0] // 2 ** 20, "MB")


def main():
    st = sys.argv[1]
    if st == "lmcheck":
        lmcheck(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif st == "anneal":
        anneal(Path(sys.argv[2]), Path(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else 2)
    elif st == "score":
        score(sys.argv[2], Path(sys.argv[3]))
    else:
        raise SystemExit("stage: lmcheck | anneal | score")


if __name__ == "__main__":
    main()
