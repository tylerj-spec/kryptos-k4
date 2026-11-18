#!/usr/bin/env python3
"""T6 item 2 (audit/NEXT_STEPS.md): independent replay of the crib-assisted exact checks of R79 (L169) and R81a
(L170) for their KEYWORD families. POST-FREEZE, CRIB-ASSISTED, EXCLUSION-ONLY. Standard library only; nothing is
imported from r79/ or r81a/. Every slot rule, stream and setting list is re-derived from the definitions in
r79/PREREGISTRATION.md, r81a/PREREGISTRATION.md and the families' docstrings. Nothing is decrypted, no keyword is
completed, nothing is ranked: output is counts and settings.

Model (both rounds): one tableau stage in place, IDX[ca][c'] = s*IDX[pa][p'] + t*(IDX[ka][W[slot(i)]] + S(i)),
(s, t) = VIG (1,1), BEAU (-1,1), VARB (1,-1); W a keyword of m letters (any letters); p' = p and c' = c except in
PROG (progressive mask a*i + b on alphabet A1, on the plaintext first ("inner") or the ciphertext last ("outer")).
At a published position the keyword value it needs is w_i = t*(y_i - s*x_i) - S(i) (mod 26). A setting is FEASIBLE
iff all published positions on one slot need the same w. checks = 24 - distinct slots read. DROP-ONE (R81a G6):
infeasible as it stands but feasible once one position is set aside (every conflicting pair contains it). In these
families no state depends on the plaintext (r81a/audit/DROP_ONE_REVIEW.md), so set-aside is exact for one wrong
plaintext letter.

Families and scope:
  R79   H7CT   slot i mod m, S = IDX[ka][c_(i-L)] (0 before L), L 1..48, CONV24, m 1..12
        H7TXT  slot i mod m, S = IDX[ka][T(o + d*i)], T = K1-K3 plaintext (first K3 copy) or K1-K3 CIA ciphertext,
               every offset, d +-1, CONV24, m 1..12
        LIB    982 slot rules (REP HELD TRIG WK REV OMIT IKN CNT CLS); stream none (CONV8) or feedback lag 1..7
               (CONV24, rules other than REP)
        PROG   pa, ca in AZ/KRY, VIG/BEAU, A1 in four alphabets (A1 != pa inner, != ca outer), a 1..25, b 0..25, m 1..12
  R81a  H7CT_A, LIB_A, PROG_A: the same on the conventions R79 did not run (PAL/ABS on the plaintext or ciphertext
        side); LIB_G4: ROT, ALT (stream none or lag 1..7), RESTART, SPLIT (stream none), every convention.
Usage: replay_kw.py TARGET.tsv OUT.json N_SHUF [FAMILIES...]"""
import json
import re
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
N, MKEY = 97, 12


def keyed(w):
    return "".join(dict.fromkeys(w + AZ))


