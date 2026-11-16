#!/usr/bin/env python3
"""R83a post-freeze audit, task T1 (audit/NEXT_STEPS.md): EXACT one-wrong-plaintext-letter check for PFX and WPX.

POST-FREEZE, CRIB-ASSISTED, EXCLUSION-ONLY. Standard library only. Independent code path: nothing is imported from
r83/exact83.py, r83/models83.py or r75/core.py. Nothing is decrypted, no key is completed, nothing is ranked. Output
is structural settings and counts only; the trial plaintext letter x is never written out.

Model (as r83/models83.py and the R83a question in r83/PREREGISTRATION.md). One tableau stage (pa, ca, s) sends p to
c with  IDX[ca][c] = s*IDX[pa][p] + k (mod 26); the free key absorbs the key-numbering alphabet, so the numeric key a
published position needs is  need(i) = IDX[ca][c_i] - s*IDX[pa][p_i].
  PF  k_i = U[i mod m] + f*IDX[beta][p_(i-L)]  (primer when i < L)
  WP  k_i = U[ptr_i],  ptr_(i+1) = ptr_i + d*(IDX[alpha][p_i] + e)  (mod m)

Semantics of "feasible" (identical to the R83a EXACT step and to the brute force in r83/tests/test_r83.py):
  there exist key letters U (and, for WP, a start pointer for every published run; for PF, a primer) such that every
  published plaintext letter enciphers to the ciphertext letter at its position. Plaintext letters at unpublished
  positions are not constrained. Consequences, stated so nobody over-reads the result:
  * PF: a published position i whose letter i-L is unpublished (or is the primer) gives no equation.
  * WP: the pointer advance across the 29 unpublished letters between the runs is unknown, so the second run's
    pointer offset is free (all m values are tried). This is how the gap is handled.
  This is a RELAXATION of the full cipher (in the real cipher the unpublished letters are fixed by decryption and
  couple the runs). So: infeasible here => infeasible in the real cipher (a sound exclusion); feasible here does NOT
  mean a full 97-letter decryption exists.

One wrong published plaintext letter (the T1 question). For published position b, the true plaintext letter there
is an unknown x in 0..25. The checker substitutes each x and re-runs the full check, so EVERY equation and state the
letter touches is recomputed:
  * PF: the equation at b (its own key) and the equation at b + L (x is its feedback letter);
  * WP: the key at b and the pointer steps after b inside b's run (positions later in that run move by
    d*(IDX[alpha][x] - IDX[alpha][p_b]) mod m); the next run's offset is free anyway.
  drop_excl(b)  = some x != published letter is feasible;  drop_incl(b) = some x, the published letter included.
R83a's DROP statistic counts settings infeasible as they stand but feasible once one letter is set aside, with checks
counted on all 24 letters; this file reports the same statistic as `new_by_checks` / `new_by_eff`.

Usage:
  exact_drop.py --k4 TARGET.tsv OUT.json [N_SHUF=20]    post-freeze audit of K4 and the first N shuffles
  exact_drop.py --random OUT.json [N=20] [SEED]          calibration on random ciphertexts and random letters"""
import json
import random
import sys
from collections import Counter
from itertools import product
from pathlib import Path

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def keyed(word):
    return "".join(dict.fromkeys(word + AZ))


ALPH = {"AZ": AZ, "KRY": keyed("KRYPTOS"), "PAL": keyed("PALIMPSEST"), "ABS": keyed("ABSCISSA")}
A4 = ("AZ", "KRY", "PAL", "ABS")
SIGNS = (1, -1)
IDX = {a: [ALPH[a].index(ch) for ch in AZ] for a in A4}          # IDX[a][letter code] = place in alphabet a
CONV1 = [(pa, ca, s) for pa in A4 for ca in A4 for s in SIGNS]    # 32 one-stage conventions
PF_CONV = [(cv, beta, f) for cv in CONV1 for beta in A4 for f in SIGNS]   # 256
MIN_CHECKS = 3


def popcount(x):
    return bin(x).count("1")


def runs(pos):
    """Maximal runs of consecutive positions (pos sorted ascending), as lists of indices into pos."""
    out = []
    for e, p in enumerate(pos):
        if out and p == pos[out[-1][-1]] + 1:
            out[-1].append(e)
        else:
            out.append([e])
    return out


class Buckets:
    """bucket(key)[v] = bitmask of conventions whose required value at a position equals v. Equality of two
    positions' required values, per convention, is then OR_v (bucket_a[v] & bucket_b[v])."""

    def __init__(self, value_fn, nconv):
        self.fn, self.nconv, self.cache, self.pairs = value_fn, nconv, {}, {}

    def bucket(self, key):
        b = self.cache.get(key)
        if b is None:
            b = [0] * 26
            for bit in range(self.nconv):
                b[self.fn(key, bit)] |= 1 << bit
            self.cache[key] = b
        return b

    def eq(self, ka, kb):
        k = (ka, kb)
        r = self.pairs.get(k)
        if r is None:
            ba, bb = self.bucket(ka), self.bucket(kb)
            r = 0
            for v in range(26):
                r |= ba[v] & bb[v]
            self.pairs[k] = r
        return r


