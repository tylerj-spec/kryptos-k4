#!/usr/bin/env python3
"""Tyler's strict check (R30 follow-up): start from the original K4 ciphertext, decrypt with a FIXED, fully specified
method (no fitted alphabets), and see whether the 24 known letters come out by themselves.
Key: every 97-letter window of the Carter text (forward/reversed; key letters numbered A-Z or KRYPTOS).
Alphabets: plaintext and ciphertext alphabet each A-Z or KRYPTOS (4 pairs). Operations: Vigenere, Beaufort,
variant Beaufort. 48 conventions x 282,828 windows = 13.6 M decryptions. Planted control first."""
import json
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e4_book as eb  # noqa: E402
from r30lib import ANCH, AZ, HERE, K4, RUNS  # noqa: E402
from k4common import KRY  # noqa: E402

BOOK = HERE.parents[1] / "archive" / "sources" / "carter_mace_1923_v1_doran_google_ocr.txt"
POS = np.array(sorted(ANCH))
ALPH = {"AZ": AZ, "KRY": KRY}
OPS = ("vig", "beau", "varb")


def decrypt_positions(ct, keys, pa, ca, op):
    """keys: (W, 97) ints. Returns (W, 24) plaintext letter indices (A=0) at the clue positions."""
    cinv = np.array([ALPH[ca].index(ct[i]) for i in POS])
    k = keys[:, POS]
    r = {"vig": cinv - k, "beau": k - cinv, "varb": cinv + k}[op] % 26
    pmap = np.array([AZ.index(ch) for ch in ALPH[pa]])
    return pmap[r]


def scan(ct, text):
    want = np.array([AZ.index(ANCH[i]) for i in POS])
    best, hist, full = (0, None), np.zeros(25, dtype=np.int64), []
    for d, s in (("fwd", text), ("rev", text[::-1])):
        for kn in ("AZ", "KRY"):
            v = np.array([ALPH[kn].index(c) for c in s], dtype=np.int64)
            W = len(v) - 96
            keys = np.lib.stride_tricks.sliding_window_view(v, 97)[:W]
            for pa in ALPH:
                for ca in ALPH:
                    for op in OPS:
                        m = (decrypt_positions(ct, keys, pa, ca, op) == want).sum(axis=1)
                        hist += np.bincount(m, minlength=25)
                        j = int(m.argmax())
                        if m[j] > best[0]:
                            best = (int(m[j]), f"{d}/{kn}/PA={pa}/CA={ca}/{op}/off{j}")
                        full += [f"{d}/{kn}/PA={pa}/CA={ca}/{op}/off{o}" for o in np.nonzero(m == 24)[0]]
    return best, hist, full


if __name__ == "__main__":
    text, _ = eb.normalise(BOOK.read_bytes().decode("utf-8", errors="replace"))
    # planted control: a known message encrypted with a Carter window under fixed KRYPTOS alphabets (Vigenere)
    P = json.loads((HERE.parent / "data" / "reference_messages.json").read_text())["calibration"][3]
    rng = random.Random(30008)
    off = rng.randrange(len(text) - 97)
    k = [KRY.index(c) for c in text[off:off + 97]]
    ct_plant = "".join(KRY[(KRY.index(P[t]) + k[t]) % 26] for t in range(97))
    pb, _, pf = scan(ct_plant, text)
    print(f"planted control (true window fwd/KRY/off{off}, PA=CA=KRY, vig): best {pb[0]}/24 at {pb[1]}; "
          f"full 24/24 matches: {pf}", flush=True)
    b, h, full = scan(K4, text)
    total = int(h.sum())
    print(f"K4: {total:,} fixed-method decryptions. Best: {b[0]}/24 clue letters ({b[1]}). Full 24/24 matches: "
          f"{len(full)}")
    print("how many decryptions got k of 24 clue letters right:",
          {kk: int(h[kk]) for kk in range(25) if h[kk]})
    json.dump({"planted_best": pb, "planted_full": pf, "k4_best": b, "k4_hist": h.tolist(), "k4_full": full,
               "decryptions": total}, open(RUNS / "strict_book_check.json", "w"), indent=1)
