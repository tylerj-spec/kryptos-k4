"""R73 word-boundary cipher families (from PR #62) and a ciphertext-only word-segmentation solver. No K4 data.
Plaintext: English words (A-Z); the word divisions are removed AFTER encipherment, so the solver must recover them.
Tableau alphabet A in {AZ, KRY}; x = A^-1(p), y = A^-1(c).
  Family I (interrupted key restarted at every plaintext word): keyword W in {KRYPTOS, PALIMPSEST, ABSCISSA},
      k_t = A^-1(W[t mod |W|]) with t the letter's position INSIDE its word (0-based);
      VIG y = x + k, BEAU y = k - x, VARB y = x - k (mod 26).                                     18 settings
  Family R26 (26-letter Ragbaby-like word-progressive): word number w (1-based), position t in the word,
      phase b in 0..25: y = x + w + t + b (mod 26).                                               52 settings
Solver: for each setting, dynamic programming over the ciphertext picks the segmentation maximising the sum of word
log-probabilities (R59 word model, column 2); an out-of-vocabulary word of length L counts as ONE word and costs
OOV * L (OOV = 7 per letter, as R59), so unknown words keep the key phase and word count in step. R26 tracks
the phase s = (w + b) mod 26 of the next word in the DP state. Returns every setting's best decode with its words."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
ALPH = {"AZ": AZ, "KRY": KRY}
KEYWORDS = ("KRYPTOS", "PALIMPSEST", "ABSCISSA")
OPS = ("VIG", "BEAU", "VARB")
MAXLEN = 18
OOV = 7.0


def load_words(path=ROOT / "k4kit/data/word_model_orth.tsv"):
    words = {}
    for line in Path(path).read_text().splitlines():
        w, ex, _ = line.split()
        ex = float(ex)
        if ex > -1e90 and len(w) <= MAXLEN and w.isalpha():
            words[w] = ex
    return words


def settings(family):
    if family == "I":
        return [(kw, a, op) for kw in KEYWORDS for a in ALPH for op in OPS]
    return [(a, b) for a in ALPH for b in range(26)]


def encrypt(words, family, setting):
    """words: list of plaintext words (A-Z). Returns the ciphertext with divisions removed."""
    out = []
    if family == "I":
        kw, a, op = setting
        A = ALPH[a]
        K = [A.index(c) for c in kw]
        for w in words:
            for t, ch in enumerate(w):
                x, k = A.index(ch), K[t % len(K)]
                out.append(A[((x + k) if op == "VIG" else (k - x) if op == "BEAU" else (x - k)) % 26])
    else:
        a, b = setting
        A = ALPH[a]
        for wi, w in enumerate(words, start=1):
            for t, ch in enumerate(w):
                out.append(A[(A.index(ch) + wi + t + b) % 26])
    return "".join(out)


def _dec_I(seg, setting):
    kw, a, op = setting
    A = ALPH[a]
    K = [A.index(c) for c in kw]
    r = []
    for t, ch in enumerate(seg):
        y, k = A.index(ch), K[t % len(K)]
        r.append(A[((y - k) if op == "VIG" else (k - y) if op == "BEAU" else (y + k)) % 26])
    return "".join(r)


def solve_I(ct, setting, words):
    n = len(ct)
    best = [-1e18] * (n + 1)
    back = [None] * (n + 1)
    best[0] = 0.0
    for i in range(n):
        if best[i] < -1e17:
            continue
        for L in range(1, min(MAXLEN, n - i) + 1):
            w = _dec_I(ct[i:i + L], setting)
            sc = words.get(w)
            cands = [(sc, w, True)] if sc is not None else []
            cands.append((-OOV * L, w, False))   # an unknown word of length L (one word: the key restarts after it)
            for s, wd, known in cands:
                v = best[i] + s
                if v > best[i + L]:
                    best[i + L], back[i + L] = v, (i, wd, known)
    return _trace(best, back, n)


def solve_R26(ct, alph, words):
    """Best decode for each phase b; DP state (position, s = phase of the next word mod 26)."""
    A = ALPH[alph]
    n = len(ct)
    y = [A.index(c) for c in ct]
    seg = {}
    for i in range(n):
        for L in range(1, min(MAXLEN, n - i) + 1):
            for s in range(26):
                seg[i, L, s] = "".join(A[(y[i + t] - s - t) % 26] for t in range(L))
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
                    w = seg[i, L, s]
                    sc = words.get(w)
                    cands = [(sc, True)] if sc is not None else []
                    cands.append((-OOV * L, False))   # an unknown word of length L counts as one word
                    for v0, known in cands:
                        key = (i + L, (s + 1) % 26)
                        v = cur + v0
                        if v > best.get(key, -1e18):
                            best[key], back[key] = v, (i, s, w, known)
        ends = [(v, k) for k, v in best.items() if k[0] == n]
        v, k = max(ends)
        ws, oov = [], 0
        while k[0] > 0:
            i, s, w, known = back[k]
            ws.append(w)
            oov += not known
            k = (i, s)
        out[b] = {"score": v, "words": ws[::-1], "oov": oov}
    return out


def _trace(best, back, n):
    ws, oov, i = [], 0, n
    while i > 0:
        j, w, known = back[i]
        ws.append(w)
        oov += not known
        i = j
    return {"score": best[n], "words": ws[::-1], "oov": oov}


def solve_all(ct, words):
    """Every setting of both families: list of dicts sorted by score (best first)."""
    res = []
    for st in settings("I"):
        r = solve_I(ct, st, words)
        res.append({"family": "I", "setting": list(st), **r})
    for a in ALPH:
        for b, r in solve_R26(ct, a, words).items():
            res.append({"family": "R26", "setting": [a, b], **r})
    res.sort(key=lambda d: -d["score"])
    return res
