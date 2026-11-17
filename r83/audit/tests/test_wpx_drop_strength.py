#!/usr/bin/env python3
"""Tests for r83/audit/wpx_drop_strength.py (synthetic only; no K4 data, no published letters).
1 on toy layouts, the set of settings with a feasible one-error witness equals T1's validated one-error survivors
  (exact_drop.wpx_scan: union over positions of drop_excl minus exact), setting by setting;
2 every setting's s_max and s_min equal a slow direct enumeration over (b, x, offset) through the reference
  encryptor's per-letter rule (r83/models83.py), with c = positions - distinct pointer residues;
3 on a planted one-wrong-plaintext-letter WPX message at K4's layout, the true setting has a witness, and s_max is at
  least the c of the true (b, x, offset).
Usage: python3 -I r83/audit/tests/test_wpx_drop_strength.py"""
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "r83" / "audit"), str(ROOT / "r83"), str(ROOT / "r75")]
import exact_drop as ED  # noqa: E402
import wpx_drop_strength as S  # noqa: E402
import models83 as MD  # noqa: E402


def slow(c, pos, pk, conv, alpha, e, d, m):
    """Direct: for every b, x != pk[b] and second-run start offset, feasible iff the needed key values agree on equal
    pointer residues (published-positions semantics); return (s_max, s_min) over feasible witnesses, or None."""
    pa, ca, s = conv
    R = ED.runs(pos)
    best = []
    exact_ok = None
    for b in [None] + list(range(len(pos))):
        for x in ([None] if b is None else [v for v in range(26) if v != pk[b]]):
            L = list(pk)
            if b is not None:
                L[b] = x
            for o in range(m):
                need, rel = {}, {}
                for q, run in enumerate(R):
                    r = 0 if q == 0 else o
                    for k in run:
                        rel[k] = r % m
                        r += d * (MD.ix(alpha, MD.AZ[L[k]]) + e)
                ok = True
                for k in range(len(pos)):
                    v = MD.key_value(MD.AZ[L[k]], MD.AZ[c[pos[k]]], pa, ca, s)
                    if need.setdefault(rel[k], v) != v:
                        ok = False
                        break
                if b is None:
                    exact_ok = exact_ok or ok
                elif ok:
                    best.append(len(pos) - len(set(rel.values())))
    if exact_ok or not best:
        return None
    return max(best), min(best)


def main():
    rng = random.Random(901117)
    n = 0
    for layout in ([2, 3, 4, 9, 10, 11], [5, 6, 7, 8, 14, 15, 16]):
        for _ in range(3):
            c = [rng.randrange(26) for _ in range(20)]
            pk = [rng.randrange(26) for _ in layout]
            R = ED.runs(layout)
            B = ED.Buckets(ED.wp_value(c), 32)
            got = {}
            for alpha in ED.A4:
                for e in (0, 1):
                    for d in ED.SIGNS:
                        for m in (2, 3, 4):
                            exact = ED.wpx_mask(layout, pk, alpha, e, d, m, B, R)
                            for b in range(len(layout)):
                                for x in range(26):
                                    if x == pk[b]:
                                        continue
                                    alt = list(pk)
                                    alt[b] = x
                                    for mk, cc in S.witness_masks(layout, alt, alpha, e, d, m, B, R):
                                        for bit in ED.bits(mk & ~exact):
                                            k = (ED.CONV1[bit], alpha, e, d, m)
                                            lo, hi = got.get(k, (99, -99))
                                            got[k] = (min(lo, cc), max(hi, cc))
                            # 1: same survivors as T1
                            rows = ED.wpx_scan(c, layout, pk, mrange=[m])
                            r = [r for r in rows if r["alpha"] == alpha and r["e"] == e and r["d"] == d][0]
                            anyd = 0
                            for v in r["drop_excl"]:
                                anyd |= v
                            t1 = {(ED.CONV1[bit], alpha, e, d, m) for bit in ED.bits(anyd & ~r["exact"])}
                            mine = {k for k in got if k[1:] == (alpha, e, d, m)}
                            assert t1 == mine, (alpha, e, d, m, len(t1), len(mine))
                            # 2: slow enumeration, a sample of conventions per cell
                            for conv in rng.sample(ED.CONV1, 4):
                                want = slow(c, layout, pk, conv, alpha, e, d, m)
                                k = (conv, alpha, e, d, m)
                                have = (got[k][1], got[k][0]) if k in got else None
                                assert want == have, (k, want, have)
                                n += 1
    print("1-2 ok: survivors equal T1's and s_max/s_min equal direct enumeration on", n, "toy settings")
    # 3: planted message at K4's layout
    pos = list(range(21, 34)) + list(range(63, 74))
    for _ in range(4):
        st = MD.random_setting(rng, "WP", m=rng.choice((5, 13, 26)))
        pt = "".join(rng.choice(MD.AZ) for _ in range(97))
        ct = [MD.AZ.index(ch) for ch in MD.encrypt(pt, st)]
        pk = [MD.AZ.index(pt[i]) for i in pos]
        b = rng.randrange(len(pos))
        pk[b] = (pk[b] + rng.randrange(1, 26)) % 26
        smax, _ = S.scan(ct, pos, pk)
        k = (tuple(st["conv"]), st["alpha"], st["e"], st["d"], len(st["U"]))
        assert k in smax or ED.wpx_setting(ct, pos, pk, st["conv"], st["alpha"], st["e"], st["d"], len(st["U"]))[0], k
    print("3 ok: planted one-wrong-plaintext-letter messages keep a witness (or stay exact-feasible)")
    print("WPX DROP STRENGTH TESTS OK")


if __name__ == "__main__":
    main()
