#!/usr/bin/env python3
"""R83 exact checks (CRIB-ASSISTED; design-round code, not yet pre-registered). Question, for each family: with ANY key
letters, can a member encipher the published plaintext letters to the ciphertext letters at their positions? The
checks are algebraic: they never decrypt, never complete a key and never rank anything, so they can only exclude.
A feasible setting is reported as a count and a setting, never as a plaintext; a K4 lead would go to a new blind
round of that family (r83/DESIGN.md §5).

Families (definitions in r83/models83.py):
  LX   linked key: one keyword, two stages on different tableaux, one stage rotated d places per row of w letters.
       Graph check (as R75 F1X, but both stages read the SAME key letters): every published position links the slot
       read by stage one to the slot read by stage two by a bijection; feasible iff every cycle (and self-loop)
       closes.
  PFX  keyword + plaintext autokey with lag L: every published position i whose letter i-L is also published pins
       U[i mod m]; feasible iff the pinned values agree within every slot.
  WPX  walking key stepped by the plaintext: inside each published run the pointer moves by known steps, so the
       pointer is known up to one offset per run; feasible iff, for some offset between the two runs, positions on
       the same ring place share one key value.
  SLX  per-slot linear progression k = A[r] + j*B[r] (SLX-A: the special case A = B); per slot, some (A, B) must fit
       every published position of that slot.
  SSX  per-slot progression by the keyword re-enciphering itself on the tableau; per slot, some keyword letter must
       generate every published key value of that slot.
"checks" = published positions minus the key unknowns they touch (SLX: minus two per touched slot), the number of
independent equations beyond fixing the key; R75's rule counts settings with >= 3.
Drop-one (G6): FEASIBLE once one published letter is set aside.

Usage: exact83.py --selftest OUT.json                (synthetic plants and random ciphertexts; no K4)
       exact83.py --checks OUT.json                  (checks per cell from the published POSITIONS only)
       exact83.py --k4 TARGET.tsv OUT.json [N_SHUF]  (refused unless r83/PROTOCOL.sha256 exists and matches)"""
import hashlib
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "r75"))
sys.path.insert(0, str(HERE))
from core import AZ, IDX, LET, N  # noqa: E402

A4 = ("AZ", "KRY", "PAL", "ABS")
SIGNS = (1, -1)
CONV1 = [(pa, ca, s) for pa in A4 for ca in A4 for s in SIGNS]                     # one stage, free key: 32
MIN_CHECKS = 3
I64 = {k: v.astype(np.int64) for k, v in IDX.items()}
L64 = {k: v.astype(np.int64) for k, v in LET.items()}


def kv1(c, pos, pk):
    """(32, n) numeric key at the published positions for every one-stage convention."""
    return np.stack([(I64[ca][c[pos]] - s * I64[pa][pk]) % 26 for pa, ca, s in CONV1])


def slot_check(res, K):
    """res (n,) unknown that each published position pins; K (nconv, n) the value it must take.
    Returns exact (nconv,), drop_one (nconv, n) and checks = n - number of distinct unknowns."""
    n = len(res)
    pairs = [(a, b) for a in range(n) for b in range(a + 1, n) if res[a] == res[b]]
    C = np.zeros(len(K), dtype=np.int32)
    Ca = np.zeros((len(K), n), dtype=np.int32)
    for a, b in pairs:
        bad = K[:, a] != K[:, b]
        C += bad
        Ca[:, a] += bad
        Ca[:, b] += bad
    return C == 0, (C > 0)[:, None] & (Ca == C[:, None]), n - len(set(int(r) for r in res))


