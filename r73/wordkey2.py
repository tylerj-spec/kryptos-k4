"""R73b solver for Family R26 (26-letter Ragbaby-like word-progressive cipher; see r73/wordkey.py for the cipher).
Change from R73 (r73/wordkey.py, frozen): an out-of-vocabulary word is scored by the R59 order-6 English LETTER model
(log10, as the word model) plus a fixed per-word penalty POOV, instead of a flat 7 per letter. A plausible unknown
word (a name such as WICKHAM) then beats a dictionary prefix followed by garbage (WICK + KDPVLR), which is what
desynchronised the word counter in R73's R26 failures. Everything else (settings, word model, DP over (position,
phase of the next word)) is unchanged. No K4 data.
Usage: from wordkey2 import Solver; s = Solver(LM_PATH, POOV); s.solve(ct) -> list of decodes, best first."""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "r73"))
import wordkey as W  # noqa: E402

MAXLEN = W.MAXLEN


class Solver:
    def __init__(self, lm_path, poov):
        mm = np.memmap(lm_path, dtype=np.uint8, mode="r")
        if bytes(mm[:5]) != b"R59LM":
            raise ValueError("not an R59 letter model")
        self.order = int(mm[5])
        off, sz, self.lm = 8, 26, {}
        for k in range(1, self.order + 1):
            self.lm[k] = np.memmap(lm_path, dtype=np.float32, mode="r", offset=off, shape=(sz,))
            off += sz * 4
            sz *= 26
        self.poov = float(poov)
        self.words = W.load_words()
        self.cache = {}

    def letter_score(self, w):
        """log10 probability of the word's letters under the letter model, starting with no context."""
        v = self.cache.get(w)
        if v is None:
            s = [ord(c) - 65 for c in w]
            v = 0.0
            for i in range(len(s)):
                L = min(i, self.order - 1)
                c = 0
                for j in range(i - L, i):
                    c = c * 26 + s[j]
                v += float(self.lm[L + 1][c * 26 + s[i]])
            self.cache[w] = v
        return v

    def solve_alphabet(self, ct, alph):
        A = W.ALPH[alph]
        n = len(ct)
        y = [A.index(c) for c in ct]
        seg = {}
        for i in range(n):
            for L in range(1, min(MAXLEN, n - i) + 1):
                for s in range(26):
                    w = "".join(A[(y[i + t] - s - t) % 26] for t in range(L))
                    known = self.words.get(w)
                    seg[i, L, s] = (w, known if known is not None else self.letter_score(w) + self.poov,
                                    known is not None)
        out = {}
        for b in range(26):
            best = {(0, (1 + b) % 26): 0.0}
            back = {}
            for i in range(n):
                for s in range(26):
                    cur = best.get((i, s))
                    if cur is None:
                        continue
                    for L in range(1, min(MAXLEN, n - i) + 1):
                        w, sc, known = seg[i, L, s]
                        key = (i + L, (s + 1) % 26)
                        v = cur + sc
                        if v > best.get(key, -1e18):
                            best[key], back[key] = v, (i, s, w, known)
            v, k = max((v, k) for k, v in best.items() if k[0] == n)
            ws, oov = [], 0
            while k[0] > 0:
                i, s, w, known = back[k]
                ws.append(w)
                oov += not known
                k = (i, s)
            out[b] = {"score": v, "words": ws[::-1], "oov": oov}
        return out

    def solve(self, ct):
        res = []
        for a in W.ALPH:
            for b, r in self.solve_alphabet(ct, a).items():
                res.append({"family": "R26", "setting": [a, b], **r})
        res.sort(key=lambda d: -d["score"])
        return res
