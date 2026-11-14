#!/usr/bin/env python3
"""R83 drop-one for R75's F1X (G6 robustness; CRIB-ASSISTED, exclusion-only; design-round code, not yet
pre-registered). R75's F1X (r75/sealed/exact.py f1x(), unchanged) checks two stacked periodic stages with any keys,
periods 1-26 each, on all four alphabets. It was never run with one published letter set aside. This calls f1x()
once per published position with that position removed, and reports the settings (cfg, m1, m2) with >= 3 checks
that are feasible only then. Never decodes for the report (the collector has no scorer), never completes a key.
Usage: f1x_drop.py --selftest OUT.json             (a synthetic two-stage plant with one published letter corrupted)
       f1x_drop.py --k4 TARGET.tsv OUT.json [N]     (refused unless r83/PROTOCOL.sha256 exists and matches)"""
import json
import random
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "r75"))
sys.path.insert(0, str(ROOT / "r75" / "sealed"))
sys.path.insert(0, str(HERE))
import exact as R75  # noqa: E402
import exact83 as X  # noqa: E402
from core import AZ, IDX, LET, N  # noqa: E402


def feasible_set(c, pos, pk):
    col = R75.Collector(None)
    R75.f1x(c, pos, pk, col)
    return {(tuple(r["setting"]["cfg"]), r["setting"]["m1"], r["setting"]["m2"]) for r in col.rows}, col


def drop_one(c, pos, pk):
    base, col = feasible_set(c, pos, pk)
    out = {"exact_feasible_ge3": len(base), "by_position": {}}
    for a in range(len(pos)):
        keep = np.array([b for b in range(len(pos)) if b != a])
        s, _ = feasible_set(c, pos[keep], pk[keep])
        new = sorted(s - base)
        out["by_position"][int(pos[a])] = {"newly_feasible": len(new), "first": [list(x) for x in new[:20]]}
    return out


def encrypt_f1x(pt, cfg, k1, k2):
    pa1, ca1, pa2, ca2, s1, s2 = cfg
    out = []
    for i, ch in enumerate(pt):
        q = int(LET[ca1][(s1 * int(IDX[pa1][AZ.index(ch)]) + k1[i % len(k1)]) % 26])
        out.append(AZ[int(LET[ca2][(s2 * int(IDX[pa2][q]) + k2[i % len(k2)]) % 26])])
    return "".join(out)


def selftest(out, seed=830500):
    rng = random.Random(seed)
    pos = X.published_positions()
    rep = []
    for _ in range(3):
        cfg = tuple(rng.choice(R75.CFG1))
        m1, m2 = rng.randint(2, 7), rng.randint(2, 7)
        k1, k2 = [rng.randrange(26) for _ in range(m1)], [rng.randrange(26) for _ in range(m2)]
        pt = "".join(rng.choice(AZ) for _ in range(N))
        ct = encrypt_f1x(pt, cfg, k1, k2)
        bad = int(rng.choice(pos))
        ct2 = ct[:bad] + rng.choice([x for x in AZ if x != ct[bad]]) + ct[bad + 1:]
        c, p = np.array([AZ.index(x) for x in ct]), np.array([AZ.index(x) for x in pt])
        c2 = np.array([AZ.index(x) for x in ct2])
        exact_ok = (cfg, m1, m2) in feasible_set(c, pos, p[pos])[0]
        corrupt_ok = (cfg, m1, m2) in feasible_set(c2, pos, p[pos])[0]
        keep = np.array([b for b in range(len(pos)) if int(pos[b]) != bad])
        drop_ok = (cfg, m1, m2) in feasible_set(c2, pos[keep], p[pos][keep])[0]
        rep.append({"cfg": cfg, "m1": m1, "m2": m2, "corrupted_position": bad, "feasible_clean": exact_ok,
                    "feasible_corrupted": corrupt_ok, "feasible_corrupted_drop_that_letter": drop_ok})
        print(rep[-1], flush=True)
    Path(out).write_text(json.dumps(rep, indent=1) + "\n")
    assert all(r["feasible_clean"] and r["feasible_corrupted_drop_that_letter"] for r in rep)


def main():
    if sys.argv[1] == "--selftest":
        selftest(sys.argv[2])
        return
    if sys.argv[1] == "--k4":
        X.guard()
        sys.path.insert(0, str(ROOT / "r73" / "sealed"))
        from reveal_k4 import CLUES
        tsv, out = sys.argv[2], sys.argv[3]
        n = int(sys.argv[4]) if len(sys.argv) > 4 else 5
        pos = np.array([o + i for o, t in CLUES for i in range(len(t))])
        pk = np.array([AZ.index(ch) for _, t in CLUES for ch in t])
        rows = [l.split("\t") for l in Path(tsv).read_text().splitlines()[1:] if l]
        res = {}
        for rid, ct in [r for r in rows if r[0] == "K4"] + [r for r in rows if r[0] != "K4"][:n]:
            res[rid] = drop_one(np.array([AZ.index(x) for x in ct]), pos, pk)
            print(rid, res[rid]["exact_feasible_ge3"], sum(v["newly_feasible"] for v in res[rid]["by_position"].values()),
                  flush=True)
        Path(out).write_text(json.dumps(res, indent=1) + "\n")
        return
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
