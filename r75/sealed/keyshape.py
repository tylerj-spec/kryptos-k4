#!/usr/bin/env python3
"""R75 step 1 (SEALED DIAGNOSIS): the shape of the key that the published letters imply.
Uses the 24 published letters (imported from r73/sealed/reveal_k4.py) and the K4 ciphertext. It produces NO plaintext
and feeds NO solver; its only output is a report on whether the implied key has structure beyond chance. Approved by
Tyler on 9 Nov 2026 as a diagnosis ("I'm fine with it"). Rules fixed in r75/PREREGISTRATION.md.

For a numbering convention (pa, ca, form) the implied key at a published position is
    K = IDX[ca][c] - IDX[pa][p]  (form DIFF)     or     K = IDX[ca][c] + IDX[pa][p]  (form SUM)      (mod 26).
Primary family: pa, ca in {AZ, KRY} x {DIFF, SUM} = 8 conventions. Secondary: pa, ca in {AZ, KRY, PAL, ABS} = 32.
Statistics (all "larger = more structure"):
  T1 total coincidences   pairs of published positions with equal K;
  T2 near repeats         equal K at distance 1 or 2 inside a block;
  T3 step coincidences    coincidences among the 22 first differences K[i+1] - K[i] inside the blocks;
  T4 best cross-block lag max over lags 30..52 of the number of positions with K[i] = K[i+lag];
  T5 neighbour feedback   max over source (plaintext number, ciphertext number), distance 1..3 and sign of the largest
                          number of positions sharing one value of K[i] -/+ source[i-distance];
  T6 small values         positions with K within 3 of 0 (circular).
Null: the same statistics with the ciphertext replaced by random permutations of itself (the published plaintext
letters stay where they are). Per-cell p = share of null draws at or above the observed value. Family-wise p (min-p):
share of null draws whose smallest per-cell p is at or below the observed smallest per-cell p.
Verdict: SHAPE_CONFIRMED if the primary family-wise p <= 0.05; SUGGESTIVE if <= 0.20; else NO_SHAPE.
Usage: keyshape.py OUT.json [DRAWS=200000]        (K4)
       keyshape.py --selftest BOOK OUT.json        (synthetic ciphers at the same 24 positions; no K4)"""
import hashlib
import json
import random
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r75"))
import core  # noqa: E402

SEED = 750100
BLOCKS = ((21, 13), (63, 11))      # 0-based start and length of the two published blocks (positions only)
POS = np.array([o + i for o, n in BLOCKS for i in range(n)])
B1 = np.arange(BLOCKS[0][1])
B2 = BLOCKS[0][1] + np.arange(BLOCKS[1][1])
NEAR = [(i, i + d) for blk in (B1, B2) for d in (1, 2) for i in blk[:-d]]
STEP = [(i, i + 1) for blk in (B1, B2) for i in blk[:-1]]
LAGS = range(30, 53)
STATS = ("T1_total_coincidences", "T2_near_repeats", "T3_step_coincidences", "T4_best_cross_block_lag",
         "T5_neighbour_feedback", "T6_small_values")
PRIMARY = [(pa, ca, f) for pa in ("AZ", "KRY") for ca in ("AZ", "KRY") for f in ("DIFF", "SUM")]
SECONDARY = [(pa, ca, f) for pa in core.ALPH for ca in core.ALPH for f in ("DIFF", "SUM")]


