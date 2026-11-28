"""R119 routes (PREREGISTRATION section 1): L161's 26 directed routes with no documented run, rebuilt from
r72/reconstruct.py (two same-direction quarter turns of a 98-cell sheet) and r72/novelty.py (extra cell removed first
or last; forward or inverse), each matched to its r72/data/NOVELTY.json row by sha256 prefix. Convention: CT[j] = X[perm[j]]."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "r72")]
import reconstruct as RC  # noqa: E402
import novelty as NV  # noqa: E402


def routes():
    rows = json.loads((ROOT / "r72/data/NOVELTY.json").read_text())["rows"]
    seen98 = {}
    for w1 in (2, 7, 14, 49):
        for w2 in (2, 7, 14, 49):
            for cw in (True, False):
                p = RC.compose(RC.turn(98, w1, cw), RC.turn(98, w2, cw))
                seen98.setdefault(RC.decimation(p), p)
    out = []
    for k, o in sorted(seen98.items()):
        for cell, label in ((0, "extra cell first"), (97, "extra cell last")):
            r = NV.drop_cell(o, cell)
            for direction, q in (("forward", r), ("inverse", NV.inv(r))):
                row = [x for x in rows if x["k_mod_99"] == k and x["extra_cell"] == label and x["direction"] == direction]
                if len(row) != 1:
                    raise SystemExit(f"REFUSED: no unique NOVELTY row for k={k} {label} {direction}")
                if hashlib.sha256(",".join(map(str, q)).encode()).hexdigest()[:16] != row[0]["sha256"]:
                    raise SystemExit(f"REFUSED: route k={k} {label} {direction} does not match NOVELTY.json")
                if row[0]["status"] in ("NEW", "GENERATED_ONLY"):
                    out.append({"name": f"k{k}_{'first' if cell == 0 else 'last'}_{direction}", "perm": list(q),
                                "status": row[0]["status"]})
    if len(out) != 26 or any(sorted(r["perm"]) != list(range(97)) for r in out):
        raise SystemExit("REFUSED: expected 26 routes, each a permutation of 0-96")
    return out


def route(x, perm):
    return "".join(x[i] for i in perm)


def unroute(ct, perm):
    xs = [None] * len(perm)
    for j, i in enumerate(perm):
        xs[i] = ct[j]
    return "".join(xs)
