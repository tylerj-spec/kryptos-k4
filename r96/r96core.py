#!/usr/bin/env python3
"""R96 shared code (standard library only): alphabets, RX2-O shifts and decryption, the R95 objective (reference
scorer and ctypes tables), the order-1 assignment (Hungarian), seeds, the kernel loader and the condition reader."""
import array
import ctypes
import hashlib
import os
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
MODEL_SHA = "e9c0848f5e256814387968c09006a44804e90a72aeb79034d0b12abfcce31abd"
R, T0 = 16, 4.0


def keyed(w):
    return "".join(dict.fromkeys(w + AZ))


ALPH = {"AZ": AZ, "KRY": keyed("KRYPTOS"), "PAL": keyed("PALIMPSEST"), "ABS": keyed("ABSCISSA")}


def parse_label(s):
    f = s.split(",")
    return (f[0], f[1], *map(int, f[2:]))


def shifts(lab, N=97):
    _, _, n, r, h, d1, d2 = lab
    s1, s2 = [], []
    for i in range(N):
        tau = (i + r) // n
        s1.append((d1 * tau) % 26)
        s2.append((d2 * ((tau + h) // 26)) % 26)
    return s1, s2


def decrypt(ct, U, V, lab):
    ein, eout = lab[0], lab[1]
    s1, s2 = shifts(lab, len(ct))
    out = []
    for c, a, b in zip(ct, s1, s2):
        m = (V[(ALPH[eout].index(c) + b) % 26] - b) % 26
        out.append(ALPH[ein][(U[(m + a) % 26] - a) % 26])
    return "".join(out)


class Model:
    def __init__(self, path):
        raw = Path(path).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == MODEL_SHA, "model digest"
        assert raw[:5] == b"R59LM" and raw[5] == 5
        self.t, off = [], 8
        for k in range(1, 6):
            a = array.array("f")
            a.frombytes(raw[off:off + 4 * 26 ** k])
            self.t.append(a)
            off += 4 * 26 ** k
        self.c = [(ctypes.c_float * len(a)).from_buffer(a) for a in self.t]

    def score(self, text):
        c = [ord(ch) - 65 for ch in text]
        tot = 0.0
        for i in range(len(c)):
            k = min(i + 1, 5)
            code = 0
            for ch in c[i - k + 1:i + 1]:
                code = code * 26 + ch
            tot += self.t[k - 1][code]
        return tot


def seed_of(prefix, rid, cond, start):
    return int(hashlib.sha256(f"{prefix}|{rid}|{cond}|{start}".encode()).hexdigest()[:15], 16)


def hungarian_max(cost):
    """Exact maximum-weight perfect assignment on an n x n matrix (row -> column); O(n^3) shortest augmenting path."""
    n = len(cost)
    INF = float("inf")
    a = [[-cost[i][j] for j in range(n)] for i in range(n)]
    u, v, p, way = [0.0] * (n + 1), [0.0] * (n + 1), [0] * (n + 1), [0] * (n + 1)
    for i in range(1, n + 1):
        p[0], j0 = i, 0
        minv, used = [INF] * (n + 1), [False] * (n + 1)
        while True:
            used[j0] = True
            i0, delta, j1 = p[j0], INF, 0
            for j in range(1, n + 1):
                if not used[j]:
                    cur = a[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j], way[j] = cur, j0
                    if minv[j] < delta:
                        delta, j1 = minv[j], j
            for j in range(n + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break
    res = [0] * n
    for j in range(1, n + 1):
        res[p[j] - 1] = j - 1
    return res


def assignment_start(ct, lab, mode, fixed, model, seed):
    """Version 2's exact order-1 start for the searched inverse wiring (PREREGISTRATION section 4)."""
    import random
    ein, eout = lab[0], lab[1]
    s1, s2 = shifts(lab, len(ct))
    a = [(ALPH[eout].index(c) + b) % 26 for c, b in zip(ct, s2)]
    T1 = model.t[0]
    cost = [[0.0] * 26 for _ in range(26)]
    for i in range(len(ct)):
        if mode == 0:            # U searched, V fixed: b_i = m_i + s1_i
            b = ((fixed[a[i]] - s2[i]) % 26 + s1[i]) % 26
            for u in range(26):
                cost[b][u] += T1[ord(ALPH[ein][(u - s1[i]) % 26]) - 65]
        else:                    # V searched, U fixed
            for v in range(26):
                q = (fixed[(v - s2[i] + s1[i]) % 26] - s1[i]) % 26
                cost[a[i]][v] += T1[ord(ALPH[ein][q]) - 65]
    rng = random.Random(seed)
    for x in range(26):
        for y in range(26):
            cost[x][y] += 1e-9 * rng.random()
    return hungarian_max(cost)


_LIB = None


def lib():
    global _LIB
    if _LIB is None:
        src = HERE / "kernel" / "anneal96.c"
        so = HERE / ".build" / f"anneal96_{hashlib.sha256(src.read_bytes()).hexdigest()[:16]}.so"
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
        L.run_v1.restype = ctypes.c_double
        L.run_v1.argtypes = [IP, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_uint64, IP]
        L.run_v2.restype = ctypes.c_double
        L.run_v2.argtypes = [IP, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_uint64, IP, IP]
        _LIB = L
    return _LIB


class Case:
    """Binds one ciphertext and label to the kernel (setup keeps pointers, so the arrays live on this object)."""

    def __init__(self, ct, lab, model):
        s1, s2 = shifts(lab, len(ct))
        IA = ctypes.c_int * len(ct)
        self.a = IA(*[(ALPH[lab[1]].index(c) + b) % 26 for c, b in zip(ct, s2)])
        self.s1, self.s2 = IA(*s1), IA(*s2)
        self.ein = (ctypes.c_int * 26)(*[ord(ALPH[lab[0]][k]) - 65 for k in range(26)])
        self.n = len(ct)
        self.model = model

    def bind(self):
        lib().setup(self.a, self.s1, self.s2, self.ein, *self.model.c, self.n)


def read_conditions(path=ROOT / "r96/inputs/CONDITIONS.tsv"):
    rows = []
    for line in Path(path).read_text().splitlines()[1:]:
        rid, cond, lab, ct, sup = line.split("\t")
        rows.append((rid, cond, parse_label(lab), ct, [int(x) for x in sup.split(",")]))
    return rows
