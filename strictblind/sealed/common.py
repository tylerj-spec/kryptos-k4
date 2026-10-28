"""strictblind SEALED helpers: the known clue letters and an encryptor written independently of blind/scan.cpp."""
import hashlib
from pathlib import Path

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
CLUES = {21 + i: c for i, c in enumerate("EASTNORTHEAST")} | {63 + i: c for i, c in enumerate("BERLINCLOCK")}
ALPHABETS = {"AZ": AZ, "KRY": KRY, "PAL": "PALIMSETBCDFGHJKNOQRUVWXYZ", "ABS": "ABSCIDEFGHJKLMNOPQRTUVWXYZ"}
N = 97


def letters(path):
    return "".join(c for c in Path(path).read_text().upper() if "A" <= c <= "Z")


def read_routes(path):
    out = {}
    for ln in Path(path).read_text().splitlines():
        if ln.strip():
            name, order, ps = ln.split()
            p = [int(x) for x in ps.split(",")]
            assert sorted(p) == list(range(N))
            out[name, order] = p
    return out


def make_key(kind, arg, spec, text_cache={}):
    """kind TEXT: spec 'fwd|rev/AZ|KRY/offN'; kind CHAIN: spec 'primerDDD'."""
    if kind == "TEXT":
        if arg not in text_cache:
            text_cache[arg] = letters(arg)
        d, num, off = spec.split("/")
        s = text_cache[arg] if d == "fwd" else text_cache[arg][::-1]
        al = AZ if num == "AZ" else KRY
        o = int(off[3:])
        return [al.index(c) for c in s[o:o + N]]
    if kind == "CHAIN":
        base, b = 10, int(arg)
    elif kind in ("CHAINBASE", "CHAINALPH"):
        base, b = map(int, arg.split(","))
    else:
        raise ValueError(f"invalid key kind: {kind}")
    symbols = "0123456789ABCDEFGHIJKLMNOP"
    k = [symbols.index(c) for c in spec[6:]]
    if len(k) != b or any(x >= base for x in k):
        raise ValueError("invalid base primer")
    while len(k) < N:
        k.append((k[-b] + k[-b + 1]) % base)
    return k


def encrypt(plain, perm, order, key, pa, ca, op):
    """Forward encryption, written from the definitions: S_then_T CT[j] = X[perm[j]] with X[i] = sub(P[i], k_i);
    T_then_S CT[j] = sub(P[perm[j]], k_j); ID CT[j] = sub(P[j], k_j)."""
    out = []
    for j in range(N):
        t = j if order == "ID" else perm[j]
        k = key[t] if order == "S_then_T" else key[j]
        x = pa.index(plain[t])
        out.append(ca[(x + k) % 26 if op == "VIG" else (k - x) % 26 if op == "BEAU" else (x - k) % 26])
    return "".join(out)


def check_frozen(exp):
    for ln in (Path(exp) / "FROZEN.sha256").read_text().splitlines():
        h, f = ln.split(maxsplit=1)
        assert hashlib.sha256((Path(exp) / f.strip()).read_bytes()).hexdigest() == h, f"{f} changed after freeze"
