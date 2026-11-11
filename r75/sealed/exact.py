#!/usr/bin/env python3
"""R75 exact checks (CRIB-ASSISTED; on K4 they run ONLY after the blind results are frozen, pushed and verified, and
are reported separately from the blind outcome, labelled as in R70 Erratum 1).
Question: with ANY key letters (not just keywords), can a member of each family encipher the published letters to
K4's letters? Where the published letters pin the whole key, the complete 97-letter decode is produced and scored.
  F0X  plain periodic key, period 1..26 (a control: reproduces ledger rows L03/L04).
  F1X  two stacked periodic stages in place, periods m1, m2 in 1..26, pa1, ca1, pa2, ca2 in AZ/KRY/PAL/ABS, each
       stage additive or reverse (s = +1/-1).  Graph check: every published position links key letter (pos mod m1) of
       stage 1 to key letter (pos mod m2) of stage 2 by a bijection; a setting is feasible iff every cycle closes.
  F2X  interrupted key (RESTART/STALL/SKIP after a plaintext- or ciphertext-letter trigger), period 1..26.
  F3X  held key (each key letter used HOLD = 2..12 times), period 1..26, every phase.
"checks" = number of independent equations the published letters impose beyond fixing the key.
Usage: exact.py K4 LM TARGET.tsv OUT.json [N_SHUFFLES=20]  (K4 row and the first N shuffled rows of the frozen target)
       exact.py --selftest LM BOOK OUT.json                 (synthetic plants with random keys; no K4)"""
import itertools
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r75"))
import core  # noqa: E402
from core import IDX, LET, N  # noqa: E402

A4 = ("AZ", "KRY", "PAL", "ABS")
CONV = [(pa, ca, s) for pa in A4 for ca in A4 for s in (1, -1)]            # one stage, any key: 32
ACTIONS = ("RESTART", "STALL", "SKIP")
CUT_LM, CUT_WORD = -1.45, -2.50
MIN_CHECKS = 3
DECODE_CAP = 400       # plaintext-trigger settings decoded per ciphertext, best-checked first
POSN = np.arange(N)


def kall(c, pos, pk):
    """(32, 24) implied key at the published positions for every one-stage convention: y = s*x + k."""
    return np.stack([(IDX[ca][c[pos]] - s * IDX[pa][pk]) % 26 for pa, ca, s in CONV])


def group_check(res, K):
    """res (24,) key-letter index of each published position; K (nconv, 24). feasible (nconv,), number of checks."""
    o = np.argsort(res, kind="stable")
    same = res[o][1:] == res[o][:-1]
    Ks = K[:, o]
    return (Ks[:, 1:][:, same] == Ks[:, :-1][:, same]).all(axis=1), int(same.sum())


def grid_of(u):
    """All 26**u value combinations for u unpinned key letters, shape (26**u, u); one empty row when u = 0."""
    if u == 0:
        return np.zeros((1, 0), dtype=np.int64)
    return np.array(list(itertools.product(range(26), repeat=u)), dtype=np.int64)


def decode_indexed(c, idx_all, res, Krow, conv, col=None, max_unknown=3):
    """Full decode from a key-index map. Key letters pinned by the published positions are used as they are; up to
    max_unknown key letters that no published position pins are completed blind (every combination tried, the best
    by quadgram score kept). Returns (text or None, number of key letters completed)."""
    key = {int(r): int(k) for r, k in zip(res, Krow)}
    unknown = sorted(set(int(x) for x in idx_all) - set(key))
    pa, ca, s = conv
    if len(unknown) > max_unknown or (unknown and (col is None or col.scorer is None)):
        return None, len(unknown)
    grid = grid_of(len(unknown))
    KV = np.zeros((len(grid), N), dtype=np.int64)
    for i, x in enumerate(idx_all):
        KV[:, i] = key[int(x)] if int(x) in key else grid[:, unknown.index(int(x))]
    P = LET[pa][(s * (IDX[ca][c][None, :] - KV)) % 26]
    best = int(np.argmax(col.scorer.quad_score(P))) if len(P) > 1 else 0
    return core.text(P[best]), len(unknown)


