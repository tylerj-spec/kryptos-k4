#!/usr/bin/env python3
"""R81a G5X: CRIB-ASSISTED EXCLUSION CHECK (approved by Tyler, 13 Nov 2026: "You can do this check ... if we get a
possible solution, we will have to have legit proof"). Run ONLY after the R81a blind results are frozen, pushed,
verified and revealed. It decides consistency with the published letters; it never produces a solution.
Scope: R79's keyword families H7CT (keyword + ciphertext feedback, lag 1..48), H7TXT (keyword + K1-K3 text stream)
and LIB (982 slot rules; stream none or feedback lag 1..7), keyword 1..12 letters, with ONE unknown keyword alphabet:
  PA-free  plaintext alphabet any of R76's 77,229 large-tier orderings; ciphertext and key alphabets AZ or KRY;
  CA-free  ciphertext alphabet any of the 77,229; plaintext and key alphabets AZ or KRY.
Method (exact; a hash join as R76's H1X): published positions in one slot must imply one shift. Over the chain of
consecutive same-slot published positions:
  PA-free  IDX[PA][p_a] - IDX[PA][p_b] = s*((y_a - y_b) - t*(S_a - S_b))      (alphabet side vs setting side)
  CA-free  IDX[CA][c_a] - IDX[CA][c_b] = s*(IDX[pa][p_a] - IDX[pa][p_b]) + t*(S_a - S_b)
Every setting has >= 12 such checks (24 letters, at most 12 slots), so a random setting passes with probability
about 26^-12 per alphabet.
A K4 setting that passes is a LEAD only. Before anything else it needs independent proof: a decode readable over
all 97 letters, a meaningful key, and an independent re-derivation; nothing goes to any outside checker without Tyler.
Usage: g5x.py TARGET.tsv OUT.json [N_SHUFFLES=10]"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r75"))
sys.path.insert(0, str(ROOT / "r76"))
sys.path.insert(0, str(ROOT / "r79"))
sys.path.insert(0, str(ROOT / "r73" / "sealed"))
import core  # noqa: E402
import alphabets as AL  # noqa: E402
import families as F79  # noqa: E402
from reveal_k4 import CLUES  # noqa: E402

POS = np.array([o + i for o, t in CLUES for i in range(len(t))])
WANT = np.array([ord(c) - 65 for _, t in CLUES for c in t])
A2 = ("AZ", "KRY")
OPS = core.OPS
IDX = {k: v.astype(np.int64) for k, v in core.IDX.items()}


def tier():
    t = AL.large_tier()
    return [n for n, _ in t], np.stack([np.array([a.index(ch) for ch in core.AZ]) for _, a in t]).astype(np.int64)


def chain(r):
    """Consecutive same-slot pairs (indices into POS) for slot map r."""
    rp = np.asarray(r)[POS]
    order = sorted(range(len(POS)), key=lambda k: (rp[k], POS[k]))
    return tuple((order[k], order[k + 1]) for k in range(len(order) - 1) if rp[order[k]] == rp[order[k + 1]])


def index_of(sig_rows):
    d = defaultdict(list)
    for k, row in enumerate(sig_rows):
        d[row.tobytes()].append(k)
    return d


def streams_for(fam, c):
    """(label, S at the published positions as a function of ka) for each stream of the family."""
    out = []
    if fam == "H7CT":
        for L in range(1, 49):
            src = POS - L
            out.append((("L", L), lambda ka, src=src: np.where(src >= 0, IDX[ka][c[np.maximum(src, 0)]], 0)))
    elif fam == "H7TXT":
        names, SL = F79.streams()
        for k, nm in enumerate(names):
            out.append((("T",) + tuple(nm), lambda ka, row=SL[k][POS]: IDX[ka][row]))
    return out


def run_ct(ct, names, TI):
    c = core.codes(ct).astype(np.int64)
    found = {"PA-free": [], "CA-free": []}
    counts = {"PA-free": 0, "CA-free": 0}
    # slot maps: REP m 1..12 for H7CT / H7TXT; R79's 982 rules for LIB
    jobs = [("H7CT", ("REP", (), m), F79.REPMAP[m]) for m in range(1, 13)]
    jobs += [("H7TXT", ("REP", (), m), F79.REPMAP[m]) for m in range(1, 13)]
    jobs += [("LIB", (r, p, m), np.array(F79.slot_map(r, p, m, ct))) for r, p, m, _ in F79.mapdefs()]
    cache = {}
    for fam, rule, r in jobs:
        pairs = chain(r)
        if not pairs:
            continue
        a, b = np.array([x for x, _ in pairs]), np.array([y for _, y in pairs])
        key = (pairs, )
        if key not in cache:
            sigP = ((TI[:, WANT[a]] - TI[:, WANT[b]]) % 26).astype(np.uint8)
            sigC = ((TI[:, c[POS[a]]] - TI[:, c[POS[b]]]) % 26).astype(np.uint8)
            cache = {key: (index_of(sigP), index_of(sigC))}        # keep one entry: maps rarely repeat
        dP, dC = cache[key]
        if fam == "LIB":
            sts = [(("L", 0), None)] + [(("L", L), (lambda ka, src=POS - L: np.where(src >= 0, IDX[ka][c[np.maximum(
                src, 0)]], 0))) for L in range(1, 8)]
        else:
            sts = streams_for(fam, c)
        for lab, Sf in sts:
            ops = ("VIG", "BEAU") if Sf is None else ("VIG", "BEAU", "VARB")
            for ka in (A2 if Sf is not None else ("AZ",)):
                S = np.zeros(len(POS), dtype=np.int64) if Sf is None else Sf(ka)
                dS = S[a] - S[b]
                for op in ops:
                    s, t = OPS[op]
                    for fixed in A2:
                        # PA-free: fixed = ca
                        y = IDX[fixed][c[POS]]
                        rhs = ((s * ((y[a] - y[b]) - t * dS)) % 26).astype(np.uint8).tobytes()
                        counts["PA-free"] += 1
                        for k in dP.get(rhs, ()):
                            found["PA-free"].append({"family": fam, "rule": [rule[0], list(rule[1]), rule[2]],
                                                     "stream": list(lab), "ka": ka, "op": op, "ca": fixed,
                                                     "pa": names[k], "checks": len(pairs)})
                        # CA-free: fixed = pa
                        lhs = IDX[fixed][WANT[a]] - IDX[fixed][WANT[b]]
                        tgt = ((s * lhs + t * dS) % 26).astype(np.uint8).tobytes()
                        counts["CA-free"] += 1
                        for k in dC.get(tgt, ()):
                            found["CA-free"].append({"family": fam, "rule": [rule[0], list(rule[1]), rule[2]],
                                                     "stream": list(lab), "ka": ka, "op": op, "pa": fixed,
                                                     "ca": names[k], "checks": len(pairs)})
    return counts, found


_T = None


def _work(item):
    global _T
    if _T is None:
        _T = tier()
    rid, ct = item
    return rid, run_ct(ct, *_T)


def main():
    from multiprocessing import Pool
    tsv, outp = sys.argv[1], sys.argv[2]
    nsh = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    cts = dict(l.split("\t") for l in Path(tsv).read_text().splitlines()[1:] if l)
    names, _ = tier()
    ids = ["K4"] + [i for i in cts if i != "K4"][:nsh]
    out = {"label": "CRIB-ASSISTED EXCLUSION CHECK (post-freeze; a pass is a lead needing independent proof)",
           "alphabets": len(names), "rows": {}}
    with Pool(4) as pool:
        results = dict(pool.map(_work, [(i, cts[i]) for i in ids], chunksize=1))
    for rid in ids:
        counts, found = results[rid]
        out["rows"][rid] = {"settings_x_alphabets": {k: v * len(names) for k, v in counts.items()},
                            "feasible": {k: len(v) for k, v in found.items()},
                            "feasible_list": found if rid == "K4" else None}
        print(rid, {k: len(v) for k, v in found.items()}, flush=True)
    Path(outp).write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
