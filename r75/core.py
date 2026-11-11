"""R75 core: alphabets, tableau stages and English scorers. No K4 data, no published letters.
Letters are A-Z codes 0..25 (numpy). An alphabet NAME has ALPH[NAME] (26 letters), IDX[NAME][code] = position of that
letter in the alphabet, LET[NAME][position] = letter code.
A STAGE is (pa, ca, ka, op): x = IDX[pa][p]; k = IDX[ka][key letter]; y = s*x + t*k (mod 26); c = LET[ca][y], with
(s, t) = VIG (1, 1), BEAU (-1, 1), VARB (1, -1). K1/K2 are (KRY, KRY, KRY, VIG)."""
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
N = 97
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def keyed(word):
    out = []
    for ch in word + AZ:
        if ch not in out:
            out.append(ch)
    return "".join(out)


ALPH = {"AZ": AZ, "KRY": keyed("KRYPTOS"), "PAL": keyed("PALIMPSEST"), "ABS": keyed("ABSCISSA")}
IDX = {n: np.array([a.index(ch) for ch in AZ], dtype=np.int16) for n, a in ALPH.items()}
LET = {n: np.array([ord(ch) - 65 for ch in a], dtype=np.int16) for n, a in ALPH.items()}
OPS = {"VIG": (1, 1), "BEAU": (-1, 1), "VARB": (1, -1)}
SCULPTURE_KEYS = ("KRYPTOS", "PALIMPSEST", "ABSCISSA")


def codes(text):
    return np.frombuffer(text.encode(), dtype=np.uint8).astype(np.int16) - 65


def text(row):
    return "".join(chr(65 + int(v)) for v in row)


def stage_dec(C, K, pa, ca, op):
    """Vectorised inverse of one stage. C letter codes, K key positions (broadcastable)."""
    s, t = OPS[op]
    return LET[pa][(s * (IDX[ca][C] - t * K)) % 26]


def stage_enc_text(pt, key_letters, pa, ca, ka, op):
    """Explicit scalar encryption of one stage (strings only; independent of the vectorised path)."""
    s, t = OPS[op]
    A_p, A_c, A_k = ALPH[pa], ALPH[ca], ALPH[ka]
    return "".join(A_c[(s * A_p.index(p) + t * A_k.index(k)) % 26] for p, k in zip(pt, key_letters))


def load_words(path=ROOT / "k4kit/data/word_model_orth.tsv", maxlen=18):
    words = {}
    for line in Path(path).read_text().splitlines():
        w, ex, _ = line.split()
        ex = float(ex)
        if ex > -1e90 and len(w) <= maxlen and w.isalpha():
            words[w] = ex
    return words


class Scorer:
    """quad: generic English quadgram table (k4kit/data/quad_log10.f32), mean log10 per quadgram;
    lm: R59 order-6 letter model (log10 per letter, no starting context); word: R59 word model, best segmentation,
    -7 per unknown letter (log10 per letter)."""

    def __init__(self, lm_path=None):
        self.quad = np.fromfile(ROOT / "k4kit/data/quad_log10.f32", dtype=np.float32)
        assert self.quad.size == 26 ** 4
        self.lm = None
        if lm_path is not None:
            mm = np.memmap(lm_path, dtype=np.uint8, mode="r")
            if bytes(mm[:5]) != b"R59LM":
                raise ValueError("not an R59 letter model")
            self.order = int(mm[5])
            off, sz, self.lm = 8, 26, {}
            for k in range(1, self.order + 1):
                self.lm[k] = np.memmap(lm_path, dtype=np.float32, mode="r", offset=off, shape=(sz,))
                off += sz * 4
                sz *= 26
        self.vocab = None

    def quad_score(self, P):
        P = P.astype(np.int32)
        idx = ((P[:, :-3] * 26 + P[:, 1:-2]) * 26 + P[:, 2:-1]) * 26 + P[:, 3:]
        return self.quad[idx].sum(axis=1, dtype=np.float64) / (P.shape[1] - 3)

    def lm_score(self, P):
        P = P.astype(np.int64)
        tot = np.zeros(P.shape[0])
        for i in range(P.shape[1]):
            L = min(i, self.order - 1)
            ctx = np.zeros(P.shape[0], dtype=np.int64)
            for j in range(i - L, i):
                ctx = ctx * 26 + P[:, j]
            tot += np.asarray(self.lm[L + 1][ctx * 26 + P[:, i]], dtype=np.float64)
        return tot / P.shape[1]

    def word_score(self, t, maxlen=18, oov=7.0):
        if self.vocab is None:
            self.vocab = load_words()
        best = [0.0] + [-1e18] * len(t)
        for i in range(len(t)):
            for L in range(1, min(maxlen, len(t) - i) + 1):
                v = max(self.vocab.get(t[i:i + L], -1e18), -oov * L)
                if best[i] + v > best[i + L]:
                    best[i + L] = best[i] + v
        return best[-1] / len(t)
