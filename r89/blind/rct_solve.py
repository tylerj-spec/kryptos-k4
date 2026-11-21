#!/usr/bin/env python3
"""R89 BLIND solver for arm RCT (ciphertext-stepped rotor, unknown wiring; r89/rct.py). Reads only a ciphertext and
the generic English quadgram table. No K4 data, no published letters, no truth files.
Settings: E_in, E_out in AZ/KRY/PAL/ABS (16) x 28 schedules (d +-1, m 2..5, q 0..m-1) = 448.
For each setting the offsets s_i are computed from the ciphertext (rct.offsets), and R87's annealing kernel
(r87/blind/anneal.c, unchanged) searches the wiring in the rotor frame x_i = E_out-place(c_i) + s_i, decoding
p_i = E_in[(Winv[x_i] - s_i) mod 26]. Passes as R87/R88 (parameters measured on spent books, r87/dev/DEV.md):
  pass 1  every setting, R1 restarts x I1 iterations; keep the TOP best;  pass 2  R2 x I2 on those, keeping the better
  of the two wirings. Each kept decode is re-derived by rct.decrypt and checked to re-encrypt.
Every annealing seed is derived from (SEED, ciphertext, setting, pass), so a run is deterministic.
Functions: solve(ct) -> (candidates best first, number of settings)."""
import ctypes
import hashlib
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RND = HERE.parent
ROOT = RND.parent
sys.path.insert(0, str(RND))
import rct as R  # noqa: E402

PARAMS = {"R1": 3, "I1": 20000, "TOP": 48, "R2": 12, "I2": 40000, "T0": 4.0, "SEED": 890101}
KERNEL = ROOT / "r87/blind/anneal.c"
_LIB, _QUAD = None, None


def lib():
    global _LIB, _QUAD
    if _LIB is None:
        h = hashlib.sha256(KERNEL.read_bytes()).hexdigest()[:16]
        so = RND / ".build" / f"anneal_{h}.so"
        if not so.exists():
            so.parent.mkdir(exist_ok=True)
            tmp = so.with_suffix(f".{os.getpid()}.tmp.so")     # per-process name: no compile race
            subprocess.run(["gcc", "-O3", "-march=native", "-shared", "-fPIC", "-o", str(tmp), str(KERNEL), "-lm"],
                           check=True)
            tmp.replace(so)
        L = ctypes.CDLL(str(so))
        L.anneal.restype = ctypes.c_double
        L.anneal.argtypes = [ctypes.POINTER(ctypes.c_int)] * 3 + [ctypes.POINTER(ctypes.c_float), ctypes.c_int,
                             ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_uint64, ctypes.POINTER(ctypes.c_int)]
        raw = (ROOT / "k4kit/data/quad_log10.f32").read_bytes()
        _QUAD = (ctypes.c_float * (len(raw) // 4)).from_buffer_copy(raw)
        _LIB = L
    return _LIB, _QUAD


def settings():
    return [(ei, eo, d, m, q) for ei in R.A4 for eo in R.A4 for (d, m, q) in R.SCHEDULES]


def run_one(ct, st, restarts, iters, t0, seed):
    L, Q = lib()
    ei, eo, d, m, q = st
    N = len(ct)
    s = R.offsets(ct, d, m, q)
    x = [(R.IDX[eo][c] + si) % 26 for c, si in zip(ct, s)]
    e = [ord(R.ALPH[ei][k]) - 65 for k in range(26)]
    IA = ctypes.c_int * N
    best = (ctypes.c_int * 26)()
    sc = L.anneal(IA(*x), IA(*s), (ctypes.c_int * 26)(*e), Q, N, restarts, iters, t0, seed, best)
    return sc, R.inverse(list(best))


def seed_of(ct, st, p, base=PARAMS["SEED"]):
    return int(hashlib.sha256(f"{base}|{ct}|{st}|{p}".encode()).hexdigest()[:15], 16)


def solve(ct, P=PARAMS):
    sts = settings()
    p1 = []
    for st in sts:
        sc, W = run_one(ct, st, P["R1"], P["I1"], P["T0"], seed_of(ct, st, 1, P["SEED"]))
        p1.append((sc, st, W))
    p1.sort(key=lambda e: -e[0])
    out = []
    for k, (sc1, st, W1) in enumerate(p1[:P["TOP"]]):
        sc, W = run_one(ct, st, P["R2"], P["I2"], P["T0"], seed_of(ct, st, 2, P["SEED"]))
        if sc1 > sc:
            sc, W = sc1, W1
        text = R.decrypt(ct, W, *st)
        assert R.encrypt(text, W, *st) == ct
        out.append({"text": text, "arm": "RCT", "quad": sc, "pass1_rank": k + 1,
                    "setting": {"ein": st[0], "eout": st[1], "d": st[2], "m": st[3], "q": st[4], "wiring": W}})
    out.sort(key=lambda e: -e["quad"])
    return out, len(sts)
