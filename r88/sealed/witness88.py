#!/usr/bin/env python3
"""R88 independent forward-encryption witness check (FUTURE_TEST_GUARDRAILS G2: a separately implemented checker).
Standard library only; nothing imported from r88/blind, r88/rq88.py, r87/ or r75/. Re-enciphers every stored decode
(each ciphertext's top 5) with its stored setting, from the definition in r88/PREREGISTRATION.md G0 alone, and
requires the exact 97-letter ciphertext. Reads no published letters and no truth file.

Cipher RQ: fixed alphabet A (AZ, or KRYPTOS / PALIMPSEST / ABSCISSA keyed: keyword letters first, then the rest of A-Z
in order); offset s_i = d * floor(i / n), i from 0; W a permutation of 0..25.
  side PA:  A-place(c_i) = W[p_i] + s_i  (mod 26)          (p_i as 0..25 in A-Z order)
  side CA:  c_i = W[ A-place(p_i) + s_i  (mod 26) ]        (c_i as 0..25 in A-Z order)
Also checks: best == top[0]; top sorted by letter model; ids equal the target; W a permutation; n >= 1.
Usage: witness88.py TARGET.tsv RESULTS.jsonl OUT.json"""
import json
import sys
from pathlib import Path

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def keyed(word):
    out = []
    for ch in word + AZ:
        if ch not in out:
            out.append(ch)
    return "".join(out)


ALPH = {"AZ": AZ, "KRY": keyed("KRYPTOS"), "PAL": keyed("PALIMPSEST"), "ABS": keyed("ABSCISSA")}


def encipher(pt, st):
    A, side, n, d, W = ALPH[st["alph"]], st["side"], st["n"], st["d"], st["wiring"]
    if sorted(W) != list(range(26)) or n < 1 or d not in (1, -1) or side not in ("PA", "CA"):
        raise ValueError("bad setting")
    out = []
    for i, p in enumerate(pt):
        s = d * (i // n)
        if side == "PA":
            out.append(A[(W[ord(p) - 65] + s) % 26])
        else:
            out.append(chr(65 + W[(A.index(p) + s) % 26]))
    return "".join(out)


def check(tsv, results):
    cts = dict(l.split("\t") for l in Path(tsv).read_text().splitlines()[1:] if l)
    res = [json.loads(l) for l in Path(results).read_text().splitlines() if l]
    problems, n = [], 0
    if sorted(r["id"] for r in res) != sorted(cts):
        problems.append("ids differ from the target")
    for r in res:
        ct = cts.get(r["id"], "")
        if r["best"] != r["top"][0]:
            problems.append(f"{r['id']}: best is not top[0]")
        lms = [e["lm_per_letter"] for e in r["top"]]
        if lms != sorted(lms, reverse=True):
            problems.append(f"{r['id']}: top not sorted by letter model")
        for e in r["top"]:
            n += 1
            t = e["text"]
            try:
                ok = len(t) == 97 and not set(t) - set(AZ) and encipher(t, e["setting"]) == ct
            except (ValueError, KeyError, IndexError):
                ok = False
            if not ok:
                problems.append(f"{r['id']}: a stored decode does not re-encipher to the ciphertext")
    return {"ciphertexts": len(res), "witnesses": n, "problems": problems[:100], "passed": not problems}


def main():
    tsv, results, out = sys.argv[1:4]
    rep = check(tsv, results)
    Path(out).write_text(json.dumps(rep, indent=1) + "\n")
    print("witness", "PASSED" if rep["passed"] else "FAILED", rep["witnesses"], "decodes", rep["problems"][:3])
    sys.exit(0 if rep["passed"] else 1)


if __name__ == "__main__":
    main()
