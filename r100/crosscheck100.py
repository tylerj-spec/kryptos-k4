#!/usr/bin/env python3
"""R100 post-freeze cross-check: K4's per-lag counts recomputed from the FROZEN inputs by a second algorithm.
EXACT: one join over ALL direct links (integer codes in two words, Counter of B-side keys); DROP: a separate join for
every published position cut (no two-group candidates, no float codes, no chunked verification); distinct pairs are
enumerated only for cuts with a non-zero count. Counts only. Usage: python3 -I r100/crosscheck100.py OUT.json"""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"
import hashlib  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from collections import Counter, defaultdict  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "r76")]
import alphabets as AL  # noqa: E402
import checker100 as CK  # noqa: E402
import run_target100 as RT  # noqa: E402


def keys(V, ks):
    """Per row: a tuple key of (V[k] - V[ks[0]]) mod 26 for k in ks[1:], as two int64 words of <= 13 digits."""
    d = [(V[k].astype(np.int64) - V[ks[0]]) % 26 for k in ks[1:]]
    w1 = np.zeros(V[0].shape[0], dtype=np.int64)
    w2 = np.zeros(V[0].shape[0], dtype=np.int64)
    for r, x in enumerate(d):
        if r < 13:
            w1 += x * 26 ** r
        else:
            w2 += x * 26 ** (r - 13)
    return list(zip(w1.tolist(), w2.tolist()))


def matched(H, G, ks, enumerate_pairs=False):
    kb = keys(G, ks)
    ka = keys(H, ks)
    if not enumerate_pairs:
        cb = Counter(kb)
        return sum(cb.get(k, 0) for k in ka), None
    rows = defaultdict(list)
    for b, k in enumerate(kb):
        rows[k].append(b)
    pairs = {(a, b) for a, k in enumerate(ka) for b in rows.get(k, ())}
    return len(pairs), pairs


def main():
    out = Path(sys.argv[1])
    for line in (HERE / "k4/FROZEN.sha256").read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    tier = [a for _, a in AL.large_tier()]
    assert hashlib.sha256("\n".join(tier).encode()).hexdigest() == RT.TIER_SHA
    IT = CK.tier_idxt(tier)
    obs = RT.observations()
    name, ct = (HERE / "k4/INPUTS.tsv").read_text().splitlines()[1].split("\t")
    assert name == "K4"
    agg = json.loads((HERE / "k4/AGGREGATES.json").read_text())
    lags = {}
    for L in agg["scanned_lags"]:
        lk = CK.links(obs, L)
        m = len(lk)
        exact = 0
        drop = 0 if L in agg["drop_lags"] else None
        for s1, s2 in CK.SIGNS:
            for F in CK.FEEDBACK:
                H, G = CK.side_values(ct, obs, IT, lk, s1, s2, F)
                exact += matched(H, G, list(range(m)))[0]
                if drop is not None:
                    union = set()
                    for p in sorted(obs):
                        keep = [k for k, (i, j) in enumerate(lk) if p not in (i, j)]
                        if len(keep) == m:
                            continue
                        n, _ = matched(H, G, keep)
                        if n:
                            union |= matched(H, G, keep, True)[1]
                    drop += len(union)
        lags[str(L)] = {"links": m, "exact": exact, "drop": drop}
    frozen = json.loads((HERE / "k4/AGGREGATES.json").read_text())["inputs"][0]
    agree = frozen["id"] == "K4" and frozen["lags"] == lags
    out.write_text(json.dumps({"implementation": "integer-key Counter joins, one per cut (second algorithm)",
                               "input": "K4", "agree_with_frozen": agree, "lags": lags}, indent=1) + "\n")
    print("AGREE" if agree else "DISAGREE", lags)


if __name__ == "__main__":
    main()
