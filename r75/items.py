"""R75 synthetic item builder (development and the sealed holdout share it; no K4 data).
Positives: 97 consecutive letters from a word start in a book (some with 2 random letters changed, Sanborn-like
misspellings), enciphered by r75/families.py's explicit encryptor under a setting drawn uniformly from a sub-family.
Negatives: R71's seven wrong-family generators (r71/generators.py) on NEG_PT/NEG_KEY books, plus frequency-preserving
shuffles of positive ciphertexts."""
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "r75"))
sys.path.insert(0, str(ROOT / "r71"))
import core  # noqa: E402
import families as F  # noqa: E402
import generators as G  # noqa: E402

ARMS = ("OTP", "RUNKEY", "PERIODIC", "HOMOPHONIC", "GROMARK", "CTAK", "PTAK")


def passages(path, n, rng):
    words = re.findall(r"[A-Z]+", Path(path).read_text(encoding="utf-8", errors="ignore").upper())
    out = []
    while len(out) < n:
        i = rng.randrange(len(words) - 60)
        out.append("".join(words[i:i + 60])[:core.N])
    return out


def misspell(p, rng, k=2):
    q = list(p)
    for i in rng.sample(range(core.N), k):
        q[i] = rng.choice([c for c in core.AZ if c != q[i]])
    return "".join(q)


def build(books, per_sub_per_book, n_missp_per_book, neg_pt, neg_key, n_per_arm, n_shuffle, rng, nrng):
    """per_sub_per_book positives for each of the six sub-families from each book; the first n_missp_per_book of each
    book are misspelled."""
    items = []
    for book in books:
        plan = [s for s in F.SUBS for _ in range(per_sub_per_book)]
        rng.shuffle(plan)
        for k, (p, which) in enumerate(zip(passages(book, len(plan), rng), plan)):
            miss = k < n_missp_per_book
            if miss:
                p = misspell(p, rng)
            st = F.random_setting(rng, which)
            items.append({"kind": "POS_MISSPELLED" if miss else "POS", "sub": which, "pt": p, "setting": st,
                          "ct": F.encrypt(p, st)})
    letters = lambda p: np.frombuffer("".join(re.findall(r"[A-Z]", Path(p).read_text(  # noqa: E731
        encoding="utf-8", errors="ignore").upper())).encode(), dtype=np.uint8).astype(np.int16) - 65
    pt, kt = letters(neg_pt), letters(neg_key)
    r61 = [[int(x) for x in l.split()[2].split(",")] for l in (ROOT / "r61/routes.txt").read_text().splitlines()]
    for arm in ARMS:
        C, par = G.gen(arm, nrng, n_per_arm, pt, kt, r61)
        items += [{"kind": "NEG_" + arm, "param": int(par[i]), "ct": "".join(chr(65 + int(v)) for v in C[i])}
                  for i in range(n_per_arm)]
    for it in rng.sample([x for x in items if x["kind"].startswith("POS")], n_shuffle):
        c = list(it["ct"])
        rng.shuffle(c)
        items.append({"kind": "NEG_SHUFFLE", "ct": "".join(c)})
    return items
