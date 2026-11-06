"""R68 sealed helpers (pure Python, written independently of the C++ solver).
Paths: 'ID' (carved order) plus the 10 frozen R61 routes. For a path perm, CT[j] = Y[perm[j]] (Y = path-order text).
Models:
  M1 (substitute, then transpose; R61/R64 convention): plaintext order = path order, P = Q.
  M2 (position-aligned, key advances along the path): P[j] = Q[perm[j]], i.e. carved position j is enciphered in
     place at path step perm[j]: CT[j] = E(P[j], k_{perm[j]}).
Conventions: (Ap, Ac) in {AZ, KRY}^2 x op in {VIG, BEAU, VARB}; x = Ap^-1(p), y = Ac^-1(c):
  VIG y = x + k, BEAU y = k - x, VARB y = x - k (mod 26).
Families: PER (k_t = s[t mod p]), GRO (5-digit primer, d_t = d_{t-5} + d_{t-4} mod 10), CTAK (k_t = Ac^-1(Y[t-L]),
primer for t < L), PTAK (k_t = Ap^-1(Q[t-L]), primer for t < L)."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
ALPH = {"AZ": AZ, "KRY": KRY}
CONVS = [f"{a}/{c}_{op}" for a in ("AZ", "KRY") for c in ("AZ", "KRY") for op in ("VIG", "BEAU", "VARB")]
N = 97


def paths():
    out = {"ID": list(range(N))}
    for line in (ROOT / "r61/routes.txt").read_text().splitlines():
        name, order, p = line.split()
        assert order == "S_then_T"
        out[name] = [int(x) for x in p.split(",")]
    return out


def parse(conv):
    alph, op = conv.split("_")
    a, c = alph.split("/")
    return ALPH[a], ALPH[c], op


def enc_letter(p, k, conv):
    Ap, Ac, op = parse(conv)
    x = Ap.index(p)
    y = (x + k) if op == "VIG" else (k - x) if op == "BEAU" else (x - k)
    return Ac[y % 26]


def dec_letter(c, k, conv):
    Ap, Ac, op = parse(conv)
    y = Ac.index(c)
    x = (y - k) if op == "VIG" else (k - y) if op == "BEAU" else (y + k)
    return Ap[x % 26]


def encrypt_path(Q, family, conv, param, key):
    """Encrypt path-order plaintext Q; returns path-order ciphertext Y.
    PER: key = shift letters (A=0) of length p; GRO: key = 5-digit primer; CTAK/PTAK: key = primer shift letters."""
    Ap, Ac, _ = parse(conv)
    Y = []
    if family == "GRO":
        d = [int(ch) for ch in key]
        while len(d) < len(Q):
            d.append((d[-5] + d[-4]) % 10)
    for t, p in enumerate(Q):
        if family == "PER":
            k = AZ.index(key[t % len(key)])
        elif family == "GRO":
            k = d[t]
        else:
            L = int(param)
            if t < L:
                k = AZ.index(key[t])
            elif family == "CTAK":
                k = Ac.index(Y[t - L])
            else:
                k = Ap.index(Q[t - L])
        Y.append(enc_letter(p, k, conv))
    return "".join(Y)


def decrypt_path(Y, family, conv, param, key):
    Ap, Ac, _ = parse(conv)
    Q = []
    if family == "GRO":
        d = [int(ch) for ch in key]
        while len(d) < len(Y):
            d.append((d[-5] + d[-4]) % 10)
    for t, c in enumerate(Y):
        if family == "PER":
            k = AZ.index(key[t % len(key)])
        elif family == "GRO":
            k = d[t]
        else:
            L = int(param)
            if t < L:
                k = AZ.index(key[t])
            elif family == "CTAK":
                k = Ac.index(Y[t - L])
            else:
                k = Ap.index(Q[t - L])
        Q.append(dec_letter(c, k, conv))
    return "".join(Q)


def to_carved(Y, perm):
    return "".join(Y[perm[j]] for j in range(len(Y)))


def from_carved(CT, perm):
    y = [""] * len(CT)
    for j, t in enumerate(perm):
        y[t] = CT[j]
    return "".join(y)


def layout(Q, perm, model):
    """Plaintext order P from path order Q."""
    return Q if model == "M1" else "".join(Q[perm[j]] for j in range(len(Q)))


def unlayout(P, perm, model):
    if model == "M1":
        return P
    q = [""] * len(P)
    for j, t in enumerate(perm):
        q[t] = P[j]
    return "".join(q)


def witness_ok(CT, path, model, family, conv, param, key, plaintext):
    """Forward check: plaintext + key -> ciphertext through the model and path."""
    perm = paths()[path]
    Q = unlayout(plaintext, perm, model)
    return to_carved(encrypt_path(Q, family, conv, param, key), perm) == CT


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
