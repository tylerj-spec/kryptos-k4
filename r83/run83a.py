#!/usr/bin/env python3
"""R83a runner (CRIB-ASSISTED, exclusion-only; rules fixed in r83/PREREGISTRATION.md). Refused unless
r83/PROTOCOL.sha256 exists and every file it lists matches.
The published letters come from r73/sealed/reveal_k4.py (0-based plaintext positions 21-33 and 63-73). They are
used only inside the algebraic checks; nothing is decrypted, no key is completed, nothing is ranked.
Steps (TARGET = K4 + shuffles from r83/prepare_k4.py, seed 830400):
  EXACT  LX, PFX, WPX, SLX, SLX-A, SSX on K4 and the first 20 shuffles;
  DROP   the same with drop-one (G6): LX on K4 and the first 5 shuffles, the others on K4 and the first 20;
  SHIFT  the same, exact, with one published run moved by -2, -1, +1 or +2 positions (8 position sets; the letters
         unchanged): LX on K4 and the first 5 shuffles, the others on K4 and the first 20;
  F1XD   R75's F1X, unchanged, with drop-one, on K4 and the first 20 shuffles.
Each job is kept in OUT/parts/ (a restarted run resumes; results are deterministic). At the end: OUT/R83A.json
(aggregated) and OUT/FROZEN.sha256.
Usage: python3 -I r83/run83a.py TARGET.tsv OUTDIR [PROCS=4]"""
import hashlib
import json
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "r73" / "sealed"))
import exact83 as X  # noqa: E402

N_EXACT, N_SMALL = 20, 5
SHIFTS = [(run, dlt) for run in (0, 1) for dlt in (-2, -1, 1, 2)]
PARTS = {"LXr2": ({"LX": X.lx}, {"LX": {"rots": (2,)}}), "LXr1": ({"LX": X.lx}, {"LX": {"rots": (1,)}}),
         "REST": ({k: v for k, v in X.FAMILIES.items() if k != "LX"}, {})}


def clues():
    from reveal_k4 import CLUES
    pos = np.array([o + i for o, t in CLUES for i in range(len(t))])
    pk = np.array([ord(ch) - 65 for _, t in CLUES for ch in t])
    return pos, pk


def shifted(pos, run, dlt):
    R = X.runs_of(pos)
    out = pos.copy()
    out[R[run]] += dlt
    assert len(set(out.tolist())) == len(out) and out.min() >= 0 and out.max() < X.N
    return out


def jobs(cts):
    """EXACT: every family on K4 + 20 shuffles. DROP and SHIFT: the cheap families (REST) and F1XD on K4 + 20
    shuffles; LX, whose drop-one and shifted runs are the costly part, on K4 + 5 shuffles."""
    ids = list(cts)
    k4, sh = ids[0], ids[1:]
    out = []
    for rid in [k4] + sh[:N_EXACT]:
        for part in PARTS:
            out.append(("EXACT", "none", rid, part))
        lx = rid == k4 or rid in sh[:N_SMALL]
        for part in PARTS:
            if lx or part == "REST":
                out.append(("DROP", "none", rid, part))
                for run, dlt in SHIFTS:
                    out.append(("SHIFT", f"run{run + 1}{dlt:+d}", rid, part))
        out.append(("F1XD", "none", rid, "F1X"))
    return out


def name(j):
    return "__".join(j) + ".json"


def run_job(args):
    j, ct, outdir = args
    p = Path(outdir) / "parts" / name(j)
    if p.exists():
        return
    step, var, rid, part = j
    pos, pk = clues()
    c = np.array([ord(x) - 65 for x in ct])
    if step == "SHIFT":
        run, dlt = int(var[3]) - 1, int(var[4:])
        pos = shifted(pos, run, dlt)
    if step == "F1XD":
        import f1x_drop
        res = {"F1X": f1x_drop.drop_one(c, pos, pk)}
    else:
        fams, kw = PARTS[part]
        res = X.run_all(c, pos, pk, drop=(step == "DROP"), fams=fams, **kw)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(res, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    tmp.replace(p)


def merge(reps):
    """Merge per-part family reports (LX comes in two halves)."""
    out = {}
    for rep in reps:
        for fam, v in rep.items():
            o = out.setdefault(fam, {})
            for key, val in v.items():
                if isinstance(val, dict):
                    c = Counter({int(k): n for k, n in o.get(key, {}).items()})
                    c.update({int(k): n for k, n in val.items()})
                    o[key] = dict(sorted(c.items()))
                elif isinstance(val, list):
                    o[key] = (o.get(key, []) + val)[:300]
                else:
                    o[key] = o.get(key, 0) + val
    return out


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    X.guard()
    tsv, outdir = Path(sys.argv[1]), Path(sys.argv[2])
    procs = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    if (outdir / "R83A.json").exists():
        raise SystemExit("refusing to overwrite")
    rows = [l.split("\t") for l in tsv.read_text().splitlines()[1:] if l]
    assert rows[0][0] == "K4"
    cts = dict(rows)
    (outdir / "parts").mkdir(parents=True, exist_ok=True)
    J = jobs(cts)
    todo = [j for j in J if not (outdir / "parts" / name(j)).exists()]
    print(f"{len(J)} jobs, {len(J) - len(todo)} done, {len(todo)} to run", flush=True)
    # longest first (LX with drop-one), so the pool stays busy
    todo.sort(key=lambda j: (j[0] != "DROP", not j[3].startswith("LX")))
    with Pool(procs) as pool:
        for k, _ in enumerate(pool.imap_unordered(run_job, [(j, cts[j[2]], str(outdir)) for j in todo], chunksize=1)):
            print(f"{k + 1}/{len(todo)} jobs done", flush=True)
    agg = {}
    for j in J:
        step, var, rid, part = j
        agg.setdefault(step, {}).setdefault(var, {}).setdefault(rid, []).append(
            json.loads((outdir / "parts" / name(j)).read_text()))
    res = {step: {var: {rid: merge(reps) for rid, reps in v.items()} for var, v in vs.items()} for step, vs in agg.items()}
    (outdir / "R83A.json").write_text(json.dumps(res, indent=1) + "\n")
    man = [(tsv, "target"), (outdir / "R83A.json", "results")] + [
        (ROOT / f, "code") for f in ("r83/run83a.py", "r83/exact83.py", "r83/models83.py", "r83/f1x_drop.py",
                                     "r75/sealed/exact.py", "r75/core.py", "r73/sealed/reveal_k4.py")]
    (outdir / "FROZEN.sha256").write_text("".join(f"{sha(p)}  {lab}  {Path(p).relative_to(ROOT)}\n" for p, lab in man))
    print("R83a done:", {s: len(v) for s, v in res.items()})


if __name__ == "__main__":
    main()