def chain_mask(groups, B, full):
    """AND of pairwise equalities inside each group (consecutive members suffice: equality is transitive)."""
    m = full
    for g in groups:
        for a, b in zip(g, g[1:]):
            m &= B.eq(a, b)
            if not m:
                return 0
    return m


# ------------------------------------------------------------------------------------------------ WPX
def wp_value(c):
    def fn(key, bit):
        i, p = key
        pa, ca, s = CONV1[bit]
        return (IDX[ca][c[i]] - s * IDX[pa][p]) % 26
    return fn


def wpx_mask(pos, letters, alpha, e, d, m, B, R):
    """32-bit mask of conventions feasible for (alpha, e, d, m) with these published letters (all taken as true)."""
    full = (1 << 32) - 1
    rel = [0] * len(pos)
    for run in R:
        r = 0
        for e_ in run:
            rel[e_] = r % m
            r += d * (IDX[alpha][letters[e_]] + e)
    keys = [(pos[k], letters[k]) for k in range(len(pos))]
    # within-run groups
    per_run = []
    groups = []
    for run in R:
        g = {}
        for k in run:
            g.setdefault(rel[k], []).append(keys[k])
        per_run.append(g)
        groups.extend(g.values())
    mask = chain_mask(groups, B, full)
    if not mask or len(R) == 1:
        return mask
    out = 0
    first = per_run[0]
    for offs in product(range(m), repeat=len(R) - 1):
        # residue -> representatives, one per run
        reps = {r: [g[0]] for r, g in first.items()}
        for o, g in zip(offs, per_run[1:]):
            for r, members in g.items():
                reps.setdefault((r + o) % m, []).append(members[0])
        mk = chain_mask([v for v in reps.values() if len(v) > 1], B, mask)
        out |= mk
        if out == mask:
            break
    return out


def wpx_checks(pos, letters, alpha, e, d, m, R):
    """R83a's label: min over the free run offsets of (published positions - distinct pointer residues)."""
    rel = [0] * len(pos)
    for run in R:
        r = 0
        for e_ in run:
            rel[e_] = r % m
            r += d * (IDX[alpha][letters[e_]] + e)
    best = None
    base = [set(rel[k] for k in run) for run in R]
    for offs in product(range(m), repeat=len(R) - 1):
        s = set(base[0])
        for o, b in zip(offs, base[1:]):
            s |= {(r + o) % m for r in b}
        ck = len(pos) - len(s)
        best = ck if best is None else min(best, ck)
    return best


def wpx_scan(c, pos, pk, mrange=range(2, 27), drop=True):
    """Every WPX setting: exact mask, per-position drop masks (x != published and x any)."""
    R = runs(pos)
    B = Buckets(wp_value(c), 32)
    rows = []
    for alpha in A4:
        for e in (0, 1):
            for d in SIGNS:
                for m in mrange:
                    ex = wpx_mask(pos, pk, alpha, e, d, m, B, R)
                    ck = wpx_checks(pos, pk, alpha, e, d, m, R)
                    dx = []
                    if drop:
                        for b in range(len(pos)):
                            acc = 0
                            for x in range(26):
                                if x == pk[b]:
                                    continue
                                alt = list(pk)
                                alt[b] = x
                                acc |= wpx_mask(pos, alt, alpha, e, d, m, B, R)
                            dx.append(acc)
                    rows.append({"alpha": alpha, "e": e, "d": d, "m": m, "checks": ck, "eff": ck,
                                 "exact": ex, "drop_excl": dx})
    return rows


# ------------------------------------------------------------------------------------------------ PFX
def pf_value(c):
    def fn(key, bit):
        i, p, q = key
        (pa, ca, s), beta, f = PF_CONV[bit]
        return (IDX[ca][c[i]] - s * IDX[pa][p] - f * IDX[beta][q]) % 26
    return fn


def pfx_constrained(pos, L):
    at = {p: k for k, p in enumerate(pos)}
    return [(k, at[p - L]) for k, p in enumerate(pos) if p - L in at]


def pfx_mask(pos, letters, L, m, B, cons):
    full = (1 << 256) - 1
    g = {}
    for k, kp in cons:
        g.setdefault(pos[k] % m, []).append((pos[k], letters[k], letters[kp]))
    return chain_mask(g.values(), B, full)


