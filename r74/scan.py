"""R74 full scan (no K4 data in this file): decrypt a 97-letter ciphertext under all 15,680 distinct transforms and
score every decrypt with the R59 order-6 letter model (log10, no starting context; the same model as r73/wordkey2.py).
Vectorised with numpy; one ciphertext takes well under a second once the model is in the page cache.
Usage: from scan import Scanner; s = Scanner(LM_PATH); res = s.scan(ct) -> per-transform scores, best first."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sandwich as S  # noqa: E402

AZI = np.array([ord(c) - 65 for c in S.A], dtype=np.int64)   # KRYPTOS-alphabet rank -> A-Z index


class Scanner:
    def __init__(self, lm_path):
        mm = np.memmap(lm_path, dtype=np.uint8, mode="r")
        if bytes(mm[:5]) != b"R59LM":
            raise ValueError("not an R59 letter model")
        self.order = int(mm[5])
        off, sz, self.lm = 8, 26, {}
        for k in range(1, self.order + 1):
            self.lm[k] = np.memmap(lm_path, dtype=np.float32, mode="r", offset=off, shape=(sz,))
            off += sz * 4
            sz *= 26
        self.routes = S.load_routes()
        cls = S.classes(self.routes)
        self.keys = list(cls)
        self.labels = [v for v in cls.values()]
        rname = {v: k for k, v in self.routes.items()}
        self.route_name = [rname[k[0]] for k in self.keys]
        R = np.array([k[0] for k in self.keys], dtype=np.int64)
        self.rinv = np.argsort(R, axis=1)
        self.sig = np.array([k[1] for k in self.keys], dtype=np.int64)[:, None]
        self.V = np.array([k[2] for k in self.keys], dtype=np.int64)

    def decrypt_all(self, ct):
        """(15680, 97) plaintexts as A-Z indices (plaintext order)."""
        c = np.array([S.IDX[ch] for ch in ct], dtype=np.int64)[None, :]
        y = (self.sig * (c - self.V)) % 26                      # P[r[j]] in ciphertext order j
        return AZI[np.take_along_axis(y, self.rinv, axis=1)]    # reorder to plaintext order i

    def lm_score(self, P):
        n = P.shape[1]
        tot = np.zeros(P.shape[0])
        for i in range(n):
            L = min(i, self.order - 1)
            ctx = np.zeros(P.shape[0], dtype=np.int64)
            for j in range(i - L, i):
                ctx = ctx * 26 + P[:, j]
            tot += np.asarray(self.lm[L + 1][ctx * 26 + P[:, i]], dtype=np.float64)
        return tot

    def scan(self, ct):
        P = self.decrypt_all(ct)
        sc = self.lm_score(P)
        order = np.argsort(-sc, kind="stable")
        return P, sc, order

    def text(self, row):
        return "".join(chr(65 + int(x)) for x in row)
