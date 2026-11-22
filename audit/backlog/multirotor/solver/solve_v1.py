#!/usr/bin/env python3
"""RX2-O development solver, VERSION 1 (supplied structure). Reads only a ciphertext, its structural label and the
generic English quadgram table. No K4 data, no published letters, no truth.
For a label (ein, eout, n, r, h, d1, d2): R restarts x I iterations of joint annealing over both inverse wirings
(kernel/anneal2.c), each followed by a greedy polish. Every restart's decode is re-derived by the explicit
decryptor (rx2o.decrypt) and checked to re-encrypt. Seeds come from (SEED, ciphertext, label).
Functions: lib(), restarts(ct, label, R, I, T0, seed) -> [(quad score, W1, W2, text)], seed_of."""
import ctypes
import hashlib
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
import rx2o as X  # noqa: E402

PARAMS_V1 = {"R": 32, "I": 3000000, "T0": 4.0, "SEED": 930101, "KEEP": 8}
KERNEL = HERE / "kernel" / "anneal2.c"
_LIB, _QUAD = None, None


def lib():
    global _LIB, _QUAD
    if _LIB is None:
        h = hashlib.sha256(KERNEL.read_bytes()).hexdigest()[:16]
        so = HERE / ".build" / f"anneal2_{h}.so"
        if not so.exists():
            so.parent.mkdir(exist_ok=True)
            tmp = so.with_suffix(f".{os.getpid()}.tmp.so")
            subprocess.run(["gcc", "-O3", "-march=native", "-shared", "-fPIC", "-o", str(tmp), str(KERNEL), "-lm"],
                           check=True)
            tmp.replace(so)
        L = ctypes.CDLL(str(so))
        L.anneal2.restype = ctypes.c_double
        L.anneal2.argtypes = ([ctypes.POINTER(ctypes.c_int)] * 4 + [ctypes.POINTER(ctypes.c_float)] +
                              [ctypes.c_int] * 3 + [ctypes.c_double, ctypes.c_uint64, ctypes.POINTER(ctypes.c_double)] +
                              [ctypes.POINTER(ctypes.c_int)] * 2)
        raw = (ROOT / "k4kit/data/quad_log10.f32").read_bytes()
        _QUAD = (ctypes.c_float * (len(raw) // 4)).from_buffer_copy(raw)
        _LIB = L
    return _LIB, _QUAD


def seed_of(ct, label, base):
    return int(hashlib.sha256(f"{base}|{ct}|{label}".encode()).hexdigest()[:15], 16)


def restarts(ct, label, R, I, T0, seed):
    L, Q = lib()
    ein, eout, n, r, h, d1, d2 = label
    N = len(ct)
    s1, s2 = X.shifts(N, n, r, h, d1, d2)
    a = [(X.IDX[eout][c] + b) % 26 for c, b in zip(ct, s2)]
    e = [ord(X.ALPH[ein][k]) - 65 for k in range(26)]
    IA = ctypes.c_int * N
    sc = (ctypes.c_double * R)()
    v1, v2 = (ctypes.c_int * (26 * R))(), (ctypes.c_int * (26 * R))()
    L.anneal2(IA(*a), IA(*s1), IA(*s2), (ctypes.c_int * 26)(*e), Q, N, R, I, T0, seed, sc, v1, v2)
    out = []
    for k in range(R):
        W1, W2 = X.inverse(list(v1[26 * k:26 * k + 26])), X.inverse(list(v2[26 * k:26 * k + 26]))
        text = X.decrypt(ct, W1, W2, *label)
        assert X.encrypt(text, W1, W2, *label) == ct
        out.append((float(sc[k]), W1, W2, text))
    return out
