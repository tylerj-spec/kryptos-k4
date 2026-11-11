#!/usr/bin/env python3
"""R75 Amendment 1, part C2b: GRID KEYS (hypothesis H4 in r76/HYPOTHESES.md). CRIB-ASSISTED: on K4 it runs ONLY after
the blind results are frozen, pushed and verified, and is reported separately from the blind outcome.
Question: was the message written in rows of w letters (the first row starting at column o), with one key repeating
along every row (one letter per column) and a second key that changes once per row, each key on its own stage?
  Stage 1 key slot L(i), stage 2 key slot R(i), with q = i + o:  either L = q mod w (column), R = q div w (row), or
  L = row, R = column. Each stage: x -> s*x + k on alphabets pa -> ca, both in AZ/KRY/PAL/ABS, s = +1/-1 (the 1,024
  configurations of exact.py's F1X; ca1 = pa2 with the same s includes the plain additive form key = column + row).
  Every w in 2..48, every o in 0..w-1, both orientations.
Decision: a setting is feasible iff every cycle of the graph (published positions link L-slot to R-slot) closes.
Settings with >= MIN_CHECKS independent checks and at most MAX_SOL key solutions are decoded: pinned slots as forced,
unpinned slots (rows or columns with no published letter) completed blind by coordinate ascent on the quadgram score.
A decode is READABLE iff it clears both pre-registered cuts (letter model >= -1.45, word model >= -2.50 per letter).
Usage: gridx.py K4 LM TARGET.tsv OUT.json [N_SHUFFLES=20]   (K4 row and the first N shuffled rows of the target)
       gridx.py --selftest LM BOOK OUT.json                 (synthetic grid-key plants and random ciphertexts; no K4)"""
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
sys.path.insert(0, str(ROOT / "r75" / "sealed"))
import core  # noqa: E402
from core import IDX, LET, N  # noqa: E402
from exact import CFG1, CUT_LM, CUT_WORD  # noqa: E402

MIN_CHECKS, MAX_SOL, SWEEPS = 5, 26, 3
WIDTHS = range(2, 49)
POSN = np.arange(N)


def g_tables(c, pos, pk):
    """G[ci, e, k1] = stage-2 key forced at published position e by stage-1 key k1; GI the inverse map."""
    k1 = np.arange(26)
    G = np.zeros((len(CFG1), len(pos), 26), dtype=np.int64)
    for ci, (pa1, ca1, pa2, ca2, s1, s2) in enumerate(CFG1):
        a, b = IDX[pa1][pk].astype(np.int64), IDX[ca2][c[pos]].astype(np.int64)
        pi = IDX[pa2][LET[ca1]].astype(np.int64)
        G[ci] = (b[:, None] - s2 * pi[(s1 * a[:, None] + k1[None, :]) % 26]) % 26
    return G, np.argsort(G, axis=2)


def decrypt(c, cfg, K1, K2, Lmap, Rmap):
    """Rows of K1 (n, nL) and K2 (n, nR) -> (n, 97) plaintext codes."""
    pa1, ca1, pa2, ca2, s1, s2 = cfg
    x2 = (s2 * (IDX[ca2][c][None, :] - K2[:, Rmap])) % 26
    return LET[pa1][(s1 * (IDX[ca1][LET[pa2][x2]] - K1[:, Lmap])) % 26]


def complete(c, cfg, key1, key2, freeL, freeR, Lmap, Rmap, scorer):
    """Blind completion of unpinned slots: coordinate ascent, each free slot set to the best of 26 by quadgrams."""
    k1, k2 = key1.copy(), key2.copy()
    slots = [("L", s) for s in freeL] + [("R", s) for s in freeR]
    for _ in range(SWEEPS if slots else 0):
        changed = False
        for side, s in slots:
            K1, K2 = np.tile(k1, (26, 1)), np.tile(k2, (26, 1))
            (K1 if side == "L" else K2)[:, s] = np.arange(26)
            best = int(np.argmax(scorer.quad_score(decrypt(c, cfg, K1, K2, Lmap, Rmap))))
            cur = (k1 if side == "L" else k2)
            if cur[s] != best:
                cur[s], changed = best, True
        if not changed:
            break
    return decrypt(c, cfg, k1[None, :], k2[None, :], Lmap, Rmap)[0], k1, k2


