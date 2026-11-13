"""R80 identifiability study (synthetic only; no K4, no published letters).
Two keyword stages on different tableaux:  y = s2*tau(s1*x + a) + b,  tau = IDX[PA2] o LET[CA1].
  1 difference table of tau for every ordered pair of the four alphabets: N(d, e) = #{z: tau(z+d) - tau(z) = e};
    exact equivalent keys exist iff some N(d, e) = 26 with (d, e) != (0, 0);
  2 a small recovery experiment: coordinate ascent on quadgrams with and without the global 'gauge' move
    (k1 += d, k2 -= s2*e for the strongest (d, e)), on planted messages.
Usage: python3 -I r80/ident.py OUT.json"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "r75"))
sys.path.insert(0, str(ROOT / "r79"))
import core  # noqa: E402
import families as F  # noqa: E402

A4 = ("AZ", "KRY", "PAL", "ABS")
QUAD = np.fromfile(ROOT / "k4kit/data/quad_log10.f32", dtype=np.float32)
IDX = {a: core.IDX[a].astype(np.int64) for a in A4}
LET = {a: core.LET[a].astype(np.int64) for a in A4}


def ddt(ca1, pa2):
    tau = IDX[pa2][LET[ca1]]
    z = np.arange(26)
    T = np.zeros((26, 26), dtype=int)
    for d in range(26):
        np.add.at(T[d], (tau[(z + d) % 26] - tau) % 26, 1)
    return tau, T


def qscore(L):
    L = L.astype(np.int64)
    return QUAD[((L[..., :-3] * 26 + L[..., 1:-2]) * 26 + L[..., 2:-1]) * 26 + L[..., 3:]].sum(axis=-1)


def decode(y, k1, k2, m1, m2, tinv, pa1, s1, s2):
    i = np.arange(len(y))
    u = tinv[(s2 * (y - k2[..., i % m2])) % 26]
    return LET[pa1][(s1 * (u - k1[..., i % m1])) % 26]


def solve(y, m1, m2, tinv, pa1, s1, s2, restarts, rng, gauge):
    best, bk = -1e18, None
    for _ in range(restarts):
        k1, k2 = rng.integers(0, 26, m1), rng.integers(0, 26, m2)
        cur = float(qscore(decode(y, k1, k2, m1, m2, tinv, pa1, s1, s2)))
        for _sweep in range(40):
            changed = False
            for which, m in ((0, m1), (1, m2)):
                for r in range(m):
                    K = np.tile(k1 if which == 0 else k2, (26, 1))
                    K[:, r] = np.arange(26)
                    sc = qscore(decode(y, K if which == 0 else k1, k2 if which == 0 else K, m1, m2, tinv, pa1, s1, s2))
                    v = int(np.argmax(sc))
                    if sc[v] > cur + 1e-9:
                        (k1 if which == 0 else k2)[r] = v
                        cur, changed = float(sc[v]), True
            if gauge:
                d = np.arange(26)[:, None]
                for e_of_d in gauge:                      # e as a function of d: candidate global moves
                    K1 = (k1[None, :] + d) % 26
                    K2 = (k2[None, :] - s2 * e_of_d[:, None]) % 26
                    sc = qscore(decode(y, K1, K2, m1, m2, tinv, pa1, s1, s2))
                    v = int(np.argmax(sc))
                    if sc[v] > cur + 1e-9:
                        k1, k2, cur, changed = K1[v].copy(), K2[v].copy(), float(sc[v]), True
            if not changed:
                break
        if cur > best:
            best, bk = cur, (k1.copy(), k2.copy())
    return best, bk


def main(out):
    res = {"pairs": {}, "recovery": []}
    for ca1 in A4:
        for pa2 in A4:
            if ca1 == pa2:
                continue
            tau, T = ddt(ca1, pa2)
            T0 = T.copy()
            T0[0, 0] = 0
            perms = {tuple((tau[(np.arange(26) + a) % 26] + b) % 26) for a in range(26) for b in range(26)}
            d, e = np.unravel_index(np.argmax(T0), T0.shape)
            res["pairs"][f"{ca1}->{pa2}"] = {
                "max_entry": int(T0.max()), "at_d_e": [int(d), int(e)], "distinct_of_676": len(perms),
                "N(d,d) d=1..4": [int(T[k, k]) for k in (1, 2, 3, 4)],
                "entries_ge_8": int((T0 >= 8).sum()), "best_e_for_d": [int(np.argmax(T0[k])) for k in range(26)]}
    print(json.dumps(res["pairs"], indent=0)[:1800])
    rng = np.random.default_rng(800100)
    txt = core.codes(F.texts()["K13PT"]).astype(np.int64)
    for (pa1, ca1, pa2, ca2), (m1, m2) in ((("AZ", "AZ", "KRY", "KRY"), (7, 10)), (("KRY", "KRY", "AZ", "AZ"), (7, 8)),
                                           (("AZ", "AZ", "KRY", "KRY"), (5, 6)), (("AZ", "AZ", "KRY", "KRY"), (9, 11))):
        tau, T = ddt(ca1, pa2)
        tinv = np.argsort(tau)
        T0 = T.copy()
        T0[0, 0] = 0
        g1 = np.arange(26)                                 # e = d (pure translation gauge)
        g2 = np.argmax(T0, axis=1)                         # e = best partner of each d
        row = {"conv": [pa1, ca1, pa2, ca2], "m": [m1, m2], "plain": 0, "gauge": 0, "n": 12}
        for _ in range(12):
            o = int(rng.integers(0, len(txt) - 97))
            x = IDX[pa1][txt[o:o + 97]]
            k1, k2 = rng.integers(0, 26, m1), rng.integers(0, 26, m2)
            i = np.arange(97)
            y = (tau[(x + k1[i % m1]) % 26] + k2[i % m2]) % 26
            for name, gz in (("plain", None), ("gauge", (g1, g2))):
                _, (a, b) = solve(y, m1, m2, tinv, pa1, 1, 1, 12, np.random.default_rng(int(rng.integers(1 << 30))), gz)
                dec = decode(y, a, b, m1, m2, tinv, pa1, 1, 1)
                row[name] += int((dec == txt[o:o + 97]).sum() >= 95)
        res["recovery"].append(row)
        print(row, flush=True)
    Path(out).write_text(json.dumps(res, indent=1) + "\n")


if __name__ == "__main__":
    main(sys.argv[1])
