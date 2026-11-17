#!/usr/bin/env python3
"""L172 follow-up to the WPX strength erratum (PR #90, r83/audit/WPX_STRENGTH_ERRATUM.md): a CORRECTED strength statistic
for WPX with one wrong published plaintext letter, run identically on K4 and the 20 R83 shuffles.
POST-FREEZE, CRIB-ASSISTED, EXCLUSION-ONLY. Plan fixed before running: r83/audit/WPX_STRENGTH_PLAN.md.
Nothing is decrypted; no trial letter, offset, key or plaintext is written out: only settings and counts.

Witness: (b, x, o) = published position b whose letter is replaced by x != the published letter, and a pointer
offset o of the second run, such that the setting is feasible (r83/audit/exact_drop.py semantics). Its strength
  c(b, x, o) = 24 - (number of distinct pointer residues of the 24 published positions under the ALTERED letters and
  offset o) = the number of independent key equalities that witness actually satisfies.
Setting statistic s = max of c over its feasible witnesses (and s_min, reported). Only settings infeasible with all 24
letters are counted ("new", as R83a/T1). The trial letter is a free parameter; its effect is calibrated by running the
identical scan on the shuffles, never by a formula.
Usage: wpx_drop_strength.py TARGET.tsv OUT.json [N_SHUF=20]"""
import json
import sys
from collections import Counter
from itertools import product
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exact_drop as ED  # noqa: E402  (T1's checker; its feasibility is validated by r83/audit/tests)

ROOT = Path(__file__).resolve().parents[2]


def residues(pos, letters, alpha, e, d, m, R, offs):
    rel = [0] * len(pos)
    for q, run in enumerate(R):
        r = 0 if q == 0 else offs[q - 1]
        for k in run:
            rel[k] = r % m
            r += d * (ED.IDX[alpha][letters[k]] + e)
    return rel


def witness_masks(pos, letters, alpha, e, d, m, B, R):
    """[(conv mask feasible at this offset, c)] for every offset tuple."""
    out = []
    full = (1 << 32) - 1
    for offs in product(range(m), repeat=len(R) - 1):
        rel = residues(pos, letters, alpha, e, d, m, R, offs)
        g = {}
        for k in range(len(pos)):
            g.setdefault(rel[k], []).append((pos[k], letters[k]))
        mk = ED.chain_mask(g.values(), B, full)
        if mk:
            out.append((mk, len(pos) - len(g)))
    return out


def scan(c, pos, pk):
    R = ED.runs(pos)
    B = ED.Buckets(ED.wp_value(c), 32)
    smax, smin = {}, {}
    for alpha in ED.A4:
        for e in (0, 1):
            for d in ED.SIGNS:
                for m in range(2, 27):
                    exact = ED.wpx_mask(pos, pk, alpha, e, d, m, B, R)
                    for b in range(len(pos)):
                        for x in range(26):
                            if x == pk[b]:
                                continue
                            alt = list(pk)
                            alt[b] = x
                            for mk, cc in witness_masks(pos, alt, alpha, e, d, m, B, R):
                                for bit in ED.bits(mk & ~exact):
                                    key = (ED.CONV1[bit], alpha, e, d, m)
                                    smax[key] = max(smax.get(key, -99), cc)
                                    smin[key] = min(smin.get(key, 99), cc)
    return smax, smin


def one(args):
    rid, ct, pos, pk = args
    smax, smin = scan([ord(ch) - 65 for ch in ct], pos, pk)
    return rid, {"settings_with_witness": len(smax),
                 "by_s_max": dict(sorted(Counter(smax.values()).items())),
                 "max_s": max(smax.values()) if smax else None,
                 "settings": sorted([[list(k[0]), *k[1:], smax[k], smin[k]] for k in smax], key=lambda r: -r[5])[:50]}


def main():
    sys.path.insert(0, str(ROOT / "r73" / "sealed"))
    from reveal_k4 import CLUES  # noqa: E402  -- post-freeze audit only
    pos = [o + j for o, t in CLUES for j in range(len(t))]
    pk = [ord(ch) - 65 for _, t in CLUES for ch in t]
    rows = [l.split("\t") for l in Path(sys.argv[1]).read_text().splitlines()[1:] if l]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    rows = rows[:1 + n]
    assert rows[0][0] == "K4"
    with Pool(4) as pool:
        res = dict(pool.imap_unordered(one, [(rid, ct, pos, pk) for rid, ct in rows]))
    k4, sh = res["K4"], [res[r] for r, _ in rows[1:]]
    ge = lambda r, k: sum(v for s, v in r["by_s_max"].items() if s >= k)  # noqa: E731
    k4max = k4["max_s"] if k4["max_s"] is not None else -1
    sh_max = [r["max_s"] if r["max_s"] is not None else -1 for r in sh]
    if ge(k4, 3) == 0:
        verdict = "NO_WITNESS_S_GE_3"
    elif k4max > max(sh_max):
        verdict = "LEAD"
    else:
        verdict = "CHANCE"
    out = {"classification": "POST-FREEZE CRIB-ASSISTED EXCLUSION-ONLY; corrected WPX one-error strength",
           "verdict": verdict, "k4_max_s": k4["max_s"], "k4_settings_s_ge3": ge(k4, 3),
           "shuffle_max_s": sh_max, "shuffles_with_s_ge3": sum(ge(r, 3) > 0 for r in sh),
           "p_family": (1 + sum(m >= k4max for m in sh_max)) / (1 + len(sh)),
           "results": {r: res[r] for r, _ in rows}}
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "results"}))


if __name__ == "__main__":
    main()