def check_maps(c, pos, pk, G, GI, Lmap, Rmap, nL, nR, scorer, meta, tested, feasible, rows):
    ends = [(("L", int(Lmap[p])), ("R", int(Rmap[p]))) for p in pos]
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
    checks = len(pos) - len(adj) + len(comps)
    nc = len(CFG1)
    tested[checks] += nc
    if checks < MIN_CHECKS:
        return
    feas, nsol, state = np.ones(nc, dtype=bool), np.ones(nc, dtype=np.int64), []
    for root, tree, extra in comps:
        val = {root: np.tile(np.arange(26), (nc, 1))}
        for e, u, v in tree:
            val[v] = np.take_along_axis((G if u[0] == "L" else GI)[:, e, :], val[u], axis=1)
        ok = np.ones((nc, 26), dtype=bool)
        for e in extra:
            u, v = ends[e]
            ok &= np.take_along_axis(G[:, e, :], val[u], axis=1) == val[v]
        feas &= ok.any(axis=1)
        nsol *= ok.sum(axis=1)
        state.append((ok, val))
    feasible[checks] += int(feas.sum())
    freeL = [s for s in range(nL) if ("L", s) not in adj]
    freeR = [s for s in range(nR) if ("R", s) not in adj]
    for ci in np.where(feas)[0]:
        st = {**meta, "cfg": CFG1[ci], "checks": checks, "solutions": int(nsol[ci]),
              "completed_slots": len(freeL) + len(freeR)}
        if nsol[ci] > MAX_SOL or scorer is None:
            rows.append({"setting": st, "decode": None})
            continue
        best = None
        for roots in itertools.product(*[np.where(ok[ci])[0] for ok, _ in state]):
            key1, key2 = np.zeros(nL, dtype=np.int64), np.zeros(nR, dtype=np.int64)
            for (ok, val), rv in zip(state, roots):
                for node, arr in val.items():
                    (key1 if node[0] == "L" else key2)[node[1]] = arr[ci, rv]
            P, k1, k2 = complete(c, CFG1[ci], key1, key2, freeL, freeR, Lmap, Rmap, scorer)
            assert (P[pos] == pk).all()
            q = float(scorer.quad_score(P[None, :])[0])
            if best is None or q > best[0]:
                best = (q, core.text(P), k1, k2)
        rows.append({"setting": {**st, "key1": [int(v) for v in best[2]], "key2": [int(v) for v in best[3]]},
                     "decode": best[1]})


def run(ct, known, scorer):
    c = core.codes(ct)
    pos = np.array(sorted(known))
    pk = np.array([ord(known[int(p)]) - 65 for p in pos], dtype=np.int16)
    G, GI = g_tables(c, pos, pk)
    tested, feasible, rows = Counter(), Counter(), []
    for w in WIDTHS:
        for o in range(w):
            q = POSN + o
            colm, rowm = q % w, q // w
            nrow = int(rowm.max()) + 1
            for orient in ("L=column", "L=row"):
                Lmap, Rmap, nL, nR = (colm, rowm, w, nrow) if orient == "L=column" else (rowm, colm, nrow, w)
                check_maps(c, pos, pk, G, GI, Lmap, Rmap, nL, nR, scorer,
                           {"width": w, "offset": o, "orientation": orient}, tested, feasible, rows)
    dec = [r for r in rows if r["decode"]]
    if dec and scorer is not None:
        lm = scorer.lm_score(np.stack([core.codes(r["decode"]) for r in dec]))
        for r, v in zip(dec, lm):
            r["lm_per_letter"] = float(v)
        for r in sorted(dec, key=lambda r: -r["lm_per_letter"])[:200]:
            r["word_per_letter"] = scorer.word_score(r["decode"])
    d = sorted([r for r in rows if "lm_per_letter" in r], key=lambda r: -r["lm_per_letter"])
    readable = [r for r in d if r["lm_per_letter"] >= CUT_LM and r.get("word_per_letter", -9) >= CUT_WORD]
    return {"settings_with_checks": dict(sorted(tested.items())), "feasible_by_checks": dict(sorted(feasible.items())),
            "feasible_ge_%d_checks" % MIN_CHECKS: len(rows), "full_decodes": len(d),
            "best_decode_lm": d[0]["lm_per_letter"] if d else None,
            "verdict": "CONSISTENT" if readable else "NO_SOLUTION", "readable": readable, "top_decodes": d[:10],
            "feasible_list": [r["setting"] for r in rows[:300]]}


