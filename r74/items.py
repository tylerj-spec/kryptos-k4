"""R74 synthetic item builder (development and sealed holdout share it; no K4 data, no truth stored here).
Positives: 97 consecutive letters from a word start in a book, a 'misspelled' subset with 2 random letters changed
(Sanborn-like errors such as IQLUSION), enciphered by r74/sandwich.py's explicit encrypt under a raw setting drawn
uniformly from the 20,160. Negatives: R71's seven generators (r71/generators.py) on NEG_PT/NEG_KEY books, plus
frequency-preserving shuffles of positive ciphertexts."""
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "r74"))
sys.path.insert(0, str(ROOT / "r71"))
import sandwich as S  # noqa: E402
import generators as G  # noqa: E402

ARMS = ("OTP", "RUNKEY", "PERIODIC", "HOMOPHONIC", "GROMARK", "CTAK", "PTAK")


def passages(path, n, rng):
    words = re.findall(r"[A-Z]+", Path(path).read_text(encoding="utf-8", errors="ignore").upper())
    out = []
    while len(out) < n:
        i = rng.randrange(len(words) - 60)
        out.append("".join(words[i:i + 60])[:S.N])
    return out


def misspell(p, rng, k=2):
    q = list(p)
    for i in rng.sample(range(S.N), k):
        q[i] = rng.choice([c for c in S.A if c != q[i]])
    return "".join(q)


def build(books, n_per_book, n_missp_per_book, neg_pt, neg_key, n_per_arm, n_shuffle, rng, nrng):
    routes = S.load_routes()
    raw = list(S.configs(routes))
    items = []
    for book in books:
        for k, p in enumerate(passages(book, n_per_book, rng)):
            miss = k < n_missp_per_book
            if miss:
                p = misspell(p, rng)
            cfg, r = raw[rng.randrange(len(raw))]
            ct = S.encrypt(p, cfg["ka"], cfg["kb"], cfg["a"], cfg["b"], cfg["op_a"], cfg["op_b"], r)
            items.append({"kind": "POS_MISSPELLED" if miss else "POS", "pt": p, "setting": cfg, "ct": ct})
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


def true_key(it):
    cfg = it["setting"]
    r = S.load_routes()[cfg["route"]]
    return S.transform(cfg["ka"], cfg["kb"], cfg["a"], cfg["b"], cfg["op_a"], cfg["op_b"], r)
