#!/usr/bin/env python3
"""T6 item 1 (audit/NEXT_STEPS.md): independent replay of R83a's EXACT step (L172) for LX, SLX, SLX-A and SSX.
WPX and PFX EXACT are replayed in full by r83/audit/exact_drop.py (T1); this file re-uses that output.

POST-FREEZE, CRIB-ASSISTED, EXCLUSION-ONLY. Standard library only; nothing imported from r83/exact83.py or
r83/models83.py. Nothing is decrypted, no key is completed, nothing is ranked. Output: structural settings and counts.

Semantics (r83/PREREGISTRATION.md, r83/models83.py): a setting is feasible if some key letters send every published
plaintext letter to the ciphertext letter at its position (unpublished letters unconstrained). One stage (pa, ca, s):
IDX[ca][c] = s*IDX[pa][p] + k (mod 26); a free key absorbs its numbering alphabet.
  SLX    per slot r = i mod m, pass j = i div m:  k_i = A[r] + j*B[r]             (some A, B per slot; brute 26 x 26)
  SLX-A  k_i = (j + 1)*A[r]                                                       (some A per slot; brute 26)
  SSX    conv (pa, ca, ka, s); slot r has keyword letter W[r]; pass-0 key letter W[r]; pass j+1 letter =
         LET[ca][s*IDX[pa][previous] + IDX[ka][W[r]]]; k_i = IDX[ka][key letter]  (some W per slot; brute 26)
  LX     conv (pa1, ca1, pa2, ca2, s1, s2, t2, ka1, ka2), one keyword x of m numbers; at position i stage one reads
         slot a, stage two slot b (b = (i + d*(i div w)) mod m rotated; rot = 2 rotates stage two, rot = 1 stage one):
         q = LET[ca1][s1*IDX[pa1][p] + x_a],  IDX[ca2][c] = s2*IDX[pa2][q] + t2*pi(x_b),  pi = IDX[ka2] o LET[ka1].
         Checked by propagation over each connected component with all 26 root values (no shortcut).
"checks" (R83a's count): SLX 24 - sum over touched slots of min(n_r, 2); SLX-A and SSX 24 - touched slots; LX
edges - nodes + components (edges = published positions).

Usage:
  replay_exact.py --slots TARGET.tsv OUT.json N_SHUF          SLX, SLX-A, SSX in full on K4 + N shuffles
  replay_exact.py --lx TARGET.tsv OUT.json RID FRACTION SEED  LX on one ciphertext: the boundary cells in full, a
                                                              random FRACTION of the rest, and every setting the
                                                              archive lists as feasible for RID"""
import json
import random
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def keyed(word):
    return "".join(dict.fromkeys(word + AZ))


ALPH = {"AZ": AZ, "KRY": keyed("KRYPTOS"), "PAL": keyed("PALIMPSEST"), "ABS": keyed("ABSCISSA")}
A4 = ("AZ", "KRY", "PAL", "ABS")
SG = (1, -1)
IDX = {a: [ALPH[a].index(ch) for ch in AZ] for a in A4}      # letter code -> place
LET = {a: [AZ.index(ch) for ch in ALPH[a]] for a in A4}      # place -> letter code
CONV1 = [(pa, ca, s) for pa in A4 for ca in A4 for s in SG]
CONV_SS = [(pa, ca, ka, s) for pa in A4 for ca in A4 for ka in A4 for s in SG]
N = 97
POS = list(range(21, 34)) + list(range(63, 74))


def clues():
    sys.path.insert(0, str(ROOT / "r73" / "sealed"))
    from reveal_k4 import CLUES  # noqa: E402  -- post-freeze audit only
    pos = [o + j for o, t in CLUES for j in range(len(t))]
    assert pos == POS
    return pos, [AZ.index(ch) for _, t in CLUES for ch in t]


def load(tsv):
    return dict(l.split("\t") for l in Path(tsv).read_text().splitlines()[1:] if l)


