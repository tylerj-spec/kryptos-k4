#!/usr/bin/env python3
"""R79 CRIB-ASSISTED validator (run ONLY after the K4 results are frozen, pushed, verified and revealed; labelled as in
R70 Erratum 1; not part of the blind outcome). For K4 and the first 10 shuffles:
  keyword families  every setting of every family that was run: the published letters pin the shift of their slots;
                    a setting is FEASIBLE when the pinned shifts agree within every slot; checks = published
                    positions - distinct slots. Counted by checks.
  H11               every route and convention: a published position i whose key position p[i] is also published is
                    one exact check; FEASIBLE when every such check holds; checks = their number.
For feasible keyword settings with >= 5 checks (at most 50 per family, most checks first) the unpinned slots are
completed by the blind solver with the pinned slots fixed, and the decode is scored (letter model). These are
crib-assisted completions and are never blind discoveries.
Usage: validate79.py LM TARGET.tsv REVEAL.json OUT.json"""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r75"))
sys.path.insert(0, str(ROOT / "r79"))
sys.path.insert(0, str(ROOT / "r73" / "sealed"))
import core  # noqa: E402
import families as F  # noqa: E402
import solver as SV  # noqa: E402
from reveal_k4 import CLUES  # noqa: E402

POS = np.array([o + i for o, t in CLUES for i in range(len(t))])
WANT = np.array([ord(c) - 65 for _, t in CLUES for c in t])
PAIRS = [(a, b) for a in range(len(POS)) for b in range(a + 1, len(POS))]
MINCHK, NCOMPLETE = 5, 50


def keyword_check(fam, ct, scorer):
    B = F.bank()[0]
    inv = np.argsort(B, axis=2)                          # inv[t, i, letter] = value v with B[t, i, v] = letter
    hist, keep = Counter(), []
    for Z, R, M, OI, info in F.chunks(fam, ct):
        V = inv[OI[:, None], POS[None, :], WANT[None, :]]
        D = (V - Z[:, POS].astype(np.int64)) % 26
        RP = R[:, POS]
        bad = np.zeros(len(Z), dtype=bool)
        for a, b in PAIRS:
            bad |= (RP[:, a] == RP[:, b]) & (D[:, a] != D[:, b])
        srt = np.sort(RP, axis=1)
        nslot = (srt[:, 1:] != srt[:, :-1]).sum(axis=1) + 1
        chk = len(POS) - nslot
        ok = ~bad
        for v, k in zip(*np.unique(chk[ok], return_counts=True)):
            hist[int(v)] += int(k)
        for j in np.flatnonzero(ok & (chk >= MINCHK)):
            keep.append((int(chk[j]), info, int(j), Z[j], R[j], int(M[j]), int(OI[j]), D[j], RP[j]))
    keep.sort(key=lambda e: -e[0])
    done = []
    for chk, info, j, z, r, m, oi, d, rp in keep[:NCOMPLETE]:
        pinned = {int(k): int(v) for k, v in zip(rp, d)}
        dfull = complete(z.astype(np.int64), r.astype(np.int64), m, B[oi], pinned)
        st = F.setting(info, j, dfull)
        t = F.decrypt(ct, st)
        done.append({"checks": chk, "setting": st, "text": t, "letters_published": int(sum(
            t[p] == chr(65 + w) for p, w in zip(POS, WANT))),
            "lm_per_letter": float(scorer.lm_score(core.codes(t)[None])[0]), "free_slots": m - len(pinned)})
    return dict(sorted(hist.items())), len(keep), done


def complete(z, r, m, out, pinned, restarts=4, seed=790777):
    """Coordinate ascent (quadgrams) over the unpinned slots; pinned slots keep their published-letter shifts."""
    rng = np.random.default_rng(seed)
    q = SV.QUAD
    free = [k for k in range(m) if k not in pinned]
    best, bestd = -1e18, None
    for rr in range(restarts):
        d = np.zeros(SV.MMAX, dtype=np.int64)
        for k, v in pinned.items():
            d[k] = v
        for k in free:
            d[k] = rng.integers(26) if rr else 0
        for _ in range(30):
            changed = False
            for k in free:
                D = np.tile(d, (26, 1))
                D[:, k] = np.arange(26)
                L = out[np.arange(97)[None, :], (z[None, :] + D[:, r]) % 26].astype(np.int64)
                sc = q[((L[:, :-3] * 26 + L[:, 1:-2]) * 26 + L[:, 2:-1]) * 26 + L[:, 3:]].sum(axis=1)
                v = int(np.argmax(sc))
                if v != d[k]:
                    d[k], changed = v, True
            if not changed:
                break
        L = out[np.arange(97), (z + d[r]) % 26].astype(np.int64)
        sc = float(q[((L[:-3] * 26 + L[1:-2]) * 26 + L[2:-1]) * 26 + L[3:]].sum())
        if sc > best:
            best, bestd = sc, d.copy()
    return bestd.astype(np.uint8)


def h11_check(ct):
    names, P = F.routes()
    c = core.codes(ct).astype(np.int64)
    p = np.full(97, -1)
    p[POS] = WANT
    use = np.isin(P[:, POS], POS)                       # (routes, 24): key position also published
    nchk = use.sum(axis=1)
    out = {}
    for k, (pa, ka, ca, op) in enumerate(F.H11_CONV):
        s, t = F.OPS[op]
        keyp = p[P[:, POS].astype(np.int64)]
        ok_pos = (F.LET[ca][(s * F.IDX[pa][WANT][None, :] + t * F.IDX[ka][np.maximum(keyp, 0)]) % 26]
                  == c[POS][None, :]) | ~use
        feas = ok_pos.all(axis=1)
        out["/".join((pa, ka, ca, op))] = {str(v): int(((nchk == v) & feas).sum()) for v in range(3, 25)
                                           if ((nchk == v) & feas).any()}
    return {"routes_with_ge3_checks": int((nchk >= 3).sum()), "feasible_by_checks": out}


def main():
    lm, tsv, reveal, outp = sys.argv[1:5]
    rv = json.loads(Path(reveal).read_text())
    fams = rv["families"]
    cts = dict(l.split("\t") for l in Path(tsv).read_text().splitlines()[1:] if l)
    ids = ["K4"] + [i for i in cts if i != "K4"][:10]
    scorer = core.Scorer(lm)
    out = {"label": "CRIB-ASSISTED (post-freeze validator; never a blind discovery)", "families": fams, "rows": {}}
    for rid in ids:
        row = {}
        for fam in fams:
            if fam == "H11":
                row[fam] = h11_check(cts[rid])
            else:
                hist, nfeas, done = keyword_check(fam, cts[rid], scorer) if rid == "K4" else \
                    keyword_check_counts(fam, cts[rid])
                row[fam] = {"feasible_by_checks": hist, "feasible_ge%d" % MINCHK: nfeas, "completions": done}
        out["rows"][rid] = row
        print(rid, {f: (v.get("feasible_ge%d" % MINCHK), max([d["lm_per_letter"] for d in v.get("completions", [])],
                                                             default=None)) if f != "H11" else
                    sum(sum(x.values()) for x in v["feasible_by_checks"].values()) for f, v in row.items()}, flush=True)
    Path(outp).write_text(json.dumps(out, indent=1) + "\n")


def keyword_check_counts(fam, ct):
    global NCOMPLETE
    saved, NCOMPLETE = NCOMPLETE, 0
    try:
        return keyword_check(fam, ct, None)
    finally:
        NCOMPLETE = saved


if __name__ == "__main__":
    main()
