"""R76 blind fixed-method families (no K4 data, no published letters). Every member turns a 97-letter ciphertext into
exactly one text.
  B1  (H1) one keyword stage with KEYED ALPHABETS on both sides: plaintext alphabet PA and ciphertext alphabet CA each
      one of 81 (A-Z and the 'asc' alphabet of every r75/data/kryptos_words.txt word), key = one of those 80 words
      (phase 0), key numbering AZ or KRY, VIG/BEAU/VARB.                                         3,149,280 methods
  B2  (H2) a keyword key SCRAMBLED by a sheet route, message in place: key letter at position j = word[(p[j] + phase)
      mod |word|] with p a route of r76/routes76.py sets sheet36 + rot2 + rot1 (17,524 routes); words KRYPTOS,
      PALIMPSEST, ABSCISSA at every phase; PA, CA, key numbering in AZ/KRY; VIG/BEAU/VARB.         10,514,400 methods
  B3  (H2c) R74's K1 -> K3 -> K2 sandwich (r74/sandwich.py) with R72's sheet routes (sheet36) in place of the R61 routes:
      all keyword orders, phases and operations.                                                    36,960 methods
A stage: x = IDX[pa][p]; k = IDX[ka][key letter]; y = s*x + t*k (mod 26); c = LET[ca][y]; (s, t) = VIG (1, 1),
BEAU (-1, 1), VARB (1, -1).
API (as r75/families.py): batches(C) -> (P, meta); setting(meta, row); encrypt(pt, setting); sub(setting);
random_setting(rng, which); SUBS; count()."""
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "r75"))
sys.path.insert(0, str(ROOT / "r76"))
import core  # noqa: E402
import routes76 as RT  # noqa: E402
import alphabets as AL  # noqa: E402

N, AZ = core.N, core.AZ
OPS = core.OPS
OPN = ("VIG", "BEAU", "VARB")
SUBS = ("B1", "B2", "B3")
A2 = ("AZ", "KRY")
B2_WORDS = core.SCULPTURE_KEYS
CHUNK = 1000


def arrays(a):
    return (np.array([a.index(ch) for ch in AZ], dtype=np.int16), np.array([ord(ch) - 65 for ch in a], dtype=np.int16))


@lru_cache(maxsize=1)
def b1_alphabets():
    words = AL.kryptos_words()
    names = ["AZ"] + words
    alph = [AZ] + [AL.variants(w)["asc"] for w in words]
    idx = np.stack([arrays(a)[0] for a in alph])
    let = np.stack([arrays(a)[1] for a in alph])
    return names, alph, words, idx, let


@lru_cache(maxsize=1)
def b2_routes():
    rs = RT.merged(["sheet36", "rot2", "rot1"])
    return [n for n, _ in rs], np.array([p for _, p in rs], dtype=np.int64)


def b2_labels():
    return [(w, ph) for w in B2_WORDS for ph in range(len(w))]


@lru_cache(maxsize=1)
def b3_classes():
    routes = {n: p for n, p in RT.merged(["sheet36"])}
    cls = RT.SW.classes(routes)
    keys = list(cls)
    labels = [v[0] for v in cls.values()]
    rname = {v: k for k, v in routes.items()}
    R = np.array([k[0] for k in keys], dtype=np.int64)
    return keys, labels, [rname[k[0]] for k in keys], np.argsort(R, axis=1), \
        np.array([k[1] for k in keys], dtype=np.int64)[:, None], np.array([k[2] for k in keys], dtype=np.int64), routes


def key_positions(words, phases, ka, idx_map=None):
    """K[r, i] = IDX[ka][word_r[(index[r, i] + phase_r) mod len_r]]; index = i unless idx_map (R, 97) is given."""
    ia = core.IDX[ka]
    out = np.zeros((len(words), N), dtype=np.int64)
    for r, (w, ph) in enumerate(zip(words, phases)):
        wc = ia[core.codes(w)].astype(np.int64)
        ii = np.arange(N) if idx_map is None else idx_map[r]
        out[r] = wc[(ii + ph) % len(w)]
    return out


# ------------------------------------------------------------------------------------------- enumeration
def batches_B1(C):
    names, alph, words, IDXA, LETA = b1_alphabets()
    for ka in A2:
        K = key_positions(words, [0] * len(words), ka)                              # (80, 97)
        for op in OPN:
            s, t = OPS[op]
            for ci in range(len(alph)):
                X = (s * (IDXA[ci][C][None, :].astype(np.int64) - t * K)) % 26       # (80, 97)
                P = LETA[:, X]                                                        # (81, 80, 97)
                yield P.reshape(-1, N), ("B1", "", ka, op, ci, len(words))


