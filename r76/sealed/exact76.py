#!/usr/bin/env python3
"""R76 exact checks (CRIB-ASSISTED; on K4 they run ONLY after the blind results are frozen, pushed and verified, and
are reported separately from the blind outcome, labelled as in R70 Erratum 1). For ANY key letters:
  H1X  one stage, keyed alphabets: IDX[CA][c_i] = s*IDX[PA][p_i] + k[i mod m] (mod 26), s = +1/-1, m = 2..52.
       PA, CA from the large alphabet tier (r76/alphabets.py: 77,229 orderings from every 4-15 letter word of the R59 word
       model, three constructions each, plus A-Z). Decided by a hash join: for the published positions that share a key
       slot, the ciphertext-side signature (IDX[CA][c_i] - IDX[CA][c_j]) must equal the plaintext-side signature
       s*(IDX[PA][p_i] - IDX[PA][p_j]). Periods with >= 8 same-slot pairs use the large tier; 5-7 pairs the small tier
       (241 orderings from r75/data/kryptos_words.txt); fewer are skipped. Periods that ledger row L21 already excludes
       for arbitrary per-slot alphabets (m 2-7, 9, 10, 14, 15, 17, 21, 25, 34, 42, 43, 45, 50) are a CONTROL: they must
       give 0 feasible settings.
  H2X  scrambled key, message in place: key slot of position j = p[j] mod m, p a route of r76/routes76.py (all five
       sets, 64,782 routes; identity as a control), m = 2..24, the 32 one-stage conventions of r75/sealed/exact.py.
  H2bX text routed, repeating key: substitute then route (slot q mod m) or route then substitute (slot inv[q] mod m)
       for the published plaintext position q, routes sheet36 + r61 (47), m = 1..24, 32 conventions.
  H6   for H1X and H2X, the key index of the second published string shifted by -2, -1, +1, +2 (a dropped or extra
       letter between the strings, as in K2). Shifted settings are reported as feasibility only (the drop's position is
       unknown, so no decode).
Decodes: H2X/H2bX as r75/sealed/exact.py (pinned slots forced; up to 3 unpinned completed by exhaustive quadgram
search). H1X: pinned slots forced, unpinned slots completed blind by coordinate ascent on quadgrams; the same
completion applied to NULL_FORCED random (PA, CA, s) settings of the same ciphertext and period measures how English
the completion alone can make a text.
Verdict per check: CONSISTENT iff some unshifted full decode clears both cuts (letter model >= -1.45, word model >=
-2.50 per letter) AND, for H1X, also beats every forced null decode at its period; else NO_SOLUTION.
Usage: exact76.py K4 LM TARGET.tsv OUT.json [N_SHUFFLES=10]
       exact76.py --selftest LM BOOK OUT.json"""
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r75"))
sys.path.insert(0, str(ROOT / "r76"))
sys.path.insert(0, str(ROOT / "r75" / "sealed"))
import core  # noqa: E402
from core import IDX, LET, N  # noqa: E402
import alphabets as AL  # noqa: E402
import routes76 as RT  # noqa: E402
from exact import CONV, CUT_LM, CUT_WORD, decode_indexed, kall  # noqa: E402

L21_EXCL = (2, 3, 4, 5, 6, 7, 9, 10, 14, 15, 17, 21, 25, 34, 42, 43, 45, 50)
SHIFTS = (0, -2, -1, 1, 2)
MIN_CHECKS_H2, MIN_CHECKS_H2B, NULL_FORCED, SWEEPS = 5, 3, 50, 3
POSN = np.arange(N)


def tier_arrays(tier):
    idx = np.stack([np.array([a.index(ch) for ch in core.AZ], dtype=np.int16) for _, a in tier])
    let = np.stack([np.array([ord(ch) - 65 for ch in a], dtype=np.int16) for _, a in tier])
    return [n for n, _ in tier], idx, let


def slots_for(pos, m, shift, nfirst):
    s = pos.copy()
    s[nfirst:] = s[nfirst:] + shift
    return s % m


def same_slot_pairs(slots):
    last, pairs = {}, []
    for e, sl in enumerate(slots):
        if sl in last:
            pairs.append((last[sl], e))
        last[sl] = e
    return pairs


