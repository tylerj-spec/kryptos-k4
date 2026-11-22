#!/usr/bin/env python3
"""RX2-O development solver, VERSION 3 (supplied structure; the last version the work order allows). Version 1's
search (joint annealing over both inverse wirings, greedy polish) with the R59 letter model truncated at order 5 as
the objective (kernel/anneal5.c), because version 2 showed the quadgram objective overfits (dev/v2/V2.md). Reads only
a ciphertext, its structural label and the letter model's order-1..5 tables (47.5 MB in all, sha256 of the whole
model file checked by the caller). No K4 data, no published letters, no truth.
Functions: lib(), load_lm5(path), restarts(ct, label, R, I, T0, seed) -> [(order-5 total, W1, W2, text)], seed_of."""
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

PARAMS_V3 = {"R": 8, "I": 4500000, "T0": 4.0, "SEED": 930301, "KEEP": 8}   # I from the measured speed (V3.md)
KERNEL = HERE / "kernel" / "anneal5.c"
_LIB, _LM = None, None


def load_lm5(path):
    """The order-1..5 tables of the R59 model, read (not mapped) at core.Scorer's offsets."""
    global _LM
    if _LM is None:
        import array
        with open(path, "rb") as f:
            head = f.read(8)
            assert head[:5] == b"R59LM" and head[5] >= 5
            tabs, off, sz = [], 8, 26
            for k in range(1, 6):
                f.seek(off)
                a = array.array("f")
                a.frombytes(f.read(sz * 4))
                tabs.append((ctypes.c_float * sz).from_buffer(a))
                tabs[-1]._keep = a
                off += sz * 4
                sz *= 26
        _LM = tabs
    return _LM


def lib():
    global _LIB
    if _LIB is None:
        h = hashlib.sha256(KERNEL.read_bytes()).hexdigest()[:16]
        so = HERE / ".build" / f"anneal5_{h}.so"
        if not so.exists():
            so.parent.mkdir(exist_ok=True)
            tmp = so.with_suffix(f".{os.getpid()}.tmp.so")
            subprocess.run(["gcc", "-O3", "-march=native", "-shared", "-fPIC", "-o", str(tmp), str(KERNEL), "-lm"],
                           check=True)
            tmp.replace(so)
        L = ctypes.CDLL(str(so))
        L.anneal5.restype = ctypes.c_double
        L.anneal5.argtypes = ([ctypes.POINTER(ctypes.c_int)] * 4 + [ctypes.POINTER(ctypes.c_float)] * 5 +
                              [ctypes.c_int] * 3 + [ctypes.c_double, ctypes.c_uint64, ctypes.POINTER(ctypes.c_double)] +
                              [ctypes.POINTER(ctypes.c_int)] * 2)
        _LIB = L
    return _LIB


def seed_of(ct, label, base):
    return int(hashlib.sha256(f"{base}|{ct}|{label}".encode()).hexdigest()[:15], 16)


def restarts(ct, label, R, I, T0, seed, lm_path):
    L, T = lib(), load_lm5(lm_path)
    ein, eout, n, r, h, d1, d2 = label
    N = len(ct)
    s1, s2 = X.shifts(N, n, r, h, d1, d2)
    a = [(X.IDX[eout][c] + b) % 26 for c, b in zip(ct, s2)]
    e = [ord(X.ALPH[ein][k]) - 65 for k in range(26)]
    IA = ctypes.c_int * N
    sc = (ctypes.c_double * R)()
    v1, v2 = (ctypes.c_int * (26 * R))(), (ctypes.c_int * (26 * R))()
    L.anneal5(IA(*a), IA(*s1), IA(*s2), (ctypes.c_int * 26)(*e), *T, N, R, I, T0, seed, sc, v1, v2)
    out = []
    for k in range(R):
        W1, W2 = X.inverse(list(v1[26 * k:26 * k + 26])), X.inverse(list(v2[26 * k:26 * k + 26]))
        text = X.decrypt(ct, W1, W2, *label)
        assert X.encrypt(text, W1, W2, *label) == ct
        out.append((float(sc[k]), W1, W2, text))
    return out
