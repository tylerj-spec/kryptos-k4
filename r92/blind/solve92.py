#!/usr/bin/env python3
"""R92 BLIND solver for the RXP family (single stepping rotor with a step-boundary phase, unknown wiring; r92/rotor92.py). Reads only a
ciphertext and the generic English quadgram table. No K4 data, no published letters, no truth files.
Settings: the 192 of rotor92.SETTINGS (16 contact pairs x n 2..4, r 1..n-1, d +-1); R87's kernel and schedule. Annealing: linear cooling from T0 (log10 quadgram units).
  pass 1  every setting: annealing (R1 restarts x I1 iterations) + greedy polish; keep the TOP best settings;
  pass 2  those settings again with R2 restarts x I2 iterations (the pass-1 wiring is kept if it scores higher);
          the best decode per setting is re-derived by the
          explicit decryptor (rotor92.decrypt), checked to re-encrypt, and kept.
  (pass 3, the letter-model polish of the best candidates, is in run92.py, which holds the letter model.)
Every annealing seed is derived from (SEED, ciphertext, setting, pass), so a run is deterministic.
Functions: solve(ct, params) -> (candidates best first, pass-1 ranks, number of settings)."""
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
import rotor92 as R  # noqa: E402

PARAMS = {"R1": 3, "I1": 20000, "TOP": 48, "R2": 12, "I2": 40000, "T0": 4.0, "SEED": 920101}
KERNEL = ROOT / "r87/blind/anneal.c"
_LIB, _QUAD = None, None


def lib():
    global _LIB, _QUAD
    if _LIB is None:
        src = KERNEL
        h = hashlib.sha256(src.read_bytes()).hexdigest()[:16]
        so = RND / ".build" / f"anneal_{h}.so"
        if not so.exists():
            so.parent.mkdir(exist_ok=True)
            tmp = so.with_suffix(f".{os.getpid()}.tmp.so")   # per-process name: no compile race
            subprocess.run(["gcc", "-O3", "-march=native", "-shared", "-fPIC", "-o", str(tmp), str(src), "-lm"], check=True)
            tmp.replace(so)
        L = ctypes.CDLL(str(so))
        L.anneal.restype = ctypes.c_double
        L.anneal.argtypes = [ctypes.POINTER(ctypes.c_int)] * 3 + [ctypes.POINTER(ctypes.c_float), ctypes.c_int,
                             ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_uint64, ctypes.POINTER(ctypes.c_int)]
        raw = (ROOT / "k4kit/data/quad_log10.f32").read_bytes()
        _QUAD = (ctypes.c_float * (len(raw) // 4)).from_buffer_copy(raw)
        _LIB = L
    return _LIB, _QUAD


def settings(nmax=None):
    return list(R.SETTINGS)


def run_one(ct, st, restarts, iters, t0, seed):
    L, Q = lib()
    ein, eout, n, r, d = st
    N = len(ct)
    s = R.offsets(N, n, r, d)
    x = [(R.IDX[eout][c] + si) % 26 for c, si in zip(ct, s)]
    e = [ord(R.ALPH[ein][k]) - 65 for k in range(26)]
    IA = ctypes.c_int * N
    best = (ctypes.c_int * 26)()
    sc = L.anneal(IA(*x), IA(*s), (ctypes.c_int * 26)(*e), Q, N, restarts, iters, t0, seed, best)
    winv = list(best)
    W = [0] * 26
    for y, xx in enumerate(winv):
        W[xx] = y
    return sc, W


def seed_of(ct, st, p, base=PARAMS["SEED"]):
    return int(hashlib.sha256(f"{base}|{ct}|{st}|{p}".encode()).hexdigest()[:15], 16)


def solve(ct, P=PARAMS):
    sts = settings()
    p1 = []
    for st in sts:
        sc, W = run_one(ct, st, P["R1"], P["I1"], P["T0"], seed_of(ct, st, 1, P["SEED"]))
        p1.append((sc, st, W))
    p1.sort(key=lambda e: -e[0])
    rank1 = {st: k + 1 for k, (_, st, _) in enumerate(p1)}
    out = []
    for sc1, st, W1 in p1[:P["TOP"]]:
        sc, W = run_one(ct, st, P["R2"], P["I2"], P["T0"], seed_of(ct, st, 2, P["SEED"]))
        if sc1 > sc:                      # never lose a better pass-1 wiring
            sc, W = sc1, W1
        text = R.decrypt(ct, W, *st)
        assert R.encrypt(text, W, *st) == ct
        out.append({"text": text, "setting": {"ein": st[0], "eout": st[1], "n": st[2], "r": st[3], "d": st[4], "wiring": W},
                    "quad": sc, "pass1_rank": rank1[st]})
    out.sort(key=lambda e: -e["quad"])
    return out, rank1, len(sts)
