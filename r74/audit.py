#!/usr/bin/env python3
"""R74 step A (no K4 data): reference checks, transform count and the novelty audit asked for in PR #65.
  1. K1 and K2 historical vectors: single-stage VIG on the KRYPTOS tableau with PALIMPSEST / ABSCISSA.
  2. For every one of the 20,160 raw settings, the composite C = sigma * P[r] + v equals the explicit three-stage
     encryption on two random plaintexts, and decrypt() inverts it.
  3. Distinct transforms (route, sigma, v), and why 9 operation pairs give 7 classes.
  4. Periods: whether a transform collapses to a family already run here:
       - in place (no transposition; L36): no route is the identity;
       - substitute-then-transpose with summed periodic keys in plaintext order (L47/L48, R68 M1): needs the
         second-stage term, read in plaintext order, to be periodic;
       - transpose-then-substitute with periodic keys in ciphertext order (L47/L48, R58 TV, R68): needs the
         first-stage term, read in ciphertext order, to be periodic.
Usage: python3 -I r74/audit.py K1K3_CT K1K3_PT OUT.json"""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sandwich as S  # noqa: E402


def minper(seq):
    n = len(seq)
    for p in range(1, n + 1):
        if all(seq[i] == seq[i + p] for i in range(n - p)):
            return p
    return n


def main():
    ct_p, pt_p, out = sys.argv[1:4]
    ct, pt = Path(ct_p).read_text().strip(), Path(pt_p).read_text().strip()
    dec = lambda c, key: "".join(S.A[S.stage(S.IDX[ch], -S.IDX[key[i % len(key)]] % 26, "VIG")]  # noqa: E731
                                 for i, ch in enumerate(c))
    k1 = dec(ct[:63], "PALIMPSEST")
    k2 = dec(ct[63:63 + 369], "ABSCISSA")
    k2_match = next((i for i in range(369) if k2[i] != pt[63 + i]), 369)
    vectors = {"K1_exact_63_of_63": k1 == pt[:63],
               "K2_first_mismatch": k2_match, "K2_tail_decrypt": k2[340:], "K2_tail_reference": pt[63 + 340:63 + 369],
               "K2_note": "the last 8 letters decrypt to IDBYROWS: the documented carving anomaly (a letter omitted; "
                          "Sanborn's intended ending XLAYERTWO), not a tableau error"}
    routes = S.load_routes()
    rng = random.Random(740001)
    p1 = "".join(rng.choice(S.A) for _ in range(S.N))
    p2 = "".join(rng.choice(S.A) for _ in range(S.N))
    raw, bad = 0, 0
    cls = {}
    for cfg, r in S.configs(routes):
        raw += 1
        key = S.transform(cfg["ka"], cfg["kb"], cfg["a"], cfg["b"], cfg["op_a"], cfg["op_b"], r)
        cls.setdefault(key, []).append(cfg)
        for p in (p1, p2):
            c = S.encrypt(p, cfg["ka"], cfg["kb"], cfg["a"], cfg["b"], cfg["op_a"], cfg["op_b"], r)
            cc = "".join(S.A[(key[1] * S.IDX[p[r[j]]] + key[2][j]) % 26] for j in range(S.N))
            if c != cc or S.decrypt(c, *key) != p:
                bad += 1
    op_classes = {}
    for oa, (sa, ta) in S.OPS.items():
        for ob, (sb, tb) in S.OPS.items():
            op_classes.setdefault((sa * sb, sb * ta, tb), []).append(f"{oa}/{ob}")
    rnames = {v: k for k, v in routes.items()}
    per = {}
    for rn, r in routes.items():
        rinv = [0] * S.N
        for j, v in enumerate(r):
            rinv[v] = j
        # second-stage key term read in plaintext order; first-stage term read in ciphertext order
        pt_order = min(minper([S.IDX[kw[(rinv[i] + b) % len(kw)]] for i in range(S.N)])
                       for kw in S.KEYWORDS for b in range(len(kw)))
        ct_order = min(minper([S.IDX[kw[(r[j] + a) % len(kw)]] for j in range(S.N)])
                       for kw in S.KEYWORDS for a in range(len(kw)))
        per[rn] = {"identity": list(r) == list(range(S.N)),
                   "second_stage_term_min_period_in_plaintext_order": pt_order,
                   "first_stage_term_min_period_in_ciphertext_order": ct_order}
    comp_ct = min(minper(list(k[2])) for k in cls)
    comp_pt = min(minper([k[2][j] for j in sorted(range(S.N), key=lambda j: k[0][j])]) for k in cls)
    rep = {"vectors": vectors, "routes": len(routes), "route_names": list(routes),
           "raw_settings": raw, "composite_mismatches": bad, "distinct_transforms": len(cls),
           "max_labels_per_transform": max(len(v) for v in cls.values()),
           "operation_pair_classes": {str(k): v for k, v in op_classes.items()},
           "periods_by_route": per,
           "composite_min_period_ciphertext_order": comp_ct, "composite_min_period_plaintext_order": comp_pt,
           "transforms_by_route": {rn: sum(1 for k in cls if rnames[k[0]] == rn) for rn in routes}}
    Path(out).write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps({k: v for k, v in rep.items() if k not in ("periods_by_route", "route_names")}, indent=1))
    for rn, v in per.items():
        print(rn, v)


if __name__ == "__main__":
    main()