def pfx_scan(c, pos, pk, lrange=range(1, 13), mrange=range(1, 27), drop=True):
    B = Buckets(pf_value(c), 256)
    rows = []
    for L in lrange:
        cons = pfx_constrained(pos, L)
        if not cons:
            continue
        touched = set(k for k, _ in cons) | set(kp for _, kp in cons)
        for m in mrange:
            ck = len(cons) - len({pos[k] % m for k, _ in cons})
            ex = pfx_mask(pos, pk, L, m, B, cons)
            dx = []
            if drop:
                for b in range(len(pos)):
                    if b not in touched:
                        dx.append(ex)         # x enters no equation: every x is as feasible as the published letter
                        continue
                    acc = 0
                    for x in range(26):
                        if x == pk[b]:
                            continue
                        alt = list(pk)
                        alt[b] = x
                        acc |= pfx_mask(pos, alt, L, m, B, cons)
                    dx.append(acc)
            rows.append({"L": L, "m": m, "checks": ck, "eff": ck, "exact": ex, "drop_excl": dx})
    return rows


# ------------------------------------------------------------------------------------------------ setting queries
def wpx_setting(c, pos, pk, conv, alpha, e, d, m):
    """(exact, drop_excl per position) for exactly one WPX setting."""
    rows = wpx_scan(c, pos, pk, mrange=[m], drop=True)
    bit = 1 << CONV1.index(tuple(conv))
    r = [r for r in rows if r["alpha"] == alpha and r["e"] == e and r["d"] == d][0]
    return bool(r["exact"] & bit), [bool(v & bit) for v in r["drop_excl"]]


def pfx_setting(c, pos, pk, conv, beta, f, L, m):
    bit = 1 << PF_CONV.index((tuple(conv), beta, f))
    rows = pfx_scan(c, pos, pk, lrange=[L], mrange=[m], drop=True)
    if not rows:                       # no equation at all: trivially feasible
        return True, [True] * len(pos)
    r = rows[0]
    return bool(r["exact"] & bit), [bool(v & bit) for v in r["drop_excl"]]


# ------------------------------------------------------------------------------------------------ summaries
def describe(fam, row, bit):
    if fam == "WPX":
        pa, ca, s = CONV1[bit]
        return {"conv": [pa, ca, s], "alpha": row["alpha"], "e": row["e"], "d": row["d"], "m": row["m"]}
    (pa, ca, s), beta, f = PF_CONV[bit]
    return {"conv": [pa, ca, s], "beta": beta, "f": f, "L": row["L"], "m": row["m"]}


def bits(x):
    out, k = [], 0
    while x:
        if x & 1:
            out.append(k)
        x >>= 1
        k += 1
    return out


def summarize(fam, rows, pos, nconv, cap=400):
    tested, exact, new_ck, new_eff, incl_ck = Counter(), Counter(), Counter(), Counter(), Counter()
    by_pos_excl, by_pos_incl, by_pos_new = Counter(), Counter(), Counter()
    listing = []
    for r in rows:
        tested[r["checks"]] += nconv
        exact[r["checks"]] += popcount(r["exact"])
        anyd = 0
        for b, v in enumerate(r["drop_excl"]):
            anyd |= v
            by_pos_excl[pos[b]] += popcount(v)
            by_pos_incl[pos[b]] += popcount(v | r["exact"])
            by_pos_new[pos[b]] += popcount(v & ~r["exact"])
        new = anyd & ~r["exact"]
        new_ck[r["checks"]] += popcount(new)
        new_eff[r["eff"]] += popcount(new)
        incl_ck[r["checks"]] += popcount(anyd | r["exact"])
        if r["checks"] >= MIN_CHECKS:
            for bit in bits(anyd | r["exact"]):
                if len(listing) < cap:
                    listing.append({**describe(fam, r, bit), "checks": r["checks"], "eff": r["eff"],
                                    "exact_feasible": bool(r["exact"] >> bit & 1),
                                    "freed_by": [pos[b] for b, v in enumerate(r["drop_excl"]) if v >> bit & 1]})
    ge = lambda d: sum(v for k, v in d.items() if k >= MIN_CHECKS)  # noqa: E731
    return {"tested_by_checks": dict(sorted(tested.items())),
            "exact_feasible_by_checks": dict(sorted(exact.items())),
            "new_by_checks": dict(sorted(new_ck.items())),
            "new_by_eff": dict(sorted(new_eff.items())),
            "drop_incl_by_checks": dict(sorted(incl_ck.items())),
            "settings_ge3": ge(tested), "exact_ge3": ge(exact), "new_ge3": ge(new_ck), "drop_incl_ge3": ge(incl_ck),
            "drop_excl_by_position": {int(k): v for k, v in sorted(by_pos_excl.items())},
            "drop_incl_by_position": {int(k): v for k, v in sorted(by_pos_incl.items())},
            "new_by_position": {int(k): v for k, v in sorted(by_pos_new.items())},
            "settings_ge3_list": listing, "list_capped": len(listing) >= cap}


