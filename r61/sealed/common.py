"""R61 SEALED helpers: independent encryptor (substitute, then transpose) and route table."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
ROUTES = {l.split()[0]: [int(x) for x in l.split()[2].split(",")] for l in (ROOT / "r61/routes.txt").read_text().splitlines()}


def sub(p, k, conv):
    xn, op = conv.split("_")
    X = AZ if xn == "AZ" else KRY
    return "".join(X[(X.index(a) + X.index(b)) % 26 if op == "VIG" else (X.index(b) - X.index(a)) % 26 if op == "BEAU"
                     else (X.index(a) - X.index(b)) % 26] for a, b in zip(p, k))


def encrypt(p, k, conv, route):
    x = sub(p, k, conv)
    perm = ROUTES[route]
    return "".join(x[perm[j]] for j in range(len(x)))
