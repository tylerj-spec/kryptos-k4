#!/usr/bin/env python3
"""R97 shared code: R96's model, cipher, seed and case helpers (r96/r96core.py, unchanged) plus the R97 kernel
(r97/kernel/anneal97.c) and the alternation building blocks of PREREGISTRATION sections 3-5."""
import ctypes
import hashlib
import os
import random
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "r96"))
import r96core as C96  # noqa: E402

ALPH, AZ, Model, Case, decrypt, parse_label, shifts, seed_of = (C96.ALPH, C96.AZ, C96.Model, C96.Case, C96.decrypt,
                                                               C96.parse_label, C96.shifts, C96.seed_of)
MODEL_SHA, T0 = C96.MODEL_SHA, 4.0
_LIB = None


def lib():
    global _LIB
    if _LIB is None:
        src = HERE / "kernel" / "anneal97.c"
        so = HERE / ".build" / f"anneal97_{hashlib.sha256(src.read_bytes()).hexdigest()[:16]}.so"
        if not so.exists():
            so.parent.mkdir(exist_ok=True)
            tmp = so.with_suffix(f".{os.getpid()}.tmp.so")
            subprocess.run(["gcc", "-O3", "-shared", "-fPIC", "-o", str(tmp), str(src), "-lm"], check=True)
            tmp.replace(so)
        L = ctypes.CDLL(str(so))
        IP, FP = ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_float)
        L.setup.argtypes = [IP] * 4 + [FP] * 5 + [ctypes.c_int]
        L.score_pair.restype = ctypes.c_double
        L.score_pair.argtypes = [IP, IP]
        L.cond.restype = ctypes.c_double
        L.cond.argtypes = [IP, ctypes.c_int, IP, ctypes.c_int, ctypes.c_double, ctypes.c_uint64, IP]
        _LIB = L
    return _LIB


def bind(ct, lab, model):
    """Bind a case to the kernel; the returned object keeps the arrays alive (R96's Case uses its own .so)."""
    case = Case(ct, lab, model)
    lib().setup(case.a, case.s1, case.s2, case.ein, *case.model.c, case.n)
    return case


def cond(fixed, side, start, iters, t_start, seed):
    """side 'U': search U with V = fixed; side 'V': search V with U = fixed. Returns (score, wiring)."""
    w = (ctypes.c_int * 26)()
    st = (ctypes.c_int * 26)(*start) if start is not None else None
    sc = lib().cond((ctypes.c_int * 26)(*fixed), 0 if side == "U" else 1, st, iters, t_start, seed, w)
    return sc, list(w)


def joint(U, V):
    return lib().score_pair((ctypes.c_int * 26)(*U), (ctypes.c_int * 26)(*V))


def rand_perm(seed):
    p = list(range(26))
    random.Random(seed).shuffle(p)
    return p


def read_panel(path=ROOT / "r94/inputs/PANEL.tsv"):
    raw = Path(path).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "9b3ed6b49d437d4289f2a1126dd79b61ed7158b0e35b408bb39b1409aab8786c"
    rows = []
    for line in raw.decode().splitlines()[1:]:
        rid, lab, ct = line.split("\t")
        rows.append((rid, parse_label(lab), ct))
    return rows


def round_v1(U, V, t, Ic, sd):
    """One version-1 round (PREREGISTRATION section 4). sd(tag) -> seed. Returns (U, V)."""
    a = cond(V, "U", None, Ic, T0, sd(f"U{t}a"))
    b = cond(V, "U", U, Ic, T0 / 4, sd(f"U{t}b")) if U is not None else cond(V, "U", None, Ic, T0, sd(f"U{t}b"))
    U = a[1] if a[0] >= b[0] else b[1]
    a = cond(U, "V", V, Ic, T0 / 4, sd(f"V{t}a"))
    b = cond(U, "V", None, Ic, T0, sd(f"V{t}b"))
    V = a[1] if a[0] >= b[0] else b[1]
    return U, V
