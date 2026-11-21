#!/usr/bin/env python3
"""R90 BLIND exhaustive solver for F26C (r90/f26c.py), numpy. Reads only a ciphertext and the generic English
quadgram table; no K4 data, no published letters, no truth files.
Stage 1 (every setting): all 104,340 fixed decryptions are scored by quadgrams.  Retention rule (pre-registered):
the KEEP = 256 best by quadgram score (ties broken by setting order) go to stage 2, the order-6 letter model, in
run90.py. Each retained decode is re-derived by the explicit decryptor (f26c.decrypt) and checked to re-encrypt.
Functions: solve(ct, keep) -> (candidates in quadgram order, number of settings)."""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RND = HERE.parent
ROOT = RND.parent
sys.path.insert(0, str(RND))
import f26c as F  # noqa: E402

KEEP = 256
_QUAD, _MAPS = None, None


def quad():
    global _QUAD
    if _QUAD is None:
        _QUAD = np.fromfile(ROOT / "k4kit/data/quad_log10.f32", dtype=np.float32)
    return _QUAD


def maps(n):
    global _MAPS
    if _MAPS is None or _MAPS[0] != n:
        keys, IR, IH = [], [], []
        for b in F.BLOCKS:
            for (u, v) in F.pairs(b):
                ir, ih = [], []
                for o, t in F.blocks(n, b):
                    for j in range(t):
                        ir.append(o + (j - u) % t)
                        ih.append(o + (j - v) % t)
                keys.append((b, u, v))
                IR.append(ir)
                IH.append(ih)
        _MAPS = (n, keys, np.array(IR), np.array(IH))
    return _MAPS[1:]


def tag(st):
    a, b, u, v, o = st
    return f"{a}|{b}|{u}|{v}|" + ("-|-|-" if o is None else f"{o[0]}|{o[1]}|{o[2]}")


def solve(ct, keep=KEEP):
    n = len(ct)
    Q = quad()
    keys, IR, IH = maps(n)
    kry = np.array([ord(ch) - 65 for ch in F.KRY])
    kry_inv = np.argsort(kry)
    c = np.array([ord(ch) - 65 for ch in ct])
    inners = [(None, c)]
    for (key, sg, ph) in F.outer_options():
        U = F.KEYS[key]
        shift = np.array([kry_inv[ord(U[(i + ph) % len(U)]) - 65] for i in range(n)])
        inners.append(((key, sg, ph), kry[(kry_inv[c] - sg * shift) % 26]))
    scores, index = [], []
    for oi, (outer, m) in enumerate(inners):
        for ai, (a, A) in enumerate(F.ALPHABETS.items()):
            Aarr = np.array([ord(ch) - 65 for ch in A])
            place = np.argsort(Aarr)[m]
            P = Aarr[13 * (place[IR] // 13) + place[IH] % 13]
            scores.append(Q[P[:, :-3] * 17576 + P[:, 1:-2] * 676 + P[:, 2:-1] * 26 + P[:, 3:]].sum(1))
            index.append((oi, ai))
    S = np.concatenate(scores)                      # setting order: outer, alphabet, (b, u, v)
    order = np.lexsort((np.arange(len(S)), -S))[:keep]
    names = list(F.ALPHABETS)
    out = []
    for g in order:
        blk, k = divmod(int(g), len(keys))
        oi, ai = index[blk]
        b, u, v = keys[k]
        st = (names[ai], b, u, v, inners[oi][0])
        text = F.decrypt(ct, st)
        assert F.encrypt(text, st) == ct
        o = st[4]
        out.append({"text": text, "arm": "F26" if o is None else "F26C", "quad": float(S[g]), "tag": tag(st),
                    "setting": {"alphabet": st[0], "b": b, "u": u, "v": v,
                                "outer": None if o is None else {"key": o[0], "sign": o[1], "phase": o[2]}}})
    return out, len(S)
