"""R79 ctypes wrapper for r79/slotsolve.c (compiled on first use into r79/.build/, keyed by the source sha256).
slot_batch(Z, R, M, OI, BANK, restarts, seed, base) -> (score[S], delta[S, 32])
cyc_batch(PERMS, Y, STEP, LET, restarts, seed, base) -> (score[nr, nconv], log10 candidates[nr, nconv])
cyc_text(y, perm, step, let, restarts, seed, index) -> (text codes, score) or (None, -1e9)
UNI: log10 English letter frequencies (standard table), used only to start the ascent."""
import ctypes
import hashlib
import subprocess
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = HERE / "slotsolve.c"
MMAX = 32
QUAD = np.ascontiguousarray(np.fromfile(ROOT / "k4kit/data/quad_log10.f32", dtype=np.float32))
assert QUAD.size == 26 ** 4
_ENG = np.array([8.167, 1.492, 2.782, 4.253, 12.702, 2.228, 2.015, 6.094, 6.966, 0.153, 0.772, 4.025, 2.406, 6.749,
                 7.507, 1.929, 0.095, 5.987, 6.327, 9.056, 2.758, 0.978, 2.360, 0.150, 1.974, 0.074])
UNI = np.ascontiguousarray(np.log10(_ENG / _ENG.sum()).astype(np.float32))
_LIB = None


def lib():
    global _LIB
    if _LIB is None:
        h = hashlib.sha256(SRC.read_bytes()).hexdigest()[:16]
        so = HERE / ".build" / f"slotsolve_{h}.so"
        if not so.exists():
            so.parent.mkdir(exist_ok=True)
            tmp = so.with_suffix(".tmp.so")
            subprocess.run(["gcc", "-O2", "-shared", "-fPIC", "-o", str(tmp), str(SRC), "-lm"], check=True)
            tmp.replace(so)
        L = ctypes.CDLL(str(so))
        P = ctypes.c_void_p
        L.slot_batch.argtypes = [ctypes.c_int, ctypes.c_int, P, P, P, P, P, P, P, ctypes.c_int, ctypes.c_uint64,
                                 ctypes.c_int64, P, P]
        L.cyc_batch.argtypes = [ctypes.c_int, ctypes.c_int, P, ctypes.c_int, P, P, P, P, P, ctypes.c_int,
                                ctypes.c_uint64, ctypes.c_int64, P, P]
        L.cyc_text.argtypes = [ctypes.c_int, P, P, P, P, P, P, ctypes.c_int, ctypes.c_uint64, ctypes.c_int64, P, P]
        _LIB = L
    return _LIB


def _p(a):
    return a.ctypes.data_as(ctypes.c_void_p)


def slot_batch(Z, R, M, OI, BANK, restarts, seed, base=0):
    Z = np.ascontiguousarray(Z, dtype=np.uint8)
    R = np.ascontiguousarray(R, dtype=np.uint8)
    M = np.ascontiguousarray(M, dtype=np.int32)
    OI = np.ascontiguousarray(OI, dtype=np.int32)
    BANK = np.ascontiguousarray(BANK, dtype=np.uint8)
    S, n = Z.shape
    assert R.shape == Z.shape and M.shape == (S,) and OI.shape == (S,) and int(M.max(initial=1)) <= MMAX
    assert int(R.max(initial=0)) < int(M.max(initial=1)) + 1 and BANK.shape[1:] == (n, 26)
    score = np.zeros(S, dtype=np.float32)
    delta = np.zeros((S, MMAX), dtype=np.uint8)
    lib().slot_batch(S, n, _p(Z), _p(R), _p(M), _p(OI), _p(BANK), _p(QUAD), _p(UNI), int(restarts),
                     ctypes.c_uint64(seed & (2 ** 64 - 1)), int(base), _p(score), _p(delta))
    return score, delta


def cyc_batch(PERMS, Y, STEP, LET, restarts, seed, base=0):
    PERMS = np.ascontiguousarray(PERMS, dtype=np.uint8)
    Y = np.ascontiguousarray(Y, dtype=np.uint8)
    STEP = np.ascontiguousarray(STEP, dtype=np.uint8)
    LET = np.ascontiguousarray(LET, dtype=np.uint8)
    nr, n = PERMS.shape
    nconv = Y.shape[0]
    assert Y.shape == (nconv, n) and STEP.shape == (nconv, 676) and LET.shape == (nconv, 26)
    score = np.zeros((nr, nconv), dtype=np.float32)
    lc = np.zeros((nr, nconv), dtype=np.float32)
    lib().cyc_batch(nr, n, _p(PERMS), nconv, _p(Y), _p(STEP), _p(LET), _p(QUAD), _p(UNI), int(restarts),
                    ctypes.c_uint64(seed & (2 ** 64 - 1)), int(base), _p(score), _p(lc))
    return score, lc


def cyc_text(y, perm, step, let, restarts, seed, index):
    y, perm = np.ascontiguousarray(y, dtype=np.uint8), np.ascontiguousarray(perm, dtype=np.uint8)
    step, let = np.ascontiguousarray(step, dtype=np.uint8), np.ascontiguousarray(let, dtype=np.uint8)
    text = np.zeros(len(y), dtype=np.uint8)
    sc = np.zeros(1, dtype=np.float32)
    ok = lib().cyc_text(len(y), _p(y), _p(perm), _p(step), _p(let), _p(QUAD), _p(UNI), int(restarts),
                        ctypes.c_uint64(seed & (2 ** 64 - 1)), int(index), _p(text), _p(sc))
    return (text, float(sc[0])) if ok else (None, -1e9)
