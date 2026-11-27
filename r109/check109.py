#!/usr/bin/env python3
"""R109 per-cell check (PREREGISTRATION section 2) on R102's solvers. Verdicts only; witnesses never leave this module
except to the gate's re-encryption test."""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "r102"), str(ROOT / "r100")]
import s3b102 as S  # noqa: E402
import dfs102 as D  # noqa: E402
import autokey100 as AK  # noqa: E402

AZ = AK.AZ
SIGNS = AK.SIGNS
FEEDBACK = AK.FEEDBACK
DFS_CAP = 100_000
DMAX = 5                                   # AMENDMENT_1 (approved): primary enumeration limit 7 -> 5


def exact(ct, hyp, L, s1, s2, F, with_witness=False):
    """EXACT verdict: primary, then the DFS for an undecided primary. Returns (verdict, primary_verdict, witness)."""
    st, d, wit = S.solve(ct, hyp, L, s1, s2, F, dmax=DMAX)
    if st == "NO_EQUATIONS":
        return "NO_EQUATIONS", st, None
    if st == "UNDECIDED":
        return D.solve(ct, hyp, L, s1, s2, F, node_cap=DFS_CAP), st, None
    return st, st, (wit if with_witness else None)


def dfs_crosscheck(ct, hyp, L, s1, s2, F):
    return D.solve(ct, hyp, L, s1, s2, F, node_cap=DFS_CAP)


def drop(ct, hyp, L, s1, s2, F):
    """EXCLUDED_DROP if, for every published position j, the primary alone finds hyp-without-j INCONSISTENT."""
    known = [j for j, ch in enumerate(hyp) if ch is not None]
    for j in known:
        h2 = list(hyp)
        h2[j] = None
        if S.solve(ct, h2, L, s1, s2, F, dmax=DMAX)[0] != "INCONSISTENT":
            return False
    return True


def primary_only(ct, hyp, L, s1, s2, F):
    return S.solve(ct, hyp, L, s1, s2, F, dmax=DMAX)[0]


def witness_ok(ct, hyp, L, s1, s2, F, wit):
    A, B, c = wit
    return all(AK.enc_letter(hyp[i], hyp[i - L], A, B, F, s1, s2, c) == ct[i]
               for i in range(L, len(ct)) if hyp[i] is not None and hyp[i - L] is not None)