class Tally:
    """Per family: settings tested and feasible by number of checks, a list of feasible settings; with drop-one, the
    settings infeasible as they stand but feasible once one published letter is set aside, by checks and by position,
    with a list (each with the positions whose removal makes it feasible)."""

    def __init__(self, list_min=MIN_CHECKS, cap=300):
        self.tested, self.feasible = defaultdict(Counter), defaultdict(Counter)
        self.drop, self.drop_checks = defaultdict(Counter), defaultdict(Counter)
        self.tested_eff, self.feasible_eff, self.drop_eff = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
        self.rows, self.drows, self.list_min, self.cap = defaultdict(list), defaultdict(list), list_min, cap

    def add(self, fam, checks, n, feas, make, dmat=None, dpos=None, eff=None):
        """feas: (n,) bool; make(i): setting dict of row i; dmat: (n, len(dpos)) bool, newly feasible once that
        position is dropped (rows already feasible must be False). eff: the effective strength, -log26 of the chance
        that a setting is feasible on a random ciphertext (= checks for the slot checks; edges - slots for the graph
        checks, whose components each have 26 tries); default checks."""
        feas = np.asarray(feas, dtype=bool)
        eff = checks if eff is None else eff
        self.tested[fam][checks] += n
        self.feasible[fam][checks] += int(feas.sum())
        self.tested_eff[fam][eff] += n
        self.feasible_eff[fam][eff] += int(feas.sum())
        if checks >= self.list_min:
            for i in np.flatnonzero(feas)[:max(0, self.cap - len(self.rows[fam]))]:
                self.rows[fam].append({**make(int(i)), "checks": checks, "eff": eff})
        if dmat is not None:
            dmat = np.asarray(dmat, dtype=bool) & ~feas[:, None]
            for a in np.flatnonzero(dmat.any(axis=0)):
                self.drop[fam][int(dpos[a])] += int(dmat[:, a].sum())
            anyd = dmat.any(axis=1)
            self.drop_checks[fam][checks] += int(anyd.sum())
            self.drop_eff[fam][eff] += int(anyd.sum())
            if checks >= self.list_min:
                for i in np.flatnonzero(anyd)[:max(0, self.cap - len(self.drows[fam]))]:
                    self.drows[fam].append({**make(int(i)), "checks": checks, "eff": eff,
                                            "dropped": [int(dpos[a]) for a in np.flatnonzero(dmat[i])]})

    def report(self):
        out = {}
        for fam in self.tested:
            t, f = self.tested[fam], self.feasible[fam]
            out[fam] = {"tested_by_checks": dict(sorted(t.items())), "feasible_by_checks": dict(sorted(f.items())),
                        "settings_ge_%d_checks" % MIN_CHECKS: sum(v for k, v in t.items() if k >= MIN_CHECKS),
                        "feasible_ge_%d_checks" % MIN_CHECKS: sum(v for k, v in f.items() if k >= MIN_CHECKS),
                        "drop_one_feasible_by_position": dict(sorted(self.drop[fam].items())),
                        "drop_one_feasible_by_checks": dict(sorted(self.drop_checks[fam].items())),
                        "tested_by_eff": dict(sorted(self.tested_eff[fam].items())),
                        "feasible_by_eff": dict(sorted(self.feasible_eff[fam].items())),
                        "drop_one_feasible_by_eff": dict(sorted(self.drop_eff[fam].items())),
                        "drop_one_list": self.drows[fam],
                        "feasible_list": self.rows[fam]}
        return out


# ------------------------------------------------------------------------------------------------ PFX
def pfx(c, pos, pk, tally, lmax=12, mmax=26, drop=False):
    K1 = kv1(c, pos, pk)
    at = {int(p): e for e, p in enumerate(pos)}
    conv = [(cv, beta, f) for cv in CONV1 for beta in A4 for f in SIGNS]               # 256
    for L in range(1, lmax + 1):
        idx = [e for e, p in enumerate(pos) if int(p) - L in at]
        if not idx:
            continue
        fb = np.array([pk[at[int(pos[e]) - L]] for e in idx])
        K = np.stack([(K1[CONV1.index(cv)][idx] - f * I64[beta][fb]) % 26 for cv, beta, f in conv])
        for m in range(1, mmax + 1):
            ex, d1, checks = slot_check(pos[idx] % m, K)
            tally.add("PFX", checks, len(conv), ex,
                      lambda i, L=L, m=m: {"conv": conv[i][0], "beta": conv[i][1], "f": conv[i][2], "L": L, "m": m},
                      d1 if drop else None, pos[idx])


# ------------------------------------------------------------------------------------------------ WPX
def runs_of(pos):
    out, cur = [], [0]
    for e in range(1, len(pos)):
        if pos[e] == pos[e - 1] + 1:
            cur.append(e)
        else:
            out.append(cur)
            cur = [e]
    return out + [cur]


