"""R70 sealed helpers (pure Python, written independently of the C++ scanner).
Rows (21, as R68): 'ID' (carved order, in place) plus the 10 frozen R61 routes x models M1/M2. For a route perm:
  M1: Y[t] = E(P[t], key[t]) in path order, CT[j] = Y[perm[j]]  (plaintext P in path order);
  M2: CT[j] = E(P[j], key[perm[j]])                                (plaintext P in carved order);
  ID: CT[j] = E(P[j], key[j]).
key = the 97-letter window of the normalised source starting at the offset.
Conventions (6): tableau A in {AZ, KRY} for plaintext, ciphertext and key letter; x = A^-1(p), y = A^-1(c),
k = A^-1(key letter): VIG y = x + k, BEAU y = k - x, VARB y = x - k (mod 26)."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
CONVS = [f"{a}_{op}" for a in ("AZ", "KRY") for op in ("VIG", "BEAU", "VARB")]
N = 97


def routes():
    out = {}
    for line in (ROOT / "r61/routes.txt").read_text().splitlines():
        name, order, p = line.split()
        assert order == "S_then_T"
        out[name] = [int(x) for x in p.split(",")]
    return out


def rows():
    r = [("ID", "M1")]
    for name in routes():
        r += [(name, "M1"), (name, "M2")]
    return r


def enc_letter(p, kl, conv):
    a, op = conv.split("_")
    A = AZ if a == "AZ" else KRY
    x, k = A.index(p), A.index(kl)
    return A[((x + k) if op == "VIG" else (k - x) if op == "BEAU" else (x - k)) % 26]


def dec_letter(c, kl, conv):
    a, op = conv.split("_")
    A = AZ if a == "AZ" else KRY
    y, k = A.index(c), A.index(kl)
    return A[((y - k) if op == "VIG" else (k - y) if op == "BEAU" else (y + k)) % 26]


def encrypt(P, key, path, model, conv):
    if path == "ID":
        return "".join(enc_letter(P[j], key[j], conv) for j in range(N))
    perm = routes()[path]
    if model == "M1":
        Y = [enc_letter(P[t], key[t], conv) for t in range(N)]
        return "".join(Y[perm[j]] for j in range(N))
    return "".join(enc_letter(P[j], key[perm[j]], conv) for j in range(N))


def decrypt(CT, key, path, model, conv):
    if path == "ID":
        return "".join(dec_letter(CT[j], key[j], conv) for j in range(N))
    perm = routes()[path]
    if model == "M1":
        Y = [""] * N
        for j, t in enumerate(perm):
            Y[t] = CT[j]
        return "".join(dec_letter(Y[t], key[t], conv) for t in range(N))
    return "".join(dec_letter(CT[j], key[perm[j]], conv) for j in range(N))


def witness_ok(CT, source_text, d):
    """d: a frozen decode {offset, path, model, convention, plaintext, keytext}."""
    key = source_text[d["offset"]:d["offset"] + N]
    return key == d["keytext"] and encrypt(d["plaintext"], key, d["path"], d["model"], d["convention"]) == CT


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