def need(c, p, pa, ca, s):
    return (IDX[ca][c] - s * IDX[pa][p]) % 26


# ------------------------------------------------------------------------------------------------ slot families
def per_slot(pos, m):
    g = {}
    for e, i in enumerate(pos):
        g.setdefault(i % m, []).append(e)
    return g


def slx_ok(K, pos, m, same):
    for es in per_slot(pos, m).values():
        js = [pos[e] // m for e in es]
        if same:
            if not any(all(((j + 1) * A) % 26 == K[e] for j, e in zip(js, es)) for A in range(26)):
                return False
        elif not any(all((A + j * B) % 26 == K[e] for j, e in zip(js, es)) for A in range(26) for B in range(26)):
            return False
    return True


def ss_seq(pa, ca, ka, s, W, jmax):
    """Numeric keys on passes 0..jmax of a slot whose keyword letter (AZ code) is W."""
    out, cur, w = [], W, IDX[ka][W]
    for _ in range(jmax + 1):
        out.append(IDX[ka][cur])
        cur = LET[ca][(s * IDX[pa][cur] + w) % 26]
    return out


def ssx_ok(K, pos, m, conv):
    pa, ca, ka, s = conv
    for es in per_slot(pos, m).values():
        js = [pos[e] // m for e in es]
        if not any(all(seq[j] == K[e] for j, e in zip(js, es))
                   for seq in (ss_seq(pa, ca, ka, s, W, max(js)) for W in range(26))):
            return False
    return True


def slots_one(args):
    rid, ct, pos, pk = args
    c = [AZ.index(ch) for ch in ct]
    out = {}
    for fam in ("SLX", "SLX-A", "SSX"):
        tested, feas, lst = Counter(), Counter(), []
        for m in range(1, 27):
            sl = per_slot(pos, m)
            ck = len(pos) - (sum(min(len(v), 2) for v in sl.values()) if fam == "SLX" else len(sl))
            convs = CONV_SS if fam == "SSX" else CONV1
            for conv in convs:
                pa, ca, s = (conv[0], conv[1], conv[3]) if fam == "SSX" else conv
                K = [need(c[i], p, pa, ca, s) for i, p in zip(pos, pk)]
                ok = ssx_ok(K, pos, m, conv) if fam == "SSX" else slx_ok(K, pos, m, fam == "SLX-A")
                tested[ck] += 1
                if ok:
                    feas[ck] += 1
                    if ck >= 3:
                        lst.append({"conv": list(conv), "m": m, "checks": ck})
        out[fam] = {"tested_by_checks": dict(sorted(tested.items())), "feasible_by_checks": dict(sorted(feas.items())),
                    "feasible_ge3": lst}
    return rid, out


# ------------------------------------------------------------------------------------------------ LX
def lx_conventions():
    pis, seen = [], set()
    for ka1 in A4:
        for ka2 in A4:
            p = tuple(IDX[ka2][LET[ka1][x]] for x in range(26))
            if p not in seen:
                seen.add(p)
                pis.append((ka1, ka2))
    return [(pa1, ca1, pa2, ca2, s1, s2, t2, ka1, ka2) for pa1 in A4 for ca1 in A4 for pa2 in A4 for ca2 in A4
            for s1 in SG for s2 in SG for t2 in SG for ka1, ka2 in pis]


def lx_slots(i, m, w, d, rot):
    a, b = i % m, (i + d * (i // w)) % m
    return (a, b) if rot == 2 else (b, a)


def lx_cells():
    out = []
    for rot in (2, 1):
        for m in range(2, 21):
            for w in list(range(2, 49)) + [97]:
                for d in (1, -1):
                    if w >= N and d != 1:
                        continue
                    out.append((m, w, d, rot))
    return out


BOUNDARY = lambda cell: cell[0] in (2, 20) or cell[1] in (2, 48, 97)  # noqa: E731


def lx_edge_maps(c, pos, pk, conv):
    """f[e][x_a] = the x_b the equation at published position e requires (a bijection of x_a)."""
    pa1, ca1, pa2, ca2, s1, s2, t2, ka1, ka2 = conv
    pi = [IDX[ka2][LET[ka1][x]] for x in range(26)]
    piinv = [0] * 26
    for x, y in enumerate(pi):
        piinv[y] = x
    maps = []
    for i, p in zip(pos, pk):
        y = IDX[ca2][c[i]]
        row = []
        for xa in range(26):
            q = LET[ca1][(s1 * IDX[pa1][p] + xa) % 26]
            row.append(piinv[(t2 * (y - s2 * IDX[pa2][q])) % 26])
        maps.append(row)
    return maps


def lx_feasible(maps, ends, m):
    """(feasible, checks): exhaustive over 26 root values per component, propagating every edge."""
    adj = {}
    for e, (a, b) in enumerate(ends):
        adj.setdefault(a, []).append((e, b, True))
        adj.setdefault(b, []).append((e, a, False))
    inv = {}
    seen, comps = set(), []
    for root in adj:
        if root in seen:
            continue
        comp, stack = [], [root]
        seen.add(root)
        while stack:
            u = stack.pop()
            comp.append(u)
            for _, v, _ in adj[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        comps.append(comp)
    checks = len(ends) - len(adj) + len(comps)
    for comp in comps:
        root = comp[0]
        good = False
        for x0 in range(26):
            val, stack, ok = {root: x0}, [root], True
            while stack and ok:
                u = stack.pop()
                for e, v, fwd in adj[u]:
                    if fwd:
                        want = maps[e][val[u]]
                    else:
                        if e not in inv:
                            r = [0] * 26
                            for xa, xb in enumerate(maps[e]):
                                r[xb] = xa
                            inv[e] = r
                        want = inv[e][val[u]]
                    if v in val:
                        if val[v] != want:
                            ok = False
                            break
                    else:
                        val[v] = want
                        stack.append(v)
            if ok:
                good = True
                break
        if not good:
            return False, checks
    return True, checks


def lx_job(args):
    """One chunk of conventions. Returns (settings checked, feasible settings, checks by cell, tested-by-checks)."""
    rid, ct, pos, pk, work = args
    c = [AZ.index(ch) for ch in ct]
    n, feas, ckmap, tested = 0, [], {}, Counter()
    for ci, cells in work:
        maps = lx_edge_maps(c, pos, pk, CONVS[ci])
        for cell in (ALL_CELLS if cells is None else cells):
            m, w, d, rot = cell
            ok, ck = lx_feasible(maps, [lx_slots(i, m, w, d, rot) for i in pos], m)
            n += 1
            tested[ck] += 1
            ckmap[cell] = ck
            if ok:
                feas.append((ci, cell, ck))
    return n, feas, ckmap, tested


CONVS = lx_conventions()
ALL_CELLS = lx_cells()


def lx_main(tsv, out, rid, frac, seed, procs=4):
    """frac >= 1: every LX setting. Otherwise the boundary cells (m 2 or 20, w 2, 48 or 97) in full, a random frac of
    the other settings, and every setting the archive lists as feasible for rid."""
    pos, pk = clues()
    ct = load(tsv)[rid]
    arch = json.loads((ROOT / "r83/k4/run/R83A.json").read_text())["EXACT"]["none"][rid]["LX"]
    listed = {(tuple(r["conv"]), r["m"], r["w"], r["d"], r["rot"]) for r in arch["feasible_list"]}
    assert len(listed) == arch["feasible_ge_3_checks"], "archive list incomplete"
    cidx = {cv: k for k, cv in enumerate(CONVS)}
    work = []
    if frac >= 1:
        work = [(ci, None) for ci in range(len(CONVS))]
    else:
        rng = random.Random(seed)
        extra = {}
        for cv, m, w, d, rot in listed:
            extra.setdefault(cidx[cv], set()).add((m, w, d, rot))
        for ci in range(len(CONVS)):
            cells = [cell for cell in ALL_CELLS if BOUNDARY(cell) or rng.random() < frac or cell in extra.get(ci, ())]
            work.append((ci, cells))
    chunks = [work[k::procs * 8] for k in range(procs * 8)]
    n, feas, ckmap, tested = 0, set(), {}, Counter()
    with Pool(procs) as pool:
        for nn, ff, cm, tt in pool.imap_unordered(lx_job, [(rid, ct, pos, pk, ch) for ch in chunks]):
            n += nn
            feas |= {(CONVS[ci], *cell) for ci, cell, _ in ff}
            ckmap.update(cm)
            tested.update(tt)
    dis = [{"setting": [list(s[0]), *s[1:]], "replay": s in feas, "archive": s in listed}
           for s in feas ^ listed]
    rep = {"rid": rid, "fraction": frac, "seed": seed, "settings_checked": n,
           "tested_by_checks": dict(sorted(tested.items())), "archive_listed": len(listed),
           "archive_listed_feasible_in_replay": len(listed & feas), "feasible_in_replay": len(feas),
           "n_disagreements": len(dis), "disagreements": dis, "min_checks": min(ckmap.values()),
           "feasible_settings": sorted([list(s[0]), *s[1:], ckmap[s[1:]]] for s in feas)}
    if frac >= 1:
        rep["archive_tested_by_checks_equal"] = {int(k): v for k, v in arch["tested_by_checks"].items() if v} == \
            dict(tested)
        rep["archive_feasible_by_checks_equal"] = {int(k): v for k, v in arch["feasible_by_checks"].items() if v} == \
            dict(Counter(ckmap[s[1:]] for s in feas))
    Path(out).write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps({k: v for k, v in rep.items() if k not in ("feasible_settings", "tested_by_checks")}))


def slots_main(tsv, out, nshuf, procs=4):
    pos, pk = clues()
    rows = [l.split("\t") for l in Path(tsv).read_text().splitlines()[1:] if l][:1 + nshuf]
    with Pool(procs) as pool:
        res = dict(pool.imap_unordered(slots_one, [(rid, ct, pos, pk) for rid, ct in rows]))
    arch = json.loads((ROOT / "r83/k4/run/R83A.json").read_text())["EXACT"]["none"]
    cmp = {}
    for rid in res:
        for fam, r in res[rid].items():
            a = arch[rid][fam]
            norm = lambda d: {int(k): v for k, v in d.items() if v}  # noqa: E731
            new = {(tuple(x["conv"]), x["m"]) for x in r["feasible_ge3"]}
            old = {(tuple(x["conv"]), x["m"]) for x in a["feasible_list"]}
            cmp[f"{rid}:{fam}"] = {"tested_equal": norm(r["tested_by_checks"]) == norm(a["tested_by_checks"]),
                                   "feasible_equal": norm(r["feasible_by_checks"]) == norm(a["feasible_by_checks"]),
                                   "feasible_ge3_replay": len(new), "feasible_ge3_archive": len(old),
                                   "sets_equal": new == old}
    ok = all(all(v[k] for k in ("tested_equal", "feasible_equal", "sets_equal")) for v in cmp.values())
    Path(out).write_text(json.dumps({"all_agree": ok, "comparison": cmp, "results": res}, indent=1) + "\n")
    print("all_agree", ok, {k: v for k, v in cmp.items() if not all(v[x] for x in ("tested_equal", "feasible_equal",
                                                                                    "sets_equal"))})


if __name__ == "__main__":
    if sys.argv[1] == "--slots":
        slots_main(sys.argv[2], sys.argv[3], int(sys.argv[4]))
    elif sys.argv[1] == "--lx":
        lx_main(sys.argv[2], sys.argv[3], sys.argv[4], float(sys.argv[5]), int(sys.argv[6]))
    else:
        raise SystemExit(__doc__)
