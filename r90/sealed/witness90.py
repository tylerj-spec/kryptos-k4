#!/usr/bin/env python3
"""R90 independent forward-encryption witness check (FUTURE_TEST_GUARDRAILS G2). Standard library only; nothing
imported from r90/blind, r90/f26c.py, r89/ or r75/. Re-enciphers every stored decode (top 5 and each sub-family's
best) with its stored setting, from r90/PREREGISTRATION.md G0 alone, and requires the exact 97-letter ciphertext.
F26 / F26C: alphabet A = keyword then the rest of A-Z, for the 15 words in G0; blocks of b (last block 97 mod b);
  output j of a block of length t takes the row (place // 13) of input (j + u) mod t and the column (place % 13) of
  input (j + v) mod t; F26C then adds sign * KRYPTOS-place(key[(i + phase) mod len]) in the KRYPTOS alphabet.
Also checks: best == top[0]; top sorted by letter model; best is the maximum of the sub-family bests; arm labels;
256 retained settings per record; ids equal the target. Usage: witness90.py TARGET.tsv RESULTS.jsonl OUT.json"""
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


KRY = keyed("KRYPTOS")
WORDS = ("ORCHARD", "MYSTERY", "TRAVEL", "MECHANIC", "RIVER", "PHILOSOPHY", "HORIZON", "GARDEN", "SECRET", "TEMPLE",
         "MARKET", "TUNNEL", "LIBRARY", "MIRROR", "CIPHER")
ALPH = {w: keyed(w) for w in WORDS}
OUTER_KEYS = {"PAL": "PALIMPSEST", "ABS": "ABSCISSA"}


def encipher(e):
    st = e["setting"]
    A = ALPH[st["alphabet"]]
    b, u, v = st["b"], st["u"], st["v"]
    if not (b in (5, 7, 9, 11) and 1 <= u < b and 1 <= v < b and u != v):
        raise ValueError("bad setting")
    out = []
    for o in range(0, len(e["text"]), b):
        blk = e["text"][o:o + b]
        t = len(blk)
        for j in range(t):
            out.append(A[13 * (A.index(blk[(j + u) % t]) // 13) + A.index(blk[(j + v) % t]) % 13])
    m = "".join(out)
    o = st["outer"]
    if o is None:
        return m
    U = OUTER_KEYS[o["key"]]
    if o["sign"] not in (1, -1) or not 0 <= o["phase"] < len(U):
        raise ValueError("bad outer setting")
    return "".join(KRY[(KRY.index(ch) + o["sign"] * KRY.index(U[(i + o["phase"]) % len(U)])) % 26]
                   for i, ch in enumerate(m))


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
        if max(e["lm_per_letter"] for e in r["best_by_arm"].values()) != r["best"]["lm_per_letter"]:
            problems.append(f"{r['id']}: best is not the maximum over sub-families")
        if len(r["retained"]) != 256 or len(set(r["retained"])) != 256:
            problems.append(f"{r['id']}: retained list is not 256 distinct settings")
        for e in r["top"] + list(r["best_by_arm"].values()):
            n += 1
            if (e["arm"] == "F26C") != (e["setting"]["outer"] is not None):
                problems.append(f"{r['id']}: arm label does not match the outer stage")
            try:
                ok = len(e["text"]) == 97 and not set(e["text"]) - set(AZ) and encipher(e) == ct
            except (ValueError, KeyError, IndexError, TypeError):
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