class Collector:
    def __init__(self, scorer):
        self.scorer, self.rows = scorer, []
        self.tested, self.feasible = defaultdict(Counter), defaultdict(Counter)

    def best_reading(self, alts):
        """alts: [(text, tag)]: the alternative that reads best by quadgrams (first one if no scorer)."""
        if self.scorer is None or len(alts) == 1:
            return alts[0]
        q = self.scorer.quad_score(np.stack([core.codes(a[0]) for a in alts]))
        return alts[int(np.argmax(q))]

    def add(self, fam, setting, checks, decode):
        self.rows.append({"family": fam, "setting": setting, "checks": checks, "decode": decode})

    def finish(self):
        dec = [r for r in self.rows if r["decode"]]
        if dec and self.scorer is not None:
            lm = self.scorer.lm_score(np.stack([core.codes(r["decode"]) for r in dec]))
            for r, v in zip(dec, lm):
                r["lm_per_letter"] = float(v)
            for r in sorted(dec, key=lambda r: -r["lm_per_letter"])[:200]:
                r["word_per_letter"] = self.scorer.word_score(r["decode"])
        out = {}
        for fam in ("F0X", "F1X", "F2X", "F3X"):
            rows = [r for r in self.rows if r["family"] == fam]
            d = sorted([r for r in rows if "lm_per_letter" in r], key=lambda r: -r["lm_per_letter"])
            readable = [r for r in d if r["lm_per_letter"] >= CUT_LM and r.get("word_per_letter", -9) >= CUT_WORD]
            out[fam] = {"settings_with_checks": dict(sorted(self.tested[fam].items())),
                        "feasible_by_checks": dict(sorted(self.feasible[fam].items())),
                        "feasible_ge_%d_checks" % MIN_CHECKS: len({json.dumps({k: v for k, v in r["setting"].items()
                                                                                if k not in ("key1", "key2")},
                                                                               sort_keys=True) for r in rows}),
                        "full_decodes": len(d),
                        "best_decode_lm": d[0]["lm_per_letter"] if d else None,
                        "verdict": "CONSISTENT" if readable else "NO_SOLUTION",
                        "readable": readable, "top_decodes": d[:10],
                        "feasible_list": [{k: r[k] for k in ("setting", "checks")} for r in rows[:300]]}
        return out


