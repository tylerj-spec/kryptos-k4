"""R80a: two keyword stages on different tableaux, one key from a list, the other free (r80/FABLE_IDENTIFIABILITY.md
§1.5-1.7). Synthetic only in R80a: no K4 data, no published letters.

Cipher (explicit, both directions):
  stage one   q_i = CA1[ s1*IDX[PA1][p_i] + t1*IDX[KA1][k1[i mod m1]] ]
  stage two   c_i = CA2[ s2*IDX[PA2][q_i] + t2*IDX[KA2][k2[i mod m2]] ]
  (s, t) = VIG (1, 1), BEAU (-1, 1), VARB (1, -1); alphabets AZ or KRY; CA1 != PA2 (if equal, the stages collapse to
  one Vigenere with the summed key, closed in L36).
Families:
  L1  listed key in stage one (a word, phase 0), free key in stage two;
  L2  listed key in stage two, free key in stage one;
  X1, X2  the same with the fixed key any string of 1-3 letters (mode X).
Conventions per family: PA1, CA1, PA2, CA2 (8 with CA1 != PA2) x listed-stage operation (3) x listed-key numbering
(AZ, KRY) x free-stage sign (VIG or BEAU; variant Beaufort and the numbering are absorbed by a free key) = 96.
Free key: 1..MFREE letters, any letters."""
import ctypes
import hashlib
import itertools
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "r75"))
sys.path.insert(0, str(ROOT / "r76"))
sys.path.insert(0, str(ROOT / "r79"))
import core  # noqa: E402
import solver as SV  # noqa: E402

N = 97
MFREE = 12
A2 = ("AZ", "KRY")
OPS = core.OPS
AZ = core.AZ
ALPH = core.ALPH
IDX = {k: v.astype(np.int64) for k, v in core.IDX.items()}
FAMS = ("L1", "L2", "X1", "X2")
CONVS = [(pa1, ca1, pa2, ca2, op, ka, sf) for pa1 in A2 for ca1 in A2 for pa2 in A2 for ca2 in A2 if ca1 != pa2
         for op in ("VIG", "BEAU", "VARB") for ka in A2 for sf in (1, -1)]
assert len(CONVS) == 96


@lru_cache(maxsize=1)
def word_list():
    """Listed keys: the 80 Kryptos words (r75/data/kryptos_words.txt) and every word of 3-15 letters in the R59 word
    model (k4kit/data/word_model_orth.tsv), sorted, without repeats."""
    import alphabets as AL
    w = set(AL.kryptos_words()) | {x for x in core.load_words(maxlen=15) if 3 <= len(x) <= 15}
    return sorted(x for x in w if x.isalpha() and x.isupper())


@lru_cache(maxsize=1)
def short_keys():
    """Mode X: every string of 1-3 letters (18,278)."""
    return ["".join(t) for n in (1, 2, 3) for t in itertools.product(AZ, repeat=n)]


def keys_for(fam):
    return word_list() if fam in ("L1", "L2") else short_keys()


def direction(fam):
    return 1 if fam in ("L1", "X1") else 2


# ------------------------------------------------------------------------------------------------ explicit cipher
def stages(st):
    """(stage-one (pa, ca, ka, s, t, key), stage-two (...)) for a setting."""
    pa1, ca1, pa2, ca2, op, ka, sf = st["conv"]
    lst = (OPS[op], ka, st["word"])
    fre = ((1, 1) if sf == 1 else (-1, 1), "AZ", st["free"])
    a, b = (lst, fre) if direction(st["fam"]) == 1 else (fre, lst)
    return (pa1, ca1) + a, (pa2, ca2) + b


def encrypt(pt, st):
    (pa1, ca1, (s1, t1), ka1, k1), (pa2, ca2, (s2, t2), ka2, k2) = stages(st)
    out = []
    for i, p in enumerate(pt):
        u = (s1 * ALPH[pa1].index(p) + t1 * ALPH[ka1].index(k1[i % len(k1)])) % 26
        q = ALPH[ca1][u]
        v = (s2 * ALPH[pa2].index(q) + t2 * ALPH[ka2].index(k2[i % len(k2)])) % 26
        out.append(ALPH[ca2][v])
    return "".join(out)


def decrypt(ct, st):
    (pa1, ca1, (s1, t1), ka1, k1), (pa2, ca2, (s2, t2), ka2, k2) = stages(st)
    out = []
    for i, c in enumerate(ct):
        x2 = (s2 * (ALPH[ca2].index(c) - t2 * ALPH[ka2].index(k2[i % len(k2)]))) % 26
        q = ALPH[pa2][x2]
        x1 = (s1 * (ALPH[ca1].index(q) - t1 * ALPH[ka1].index(k1[i % len(k1)]))) % 26
        out.append(ALPH[pa1][x1])
    return "".join(out)


# ------------------------------------------------------------------------------------------------ solver tables
def tables(conv):
    """(H, P1, s_list, t_list, s_free, ka) for the C pass; see r80a/twostage.c."""
    pa1, ca1, pa2, ca2, op, ka, sf = conv
    H = np.array([IDX[ca1][AZ.index(ALPH[pa2][v])] for v in range(26)], dtype=np.uint8)
    P1 = np.array([AZ.index(ALPH[pa1][x]) for x in range(26)], dtype=np.uint8)
    s, t = OPS[op]
    return H, P1, s, t, sf, ka