# ------------------------------------------------------------------------------------------------ H1X
def complete_periodic(cc, pidx_let, cidx, s, m, key, free, scorer):
    """cc ciphertext codes; plaintext letters = pidx_let[(s * (cidx[cc] - k[i mod m])) % 26] with s = +-1."""
    k = key.copy()
    y = cidx[cc].astype(np.int64)
    sl = POSN % m

    def dec(K):
        return pidx_let[(s * (y[None, :] - K[:, sl])) % 26]
    for _ in range(SWEEPS if free else 0):
        changed = False
        for u in free:
            K = np.tile(k, (26, 1))
            K[:, u] = np.arange(26)
            b = int(np.argmax(scorer.quad_score(dec(K))))
            if b != k[u]:
                k[u], changed = b, True
        if not changed:
            break
    return dec(k[None, :])[0], k


def h1x(c, pos, pk, scorer, tiers, rng, report):
    nfirst = int((np.diff(pos) > 1).nonzero()[0][0]) + 1
    res = {"by_period": {}, "control_violations": [], "feasible": [], "decodes": []}
    for m in range(2, 53):
        for shift in SHIFTS:
            slots = slots_for(pos, m, shift, nfirst)
            pairs = same_slot_pairs(slots.tolist())
            if len(pairs) >= 8:
                tname = "large"
            elif len(pairs) >= 5:
                tname = "small"
            else:
                continue
            names, IDXT, LETT = tiers[tname]
            e1 = np.array([a for a, _ in pairs])
            e2 = np.array([b for _, b in pairs])
            csig = (IDXT[:, c[pos[e1]]].astype(np.int16) - IDXT[:, c[pos[e2]]]) % 26
            table = defaultdict(list)
            for ci, row in enumerate(csig.astype(np.uint8)):
                table[row.tobytes()].append(ci)
            hits = []
            for s in (1, -1):
                psig = (s * (IDXT[:, pk[e1]].astype(np.int16) - IDXT[:, pk[e2]])) % 26
                for pi, row in enumerate(psig.astype(np.uint8)):
                    for ci in table.get(row.tobytes(), ()):
                        hits.append((pi, ci, s))
            res["by_period"].setdefault(m, {})[shift] = {"pairs": len(pairs), "tier": tname, "feasible": len(hits)}
            if shift == 0 and m in L21_EXCL and hits:
                res["control_violations"].append({"m": m, "count": len(hits)})
            for pi, ci, s in hits[:200]:
                res["feasible"].append({"m": m, "shift": shift, "tier": tname, "pa": names[pi], "ca": names[ci],
                                        "s": s, "pairs": len(pairs)})
            if shift != 0 or not hits or scorer is None:
                continue
            pinned = sorted(set(slots.tolist()))
            free = [u for u in range(m) if u not in pinned]
            nulls = []
            for _ in range(NULL_FORCED):
                pi, ci, s = rng.randrange(len(names)), rng.randrange(len(names)), rng.choice((1, -1))
                key = np.zeros(m, dtype=np.int64)
                for e in range(len(pos)):
                    key[slots[e]] = (int(IDXT[ci][c[pos[e]]]) - s * int(IDXT[pi][pk[e]])) % 26
                P, _ = complete_periodic(c, LETT[pi], IDXT[ci], s, m, key, free, scorer)
                nulls.append(core.text(P))
            null_lm = scorer.lm_score(np.stack([core.codes(t) for t in nulls]))
            null_max = float(null_lm.max())
            res["by_period"][m][0]["forced_null_lm_max"] = null_max
            for pi, ci, s in hits[:200]:
                key = np.zeros(m, dtype=np.int64)
                for e in range(len(pos)):
                    key[slots[e]] = (int(IDXT[ci][c[pos[e]]]) - s * int(IDXT[pi][pk[e]])) % 26
                P, k = complete_periodic(c, LETT[pi], IDXT[ci], s, m, key, free, scorer)
                assert (P[pos] == pk).all()
                res["decodes"].append({"m": m, "pa": names[pi], "ca": names[ci], "s": s, "free_slots": len(free),
                                       "key": [int(v) for v in k], "decode": core.text(P), "null_lm_max": null_max})
    return res