def selftest(lm, book, out):
    sys.path.insert(0, str(ROOT / "r75" / "sealed"))
    from keyshape import POS  # positions only
    scorer = core.Scorer(lm)
    words = re.findall(r"[A-Z]+", Path(book).read_text(encoding="utf-8", errors="ignore").upper())
    rng = random.Random(750501)
    rep = defaultdict(list)
    plans = [("W7", 7), ("W7", 7), ("W21", 21), ("W21", 21), ("WRAND", None), ("WRAND", None)] + [("RANDOM", None)] * 6
    for name, w in plans:
        i = rng.randrange(len(words) - 60)
        pt = "".join(words[i:i + 60])[:N]
        if name == "RANDOM":
            ct = "".join(rng.choice(core.AZ) for _ in range(N))
            truth = None
        else:
            w = w or rng.randint(3, 12)
            o = rng.randrange(w)
            q = POSN + o
            colm, rowm = q % w, q // w
            cfg = rng.choice(CFG1)
            orient = rng.choice(("L=column", "L=row"))
            Lmap, Rmap = (colm, rowm) if orient == "L=column" else (rowm, colm)
            k1 = np.array([rng.randrange(26) for _ in range(int(Lmap.max()) + 1)])
            k2 = np.array([rng.randrange(26) for _ in range(int(Rmap.max()) + 1)])
            pa1, ca1, pa2, ca2, s1, s2 = cfg
            x1 = LET[ca1][(s1 * IDX[pa1][core.codes(pt)] + k1[Lmap]) % 26]
            ctc = LET[ca2][(s2 * IDX[pa2][x1] + k2[Rmap]) % 26]
            ct = core.text(ctc)
            assert core.text(decrypt(ctc, cfg, k1[None, :], k2[None, :], Lmap, Rmap)[0]) == pt
            truth = {"width": w, "offset": o, "orientation": orient}
        r = run(ct, {int(p): pt[int(p)] for p in POS}, scorer)
        found = any(x["decode"] == pt for x in r["readable"])
        true_feasible = truth is not None and any(all(s.get(k) == v for k, v in truth.items()) for s in
                                                  [x["setting"] for x in r["readable"] + r["top_decodes"]])
        row = {"plant": name, "truth": truth, "feasible": r["feasible_ge_%d_checks" % MIN_CHECKS],
               "readable": len(r["readable"]), "plant_decoded": found, "true_grid_among_top": true_feasible,
               "best_decode_lm": r["best_decode_lm"],
               "best_readable_letters_right": max([sum(a == b for a, b in zip(x["decode"], pt)) for x in r["readable"]]
                                                  or [None], key=lambda v: -1 if v is None else v),
               "best_wrong_readable_lm": max([x["lm_per_letter"] for x in r["readable"] if x["decode"] != pt] or [None],
                                             key=lambda v: -9 if v is None else v)}
        rep[name].append(row)
        print(json.dumps(row), flush=True)
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
    rep = {"K4": run(rows[0][1], known, scorer), "shuffles": {}}
    r = rep["K4"]
    print("F4X", r["verdict"], "| feasible with >= %d checks:" % MIN_CHECKS, r["feasible_ge_%d_checks" % MIN_CHECKS],
          "| full decodes", r["full_decodes"], "| best decode lm", r["best_decode_lm"])
    for d in r["top_decodes"][:3]:
        print("    %.3f" % d["lm_per_letter"], d["decode"], json.dumps(d["setting"]))
    for rid, ct in rows[1:1 + nshuf]:
        s = run(ct, known, scorer)
        rep["shuffles"][rid] = {"feasible": s["feasible_ge_%d_checks" % MIN_CHECKS], "full_decodes": s["full_decodes"],
                                "best_decode_lm": s["best_decode_lm"], "verdict": s["verdict"]}
    vals = sorted(v["feasible"] for v in rep["shuffles"].values())
    best = sorted(v["best_decode_lm"] for v in rep["shuffles"].values() if v["best_decode_lm"] is not None)
    if vals:
        print("F4X shuffles: feasible median", vals[len(vals) // 2], "max", vals[-1], "| best decode lm max",
              best[-1] if best else None, "| CONSISTENT in",
              sum(v["verdict"] == "CONSISTENT" for v in rep["shuffles"].values()), "of", len(vals))
    Path(out).write_text(json.dumps(rep, indent=1) + "\n")


if __name__ == "__main__":
    main()