@lru_cache(maxsize=8)
def packed(fam, ka):
    ks = keys_for(fam)
    codes = np.concatenate([IDX[ka][core.codes(k).astype(np.int64)] for k in ks]).astype(np.uint8)
    lens = np.array([len(k) for k in ks], dtype=np.int32)
    offs = np.concatenate([[0], np.cumsum(lens)[:-1]]).astype(np.int32)
    return codes, offs, lens


_LIB = None


def lib():
    global _LIB
    if _LIB is None:
        src = HERE / "twostage.c"
        h = hashlib.sha256(src.read_bytes()).hexdigest()[:16]
        so = HERE / ".build" / f"twostage_{h}.so"
        if not so.exists():
            so.parent.mkdir(exist_ok=True)
            tmp = so.with_suffix(".tmp.so")
            subprocess.run(["gcc", "-O2", "-shared", "-fPIC", "-o", str(tmp), str(src)], check=True)
            tmp.replace(so)
        L = ctypes.CDLL(str(so))
        P, I = ctypes.c_void_p, ctypes.c_int
        L.two_scan.argtypes = [I, P, I, P, P, I, I, I, I, P, P, P, I, P, P, I, P]
        L.two_build.argtypes = [I, P, I, P, P, I, I, I, P, I, P, P]
        L.two_scan_ref.argtypes = [I, P, I, P, P, I, I, I, I, P, P, P, I, P, P, P]
        _LIB = L
    return _LIB


def _p(a):
    return a.ctypes.data_as(ctypes.c_void_p)


def ycodes(ct, conv):
    return IDX[conv[3]][core.codes(ct).astype(np.int64)].astype(np.uint8)


def scan(ct, fam, ci, sweeps=0):
    """Pass-0 scores [n_keys, MFREE] for one family and convention."""
    conv = CONVS[ci]
    H, P1, s, t, sf, ka = tables(conv)
    y = np.ascontiguousarray(ycodes(ct, conv))
    codes, offs, lens = packed(fam, ka)
    out = np.zeros((len(lens), MFREE), dtype=np.float32)
    lib().two_scan(N, _p(y), direction(fam), _p(H), _p(P1), s, t, sf, len(lens), _p(codes), _p(offs), _p(lens), MFREE,
                   _p(SV.QUAD), _p(SV.UNI), int(sweeps), _p(out))
    return out


def scan_ref(ct, fam, ci, wi_lo, wi_hi):
    """Reference pass 0 (one key at a time) for keys wi_lo..wi_hi-1; the tests compare it with scan()."""
    conv = CONVS[ci]
    H, P1, s, t, sf, ka = tables(conv)
    y = np.ascontiguousarray(ycodes(ct, conv))
    codes, offs, lens = packed(fam, ka)
    o = np.ascontiguousarray(offs[wi_lo:wi_hi])
    ln = np.ascontiguousarray(lens[wi_lo:wi_hi])
    out = np.zeros((wi_hi - wi_lo, MFREE), dtype=np.float32)
    lib().two_scan_ref(N, _p(y), direction(fam), _p(H), _p(P1), s, t, sf, wi_hi - wi_lo, _p(codes), _p(o), _p(ln),
                       MFREE, _p(SV.QUAD), _p(SV.UNI), _p(out))
    return out


def build(ct, fam, ci, wi):
    """(z[97], OUT[97, 26]) for the full solver (r79 slot_batch) with the listed key fixed."""
    conv = CONVS[ci]
    H, P1, s, t, sf, ka = tables(conv)
    y = np.ascontiguousarray(ycodes(ct, conv))
    codes, offs, lens = packed(fam, ka)
    key = np.ascontiguousarray(codes[offs[wi]:offs[wi] + lens[wi]])
    z = np.zeros(N, dtype=np.uint8)
    out = np.zeros((N, 26), dtype=np.uint8)
    lib().two_build(N, _p(y), direction(fam), _p(H), _p(P1), s, t, sf, _p(key), int(lens[wi]), _p(z), _p(out))
    return z, out


def setting(fam, ci, wi, m, delta):
    """Setting dict from a solver result. The free stage decrypts with shift delta = -key value (s_free folded into
    the output table), so the free key letter of slot j is AZ[-delta[j]]."""
    return {"fam": fam, "conv": list(CONVS[ci]), "word": keys_for(fam)[wi],
            "free": "".join(AZ[(-int(d)) % 26] for d in delta[:m]), "m_free": m}


def decode_with(z, out, m, delta):
    return "".join(AZ[out[i][(int(z[i]) + int(delta[i % m])) % 26]] for i in range(N))


def log10_settings():
    """Theorem K count per family: settings times 26^(free letters)."""
    ms = np.arange(1, MFREE + 1)
    one = float(np.log10(np.sum(26.0 ** ms)))
    return {f: float(np.log10(len(keys_for(f)) * len(CONVS)) + one) for f in FAMS}


def random_setting(rng, fam, mlo=1, mhi=10, lw_lo=3, lw_hi=12):
    """A plant: the listed key is a word from the list (length lw_lo..lw_hi, chosen uniformly by length) for L1/L2, or
    a random 1-3 letter key for X1/X2; the free key has mlo..mhi random letters."""
    if fam in ("L1", "L2"):
        ws = word_list()
        lw = rng.randint(lw_lo, lw_hi)
        cand = [w for w in ws if len(w) == lw]
        word = cand[rng.randrange(len(cand))]
    else:
        word = "".join(rng.choice(AZ) for _ in range(rng.randint(1, 3)))
    m = rng.randint(mlo, mhi)
    return {"fam": fam, "conv": list(CONVS[rng.randrange(len(CONVS))]), "word": word,
            "free": "".join(rng.choice(AZ) for _ in range(m)), "m_free": m}
