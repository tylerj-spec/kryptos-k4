"""Shared K4 constants and helpers (Claude, R29 toolkit). Pure Python 3.9+, no dependencies.

Conventions used everywhere in this toolkit:
- Positions are 0-based in code. The clues are EASTNORTHEAST at 0-based 21-33 (1-based 22-34) and BERLINCLOCK at
  0-based 63-73 (1-based 64-74).
- Substitution model: c_i = CA[(PA^-1(p_i) + k_i) mod 26] with plaintext alphabet PA and ciphertext alphabet CA.
- Rearrangement orders (R27 naming):
    "S_then_T": substitute in plaintext order, then rearrange:  CT[j] = X[perm[j]]
    "T_then_S": rearrange the plaintext, then substitute:       X[j] = P[perm[j]], CT[j] = sub(X[j], k_j)
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
BIN = ROOT / "bin"
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"           # keyed alphabet on the Kryptos tableau
ANCH = {21 + i: c for i, c in enumerate("EASTNORTHEAST")} | {63 + i: c for i, c in enumerate("BERLINCLOCK")}
MASK = "".join(ANCH.get(i, "?") for i in range(97))
assert len(K4) == 97 and K4[21:34] == "FLRVQQPRNGKSS" and K4[63:74] == "NYPVTTMZFPK"


def gromark_key(primer, n=97, digits=5):
    """Gromark/lagged-Fibonacci decimal stream: k_i = k_{i-L} + k_{i-L+1} mod 10 (L = digits; L=5 is standard)."""
    k = [int(x) for x in f"{int(primer):0{digits}d}"]
    while len(k) < n:
        k.append((k[-digits] + k[-digits + 1]) % 10)
    return k[:n]


def rot(n, w, cw):
    """K3's quarter-turn: write 0..n-1 in rows of width w (last row may be short), read columns. Verified on K3:
    plaintext[t] = ciphertext[q[t]] with q = [rot(336,24,True)[i] for i in rot(336,8,True)]."""
    rows = [list(range(i, min(i + w, n))) for i in range(0, n, w)]
    out = []
    for c in range(w):
        cc = c if cw else w - 1 - c
        for r in (range(len(rows) - 1, -1, -1) if cw else range(len(rows))):
            if cc < len(rows[r]):
                out.append(rows[r][cc])
    return out


def inv(p):
    q = [0] * len(p)
    for j, i in enumerate(p):
        q[i] = j
    return q


def route(name, n=97):
    """R27 route names like 'R24x8/CW/inv': double quarter-turn (w1 then w2), CW or CCW, forward or inverse.
    K3's own encryption direction corresponds to 'R24x8/CW/inv'."""
    dims, cwn, kind = name[1:].split("/")
    w1, w2 = map(int, dims.split("x"))
    cw = cwn == "CW"
    p1, p2 = rot(n, w1, cw), rot(n, w2, cw)
    p = [p1[i] for i in p2]
    return p if kind == "fwd" else inv(p)


R27_ROUTES = [f"R{a}x{b}/{d}/{k}" for a, b in ((24, 8), (23, 8), (25, 8), (24, 7), (24, 9))
              for d in ("CW", "CCW") for k in ("fwd", "inv")]


def setup(ct, perm, order, anch=ANCH):
    """Return (substitution-layer ciphertext, anchors at substitution positions, perm token for solver_s2kp)."""
    if order == "S_then_T":
        q = inv(perm)
        return "".join(ct[q[i]] for i in range(len(ct))), dict(anch), "-"
    if order == "T_then_S":
        return ct, {j: anch[i] for j, i in enumerate(perm) if i in anch}, ",".join(map(str, perm))
    raise ValueError(order)


def solver_line(label, key, ct, anch, seed, perm_token="-"):
    """One input line for bin/solver_s2kp: id KEY CT MASK SEED PERM (KEY letters A=0..Z=25)."""
    mask = "".join(anch.get(i, "?") for i in range(len(ct)))
    return f"{label} {''.join(chr(65 + (x % 26)) for x in key)} {ct} {mask} {seed} {perm_token}"