def wpx(c, pos, pk, tally, mmax=26, drop=False):
    K = kv1(c, pos, pk)
    R = runs_of(pos)
    for alpha in A4:
        for e in (0, 1):
            for d in SIGNS:
                step = d * (I64[alpha][pk] + e)
                rel = np.zeros(len(pos), dtype=np.int64)
                for run in R:
                    rel[run] = np.concatenate([[0], np.cumsum(step[run][:-1])])
                for m in range(2, mmax + 1):
                    feas = np.zeros(len(CONV1), dtype=bool)
                    dfe = np.zeros((len(CONV1), len(pos)), dtype=bool)
                    worst = None
                    for off in np.ndindex(*([m] * (len(R) - 1))):
                        res = rel.copy()
                        for q, run in enumerate(R[1:]):
                            res[run] += off[q]
                        ex, d1, checks = slot_check(res % m, K)
                        feas |= ex
                        dfe |= d1
                        worst = checks if worst is None else min(worst, checks)
                    tally.add("WPX", worst, len(CONV1), feas,
                              lambda i, alpha=alpha, e=e, d=d, m=m: {"conv": CONV1[i], "alpha": alpha, "e": e, "d": d,
                                                                     "m": m},
                              dfe if drop else None, pos)


# ------------------------------------------------------------------------------------------------ SLX / SSX
def _per_slot(pos, m):
    slots = defaultdict(list)
    for e, p in enumerate(pos):
        slots[int(p) % m].append(e)
    return slots


