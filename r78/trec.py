"""R78b T-REC: key-free test for recency-ordered alphabets (r78/PREREG_TREC.md). Reads the K4 ciphertext only.
Usage: python3 -I r78/trec.py OUT.json"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"


def rho(c):
    """(positions, recency ranks) for the positions whose letter has occurred before."""
    last, pos, r = {}, [], []
    for i, ch in enumerate(c):
        if ch in last:
            pos.append(i)
            r.append(len(set(c[last[ch] + 1:i])))
        last[ch] = i
    return pos, r


def ic(v):
    n = np.bincount(np.asarray(v), minlength=26)
    t = n.sum()
    return float((n * (n - 1)).sum() / (t * (t - 1)))


def enc_c(p, P, C0, rule):
    """Cipher list re-ordered by the cipher letter used. p, P, C0: lists of codes."""
    L, out = list(C0), []
    for x in p:
        c = L.pop(P.index(x))
        out.append(c)
        L.insert(0, c) if rule == "MTF" else L.append(c)
    return out


def enc_p(p, P0, C, rule):
    """Plaintext list re-ordered by the plaintext letter used."""
    L, out = list(P0), []
    for x in p:
        j = L.index(x)
        out.append(C[j])
        L.pop(j)
        L.insert(0, x) if rule == "MTF" else L.append(x)
    return out


def main(out):
    rng = np.random.default_rng(780200)
    txt = "".join(ch for ch in (ROOT / "k4kit/data/k1k3_plaintext.txt").read_text().upper() if ch.isalpha())[:768]
    T = [ord(ch) - 65 for ch in txt]
    k4 = [ord(ch) - 65 for ch in K4]
    alph = {"AZ": list(range(26)), "KRY": [ord(ch) - 65 for ch in KRY]}
    A_pos, B_pos, viol = [], [], 0
    for _ in range(2000):
        s = int(rng.integers(0, 768 - 97 + 1))
        p = T[s:s + 97]
        kind = rng.choice(["AZ", "KRY", "RND"])
        P = alph[kind] if kind != "RND" else [int(v) for v in rng.permutation(26)]
        rule = str(rng.choice(["MTF", "MTB"]))
        c = enc_c(p, P, [int(v) for v in rng.permutation(26)], rule)
        pos, r = rho(c)
        want = [P.index(p[i]) if rule == "MTF" else 25 - P.index(p[i]) for i in pos]
        viol += (r != want)
        A_pos.append(ic(r))
        c2 = enc_p(p, [int(v) for v in rng.permutation(26)], [int(v) for v in rng.permutation(26)], rule)
        B_pos.append(ic(c2))
    A_pos, B_pos = np.array(A_pos), np.array(B_pos)
    pos, r = rho(k4)
    A_k4, B_k4 = ic(r), ic(k4)
    sh = np.array(k4)
    A_null = np.array([ic(rho(list(rng.permutation(sh)))[1]) for _ in range(10000)])
    res = {"theorem_violations_in_plants": int(viol), "K4_repeat_positions": len(pos), "A_K4": A_k4,
           "A_null_mean": float(A_null.mean()), "A_null_p999": float(np.quantile(A_null, 0.999)),
           "K4_pct_of_shuffles": float((A_null <= A_k4).mean() * 100),
           "A_plants_p01": float(np.quantile(A_pos, 0.01)), "A_plants_median": float(np.median(A_pos)),
           "A_plants_min": float(A_pos.min()),
           "B_K4": B_k4, "B_plants_p01": float(np.quantile(B_pos, 0.01)), "B_plants_median": float(np.median(B_pos)),
           "B_plants_min": float(B_pos.min())}
    res["verdict_A"] = ("SIGNAL" if A_k4 >= res["A_null_p999"] and A_k4 >= res["A_plants_p01"] else
                        "DISFAVOURED" if A_k4 < res["A_plants_p01"] else "NO_CONCLUSION")
    res["verdict_B"] = "DISFAVOURED" if B_k4 < res["B_plants_p01"] else "NO_CONCLUSION"
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
