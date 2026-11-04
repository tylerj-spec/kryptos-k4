"""R66 sealed helpers (pure Python, independent of the C++ solver): the R61 routes, un-routing, and the homophonic
witness: a decode map f (26 letters; '?' for cipher letters absent from the text) applied to the un-routed ciphertext
must give the plaintext exactly, with at most CAP cipher letters per plaintext letter."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CAP = 4


def routes():
    out = {}
    for line in (ROOT / "r61/routes.txt").read_text().splitlines():
        name, _, p = line.split()
        out[name] = [int(x) for x in p.split(",")]
    return out


def unroute(ct, perm):
    x = [""] * len(ct)
    for j, src in enumerate(perm):
        x[src] = ct[j]
    return "".join(x)


def witness_ok(ct, perm, plaintext, fmap):
    x = unroute(ct, perm)
    if len(fmap) != 26 or len(plaintext) != len(ct):
        return False
    if any(fmap[ord(c) - 65] != p for c, p in zip(x, plaintext)):
        return False
    used = {c for c in x}
    counts = {}
    for c in used:
        counts[fmap[ord(c) - 65]] = counts.get(fmap[ord(c) - 65], 0) + 1
    return max(counts.values()) <= CAP


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