ALPH = {"AZ": AZ, "KRY": keyed("KRYPTOS"), "PAL": keyed("PALIMPSEST"), "ABS": keyed("ABSCISSA")}
IDX = {a: {ch: k for k, ch in enumerate(s)} for a, s in ALPH.items()}
A2, A4 = ("AZ", "KRY"), ("AZ", "KRY", "PAL", "ABS")
OPS = {"VIG": (1, 1), "BEAU": (-1, 1), "VARB": (1, -1)}
CONV24 = [(pa, ca, ka, op) for pa in A2 for ca in A2 for ka in A2 for op in OPS]
CONV8 = [(pa, ca, "AZ", op) for pa in A2 for ca in A2 for op in ("VIG", "BEAU")]
CONVK = [(pa, ca, ka, op) for pa in A4 for ca in A4 for ka in A2 for op in OPS]
CONV32 = [(pa, ca, "AZ", op) for pa in A4 for ca in A4 for op in ("VIG", "BEAU")]
NEWK = [c for c in CONVK if c not in CONV24]
NEW32 = [c for c in CONV32 if c not in CONV8]
PROG79 = [(pa, ca, op) for pa in A2 for ca in A2 for op in ("VIG", "BEAU")]
PROG81 = [(pa, ca, op) for pa in A4 for ca in A4 for op in ("VIG", "BEAU") if {"PAL", "ABS"} & {pa, ca}]
TRIG_SETS = {**{ch: ch for ch in AZ}, "KRYPTOS": "KRYPTOS", "PALIMPSEST": "PALIMPSEST", "ABSCISSA": "ABSCISSA"}
CLASS = {"AZH": (2, lambda ch: AZ.index(ch) // 13), "KRYH": (2, lambda ch: ALPH["KRY"].index(ch) // 13),
         "AZT": (3, lambda ch: AZ.index(ch) // 9), "KRYT": (3, lambda ch: ALPH["KRY"].index(ch) // 9),
         "INKRY": (2, lambda ch: int(ch in "KRYPTOS")), "INPAL": (2, lambda ch: int(ch in "PALIMPSEST")),
         "INABS": (2, lambda ch: int(ch in "ABSCISSA")), "VOW": (2, lambda ch: int(ch in "AEIOU"))}


# ------------------------------------------------------------------------------------------------ fixed inputs
def kryptos_words():
    out = []
    for line in (ROOT / "r75/data/kryptos_words.txt").read_text().splitlines():
        if not line.startswith("#"):
            out += line.split()
    return out


def k13_texts():
    """K1-K3 plaintext as carved up to the second copy of K3 (769 letters); K1-K3 CIA ciphertext without K4 (768)."""
    t = "".join(ch for ch in (ROOT / "k4kit/data/k1k3_plaintext.txt").read_text().upper() if "A" <= ch <= "Z")
    k = "SLOWLYDESPARATLY"
    pt = t[:t.index(k, t.index(k) + 1)]
    src = (ROOT / "archive/2026-10-26_allinone_extras/source_key_extensions/r27_sources.py").read_text()
    raw = "".join(ch for ch in re.search(r"CIA_CIPHER='''(.*?)'''", src, re.S).group(1) if ch in AZ)
    return {"K13PT": pt, "K13CT": raw[:-N]}


def text_streams():
    out = []
    for name, T in k13_texts().items():
        for d in (1, -1):
            offs = range(len(T) - N + 1) if d == 1 else range(N - 1, len(T))
            for o in offs:
                out.append(((name, d, o), [T[o + d * i] for i in range(N)]))
    return out


# ------------------------------------------------------------------------------------------------ slot rules
def rank_digits(w):
    order = sorted(range(len(w)), key=lambda k: (w[k], k))
    r = [0] * len(w)
    for rk, k in enumerate(order):
        r[k] = rk + 1
    return r


def lib_defs():
    """R79's 982 slot rules: (rule, params, m)."""
    d = [("REP", (), m) for m in range(1, MKEY + 1)]
    d += [("HELD", (h,), m) for h in (2, 3, 4) for m in range(2, MKEY + 1)]
    d += [("TRIG", (T,), m) for T in AZ for m in range(2, MKEY + 1)]
    d += [("WK", (a, e, dd), m) for a in A4 for e in (0, 1) for dd in (1, -1) for m in range(2, MKEY + 1)]
    d += [("REV", (T,), m) for T in TRIG_SETS for m in range(2, MKEY + 1)]
    d += [("OMIT", (v,), m) for v in ("skip", "shrink") for m in range(2, MKEY + 1)]
    d += [("IKN", (w,), len(w)) for w in kryptos_words() if 2 <= len(w) <= MKEY]
    d += [("CNT", (), m) for m in range(2, MKEY + 1)]
    for g, (nc, _) in CLASS.items():
        d.append(("CLS", (g, 0), nc))
        d += [("CLS", (g, m1), m1 * nc) for m1 in range(2, MKEY // nc + 1)]
    return d


def g4_defs():
    """R81a's new rules: (rule, params, m, stream allowed)."""
    d = [("ROT", (dd,), m, True) for m in range(2, MKEY + 1) for dd in range(1, m)]
    d += [("ALT", (m1, s - m1), s, True) for s in range(4, MKEY + 1) for m1 in range(2, s - 1)]
    d += [("RESTART", (c,), m, False) for c in range(10, 88) for m in range(2, MKEY + 1)]
    d += [("SPLIT", (c, m1), m1 + m2, False) for c in range(10, 88) for m1 in range(2, 7) for m2 in range(2, 7)]
    return d


def slots(rule, par, m, ct):
    """Slot read at every position (rules may read EARLIER ciphertext letters, never plaintext)."""
    if rule == "REP":
        return [i % m for i in range(N)]
    if rule == "HELD":
        return [(i // par[0]) % m for i in range(N)]
    if rule == "OMIT":
        out, j = [], 0
        while len(out) < N:
            out += [k for k in range(m) if k != j % m] if par[0] == "skip" else list(range(j % m, m))
            j += 1
        return out[:N]
    if rule == "IKN":
        dig, out, j = rank_digits(par[0]), [], 0
        while len(out) < N:
            out += list(range(dig[j % len(dig)]))
            j += 1
        return out[:N]
    if rule in ("TRIG", "WK", "REV"):
        out, ptr, dr = [], 0, 1
        for ch in ct:
            out.append(ptr)
            if rule == "TRIG":
                ptr = 0 if ch == par[0] else (ptr + 1) % m
            elif rule == "WK":
                a, e, dd = par
                ptr = (ptr + dd * (IDX[a][ch] + e)) % m
            else:
                if ch in TRIG_SETS[par[0]]:
                    dr = -dr
                ptr = (ptr + dr) % m
        return out
    if rule == "CNT":
        seen, out = {}, [0]
        for i in range(1, N):
            seen[ct[i - 1]] = seen.get(ct[i - 1], 0) + 1
            out.append((seen[ct[i - 1]] - 1) % m)
        return out
    if rule == "CLS":
        g, m1 = par
        nc, f = CLASS[g]
        return [0] + [((i % m1) * nc if m1 else 0) + f(ct[i - 1]) for i in range(1, N)]
    if rule == "ROT":
        return [(i + par[0] * (i // m)) % m for i in range(N)]
    if rule == "ALT":
        m1, m2 = par
        return [(i // 2) % m1 if i % 2 == 0 else m1 + (i // 2) % m2 for i in range(N)]
    if rule == "RESTART":
        c = par[0]
        return [i % m if i < c else (i - c) % m for i in range(N)]
    if rule == "SPLIT":
        c, m1 = par
        return [i % m1 if i < c else m1 + (i - c) % (m - m1) for i in range(N)]
    raise ValueError(rule)


# ------------------------------------------------------------------------------------------------ the check
def needed(ct, pos, pk, pa, ca, ka, op, stream, inner=None, outer=None):
    """w_i at every published position. stream: list of 97 numbers (S(i)) or None. inner/outer: (A1, a, b)."""
    s, t = OPS[op]
    out = []
    for i, p in zip(pos, pk):
        if inner:
            A1, a, b = inner
            p = ALPH[A1][(IDX[A1][p] + a * i + b) % 26]
        c = ct[i]
        if outer:
            A1, a, b = outer
            c = ALPH[A1][(IDX[A1][c] - a * i - b) % 26]
        S = stream[i] if stream else 0
        out.append((t * (IDX[ca][c] - s * IDX[pa][p]) - S) % 26)
    return out


def judge(w, sl):
    """(feasible, checks, drop_one positions): slot values must agree; drop-one by conflict containment."""
    groups = {}
    for k, r in enumerate(sl):
        groups.setdefault(r, []).append(k)
    conflicts = []
    for ks in groups.values():
        for x in range(len(ks)):
            for y in range(x + 1, len(ks)):
                if w[ks[x]] != w[ks[y]]:
                    conflicts.append((ks[x], ks[y]))
    checks = len(sl) - len(groups)
    if not conflicts:
        return True, checks, ()
    common = set(conflicts[0])
    for c in conflicts[1:]:
        common &= set(c)
        if not common:
            break
    return False, checks, tuple(sorted(common))


def ct_stream(ct, ka, L):
    return [IDX[ka][ct[i - L]] if i >= L else 0 for i in range(N)]


def run_family(fam, ct, pos, pk, tally):
    rep_slots = {m: [p % m for p in pos] for m in range(1, MKEY + 1)}

    def take(label, w, sl):
        ok, ck, drop = judge(w, sl)
        tally["tested"][ck] += 1
        tally["min_checks"] = min(tally["min_checks"], ck)
        if ok:
            tally["feasible"][ck] += 1
            if len(tally["feasible_list"]) < 200:
                tally["feasible_list"].append([*label, ck])
        elif drop:
            tally["drop"][ck] += 1
            for k in drop:
                tally["drop_pos"][pos[k]] += 1
            if len(tally["drop_list"]) < 200:
                tally["drop_list"].append([*label, ck, [pos[k] for k in drop]])

    if fam in ("H7CT", "H7CT_A"):
        for conv in (CONV24 if fam == "H7CT" else NEWK):
            for L in range(1, 49):
                w = needed(ct, pos, pk, *conv, ct_stream(ct, conv[2], L))
                for m in range(1, MKEY + 1):
                    take([list(conv), L, m], w, rep_slots[m])
    elif fam == "H7TXT":
        streams = text_streams()
        for conv in CONV24:
            for name, T in streams:
                S = [IDX[conv[2]][ch] for ch in T]
                w = needed(ct, pos, pk, *conv, S)
                for m in range(1, MKEY + 1):
                    take([list(conv), list(name), m], w, rep_slots[m])
    elif fam in ("LIB", "LIB_A", "LIB_G4"):
        if fam == "LIB_G4":
            defs = g4_defs()
            convs = {0: CONV32, **{L: CONVK for L in range(1, 8)}}
        else:
            defs = [(r, p, m, r != "REP") for r, p, m in lib_defs()]
            convs = {0: CONV8, **{L: CONV24 for L in range(1, 8)}} if fam == "LIB" else \
                {0: NEW32, **{L: NEWK for L in range(1, 8)}}
        sl = [[s_[p] for p in pos] for s_ in (slots(r, p, m, ct) for r, p, m, _ in defs)]
        for L in range(0, 8):
            for conv in convs[L]:
                w = needed(ct, pos, pk, *conv, ct_stream(ct, conv[2], L) if L else None)
                for k, (r, p, m, ok) in enumerate(defs):
                    if L and not ok:
                        continue
                    take([r, list(p), m, L, list(conv)], w, sl[k])
    elif fam in ("PROG", "PROG_A"):
        for pa, ca, op in (PROG79 if fam == "PROG" else PROG81):
            for where in ("inner", "outer"):
                for A1 in A4:
                    if A1 == (pa if where == "inner" else ca):
                        continue
                    for a in range(1, 26):
                        for b in range(26):
                            key = (A1, a, b)
                            w = needed(ct, pos, pk, pa, ca, "AZ", op, None,
                                       inner=key if where == "inner" else None,
                                       outer=key if where == "outer" else None)
                            for m in range(1, MKEY + 1):
                                take([where, pa, ca, op, A1, a, b, m], w, rep_slots[m])
    else:
        raise ValueError(fam)


ROUND = {"R79": ("H7CT", "H7TXT", "LIB", "PROG"), "R81a": ("H7CT_A", "LIB_A", "LIB_G4", "PROG_A")}


def one(args):
    rid, ct, fam, pos, pk = args
    tally = {"tested": Counter(), "feasible": Counter(), "drop": Counter(), "drop_pos": Counter(), "min_checks": 99,
             "feasible_list": [], "drop_list": []}
    run_family(fam, ct, pos, pk, tally)
    return rid, fam, {"settings": sum(tally["tested"].values()), "min_checks": tally["min_checks"],
                      "tested_by_checks": dict(sorted(tally["tested"].items())),
                      "feasible_by_checks": dict(sorted(tally["feasible"].items())),
                      "drop_one_by_checks": dict(sorted(tally["drop"].items())),
                      "drop_one_by_position": dict(sorted(tally["drop_pos"].items())),
                      "feasible_list": tally["feasible_list"], "drop_list": tally["drop_list"]}


def main():
    sys.path.insert(0, str(ROOT / "r73" / "sealed"))
    from reveal_k4 import CLUES  # noqa: E402  -- post-freeze audit only
    pos = [o + j for o, t in CLUES for j in range(len(t))]
    pk = [ch for _, t in CLUES for ch in t]
    tsv, out, nshuf = sys.argv[1], sys.argv[2], int(sys.argv[3])
    fams = sys.argv[4:]
    rows = [l.split("\t") for l in Path(tsv).read_text().splitlines()[1:] if l][:1 + nshuf]
    assert rows[0][0] == "K4"
    jobs = [(rid, ct, fam, pos, pk) for rid, ct in rows for fam in fams]
    res = {}
    with Pool(4) as pool:
        for rid, fam, r in pool.imap_unordered(one, jobs):
            res.setdefault(rid, {})[fam] = r
            print(rid, fam, r["settings"], "min checks", r["min_checks"], "feasible",
                  sum(r["feasible_by_checks"].values()), "drop-one", sum(r["drop_one_by_checks"].values()), flush=True)
    Path(out).write_text(json.dumps({"classification": "POST-FREEZE CRIB-ASSISTED EXCLUSION-ONLY REPLAY (T6 item 2)",
                                     "target": tsv, "families": fams,
                                     "results": {r: res[r] for r, _ in rows}}, indent=1) + "\n")


if __name__ == "__main__":
    main()
