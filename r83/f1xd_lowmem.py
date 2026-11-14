#!/usr/bin/env python3
"""R83a run deviation (documented in r83/RESULT.md): rerun of the two F1X drop-one jobs that could not finish.

What happened: the pre-registered run's F1XD jobs on shuffles NULL_010 and NULL_011 grew until the container's memory
limit (14.3 GB) killed them, and the pool then waited for them forever.

Root cause, in R75's f1x() (r75/sealed/exact.py, unchanged): after its feasibility test it multiplies each
component's number of solutions into an int64, nsol. In the equal-period cells m1 = m2 = 15-18 almost every key slot
pair is its own component with 26 solutions, so the product (26**14 and more) overflows and wraps. When it wraps to
a value <= decode_limit (here negative), f1x() takes its decode branch and enumerates every combination of root
values (26**14 and more), keeping a row with completed keys and a decode for each. r83/f1x_drop.py keeps only each
row's (cfg, m1, m2), so the decodes are never written, but that enumeration never ends. On NULL_010 and NULL_011, 4
feasible settings each (periods 17 and 17, with one published letter set aside) have such a wrapped count; on K4 and
the other 19 shuffles there are none, which is why those jobs finished. Feasibility (and its tested/feasible
tallies) is computed before the decode branch and does not use nsol, so the 379 finished parts are exact.

What this changes: nothing in any file r83/PROTOCOL.sha256 lists. It imports r83/run83a.py and r83/f1x_drop.py
unchanged, and in this process only replaces R75's grid_of() by one that returns None. f1x() then enters every
feasible setting once without a decode and never takes the decode branch. The set of feasible (cfg, m1, m2) and its
first-seen order are the same, and so is every part file: --check proves it byte for byte on finished jobs. No key
is completed and nothing is decoded, even in memory.

Usage: python3 -I r83/f1xd_lowmem.py --check TARGET.tsv OUTDIR SCRATCH RID [RID ...]
       python3 -I r83/f1xd_lowmem.py --run   TARGET.tsv OUTDIR RID [RID ...]"""
import json
import resource
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run83a  # noqa: E402  (puts r73/sealed on the path, imports exact83)
run83a.clues()  # load r73's reveal_k4 before f1x_drop puts r75/sealed first on the path (run83a imports it lazily)
assert sys.modules["reveal_k4"].__file__ == str(HERE.parent / "r73" / "sealed" / "reveal_k4.py")
import f1x_drop  # noqa: E402

R75 = f1x_drop.R75
R75.grid_of = lambda u: None          # f1x(): "if grid is None ...: col.add(..., None); continue" for every setting


def feasible_set(c, pos, pk):
    """f1x_drop.feasible_set with f1x's decode branch switched off: the same feasible settings, no decodes."""
    col = R75.Collector(None)
    R75.f1x(c, pos, pk, col)
    assert all(r["decode"] is None for r in col.rows)
    return {(tuple(r["setting"]["cfg"]), r["setting"]["m1"], r["setting"]["m2"]): r["checks"] for r in col.rows}, col


f1x_drop.feasible_set = feasible_set


def cts(tsv):
    rows = [l.split("\t") for l in Path(tsv).read_text().splitlines()[1:] if l]
    return dict(rows)


def one(rid, ct, outdir):
    t0 = time.time()
    run83a.run_job((("F1XD", "none", rid, "F1X"), ct, str(outdir)))
    return {"id": rid, "seconds": round(time.time() - t0, 1),
            "peak_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)}


def main():
    run83a.X.guard()
    mode, tsv = sys.argv[1], sys.argv[2]
    c = cts(tsv)
    if mode == "--check":
        outdir, scratch, ids = Path(sys.argv[3]), Path(sys.argv[4]), sys.argv[5:]
        (scratch / "parts").mkdir(parents=True, exist_ok=True)
        rep = []
        for rid in ids:
            nm = run83a.name(("F1XD", "none", rid, "F1X"))
            r = one(rid, c[rid], scratch)
            r["identical_to_run_part"] = (scratch / "parts" / nm).read_bytes() == (outdir / "parts" / nm).read_bytes()
            rep.append(r)
            print(r, flush=True)
        print(json.dumps(rep))
        assert all(r["identical_to_run_part"] for r in rep)
    elif mode == "--run":
        outdir, ids = Path(sys.argv[3]), sys.argv[4:]
        for rid in ids:
            assert not (outdir / "parts" / run83a.name(("F1XD", "none", rid, "F1X"))).exists(), rid
            print(one(rid, c[rid], outdir), flush=True)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
