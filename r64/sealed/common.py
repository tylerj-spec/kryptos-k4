"""R64 sealed helpers (pure Python, independent of the C++ solver): letterwise encryption, the R61 routes, and the
full forward witness  P, K, convention, route  ->  CT[j] = X[perm[j]],  X[i] = S(P[i], K[i])."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"


def enc(p, k, conv):
    xn, op = conv.split("_")
    X = AZ if xn == "AZ" else KRY
    return "".join(X[(X.index(a) + X.index(b)) % 26 if op == "VIG" else (X.index(b) - X.index(a)) % 26 if op == "BEAU"
                     else (X.index(a) - X.index(b)) % 26] for a, b in zip(p, k))


def routes():
    out = {}
    for line in (ROOT / "r61/routes.txt").read_text().splitlines():
        name, _, p = line.split()
        out[name] = [int(x) for x in p.split(",")]
    return out


def forward(p, k, conv, perm):
    x = enc(p, k, conv)
    return "".join(x[perm[j]] for j in range(len(x)))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