# ------------------------------------------------------------------------------------------------ H2X / H2bX
def grouped_feasible(res, K):
    """res (nr, 24) slot per published position; K (32, 24). Returns feasible (32, nr) and checks (nr,)."""
    O = np.argsort(res, axis=1, kind="stable")
    RS = np.take_along_axis(res, O, axis=1)
    same = RS[:, 1:] == RS[:, :-1]
    KO = K[:, O]
    eq = KO[:, :, 1:] == KO[:, :, :-1]
    return ~(same[None] & ~eq).any(axis=2), same.sum(axis=1)


def h2x(c, pos, pk, scorer, routes, col):
    names = ["identity"] + [n for n, _ in routes]
    RA = np.array([list(range(N))] + [list(p) for _, p in routes], dtype=np.int64)
    nfirst = int((np.diff(pos) > 1).nonzero()[0][0]) + 1
    K = kall(c, pos, pk).astype(np.int64)
    out = {"by_period": {}, "identity_control_feasible": 0, "feasible": [], "decodes": []}
    for m in range(2, 25):
        for shift in SHIFTS:
            q = pos.copy()
            q[nfirst:] = np.clip(q[nfirst:] + shift, 0, N - 1)
            res = RA[:, q] % m
            feas, checks = grouped_feasible(res, K)
            ok = feas & (checks >= MIN_CHECKS_H2)[None, :]
            n_ok = int(ok.sum())
            out["by_period"].setdefault(m, {})[shift] = {"settings_with_checks": int((checks >= MIN_CHECKS_H2).sum()) * 32,
                                                          "feasible": n_ok}
            if shift == 0 and ok[:, 0].any():
                out["identity_control_feasible"] += int(ok[:, 0].sum())
            for ci, ri in zip(*np.nonzero(ok)):
                st = {"m": m, "shift": shift, "route": names[ri], "conv": CONV[ci], "checks": int(checks[ri])}
                out["feasible"].append(st)
                if shift == 0 and scorer is not None and len(out["decodes"]) < 2000:
                    idx_all = RA[ri] % m
                    dec, nc = decode_indexed(c, idx_all, idx_all[pos], K[ci], CONV[ci], col)
                    if dec:
                        assert all(dec[int(p)] == chr(65 + int(v)) for p, v in zip(pos, pk))
                        out["decodes"].append({**st, "completed_key_letters": nc, "decode": dec})
    return out


def h2bx(c, pos, pk, scorer, routes, col):
    out = {"by_period": {}, "feasible": [], "decodes": []}
    for rn, p in routes:
        inv = np.argsort(np.array(p))
        c2 = c[inv]
        K = kall(c2, pos, pk).astype(np.int64)
        for order in ("S_then_T", "T_then_S"):
            for m in range(1, 25):
                idx_all = (POSN % m) if order == "S_then_T" else (inv % m)
                res = idx_all[pos][None, :]
                feas, checks = grouped_feasible(res, K)
                key = (order, m)
                d = out["by_period"].setdefault(f"{order}/{m}", {"settings_with_checks": 0, "feasible": 0})
                if checks[0] < MIN_CHECKS_H2B:
                    continue
                d["settings_with_checks"] += 32
                d["feasible"] += int(feas[:, 0].sum())
                for ci in np.nonzero(feas[:, 0])[0]:
                    st = {"route": rn, "order": order, "m": m, "conv": CONV[ci], "checks": int(checks[0])}
                    out["feasible"].append(st)
                    if scorer is not None:
                        dec, nc = decode_indexed(c2, idx_all, res[0], K[ci], CONV[ci], col)
                        if dec:
                            out["decodes"].append({**st, "completed_key_letters": nc, "decode": dec})
                del key
    return out


class _Col:
    def __init__(self, scorer):
        self.scorer = scorer


