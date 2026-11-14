#!/usr/bin/env python3
"""R83a run deviation (documented in r83/RESULT.md): low-memory rerun of F1X drop-one jobs.

Why: two F1XD jobs of the pre-registered run (shuffles NULL_010 and NULL_011) were killed by the container's
memory limit (14.3 GB). R75's f1x() (r75/sealed/exact.py, unchanged) builds, for each feasible setting whose keys
are fully determined by the published letters (no free key letter, <= decode_limit = 64 solutions), one row per
solution with the completed keys and a decode, and keeps them all in memory; r83/f1x_drop.py keeps only each row's
(cfg, m1, m2) and throws the rest away. On those two shuffles the rows outgrew the memory limit.

What this changes: nothing in any file r83/PROTOCOL.sha256 lists. It imports r83/run83a.py and r83/f1x_drop.py
unchanged and replaces f1x_drop.feasible_set by the same function with f1x(..., decode_limit=0). f1x() computes
feasibility (and its tested/feasible tallies) before the decode branch; decode_limit only decides whether a feasible
setting is entered once without a decode or once per solution with one. The set of feasible (cfg, m1, m2) and its
first-seen order are therefore the same, and so is every part file. --check proves it byte for byte on finished jobs.
With decode_limit=0 no key is completed and nothing is decoded, even in memory.

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


def feasible_set(c, pos, pk):
    """f1x_drop.feasible_set with decode_limit=0: the same feasible settings, no rows per solution, no decodes."""
    col = R75.Collector(None)
    R75.f1x(c, pos, pk, col, decode_limit=0)
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
