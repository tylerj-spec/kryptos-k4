#!/usr/bin/env python3
"""R111 registered search (PREREGISTRATION section 1): R105's solver S105 on all 20 cells (B in {AZ, KRY} x lag 1-5
x one sign pair per sigma), with an independent re-encryption witness for every output under r100/autokey100.py."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(ROOT / "r105"), str(ROOT / "r100")]
import solve105 as S  # noqa: E402
import autokey100 as AK  # noqa: E402

AZ = AK.AZ
B_LIST = {"AZ": AZ, "KRY": "KRYPTOSABCDEFGHIJLMNQUVWXZ"}
LAGS = (1, 2, 3, 4, 5)
SIGMA_CELLS = {1: (1, -1), -1: (1, 1)}          # sigma = -s1*s2 -> representative sign pair
CELLS = [(b, L, sig) for b in B_LIST for L in LAGS for sig in (1, -1)]


def reencrypts(out, ct, B, L, s1, s2):
    P, A, c = out["plaintext"], out["A"], out["c"]
    return all(AK.enc_letter(P[i], P[i - L], A, B, "A", s1, s2, c) == ct[i] for i in range(L, len(ct)))


def search(ct, rng, keep_text=False):
    """Run S105 on every cell; returns (T, list of per-cell dicts in CELLS order)."""
    rows = []
    for b, L, sig in CELLS:
        s1, s2 = SIGMA_CELLS[sig]
        o = S.solve(ct, B_LIST[b], L, s1, s2, rng)
        row = {"B": b, "L": L, "sigma": sig, "score": o["score"], "reencrypts": reencrypts(o, ct, B_LIST[b], L, s1, s2)}
        if keep_text:
            row.update({"plaintext": o["plaintext"], "A": o["A"], "c": o["c"], "offsets": list(o["offsets"])})
        rows.append(row)
    return max(r["score"] for r in rows), rows