def finish(part, scorer, null_gate=False):
    dec = part["decodes"]
    if dec and scorer is not None:
        lm = scorer.lm_score(np.stack([core.codes(r["decode"]) for r in dec]))
        for r, v in zip(dec, lm):
            r["lm_per_letter"] = float(v)
        for r in sorted(dec, key=lambda r: -r["lm_per_letter"])[:100]:
            r["word_per_letter"] = scorer.word_score(r["decode"])
    d = sorted([r for r in dec if "lm_per_letter" in r], key=lambda r: -r["lm_per_letter"])
    readable = [r for r in d if r["lm_per_letter"] >= CUT_LM and r.get("word_per_letter", -9) >= CUT_WORD
                and (not null_gate or r["lm_per_letter"] > r["null_lm_max"])]
    part["decodes"] = d[:50]
    part["n_decodes"] = len(d)
    part["n_feasible"] = len(part["feasible"])
    part["feasible"] = part["feasible"][:300]
    part["best_decode_lm"] = d[0]["lm_per_letter"] if d else None
    part["readable"] = readable
    part["verdict"] = "CONSISTENT" if readable else "NO_SOLUTION"
    return part


def run_all(ct, known, scorer, tiers, routes_h2, routes_h2b, which=("H1X", "H2X", "H2bX"), seed=760500):
    c = core.codes(ct)
    pos = np.array(sorted(known))
    pk = np.array([ord(known[int(p)]) - 65 for p in pos], dtype=np.int16)
    col = _Col(scorer)
    out = {}
    if "H1X" in which:
        out["H1X"] = finish(h1x(c, pos, pk, scorer, tiers, random.Random(seed), None), scorer, null_gate=True)
    if "H2X" in which:
        out["H2X"] = finish(h2x(c, pos, pk, scorer, routes_h2, col), scorer)
    if "H2bX" in which:
        out["H2bX"] = finish(h2bx(c, pos, pk, scorer, routes_h2b, col), scorer)
    return out


def load_all():
    tiers = {"large": tier_arrays(AL.large_tier()), "small": tier_arrays(AL.small_tier())}
    routes_h2 = RT.merged(["sheet36", "rot2", "rot1", "colall", "r61"])
    routes_h2b = RT.merged(["sheet36", "r61"])
    return tiers, routes_h2, routes_h2b


def summary_line(name, part):
    return (f"{name} {part['verdict']} | feasible {part['n_feasible']} | decodes {part['n_decodes']} | best decode lm "
            f"{part['best_decode_lm']}")


# ------------------------------------------------------------------------------------------------ self-test
def selftest(lm, book, out):
    sys.path.insert(0, str(ROOT / "r75" / "sealed"))
    from keyshape import POS  # positions only
    scorer = core.Scorer(lm)
    tiers, routes_h2, routes_h2b = load_all()
    words = re.findall(r"[A-Z]+", Path(book).read_text(encoding="utf-8", errors="ignore").upper())
    rng = random.Random(760501)
    rep = defaultdict(list)
    names, IDXT, LETT = tiers["large"]
    plans = ([("H1", m) for m in (8, 12, 16, 20, 22, 38, 40, 44)] + [("H2", None)] * 4 +
             [("H2b", "S_then_T"), ("H2b", "T_then_S")] * 2 + [("RANDOM", None)] * 4)
    for kind, arg in plans:
        i = rng.randrange(len(words) - 60)
        pt = "".join(words[i:i + 60])[:N]
        p = core.codes(pt)
        if kind == "H1":
            m, pi, ci, s = arg, rng.randrange(len(names)), rng.randrange(len(names)), rng.choice((1, -1))
            k = np.array([rng.randrange(26) for _ in range(m)])
            ctc = LETT[ci][(s * IDXT[pi][p].astype(np.int64) + k[POSN % m]) % 26]
            truth, which = {"m": m, "pa": names[pi], "ca": names[ci], "s": s}, ("H1X",)
        elif kind == "H2":
            rn, perm = routes_h2[rng.randrange(len(routes_h2))]
            m, (pa, ca, s) = rng.randint(3, 24), rng.choice(CONV)
            k = np.array([rng.randrange(26) for _ in range(m)])
            ctc = LET[ca][(s * IDX[pa][p].astype(np.int64) + k[np.array(perm) % m]) % 26]
            truth, which = {"route": rn, "m": m}, ("H2X",)
        elif kind == "H2b":
            rn, perm = routes_h2b[rng.randrange(len(routes_h2b))]
            perm = np.array(perm)
            m, (pa, ca, s) = rng.randint(3, 24), rng.choice(CONV)
            k = np.array([rng.randrange(26) for _ in range(m)])
            if arg == "S_then_T":
                X = LET[ca][(s * IDX[pa][p].astype(np.int64) + k[POSN % m]) % 26]
                ctc = X[perm]
            else:
                Y = p[perm]
                ctc = LET[ca][(s * IDX[pa][Y].astype(np.int64) + k[POSN % m]) % 26]
            truth, which = {"route": rn, "order": arg, "m": m}, ("H2bX",)
        else:
            ctc = np.array([rng.randrange(26) for _ in range(N)])
            truth, which = None, ("H1X", "H2X", "H2bX")
        r = run_all(core.text(ctc), {int(q): pt[int(q)] for q in POS}, scorer, tiers, routes_h2, routes_h2b, which)
        row = {"plant": kind, "truth": truth}
        for name, part in r.items():
            row[name] = {"feasible": part["n_feasible"], "readable": len(part["readable"]),
                         "plant_decoded_letters_right": max([sum(a == b for a, b in zip(x["decode"], pt))
                                                             for x in part["readable"]] or [None],
                                                            key=lambda v: -1 if v is None else v),
                         "best_decode_lm": part["best_decode_lm"]}
            if name == "H1X":
                row[name]["control_violations"] = part["control_violations"]
            if name == "H2X":
                row[name]["identity_control_feasible"] = part["identity_control_feasible"]
        rep[kind].append(row)
        print(json.dumps(row), flush=True)
    Path(out).write_text(json.dumps(rep, indent=1) + "\n")


