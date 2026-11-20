#!/usr/bin/env python3
"""R88 BLIND solver for the RQ family (stepped progressive Quagmire, one free alphabet; r88/rq88.py). Reads only a
ciphertext and the generic English quadgram table. No K4 data, no published letters, no truth files.
Settings: side PA/CA x fixed alphabet AZ/KRY/PAL/ABS x d +-1 x n 1..NMAX (512 at NMAX 32).
The annealing kernel is R87's, unchanged (r87/blind/anneal.c): it decodes p_i = E[(Winv[x_i] - s_i) mod 26].
  side PA: x_i = (A-place(c_i) - d*(i//n)) mod 26, s_i = 0, E = AZ          (so p_i = Winv[x_i])
  side CA: x_i = AZ-index(c_i),                    s_i = d*(i//n), E = A    (so p_i = A[Winv[c_i] - s_i])
  In both, the encryption map is W = inverse(Winv) (rq88.py).
  pass 1  every setting: annealing (R1 restarts x I1 iterations) + greedy polish; keep the TOP best settings;
  pass 2  those settings again with R2 restarts x I2 iterations (the pass-1 wiring is kept if it scores higher);
          the best decode per setting is re-derived by the explicit decryptor (rq88.decrypt), checked to
          re-encrypt, and kept.  (Pass 3, the letter-model polish, is in run88.py.)
Parameters are R87's (measured on spent books, r87/dev/DEV.md); every annealing seed is derived from
(SEED, ciphertext, setting, pass), so a run is deterministic.
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
import rq88 as R  # noqa: E402

PARAMS = {"NMAX": 32, "R1": 3, "I1": 20000, "TOP": 48, "R2": 12, "I2": 40000, "T0": 4.0, "SEED": 880101}
KERNEL = ROOT / "r87/blind/anneal.c"
_LIB, _QUAD = None, None


def lib():
    global _LIB, _QUAD
    if _LIB is None:
        h = hashlib.sha256(KERNEL.read_bytes()).hexdigest()[:16]
        so = RND / ".build" / f"anneal_{h}.so"
        if not so.exists():
            so.parent.mkdir(exist_ok=True)
            tmp = so.with_suffix(f".{os.getpid()}.tmp.so")   # per-process name: no compile race (R87 Amendment 1)
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


def settings(nmax):
    return [(side, a, n, d) for side in R.SIDES for a in R.A4 for d in (1, -1) for n in range(1, nmax + 1)]


def frame(ct, st):
    side, a, n, d = st
    N = len(ct)
    if side == "PA":
        x = [(R.IDX[a][c] - d * (i // n)) % 26 for i, c in enumerate(ct)]
        s = [0] * N
        e = list(range(26))
    else:
        x = [R.AZ.index(c) for c in ct]
        s = [d * (i // n) for i in range(N)]
        e = [ord(R.ALPH[a][k]) - 65 for k in range(26)]
    return x, s, e


def run_one(ct, st, restarts, iters, t0, seed):
    L, Q = lib()
    x, s, e = frame(ct, st)
    N = len(ct)
    IA = ctypes.c_int * N
    best = (ctypes.c_int * 26)()
    sc = L.anneal(IA(*x), IA(*s), (ctypes.c_int * 26)(*e), Q, N, restarts, iters, t0, seed, best)
    return sc, R.inverse(list(best))


def seed_of(ct, st, p, base=PARAMS["SEED"]):
    return int(hashlib.sha256(f"{base}|{ct}|{st}|{p}".encode()).hexdigest()[:15], 16)


def solve(ct, P=PARAMS):
    sts = settings(P["NMAX"])
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
        out.append({"text": text, "setting": {"side": st[0], "alph": st[1], "n": st[2], "d": st[3], "wiring": W},
                    "quad": sc, "pass1_rank": rank1[st]})
    out.sort(key=lambda e: -e["quad"])
    return out, rank1, len(sts)
