#!/usr/bin/env python3
"""R89 BLIND exhaustive solver for arm F26L (and the bare F26 sub-family), numpy. Reads only a ciphertext and the
generic English quadgram table; no K4 data, no published letters, no truth files.
Every one of the 139,120 settings (r89/f26l.py) is a fixed decryption, so ALL are decrypted and scored by quadgrams
(no shortlist, no randomness). The best KEEP decodes (by quadgram score) are re-derived by the explicit decryptor
(f26l.decrypt), checked to re-encrypt, and returned for the letter-model rescoring in run89.py.
Functions: solve(ct, keep) -> list of candidates (text, setting, quad, arm) best first."""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RND = HERE.parent
ROOT = RND.parent
sys.path.insert(0, str(RND))
import f26l as F  # noqa: E402

KEEP = 64
_QUAD = None
_MAPS = None


def quad():
    global _QUAD
    if _QUAD is None:
        _QUAD = np.fromfile(ROOT / "k4kit/data/quad_log10.f32", dtype=np.float32)
    return _QUAD


def maps(n):
    """For every (b, u, v): the input positions that give plaintext position k its row and its column."""
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
    best = []                                   # (score, outer, alphabet, key index)
    for outer, m in inners:
        for a, A in F.F26_ALPHABETS.items():
            Aarr = np.array([ord(ch) - 65 for ch in A])
            place = np.argsort(Aarr)[m]          # place of each inner letter in A
            P = Aarr[13 * (place[IR] // 13) + place[IH] % 13]           # (188, n) decodes
            sc = Q[P[:, :-3] * 17576 + P[:, 1:-2] * 676 + P[:, 2:-1] * 26 + P[:, 3:]].sum(1)
            top = np.argsort(-sc)[:keep]
            best.extend((float(sc[k]), outer, a, int(k)) for k in top)
    best.sort(key=lambda e: -e[0])
    out = []
    for sc, outer, a, k in best[:keep]:
        b, u, v = keys[k]
        st = (a, b, u, v, outer)
        text = F.decrypt(ct, st)
        assert F.encrypt(text, st) == ct
        out.append({"text": text, "arm": "F26" if outer is None else "F26L", "quad": sc,
                    "setting": {"alphabet": a, "b": b, "u": u, "v": v,
                                "outer": None if outer is None else {"key": outer[0], "sign": outer[1], "phase": outer[2]}}})
    return out, len(inners) * len(F.F26_ALPHABETS) * len(keys)