def wpx_union_settings(rows):
    """Distinct WPX structural settings (conv, alpha, e, d, m) feasible with some one published letter unknown
    (x != published), at any checks: the set comparable with the conservative 260."""
    out = set()
    for r in rows:
        anyd = 0
        for v in r["drop_excl"]:
            anyd |= v
        for bit in bits(anyd):
            pa, ca, s = CONV1[bit]
            out.add(((pa, ca, s), r["alpha"], r["e"], r["d"], r["m"]))
    return out


def audit_one(c, pos, pk):
    w = wpx_scan(c, pos, pk)
    p = pfx_scan(c, pos, pk)
    return {"WPX": summarize("WPX", w, pos, 32), "PFX": summarize("PFX", p, pos, 256)}, w


def verdicts(res):
    """R83a's rule unchanged (r83/verdict83.py) on the drop statistic `new`."""
    out = {}
    k4 = res["K4"]
    sh = [v for k, v in res.items() if k != "K4"]
    for fam in ("WPX", "PFX"):
        kn = k4[fam]["new_ge3"]
        row = {"k4_new_ge3": kn, "shuffles_new_ge3": [s[fam]["new_ge3"] for s in sh], "shuffles": len(sh)}
        if kn == 0:
            row["verdict"] = "EXCL"
        else:
            sems = [{int(a): b for a, b in s[fam]["new_by_eff"].items()} for s in sh]
            leads = [r for r in k4[fam]["settings_ge3_list"] if not r["exact_feasible"] and r["eff"] >= MIN_CHECKS
                     and max(sum(v for a, v in se.items() if a >= r["eff"]) for se in sems) == 0]
            row["verdict"] = "LEAD" if leads else "CHANCE"
            row["leads"] = leads
            row["k4_new_by_eff"] = k4[fam]["new_by_eff"]
        out[fam] = row
    return out


def k4_main(tsv, out, nshuf=20):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "r73" / "sealed"))
    from reveal_k4 import CLUES  # noqa: E402  -- post-freeze audit only
    rows = [l.split("\t") for l in Path(tsv).read_text().splitlines()[1:] if l]
    assert rows[0][0] == "K4"
    pos = [o + j for o, t in CLUES for j in range(len(t))]
    pk = [ord(ch) - 65 for _, t in CLUES for ch in t]
    assert pos == list(range(21, 34)) + list(range(63, 74))
    res, union = {}, {}
    for rid, ct in rows[:1 + nshuf]:
        c = [ord(ch) - 65 for ch in ct]
        assert len(c) == 97
        res[rid], w = audit_one(c, pos, pk)
        union[rid] = sorted([list(s[0]), s[1], s[2], s[3], s[4]] for s in wpx_union_settings(w))
        print(rid, "WPX new>=3", res[rid]["WPX"]["new_ge3"], "PFX new>=3", res[rid]["PFX"]["new_ge3"],
              "WPX union", len(union[rid]), flush=True)
    rep = {"classification": "POST-FREEZE CRIB-ASSISTED EXCLUSION-ONLY AUDIT (T1); no decryption, no key, no ranking",
           "semantics": __doc__.split("Usage:")[0],
           "target": str(tsv), "ids": list(res), "results": res,
           "WPX_drop_excl_union_settings": union,
           "verdicts_r83_rule": verdicts(res)}
    Path(out).write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps(rep["verdicts_r83_rule"], indent=1)[:3000])


def random_main(out, n=20, seed=830777):
    """Calibration: random ciphertexts AND random published letters at K4's published positions."""
    rng = random.Random(seed)
    pos = list(range(21, 34)) + list(range(63, 74))
    res = {}
    for k in range(n):
        c = [rng.randrange(26) for _ in range(97)]
        pk = [rng.randrange(26) for _ in pos]
        r, w = audit_one(c, pos, pk)
        res[f"RAND_{k:03d}"] = {f: {key: r[f][key] for key in ("settings_ge3", "exact_ge3", "new_ge3", "drop_incl_ge3",
                                                              "new_by_checks", "exact_feasible_by_checks")}
                                for f in r}
        res[f"RAND_{k:03d}"]["WPX_union"] = len(wpx_union_settings(w))
        print(k, {f: (res[f"RAND_{k:03d}"][f]["exact_ge3"], res[f"RAND_{k:03d}"][f]["new_ge3"]) for f in r}, flush=True)
    Path(out).write_text(json.dumps({"seed": seed, "n": n, "results": res}, indent=1) + "\n")


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "--k4":
        k4_main(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 20)
    elif len(sys.argv) >= 3 and sys.argv[1] == "--random":
        random_main(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 20,
                    int(sys.argv[4]) if len(sys.argv) > 4 else 830777)
    else:
        raise SystemExit(__doc__)
