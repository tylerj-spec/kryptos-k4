# Development probe on PLANTED data only (no K4): is the cipher alphabet identifiable from PA-invariant statistics?
import json, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "r30"))
from r30lib import AZ, DATA, chain_key, encrypt
bases = json.loads((DATA / "reference_messages.json").read_text())["calibration"]
def stats(x):
    n = len(x); f = [0]*26
    for v in x: f[v] += 1
    ic = sum(c*(c-1) for c in f) / (n*(n-1))
    bg = {}
    for i in range(n-1): bg[(x[i], x[i+1])] = bg.get((x[i], x[i+1]), 0) + 1
    rb = sum(c*(c-1)//2 for c in bg.values())          # repeated-bigram pairs
    return ic, rb
def xseq(a, ct, k): return [(a[ord(c)-65] - kk) % 26 for c, kk in zip(ct, k)]
rng = random.Random(7)
for t in range(6):
    P = bases[t]; pa, ca = list(AZ), list(AZ); rng.shuffle(pa); rng.shuffle(ca)
    k = chain_key(rng.randrange(10**5), 5); ct = encrypt(P, k, pa, ca)
    a_true = [ca.index(chr(65+i)) for i in range(26)]
    ic_t, rb_t = stats(xseq(a_true, ct, k))
    best = (-1, None)
    for r in range(20):                                   # hill-climb a to maximise IC + 0.01*repeated bigrams
        a = list(range(26)); rng.shuffle(a)
        obj = lambda a: (lambda s: s[0] + 0.002*s[1])(stats(xseq(a, ct, k)))
        cur = obj(a); improved = True
        while improved:
            improved = False
            for i in range(26):
                for j in range(i+1, 26):
                    a[i], a[j] = a[j], a[i]; v = obj(a)
                    if v > cur + 1e-12: cur = v; improved = True
                    else: a[i], a[j] = a[j], a[i]
        if cur > best[0]: best = (cur, a[:])
    ic_b, rb_b = stats(xseq(best[1], ct, k))
    # distance to truth up to a common shift
    agree = max(sum((best[1][i] - a_true[i]) % 26 == s for i in range(26)) for s in range(26))
    print(f"plant {t}: true a: IC {ic_t:.4f} repbigrams {rb_t} | climbed a: IC {ic_b:.4f} repbigrams {rb_b} | letters matching truth (best shift) {agree}/26")