def coincidences(V):
    """Number of equal pairs in each row of V (values 0..25)."""
    D = V.shape[0]
    cnt = np.bincount((V + 26 * np.arange(D)[:, None]).ravel(), minlength=26 * D).reshape(D, 26)
    return (cnt * (cnt - 1) // 2).sum(axis=1)


def mode_count(V):
    D = V.shape[0]
    return np.bincount((V + 26 * np.arange(D)[:, None]).ravel(), minlength=26 * D).reshape(D, 26).max(axis=1)


def stats(C, pknown, conv):
    """C: (D, 97) ciphertext codes; pknown: (24,) or (D, 24) plaintext codes at POS. Returns (D, 6) statistics."""
    pa, ca, form = conv
    a = core.IDX[pa][pknown].astype(np.int64)
    ball = core.IDX[ca][C].astype(np.int64)
    b = ball[:, POS]
    K = (b - a) % 26 if form == "DIFF" else (b + a) % 26
    out = np.zeros((C.shape[0], 6), dtype=np.int64)
    out[:, 0] = coincidences(K)
    out[:, 1] = sum((K[:, i] == K[:, j]).astype(np.int64) for i, j in NEAR)
    out[:, 2] = coincidences(np.stack([(K[:, j] - K[:, i]) % 26 for i, j in STEP], axis=1))
    best = np.zeros(C.shape[0], dtype=np.int64)
    for lag in LAGS:
        pairs = [(i, int(np.where(POS == POS[i] + lag)[0][0])) for i in B1 if (POS[i] + lag) in POS]
        if pairs:
            best = np.maximum(best, sum((K[:, i] == K[:, j]).astype(np.int64) for i, j in pairs))
    out[:, 3] = best
    fb = np.zeros(C.shape[0], dtype=np.int64)
    for d in (1, 2, 3):
        inner = np.concatenate([B1[d:], B2[d:]])            # positions whose predecessor at distance d is published
        for sign in (1, -1):
            fb = np.maximum(fb, mode_count((K[:, inner] - sign * a[..., inner - d]) % 26))  # plaintext source
            fb = np.maximum(fb, mode_count((K - sign * ball[:, POS - d]) % 26))             # ciphertext source
    out[:, 4] = fb
    out[:, 5] = ((K <= 3) | (K >= 23)).sum(axis=1)
    return out


def analyse(ct, known, draws, seed):
    """ct: 97-letter string; known: {0-based position: letter} at POS. Returns the report dict."""
    c = core.codes(ct)
    pknown = np.array([ord(known[int(i)]) - 65 for i in POS], dtype=np.int16)
    rng = np.random.default_rng(seed)
    convs = SECONDARY
    obs = np.stack([stats(c[None, :], pknown, v)[0] for v in convs])                  # (32, 6)
    null = np.zeros((draws, len(convs), 6), dtype=np.int16)
    done = 0
    while done < draws:
        n = min(10000, draws - done)
        C = c[np.argsort(rng.random((n, core.N)), axis=1)]
        for vi, v in enumerate(convs):
            null[done:done + n, vi] = stats(C, pknown, v)
        done += n

    def tail(vals, ref):
        """share of ref (D,) values >= each of vals"""
        srt = np.sort(ref)
        return (len(srt) - np.searchsorted(srt, vals, side="left")) / len(srt)

    p_obs = np.zeros(obs.shape)
    p_null = np.zeros(null.shape, dtype=np.float32)
    for vi in range(len(convs)):
        for si in range(6):
            p_obs[vi, si] = tail(np.array([obs[vi, si]]), null[:, vi, si])[0]
            p_null[:, vi, si] = tail(null[:, vi, si], null[:, vi, si])
    report = {"draws": draws, "seed": seed, "statistics": STATS, "families": {}}
    for fam, members in (("primary", PRIMARY), ("secondary", SECONDARY)):
        ids = [convs.index(v) for v in members]
        minp_obs = float(p_obs[ids].min())
        minp_null = p_null[:, ids, :].reshape(draws, -1).min(axis=1)
        fw = float((1 + (minp_null <= minp_obs + 1e-12).sum()) / (draws + 1))
        cells = []
        for vi in ids:
            for si, sn in enumerate(STATS):
                cells.append({"convention": "/".join(convs[vi]), "statistic": sn, "observed": int(obs[vi, si]),
                              "null_mean": float(null[:, vi, si].mean()),
                              "null_p95": float(np.percentile(null[:, vi, si], 95)),
                              "p": float(p_obs[vi, si])})
        cells.sort(key=lambda x: x["p"])
        report["families"][fam] = {"conventions": len(ids), "cells": len(cells), "smallest_cell_p": minp_obs,
                                   "family_wise_p": fw, "flagged_p_le_0.01": [x for x in cells if x["p"] <= 0.01],
                                   "cells_sorted": cells}
    fw = report["families"]["primary"]["family_wise_p"]
    report["verdict"] = "SHAPE_CONFIRMED" if fw <= 0.05 else "SUGGESTIVE" if fw <= 0.20 else "NO_SHAPE"
    report["implied_key_primary"] = {}
    for v in PRIMARY:
        a = core.IDX[v[0]][pknown].astype(int)
        b = core.IDX[v[1]][c[POS]].astype(int)
        K = (b - a) % 26 if v[2] == "DIFF" else (b + a) % 26
        report["implied_key_primary"]["/".join(v)] = {"positions_1based": [int(x) + 1 for x in POS],
                                                      "key": [int(x) for x in K]}
    return report


def summary(rep):
    for fam in ("primary", "secondary"):
        f = rep["families"][fam]
        print(f"{fam}: {f['cells']} cells, smallest cell p {f['smallest_cell_p']:.5f}, family-wise p "
              f"{f['family_wise_p']:.4f}")
        for x in f["cells_sorted"][:6]:
            print(f"   {x['convention']:12s} {x['statistic']:26s} observed {x['observed']:3d}  null mean "
                  f"{x['null_mean']:.2f}  p {x['p']:.5f}")
    print("VERDICT:", rep["verdict"])


def selftest(book, out):
    """Synthetic ciphers with the 'published' letters taken from the planted plaintext at the same 24 positions."""
    words = re.findall(r"[A-Z]+", Path(book).read_text(encoding="utf-8", errors="ignore").upper())
    rng = random.Random(750101)
    res = {}
    for name in ("HELD_KEY_AZ_BEAUFORT", "PERIOD_40_KRY_VIG", "RANDOM_KEY"):
        verdicts, tops = [], []
        for rep_i in range(5):
            i = rng.randrange(len(words) - 60)
            pt = "".join(words[i:i + 60])[:core.N]
            if name == "HELD_KEY_AZ_BEAUFORT":        # reverse-alphabet cipher, key letter held for 1-4 positions
                key = []
                while len(key) < core.N:
                    key += [rng.randrange(26)] * rng.randint(1, 4)
                ct = "".join(core.AZ[(key[j] - core.AZ.index(pt[j])) % 26] for j in range(core.N))
            elif name == "PERIOD_40_KRY_VIG":
                key = [rng.randrange(26) for _ in range(40)]
                A = core.ALPH["KRY"]
                ct = "".join(A[(A.index(pt[j]) + key[j % 40]) % 26] for j in range(core.N))
            else:
                ct = "".join(core.AZ[(core.AZ.index(pt[j]) + rng.randrange(26)) % 26] for j in range(core.N))
            r = analyse(ct, {int(p): pt[int(p)] for p in POS}, 20000, 750102 + rep_i)
            verdicts.append(r["verdict"])
            top = r["families"]["primary"]["cells_sorted"][0]
            tops.append(f"{top['convention']} {top['statistic']} p={top['p']:.5f} fw={r['families']['primary']['family_wise_p']:.4f}")
        res[name] = {"verdicts": verdicts, "top_cells": tops}
        print(name, verdicts)
        for t in tops:
            print("   ", t)
    Path(out).write_text(json.dumps(res, indent=1) + "\n")


def main():
    if sys.argv[1] == "--selftest":
        return selftest(sys.argv[2], sys.argv[3])
    sys.path.insert(0, str(ROOT / "r73" / "sealed"))
    import prepare_k4 as PK  # noqa: E402
    from reveal_k4 import CLUES  # noqa: E402
    raw = PK.CT.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PK.CT_SHA256:
        raise SystemExit("K4 ciphertext hash mismatch")
    known = {o + i: ch for o, t in CLUES for i, ch in enumerate(t)}
    assert sorted(known) == [int(x) for x in POS]
    draws = int(sys.argv[2]) if len(sys.argv) > 2 else 200000
    rep = analyse(raw.decode().strip(), known, draws, SEED)
    Path(sys.argv[1]).write_text(json.dumps(rep, indent=1) + "\n")
    summary(rep)


if __name__ == "__main__":
    main()