def main():
    if sys.argv[1] == "--selftest":
        return selftest(sys.argv[2], sys.argv[3], sys.argv[4])
    _, lm, tsv, out = sys.argv[1:5]
    nshuf = int(sys.argv[5]) if len(sys.argv) > 5 else 10
    sys.path.insert(0, str(ROOT / "r73" / "sealed"))
    from reveal_k4 import CLUES  # noqa: E402
    known = {o + i: ch for o, t in CLUES for i, ch in enumerate(t)}
    rows = [l.split("\t") for l in Path(tsv).read_text().splitlines()[1:] if l]
    assert rows[0][0] == "K4"
    scorer = core.Scorer(lm)
    tiers, routes_h2, routes_h2b = load_all()
    rep = {"K4": run_all(rows[0][1], known, scorer, tiers, routes_h2, routes_h2b), "shuffles": {}}
    for name, part in rep["K4"].items():
        print(summary_line(name, part))
        for d in part["decodes"][:3]:
            print("    %.3f" % d["lm_per_letter"], d["decode"], json.dumps({k: v for k, v in d.items()
                                                                          if k not in ("decode", "key")}))
    print("H1X control violations (L21-excluded periods):", rep["K4"]["H1X"]["control_violations"])
    print("H2X identity-route control feasible:", rep["K4"]["H2X"]["identity_control_feasible"])
    for rid, ct in rows[1:1 + nshuf]:
        r = run_all(ct, known, scorer, tiers, routes_h2, routes_h2b)
        rep["shuffles"][rid] = {n: {"feasible": p["n_feasible"], "decodes": p["n_decodes"],
                                    "best_decode_lm": p["best_decode_lm"], "verdict": p["verdict"]} for n, p in r.items()}
        print(rid, {n: (v["feasible"], v["verdict"]) for n, v in rep["shuffles"][rid].items()}, flush=True)
    for name in rep["K4"]:
        vals = sorted(v[name]["feasible"] for v in rep["shuffles"].values())
        if vals:
            print(name, "shuffles: feasible median", vals[len(vals) // 2], "max", vals[-1], "| CONSISTENT in",
                  sum(v[name]["verdict"] == "CONSISTENT" for v in rep["shuffles"].values()), "of", len(vals))
    Path(out).write_text(json.dumps(rep, indent=1, default=str) + "\n")


if __name__ == "__main__":
    main()
