#!/usr/bin/env python3
"""R87 code (family RX of r85/DESIGN.md) (SYNTHETIC ONLY: no K4 ciphertext, no published letters are read by this file).
Family RX: a single stepping rotor (Hebern type) with an UNKNOWN wiring W (any of 26! permutations).
  Contacts are numbered on the input side by alphabet E_in and on the output side by E_out (AZ, KRY, PAL, ABS).
  The rotor advances d = +1 or -1 places every n letters: s_i = d * (i // n). (A starting position is absorbed by W:
  shift(-s0) o W o shift(s0) is just another wiring.)
  Encrypt:  y_i = W(E_in(p_i) + s_i) - s_i  (mod 26);  c_i = E_out^-1(y_i).
  Equivalently E_out(c_i) + s_i = W(E_in(p_i) + s_i): every position is one equation of ONE permutation W.
This is the extra structure L53 says the open per-slot-bijection periods need: all 26 slots share one wiring.
n >= 97 is a monoalphabetic substitution (excluded by L02); n = 1 has period 26 (L21's open m = 26).
Functions: encrypt / decrypt (reference), exact_check (partial-bijection test on given positions), anneal (blind
wiring search by quadgram score)."""
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def keyed(w):
    return "".join(dict.fromkeys(w + AZ))


ALPH = {"AZ": AZ, "KRY": keyed("KRYPTOS"), "PAL": keyed("PALIMPSEST"), "ABS": keyed("ABSCISSA")}
IDX = {a: {ch: i for i, ch in enumerate(s)} for a, s in ALPH.items()}
A4 = tuple(ALPH)


def steps(N, n, d):
    return [d * (i // n) for i in range(N)]


def encrypt(pt, W, ein, eout, n, d):
    out = []
    for i, p in enumerate(pt):
        s = d * (i // n)
        out.append(ALPH[eout][(W[(IDX[ein][p] + s) % 26] - s) % 26])
    return "".join(out)


def decrypt(ct, W, ein, eout, n, d):
    Winv = [0] * 26
    for x, y in enumerate(W):
        Winv[y] = x
    out = []
    for i, c in enumerate(ct):
        s = d * (i // n)
        out.append(ALPH[ein][(Winv[(IDX[eout][c] + s) % 26] - s) % 26])
    return "".join(out)


def exact_check(ct, positions, letters, ein, eout, n, d):
    """(feasible, checks): is there a wiring W with W(E_in(p)+s) = E_out(c)+s at every given position?
    checks = given positions - distinct inputs (each extra position on a used input is one equation)."""
    fwd, bwd = {}, {}
    for i, p in zip(positions, letters):
        s = d * (i // n)
        x, y = (IDX[ein][p] + s) % 26, (IDX[eout][ct[i]] + s) % 26
        if fwd.setdefault(x, y) != y or bwd.setdefault(y, x) != x:
            return False, None
    return True, len(positions) - len(fwd)


class Quad:
    def __init__(self):
        import array
        a = array.array("f")
        with open(ROOT / "k4kit/data/quad_log10.f32", "rb") as f:
            a.frombytes(f.read())
        self.t = a

    def score(self, txt):
        t, s = self.t, 0.0
        c = [ord(ch) - 65 for ch in txt]
        for i in range(len(c) - 3):
            s += t[((c[i] * 26 + c[i + 1]) * 26 + c[i + 2]) * 26 + c[i + 3]]
        return s


def anneal(ct, ein, eout, n, d, Q, rng, iters=20000, restarts=8, t0=2.0):
    """Blind: search the inverse wiring by simulated annealing on the quadgram score of the decode."""
    N = len(ct)
    xs = [(IDX[eout][c] + d * (i // n)) % 26 for i, c in enumerate(ct)]
    sh = [d * (i // n) for i in range(N)]
    inv_e = ALPH[ein]

    def dec(Winv):
        return "".join(inv_e[(Winv[x] - s) % 26] for x, s in zip(xs, sh))

    best = (-1e18, None, None)
    for _ in range(restarts):
        Winv = list(range(26))
        rng.shuffle(Winv)
        cur = Q.score(dec(Winv))
        for it in range(iters):
            T = t0 * (1 - it / iters) + 1e-3
            a, b = rng.randrange(26), rng.randrange(26)
            if a == b:
                continue
            Winv[a], Winv[b] = Winv[b], Winv[a]
            new = Q.score(dec(Winv))
            if new >= cur or rng.random() < math.exp((new - cur) / T):
                cur = new
            else:
                Winv[a], Winv[b] = Winv[b], Winv[a]
        if cur > best[0]:
            best = (cur, list(Winv), dec(Winv))
    return best
