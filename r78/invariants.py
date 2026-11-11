"""R78: two ciphertext-only, key-free tests (r78/PREREG_INVARIANTS.md). Reads the K4 ciphertext only.
  I1    S(ca) = sum_i IDX[ca][c_i] mod 26: must be 0 (Beaufort / variant) or even (Vigenere) for a self-keyed cipher
        with pa = ka, for every permutation.
  T-RK  log-likelihood ratio of K4's letter counts, 'English +- English' against uniform, 24 conventions.
Usage: python3 -I r78/invariants.py OUT.json"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "r75"))
import core  # noqa: E402

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
A4 = ("AZ", "KRY", "PAL", "ABS")
OPS = {"VIG": (1, 1), "BEAU": (-1, 1), "VARB": (1, -1)}
ENG = np.array([8.167, 1.492, 2.782, 4.253, 12.702, 2.228, 2.015, 6.094, 6.966, 0.153, 0.772, 4.025, 2.406, 6.749,
                7.507, 1.929, 0.095, 5.987, 6.327, 9.056, 2.758, 0.978, 2.360, 0.150, 1.974, 0.074])
ENG = ENG / ENG.sum()


def idx(name):
    a = core.ALPH[name]
    return np.array([a.index(ch) for ch in AZ])


def S(text_codes, ca):
    return int(idx(ca)[text_codes].sum() % 26)


def plant(rng, n, A, ca, op):
    s, t = OPS[op]
    x = rng.integers(0, 26, n)                       # plaintext as indices in alphabet A
    pi = rng.permutation(n)
    y = (s * x + t * x[pi]) % 26                     # index of the ciphertext letter in alphabet ca
    return np.array([ord(core.ALPH[ca][v]) - 65 for v in y])


def dist(pa, ka, ca, op):
    """d[letter] = P(CA[s*IDX[pa][P] + t*IDX[ka][K]] = letter), P and K independent English letters."""
    s, t = OPS[op]
    ip, ik = idx(pa), idx(ka)
    d = np.zeros(26)
    for a in range(26):
        for b in range(26):
            d[ord(core.ALPH[ca][(s * ip[a] + t * ik[b]) % 26]) - 65] += ENG[a] * ENG[b]
    return d


def main(out):
    rng = np.random.default_rng(780100)
    c = np.array([ord(ch) - 65 for ch in K4])
    res = {"controls": {}, "I1": {}, "TRK": {}}
    # ---- I1 controls
    bad = 0
    for _ in range(2000):
        A, ca, op = rng.choice(A4), rng.choice(A4), rng.choice(list(OPS))
        v = S(plant(rng, 97, A, ca, op), ca)
        bad += (v % 2 != 0) if op == "VIG" else (v != 0)
    rnd = rng.integers(0, 26, (20000, 97))
    sr = np.array([[S(r, ca) for ca in A4] for r in rnd[:5000]])
    res["controls"] = {"plants_violating": int(bad), "random_S0_rate": float((sr == 0).mean()),
                       "random_even_rate": float((sr % 2 == 0).mean())}
    # ---- I1 on K4
    for ca in A4:
        v = S(c, ca)
        res["I1"][ca] = {"S": v, "beaufort_variant_possible": v == 0, "vigenere_possible": v % 2 == 0}
    # ---- T-RK
    n = np.bincount(c, minlength=26)
    ic = float((n * (n - 1)).sum() / (97 * 96))
    res["K4_counts"] = {AZ[i]: int(n[i]) for i in range(26)}
    res["K4_IC"] = ic
    for pa in ("AZ", "KRY"):
        for ka in ("AZ", "KRY"):
            for ca in ("AZ", "KRY"):
                for op in OPS:
                    d = dist(pa, ka, ca, op)
                    w = np.log(26 * d)
                    lam = float((n * w).sum())
                    h1 = rng.multinomial(97, d, 20000) @ w
                    h0 = rng.multinomial(97, np.full(26, 1 / 26), 20000) @ w
                    s1 = rng.multinomial(97, d, 20000)
                    ic1 = (s1 * (s1 - 1)).sum(1) / (97 * 96)
                    res["TRK"][f"{pa}/{ka}/{ca}/{op}"] = {
                        "lambda_K4": round(lam, 3), "pct_under_model": round(float((h1 <= lam).mean()) * 100, 2),
                        "pct_under_uniform": round(float((h0 <= lam).mean()) * 100, 2),
                        "model_mean": round(float(h1.mean()), 2), "uniform_mean": round(float(h0.mean()), 2),
                        "model_IC_mean": round(float(ic1.mean()), 5),
                        "pct_IC_le_K4_under_model": round(float((ic1 <= ic).mean()) * 100, 2)}
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(res, indent=1))
    print(json.dumps({k: res[k] for k in ("controls", "I1", "K4_IC")}, indent=1))
    for k, v in res["TRK"].items():
        print(k, v)


if __name__ == "__main__":
    main(sys.argv[1])