# -------------------------------------------------------------------------------------------------- F0X and F3X
def f0x_f3x(c, pos, pk, col):
    K = kall(c, pos, pk)
    for hold in range(1, 13):
        fam = "F0X" if hold == 1 else "F3X"
        for m in range(1, 27):
            for ph in range(hold * m if hold > 1 else 1):
                idx_all = ((POSN + ph) // hold) % m
                feas, checks = group_check(idx_all[pos], K)
                col.tested[fam][checks] += len(CONV)
                col.feasible[fam][checks] += int(feas.sum())
                if checks >= MIN_CHECKS:
                    for ci in np.where(feas)[0]:
                        dec, nc = decode_indexed(c, idx_all, idx_all[pos], K[ci], CONV[ci], col)
                        col.add(fam, {"conv": CONV[ci], "period": m, "hold": hold, "phase": ph,
                                      "completed_key_letters": nc}, checks, dec)


# -------------------------------------------------------------------------------------------------- F2X
def idx_ctrigger(c, x, act, ph, m):
    """Key index of every position when the trigger is the ciphertext letter x. Also returns whether the start phase
    matters at position `first` (RESTART only: it matters until the first trigger has occurred)."""
    trig = (c == x)
    cum = np.concatenate([[0], np.cumsum(trig)[:-1]])
    last = np.full(N, -1)
    for i in range(1, N):
        last[i] = i - 1 if trig[i - 1] else last[i - 1]
    if act == "RESTART":
        return np.where(last >= 0, POSN - last - 1, ph + POSN) % m, last
    return ((POSN - cum) if act == "STALL" else (POSN + cum)) % m, last


def dec_ptrigger(c, key, conv, x, act, ph):
    pa, ca, s = conv
    m, j, out = len(key), ph, []
    y = IDX[ca][c]
    for i in range(N):
        p = int(LET[pa][(s * (int(y[i]) - key[j % m])) % 26])
        out.append(p)
        j = (0 if act == "RESTART" else j if act == "STALL" else j + 2) if p == x else j + 1
    return np.array(out)


def f2x(c, pos, pk, col):
    K = kall(c, pos, pk)
    blocks = [list(g) for g in np.split(np.arange(len(pos)), np.where(np.diff(pos) > 1)[0] + 1)]
    for x in range(26):
        for act in ACTIONS:
            for m in range(1, 27):
                # ciphertext trigger: the key index of every position follows from the ciphertext alone
                _, last = idx_ctrigger(c, x, act, 0, m)
                needs_phase = act == "RESTART" and last[int(pos.min())] < 0
                for ph in (range(m) if needs_phase else (0,)):
                    idx_all, _ = idx_ctrigger(c, x, act, ph, m)
                    feas, checks = group_check(idx_all[pos], K)
                    col.tested["F2X"][checks] += len(CONV)
                    col.feasible["F2X"][checks] += int(feas.sum())
                    if checks >= MIN_CHECKS:
                        for ci in np.where(feas)[0]:
                            best, nc = decode_indexed(c, idx_all, idx_all[pos], K[ci], CONV[ci], col)
                            best_ph = ph
                            if act == "RESTART" and not needs_phase and best is not None:
                                alts = [(decode_indexed(c, idx_ctrigger(c, x, act, q, m)[0], idx_all[pos], K[ci],
                                                        CONV[ci], col)[0], q) for q in range(m)]
                                best, best_ph = col.best_reading([a for a in alts if a[0]])
                            col.add("F2X", {"conv": CONV[ci], "period": m, "trigger": "C", "letter": chr(65 + x),
                                            "action": act, "phase": best_ph, "completed_key_letters": nc}, checks, best)

    # plaintext trigger: inside a published block the key index follows from the block's first index (unknown, 0..m-1
    # for each block) and from the published letters themselves. Letters that do not occur among the published
    # letters cannot trigger inside the blocks, so they share one case (x = None).
    neq = K[:, :, None] != K[:, None, :]                                        # (32, 24, 24)
    blk_of = np.zeros(len(pos), dtype=np.int64)
    for bi, blk in enumerate(blocks):
        blk_of[blk] = bi
    inside = sorted(set(int(v) for v in pk))
    pending = []
    outside = [x for x in range(26) if x not in inside]
    for x, act in [(x, act) for x in inside for act in ACTIONS] + [(None, "STALL")]:
        rel = np.zeros(len(pos), dtype=np.int64)
        pre = np.ones(len(pos), dtype=bool)                                     # index still relative to block start
        for blk in blocks:
            j, absolute = 0, False
            for e in blk:
                rel[e], pre[e] = j, not absolute
                if x is not None and pk[e] == x:
                    if act == "RESTART":
                        j, absolute = 0, True
                    elif act == "SKIP":
                        j += 2
                else:
                    j += 1
        for m in range(1, 27):
            starts = np.array(list(itertools.product(range(m), repeat=len(blocks))))
            res = np.where(pre[None, :], (starts[:, blk_of] + rel[None, :]) % m, rel[None, :] % m)
            srt = np.sort(res, axis=1)
            checks = len(pos) - ((np.diff(srt, axis=1) != 0).sum(axis=1) + 1)
            same = res[:, :, None] == res[:, None, :]
            for ci in range(len(CONV)):
                feas = ~(same & neq[ci][None]).any(axis=(1, 2))
                for ck, n in zip(*np.unique(checks, return_counts=True)):
                    col.tested["F2X"][int(ck)] += int(n)
                for ck, n in zip(*np.unique(checks[feas], return_counts=True)):
                    col.feasible["F2X"][int(ck)] += int(n)
                for si in np.where(feas & (checks >= MIN_CHECKS))[0]:
                    pending.append((int(checks[si]), ci, x, act, m, [int(v) for v in starts[si]], res[si].copy()))
    pending.sort(key=lambda r: -r[0])
    for rank, (ck, ci, x, act, m, st, res_row) in enumerate(pending):
        key = {int(r): int(k) for r, k in zip(res_row, K[ci])}
        decode, found = None, None
        missing = [r for r in range(m) if r not in key]
        if len(missing) <= 1 and rank < DECODE_CAP:
            alts = []
            for fill in (range(26) if missing else (None,)):
                kv = [key.get(r, fill) for r in range(m)]
                for xx, aa in ([(x, act)] if x is not None else [(o, a2) for o in outside for a2 in ACTIONS]):
                    for ph in range(m):
                        P = dec_ptrigger(c, kv, CONV[ci], xx, aa, ph)
                        if (P[pos] == pk).all():
                            alts.append((core.text(P), (chr(65 + xx), aa, ph)))
            if alts:
                decode, found = col.best_reading(alts)
        col.add("F2X", {"conv": CONV[ci], "period": m, "trigger": "P",
                        "letter": chr(65 + x) if x is not None else "not among the published letters",
                        "action": act if x is not None else "any", "block_starts": st, "decoded_with": found},
                ck, decode)


# -------------------------------------------------------------------------------------------------- F1X
CFG1 = [(pa1, ca1, pa2, ca2, s1, s2) for pa1 in A4 for ca1 in A4 for pa2 in A4 for ca2 in A4
        for s1 in (1, -1) for s2 in (1, -1)]


def f1x(c, pos, pk, col, decode_limit=64):
    nc, ne, k1 = len(CFG1), len(pos), np.arange(26)
    G = np.zeros((nc, ne, 26), dtype=np.int64)
    for ci, (pa1, ca1, pa2, ca2, s1, s2) in enumerate(CFG1):
        a, b, pi = IDX[pa1][pk].astype(np.int64), IDX[ca2][c[pos]].astype(np.int64), IDX[pa2][LET[ca1]].astype(np.int64)
        G[ci] = (b[:, None] - s2 * pi[(s1 * a[:, None] + k1[None, :]) % 26]) % 26       # k2 as a function of k1
    GI = np.argsort(G, axis=2)                                                          # k1 as a function of k2
    for m1 in range(1, 27):
        for m2 in range(1, 27):
            ends = [(("L", int(p) % m1), ("R", int(p) % m2)) for p in pos]
            adj = {}
            for e, (u, v) in enumerate(ends):
                adj.setdefault(u, []).append((e, v))
                adj.setdefault(v, []).append((e, u))
            seen, used, comps = set(), set(), []
            for root in adj:
                if root in seen:
                    continue
                seen.add(root)
                tree, extra, queue = [], [], [root]
                while queue:
                    u = queue.pop(0)
                    for e, v in adj[u]:
                        if e in used:
                            continue
                        used.add(e)
                        if v in seen:
                            extra.append(e)
                        else:
                            seen.add(v)
                            tree.append((e, u, v))
                            queue.append(v)
                comps.append((root, tree, extra))
            checks = ne - len(adj) + len(comps)
            feas = np.ones(nc, dtype=bool)
            nsol = np.ones(nc, dtype=np.int64)
            state = []
            for root, tree, extra in comps:
                val = {root: np.tile(k1, (nc, 1))}
                for e, u, v in tree:
                    val[v] = np.take_along_axis((G if u[0] == "L" else GI)[:, e, :], val[u], axis=1)
                ok = np.ones((nc, 26), dtype=bool)
                for e in extra:
                    u, v = ends[e]
                    ok &= np.take_along_axis(G[:, e, :], val[u], axis=1) == val[v]
                feas &= ok.any(axis=1)
                nsol *= ok.sum(axis=1)
                state.append((ok, val))
            col.tested["F1X"][checks] += nc
            col.feasible["F1X"][checks] += int(feas.sum())
            if checks < MIN_CHECKS:
                continue
            unc1 = [r for r in range(m1) if ("L", r) not in adj]
            unc2 = [r for r in range(m2) if ("R", r) not in adj]
            u = len(unc1) + len(unc2)
            grid = grid_of(u) if u <= 2 else None
            for ci in np.where(feas)[0]:
                pa1, ca1, pa2, ca2, s1, s2 = CFG1[ci]
                st = {"cfg": CFG1[ci], "m1": m1, "m2": m2, "solutions": int(nsol[ci]), "completed_key_letters": u}
                if grid is None or nsol[ci] > decode_limit or (u and col.scorer is None):
                    col.add("F1X", st, checks, None)
                    continue
                for roots in itertools.product(*[np.where(ok[ci])[0] for ok, _ in state]):
                    key1, key2 = np.zeros(m1, dtype=np.int64), np.zeros(m2, dtype=np.int64)
                    for (ok, val), rv in zip(state, roots):
                        for node, arr in val.items():
                            (key1 if node[0] == "L" else key2)[node[1]] = arr[ci, rv]
                    K1, K2 = np.tile(key1, (len(grid), 1)), np.tile(key2, (len(grid), 1))
                    for g, r in enumerate(unc1):
                        K1[:, r] = grid[:, g]
                    for g, r in enumerate(unc2):
                        K2[:, r] = grid[:, len(unc1) + g]
                    x2 = (s2 * (IDX[ca2][c][None, :] - K2[:, POSN % m2])) % 26
                    x1 = (s1 * (IDX[ca1][LET[pa2][x2]] - K1[:, POSN % m1])) % 26
                    P = LET[pa1][x1]
                    bi = int(np.argmax(col.scorer.quad_score(P))) if len(P) > 1 else 0
                    assert (P[bi][pos] == pk).all()
                    col.add("F1X", {**st, "key1": [int(v) for v in K1[bi]], "key2": [int(v) for v in K2[bi]]}, checks,
                            core.text(P[bi]))


def run_all(ct, known, scorer):
    c = core.codes(ct)
    pos = np.array(sorted(known))
    pk = np.array([ord(known[int(p)]) - 65 for p in pos], dtype=np.int16)
    col = Collector(scorer)
    f0x_f3x(c, pos, pk, col)
    f2x(c, pos, pk, col)
    f1x(c, pos, pk, col)
    return col.finish()


# -------------------------------------------------------------------------------------------------- self-test
def selftest(lm, book, out):
    """Random-key plants of each family (keys are random letters, not words); the 'published' letters are the plant's
    letters at the real 24 positions. The true setting must be found feasible and its decode must be the plant."""
    sys.path.insert(0, str(ROOT / "r75" / "sealed"))
    from keyshape import POS  # positions only
    scorer = core.Scorer(lm)
    words = re.findall(r"[A-Z]+", Path(book).read_text(encoding="utf-8", errors="ignore").upper())
    rng = random.Random(750301)
    rep = {}

    def plant():
        i = rng.randrange(len(words) - 60)
        return "".join(words[i:i + 60])[:N]

    def stage(pt, keyidx, conv):
        pa, ca, s = conv
        return core.text(LET[ca][(s * IDX[pa][core.codes(pt)] + np.array(keyidx)) % 26])
    for fam in ("F1X", "F2X", "F3X", "RANDOM"):
        found = []
        for _ in range(4):
            pt = plant()
            if fam == "F1X":
                m1, m2 = rng.randint(3, 11), rng.randint(3, 11)
                k1, k2 = [rng.randrange(26) for _ in range(m1)], [rng.randrange(26) for _ in range(m2)]
                cfg = rng.choice(CFG1)
                ct = stage(stage(pt, [k1[i % m1] for i in range(N)], (cfg[0], cfg[1], cfg[4])),
                           [k2[i % m2] for i in range(N)], (cfg[2], cfg[3], cfg[5]))
            elif fam == "F2X":
                m, conv = rng.randint(4, 10), rng.choice(CONV)
                key, x, act, trig = [rng.randrange(26) for _ in range(m)], rng.choice("ETAOINSRH"), \
                    rng.choice(ACTIONS), rng.choice("PC")
                j, cs = rng.randrange(m), []
                for i in range(N):
                    ch = stage(pt[i], [key[j % m]], conv)
                    cs.append(ch)
                    hit = (pt[i] if trig == "P" else ch) == x
                    j = (0 if act == "RESTART" else j if act == "STALL" else j + 2) if hit else j + 1
                ct = "".join(cs)
            elif fam == "F3X":
                m, hold, conv = rng.randint(3, 8), rng.randint(2, 5), rng.choice(CONV)
                key, ph = [rng.randrange(26) for _ in range(m)], rng.randrange(20)
                ct = stage(pt, [key[((i + ph) // hold) % m] for i in range(N)], conv)
            else:
                ct = "".join(rng.choice(core.AZ) for _ in range(N))
            res = run_all(ct, {int(p): pt[int(p)] for p in POS}, scorer)
            row = {f: {"feasible": res[f]["feasible_ge_%d_checks" % MIN_CHECKS], "verdict": res[f]["verdict"],
                       "plant_decoded": any(r["decode"] == pt for r in res[f]["readable"])} for f in res}
            found.append(row)
            print(fam, {f: (v["feasible"], v["verdict"], v["plant_decoded"]) for f, v in row.items()}, flush=True)
        rep[fam] = found
    Path(out).write_text(json.dumps(rep, indent=1) + "\n")


def main():
    if sys.argv[1] == "--selftest":
        return selftest(sys.argv[2], sys.argv[3], sys.argv[4])
    _, lm, tsv, out = sys.argv[1:5]
    nshuf = int(sys.argv[5]) if len(sys.argv) > 5 else 20
    sys.path.insert(0, str(ROOT / "r73" / "sealed"))
    from reveal_k4 import CLUES  # noqa: E402
    known = {o + i: ch for o, t in CLUES for i, ch in enumerate(t)}
    rows = [l.split("\t") for l in Path(tsv).read_text().splitlines()[1:] if l]
    assert rows[0][0] == "K4"
    scorer = core.Scorer(lm)
    rep = {"K4": run_all(rows[0][1], known, scorer), "shuffles": {}}
    for fam, r in rep["K4"].items():
        print(fam, r["verdict"], "| feasible with >= %d checks:" % MIN_CHECKS, r["feasible_ge_%d_checks" % MIN_CHECKS],
              "| full decodes", r["full_decodes"], "| best decode lm", r["best_decode_lm"])
        for d in r["top_decodes"][:3]:
            print("    %.3f" % d["lm_per_letter"], d["decode"], json.dumps(d["setting"]))
    for rid, ct in rows[1:1 + nshuf]:
        r = run_all(ct, known, scorer)
        rep["shuffles"][rid] = {f: {"feasible": v["feasible_ge_%d_checks" % MIN_CHECKS], "full_decodes": v["full_decodes"],
                                    "best_decode_lm": v["best_decode_lm"], "verdict": v["verdict"]} for f, v in r.items()}
    for fam in rep["K4"]:
        vals = sorted(v[fam]["feasible"] for v in rep["shuffles"].values())
        if vals:
            print(fam, "shuffles: feasible median", vals[len(vals) // 2], "max", vals[-1], "| CONSISTENT in",
                  sum(v[fam]["verdict"] == "CONSISTENT" for v in rep["shuffles"].values()), "of", len(vals))
    Path(out).write_text(json.dumps(rep, indent=1) + "\n")


if __name__ == "__main__":
    main()