def slx_feasible(K, pos, m, same=False):
    """(nconv,) feasible under k = A + j*B per slot (same: A = B, i.e. k = (j+1)*A)."""
    feas = np.ones(len(K), dtype=bool)
    v = np.arange(26)
    for r, es in _per_slot(pos, m).items():
        j = np.array([int(pos[e]) // m for e in es])
        if same:
            pred = ((j[None, :] + 1) * v[:, None]) % 26                                   # (26 A, n_r)
            feas &= (pred[None, :, :] == K[:, None, es]).all(axis=2).any(axis=1)
        else:
            A = (K[:, None, es] - j[None, None, :] * v[None, :, None]) % 26               # (nconv, 26 B, n_r)
            feas &= (A == A[:, :, :1]).all(axis=2).any(axis=1)
    return feas


def slx(c, pos, pk, tally, mmax=26, drop=False):
    K = kv1(c, pos, pk)
    for same, fam, unk in ((False, "SLX", 2), (True, "SLX-A", 1)):
        for m in range(1, mmax + 1):
            sl = _per_slot(pos, m)
            checks = len(pos) - sum(min(len(v), unk) for v in sl.values())
            feas = slx_feasible(K, pos, m, same)
            dmat = None
            if drop:
                dmat = np.stack([slx_feasible(K[:, keep], pos[keep], m, same)
                                 for keep in (np.array([b for b in range(len(pos)) if b != a]) for a in range(len(pos)))],
                                axis=1)
            tally.add(fam, checks, len(CONV1), feas, lambda i, m=m: {"conv": CONV1[i], "m": m}, dmat, pos)


CONV_SS = [(pa, ca, ka, s) for pa in A4 for ca in A4 for ka in A4 for s in SIGNS]    # 128


def ss_table(jmax=N):
    """SEQ[conv, w, j]: numeric key on pass j of a slot whose keyword letter has number w (on ka)."""
    T = np.zeros((len(CONV_SS), 26, jmax), dtype=np.int64)
    for ci, (pa, ca, ka, s) in enumerate(CONV_SS):
        w = np.arange(26)
        let = L64[ka][w]                                                                   # keyword letters (AZ codes)
        cur = let.copy()
        for j in range(jmax):
            T[ci, :, j] = I64[ka][cur]
            cur = L64[ca][(s * I64[pa][cur] + w) % 26]
    return T


def ssx(c, pos, pk, tally, mmax=26, drop=False, _T=[]):
    if not _T:
        _T.append(ss_table())
    T = _T[0]
    Kc = {cv: (I64[cv[1]][c[pos]] - cv[3] * I64[cv[0]][pk]) % 26 for cv in CONV_SS}
    K = np.stack([Kc[cv] for cv in CONV_SS])

    def feasible(Kx, px, m):
        f = np.ones(len(CONV_SS), dtype=bool)
        for r, es in _per_slot(px, m).items():
            j = np.array([int(px[e]) // m for e in es])
            f &= (T[:, :, j] == Kx[:, None, es]).all(axis=2).any(axis=1)
        return f

    for m in range(1, mmax + 1):
        sl = _per_slot(pos, m)
        checks = len(pos) - len(sl)
        feas = feasible(K, pos, m)
        dmat = None
        if drop:
            dmat = np.stack([feasible(K[:, keep], pos[keep], m)
                             for keep in (np.array([b for b in range(len(pos)) if b != a]) for a in range(len(pos)))],
                            axis=1)
        tally.add("SSX", checks, len(CONV_SS), feas, lambda i, m=m: {"conv": CONV_SS[i], "m": m}, dmat, pos)


# ------------------------------------------------------------------------------------------------ LX
def lk_conventions():
    """Stage alphabets on all four sides (CA1 = PA2 included: with a rotated stage it does not collapse to a period),
    signs s1, s2, the relative sign t2 of the stage-two key, and the stage-two renumbering pi = IDX[ka2] o LET[ka1]
    (duplicates removed: only pi matters for a free key)."""
    pis, seen = [], set()
    for ka1 in A4:
        for ka2 in A4:
            p = tuple(int(v) for v in I64[ka2][L64[ka1]])
            if p not in seen:
                seen.add(p)
                pis.append((ka1, ka2))
    return [(pa1, ca1, pa2, ca2, s1, s2, t2, ka1, ka2) for pa1 in A4 for ca1 in A4 for pa2 in A4 for ca2 in A4
            for s1 in SIGNS for s2 in SIGNS for t2 in SIGNS for ka1, ka2 in pis]


def lk_maps(c, pos, pk, conv):
    """G[conv, e, x] = the stage-two key number at edge e given stage-one number x; GI its inverse."""
    x = np.arange(26)
    G = np.zeros((len(conv), len(pos), 26), dtype=np.int16)
    for ci, (pa1, ca1, pa2, ca2, s1, s2, t2, ka1, ka2) in enumerate(conv):
        pi = I64[ka2][L64[ka1]]
        piinv = np.argsort(pi)
        q = L64[ca1][(s1 * I64[pa1][pk][:, None] + x[None, :]) % 26]                      # (n, 26) AZ codes
        y = I64[ca2][c[pos]][:, None]
        G[ci] = piinv[(t2 * (y - s2 * I64[pa2][q])) % 26]
    return G, np.argsort(G, axis=2).astype(np.int16)


def lk_check(G, GI, ends, nconv, skip=None):
    """Feasibility over all conventions for one (m, w, d, rot) graph. ends[e] = (stage-one slot, stage-two slot).
    Conventions are dropped as soon as one component rules them out, so later components cost little."""
    adj = defaultdict(list)
    for e, (u, v) in enumerate(ends):
        if e == skip:
            continue
        adj[u].append((e, v, True))
        if v != u:
            adj[v].append((e, u, False))
    comps, seen = [], set()
    for root in adj:
        if root in seen:
            continue
        seen.add(root)
        order, queue, used = [], [root], set()
        while queue:
            u = queue.pop(0)
            for e, v, fwd in adj[u]:
                if e in used:
                    continue
                used.add(e)
                order.append((e, u, v, fwd))
                if v not in seen:
                    seen.add(v)
                    queue.append(v)
        comps.append(order)
    nedge = sum(len(o) for o in comps)
    checks = nedge - len(adj) + len(comps)
    eff = nedge - len(adj)
    comps.sort(key=lambda o: -len(o))
    alive = np.arange(nconv)
    for order in comps:
        if not len(alive):
            break
        val = {order[0][1]: np.tile(np.arange(26, dtype=np.int16), (len(alive), 1))}
        ok = np.ones((len(alive), 26), dtype=bool)
        for e, u, v, fwd in order:
            M = (G if fwd else GI)[alive, e, :]
            nxt = np.take_along_axis(M, val[u], axis=1)
            if v in val:
                ok &= nxt == val[v]
                keep = ok.any(axis=1)
                if not keep.all():
                    alive, ok = alive[keep], ok[keep]
                    val = {k: x[keep] for k, x in val.items()}
                    if not len(alive):
                        break
            else:
                val[v] = nxt
        alive = alive[ok.any(axis=1)]
    feas = np.zeros(nconv, dtype=bool)
    feas[alive] = True
    return feas, checks, eff


def lx(c, pos, pk, tally, mmax=20, widths=tuple(range(2, 49)) + (97,), ds=(1, -1), drop=False, conv=None, rots=(2, 1)):
    import models83 as MD
    conv = conv or lk_conventions()
    G, GI = lk_maps(c, pos, pk, conv)
    for rot in rots:
        for m in range(2, mmax + 1):
            for w in widths:
                for d in ds:
                    if w >= N and d != 1:
                        continue
                    ends = [MD.lk_slots(int(p), m, w, d, rot) for p in pos]
                    feas, checks, eff = lk_check(G, GI, ends, len(conv))
                    dmat = None
                    if drop and checks >= MIN_CHECKS:
                        dmat = np.stack([lk_check(G, GI, ends, len(conv), skip=a)[0] for a in range(len(pos))], axis=1)
                    tally.add("LX", checks, len(conv), feas,
                              lambda i, m=m, w=w, d=d, rot=rot: {"conv": conv[i], "m": m, "w": w, "d": d, "rot": rot},
                              dmat, pos, eff)


FAMILIES = {"LX": lx, "PFX": pfx, "WPX": wpx, "SLX": slx, "SSX": ssx}


def run_all(c, pos, pk, drop=False, fams=FAMILIES, **kw):
    t = Tally()
    for name, fn in fams.items():
        fn(c, pos, pk, t, drop=drop, **kw.get(name, {}))
    return t.report()


# ------------------------------------------------------------------------------------------------ entry points
def published_positions():
    """K4's published-letter POSITIONS only (r73/sealed/reveal_k4.py: 0-based 21-33 and 63-73), for synthetic plants."""
    return np.array(list(range(21, 34)) + list(range(63, 74)))


def setting_feasible(fam, st, c, pos, pk):
    """The exact check's verdict for exactly one planted setting (fam in LK, PF, WP, SL, SS)."""
    import models83 as MD
    if fam == "LK":
        G, GI = lk_maps(c, pos, pk, [tuple(st["conv"])])
        ends = [MD.lk_slots(int(i), len(st["x"]), st["w"], st.get("d", 1), st.get("rot", 2)) for i in pos]
        return bool(lk_check(G, GI, ends, 1)[0][0])
    if fam == "PF":
        K1 = kv1(c, pos, pk)[CONV1.index(tuple(st["conv"]))]
        at = {int(p): e for e, p in enumerate(pos)}
        idx = [e for e, p in enumerate(pos) if int(p) - st["L"] in at]
        fb = np.array([pk[at[int(pos[e]) - st["L"]]] for e in idx])
        K = ((K1[idx] - st["f"] * I64[st["beta"]][fb]) % 26)[None, :]
        return bool(slot_check(pos[idx] % len(st["U"]), K)[0][0])
    m = _klen(st)
    if fam == "SL":
        return bool(slx_feasible(kv1(c, pos, pk)[CONV1.index(tuple(st["conv"]))][None, :], pos, m)[0])
    t = Tally(list_min=-99, cap=10 ** 9)
    if fam == "WP":
        wpx(c, pos, pk, t, mmax=m)
        return any(r["m"] == m and tuple(r["conv"]) == tuple(st["conv"]) and r["alpha"] == st["alpha"]
                   and r["e"] == st["e"] and r["d"] == st["d"] for r in t.rows["WPX"])
    ssx(c, pos, pk, t, mmax=m)
    return any(r["m"] == m and tuple(r["conv"]) == tuple(st["conv"]) for r in t.rows["SSX"])


def selftest(out, seed=830001, n_rand=4):
    """Synthetic only: (1) 20 plants, each must be feasible under its own setting; (2) random ciphertexts and random
    published-position letters through every check at full size: the feasible counts by checks are the chance level
    the K4 counts must be read against."""
    import models83 as MD
    rng = random.Random(seed)
    pos = published_positions()
    rep = {"plants": [], "random": []}
    for fam in ("LK", "PF", "WP", "SL", "SS"):
        for _ in range(4):
            st = MD.random_setting(rng, fam)
            pt = "".join(rng.choice(AZ) for _ in range(N))
            ct = MD.encrypt(pt, st)
            assert MD.decrypt(ct, st) == pt
            c, p = np.array([AZ.index(x) for x in ct]), np.array([AZ.index(x) for x in pt])
            rep["plants"].append({"family": fam, "m": _klen(st), "found": setting_feasible(fam, st, c, pos, p[pos])})
    for k in range(n_rand):
        c = np.array([rng.randrange(26) for _ in range(N)])
        pk = np.array([rng.randrange(26) for _ in range(len(pos))])
        r = run_all(c, pos, pk)
        rep["random"].append({f: {"feasible_by_checks": v["feasible_by_checks"],
                                  "tested_by_checks": v["tested_by_checks"]} for f, v in r.items()})
    Path(out).write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps({"plants_found": sum(p["found"] for p in rep["plants"]), "plants": len(rep["plants"]),
                      "random_feasible_ge3": [{f: sum(n for ck, n in v["feasible_by_checks"].items() if ck >= MIN_CHECKS)
                                               for f, v in r.items()} for r in rep["random"]]}))
    return rep


def _klen(st):
    for k in ("x", "U", "A", "W"):
        if k in st:
            return len(st[k])


def check_table(pos=None):
    """Positions only (no ciphertext, no letters): checks per cell for every family."""
    import models83 as MD
    pos = published_positions() if pos is None else pos
    out = {"LX_rot2_d1": {}, "LX_rot1_d1": {}, "PFX": {}, "WPX": {}, "SLX": {}, "SLX-A": {}, "SSX": {}}
    G = np.zeros((1, len(pos), 26), dtype=np.int16)
    for rot in (2, 1):
        for m in range(2, 21):
            r = {w: lk_check(G, G, [MD.lk_slots(int(p), m, w, 1, rot) for p in pos], 1)[1:]
                 for w in list(range(2, 49)) + [97]}
            out[f"LX_rot{rot}_d1"][m] = {w: v[0] for w, v in r.items()}
            out.setdefault(f"LX_eff_rot{rot}_d1", {})[m] = {w: v[1] for w, v in r.items()}
    at = set(int(p) for p in pos)
    for L in range(1, 13):
        idx = [e for e, p in enumerate(pos) if int(p) - L in at]
        out["PFX"][L] = {m: len(idx) - len({int(pos[e]) % m for e in idx}) for m in range(1, 27)}
    R = runs_of(pos)
    for m in range(2, 27):
        # worst case over the unknown offset between runs (pointer steps assumed distinct mod m inside a run)
        out["WPX"][m] = len(pos) - min(m, len(pos))
    for m in range(1, 27):
        sl = _per_slot(pos, m)
        out["SLX"][m] = len(pos) - sum(min(len(v), 2) for v in sl.values())
        out["SLX-A"][m] = len(pos) - len(sl)
        out["SSX"][m] = len(pos) - len(sl)
    return out


def guard():
    """K4 mode only after pre-registration: r83/PROTOCOL.sha256 must exist and every listed file must match."""
    p = HERE / "PROTOCOL.sha256"
    if not p.exists():
        raise SystemExit("r83 is not pre-registered (no r83/PROTOCOL.sha256): K4 mode refused")
    for line in p.read_text().splitlines():
        h, f = line.split()
        if hashlib.sha256((ROOT / f).read_bytes()).hexdigest() != h:
            raise SystemExit(f"protocol hash mismatch: {f}")


def main():
    if sys.argv[1] == "--selftest":
        selftest(sys.argv[2])
        return
    if sys.argv[1] == "--checks":
        Path(sys.argv[2]).write_text(json.dumps(check_table(), indent=1) + "\n")
        return
    if sys.argv[1] == "--k4":
        guard()
        sys.path.insert(0, str(ROOT / "r73" / "sealed"))
        from reveal_k4 import CLUES
        tsv, out = sys.argv[2], sys.argv[3]
        nshuf = int(sys.argv[4]) if len(sys.argv) > 4 else 20
        pos = np.array([o + i for o, t in CLUES for i in range(len(t))])
        pk = np.array([AZ.index(ch) for _, t in CLUES for ch in t])
        rows = [l.split("\t") for l in Path(tsv).read_text().splitlines()[1:] if l]
        res = {}
        for rid, ct in [r for r in rows if r[0] == "K4"] + [r for r in rows if r[0] != "K4"][:nshuf]:
            c = np.array([AZ.index(x) for x in ct])
            res[rid] = run_all(c, pos, pk, drop=(rid == "K4"))
            print(rid, {f: v["feasible_ge_%d_checks" % MIN_CHECKS] for f, v in res[rid].items()}, flush=True)
        Path(out).write_text(json.dumps(res, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
                             + "\n")
        return
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