def batches_B2(C):
    rnames, RA = b2_routes()
    labels = b2_labels()
    lw, lp = [w for w, _ in labels], [p for _, p in labels]
    for ka in A2:
        base = key_positions(lw, lp, ka)                                             # (25, 97): key at position i
        for c0 in range(0, len(RA), CHUNK):
            Rc = RA[c0:c0 + CHUNK]
            Kr = base[:, Rc].transpose(1, 0, 2).reshape(-1, N)                        # (nr*25, 97)
            for pa in A2:
                for ca in A2:
                    y = core.IDX[ca][C].astype(np.int64)[None, :]
                    for op in OPN:
                        s, t = OPS[op]
                        yield core.LET[pa][(s * (y - t * Kr)) % 26], ("B2", "", ka, pa, ca, op, c0)


def batches_B3(C):
    keys, labels, rn, rinv, sig, V, _ = b3_classes()
    c = core.IDX["KRY"][C].astype(np.int64)[None, :]
    y = (sig * (c - V)) % 26
    azi = np.array([ord(ch) - 65 for ch in core.ALPH["KRY"]], dtype=np.int16)
    yield azi[np.take_along_axis(y, rinv, axis=1)], ("B3", "")


def batches(C):
    yield from batches_B1(C)
    yield from batches_B2(C)
    yield from batches_B3(C)


def setting(meta, row):
    row = int(row)
    if meta[0] == "B1":
        _, _, ka, op, ci, nw = meta
        names, alph, words, _, _ = b1_alphabets()
        pi, wi = divmod(row, nw)
        return {"family": "B1", "pa": names[pi], "ca": names[ci], "ka": ka, "op": op, "word": words[wi], "phase": 0}
    if meta[0] == "B2":
        _, _, ka, pa, ca, op, c0 = meta
        rnames, _ = b2_routes()
        ri, li = divmod(row, len(b2_labels()))
        w, ph = b2_labels()[li]
        return {"family": "B2", "pa": pa, "ca": ca, "ka": ka, "op": op, "word": w, "phase": ph, "route": rnames[c0 + ri]}
    keys, labels, rn, _, _, _, _ = b3_classes()
    return {"family": "B3", **labels[row]}


def sub(st):
    return st["family"]


# ------------------------------------------------------------------------------------------- explicit encryptors
def _alpha(name):
    if name in core.ALPH:
        return core.ALPH[name]
    return AL.variants(name)["asc"]


def stage_text(pt, keys, pa, ca, ka, op):
    s, t = OPS[op]
    P, Cc, Kk = _alpha(pa), _alpha(ca), _alpha(ka)
    return "".join(Cc[(s * P.index(p) + t * Kk.index(k)) % 26] for p, k in zip(pt, keys))


def encrypt(pt, st):
    if st["family"] == "B1":
        w = st["word"]
        return stage_text(pt, [w[(i + st["phase"]) % len(w)] for i in range(N)], st["pa"], st["ca"], st["ka"], st["op"])
    if st["family"] == "B2":
        rnames, RA = b2_routes()
        p = RA[rnames.index(st["route"])]
        w = st["word"]
        return stage_text(pt, [w[(int(p[j]) + st["phase"]) % len(w)] for j in range(N)], st["pa"], st["ca"], st["ka"],
                          st["op"])
    routes = b3_classes()[6]
    return RT.SW.encrypt(pt, st["ka"], st["kb"], st["a"], st["b"], st["op_a"], st["op_b"], routes[st["route"]])


def random_setting(rng, which):
    if which == "B1":
        names, _, words, _, _ = b1_alphabets()
        return {"family": "B1", "pa": rng.choice(names), "ca": rng.choice(names), "ka": rng.choice(A2),
                "op": rng.choice(OPN), "word": rng.choice(words), "phase": 0}
    if which == "B2":
        rnames, _ = b2_routes()
        w, ph = rng.choice(b2_labels())
        return {"family": "B2", "pa": rng.choice(A2), "ca": rng.choice(A2), "ka": rng.choice(A2), "op": rng.choice(OPN),
                "word": w, "phase": ph, "route": rng.choice(rnames)}
    keys, labels, _, _, _, _, _ = b3_classes()
    return {"family": "B3", **labels[rng.randrange(len(labels))]}


def count():
    names, _, words, _, _ = b1_alphabets()
    return {"B1": len(names) ** 2 * len(words) * 2 * 3, "B2": len(b2_routes()[0]) * len(b2_labels()) * 2 * 4 * 3,
            "B3": len(b3_classes()[0])}
