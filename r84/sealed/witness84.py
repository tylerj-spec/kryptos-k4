#!/usr/bin/env python3
"""R84 independent forward-encryption witness check (FUTURE_TEST_GUARDRAILS G2: a separately implemented checker).
Standard library only; nothing imported from r80a/, r79/ or r75/. Re-enciphers every stored decode (each ciphertext's
top 5 and each family's best) with the stored setting, from the cipher definition alone, and requires the exact
97-letter ciphertext. Reads no published letters.

Cipher (r80a/two80.py docstring; r80a/PREREGISTRATION.md):
  stage one  q_i = CA1[ s1*IDX[PA1][p_i] + t1*IDX[KA1][k1[i mod m1]] ]
  stage two  c_i = CA2[ s2*IDX[PA2][q_i] + t2*IDX[KA2][k2[i mod m2]] ]
  setting conv = (PA1, CA1, PA2, CA2, op, ka, sf): the LISTED key ("word") has (s, t) = op (VIG (1,1), BEAU (-1,1),
  VARB (1,-1)) and numbering ka; the FREE key ("free") has (s, t) = (sf, 1) and numbering AZ. L1/X1: listed key in
  stage one; L2/X2: in stage two.
Usage: witness84.py TARGET.tsv RESULTS.jsonl OUT.json"""
import json
import sys
from pathlib import Path

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALPH = {"AZ": AZ, "KRY": "".join(dict.fromkeys("KRYPTOS" + AZ))}
OPS = {"VIG": (1, 1), "BEAU": (-1, 1), "VARB": (1, -1)}


def encipher(pt, st):
    pa1, ca1, pa2, ca2, op, ka, sf = st["conv"]
    listed = (OPS[op], ka, st["word"])
    free = ((sf, 1), "AZ", st["free"])
    first, second = (listed, free) if st["fam"] in ("L1", "X1") else (free, listed)
    (s1, t1), ka1, k1 = first
    (s2, t2), ka2, k2 = second
    assert ca1 != pa2 and len(k1) >= 1 and len(k2) >= 1
    out = []
    for i, p in enumerate(pt):
        q = ALPH[ca1][(s1 * ALPH[pa1].index(p) + t1 * ALPH[ka1].index(k1[i % len(k1)])) % 26]
        out.append(ALPH[ca2][(s2 * ALPH[pa2].index(q) + t2 * ALPH[ka2].index(k2[i % len(k2)])) % 26])
    return "".join(out)


def check(tsv, results):
    cts = dict(l.split("\t") for l in Path(tsv).read_text().splitlines()[1:] if l)
    res = [json.loads(l) for l in Path(results).read_text().splitlines() if l]
    problems, n = [], 0
    if sorted(r["id"] for r in res) != sorted(cts):
        problems.append("ids differ from the target")
    for r in res:
        ct = cts[r["id"]]
        if r["best"] != r["top"][0]:
            problems.append(f"{r['id']}: best is not top[0]")
        lms = [e["lm_per_letter"] for e in r["top"]]
        if lms != sorted(lms, reverse=True):
            problems.append(f"{r['id']}: top not sorted by letter model")
        if max(e["lm_per_letter"] for e in r["best_by_fam"].values()) != r["best"]["lm_per_letter"]:
            problems.append(f"{r['id']}: best is not the maximum over families")
        for e in r["top"] + list(r["best_by_fam"].values()):
            n += 1
            t = e["text"]
            if len(t) != 97 or set(t) - set(AZ):
                problems.append(f"{r['id']}: decode is not 97 letters A-Z")
            elif encipher(t, e["setting"]) != ct:
                problems.append(f"{r['id']}: {e['fam']} decode does not re-encipher to the ciphertext")
    return {"ciphertexts": len(res), "witnesses": n, "problems": problems[:100], "passed": not problems}


if __name__ == "__main__":
    v = check(sys.argv[1], sys.argv[2])
    Path(sys.argv[3]).write_text(json.dumps(v, indent=1) + "\n")
    print("witnesses", v["witnesses"], "PASSED" if v["passed"] else f"FAILED {v['problems'][:5]}")
