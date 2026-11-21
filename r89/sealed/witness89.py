#!/usr/bin/env python3
"""R89 independent forward-encryption witness check (FUTURE_TEST_GUARDRAILS G2: a separately implemented checker).
Standard library only; nothing imported from r89/blind, r89/f26l.py, r89/rct.py, r87/ or r75/. Re-enciphers every
stored decode (each ciphertext's top 5 and each sub-family's best) with its stored setting, from the definitions in
r89/PREREGISTRATION.md G0 alone, and requires the exact 97-letter ciphertext. Reads no published letters, no truth.
  F26 / F26L: alphabet A (one of the 20 named in G0); blocks of b (last block 97 mod b); output j of a block of
     length t takes the row (place // 13) of input (j + u) mod t and the column (place % 13) of input (j + v) mod t;
     F26L then adds sign * KRYPTOS-place(key[(i + phase) mod len]) in the KRYPTOS alphabet.
  RCT: offset s_0 = 0, s_{i+1} = s_i + d * (1 + [(c_i + q) mod m == 0]) (c_i as 0..25 in A-Z order);
     E_out-place(c_i) + s_i = W[E_in-place(p_i) + s_i] (mod 26).
Usage: witness89.py TARGET.tsv RESULTS.jsonl OUT.json"""
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
F26_ALPH = {"AZ": AZ, "QWERTY": "QWERTYUIOPASDFGHJKLZXCVBNM", "ALT": AZ[0::2] + AZ[1::2]}
for w in ("KRYPTOS", "PALIMPSEST", "ABSCISSA", "NUANCE", "MAGNETIC", "PASSAGE", "CANDLE", "SANBORN", "SCHEIDT",
          "LANGLEY", "WEBSTER", "SHADING", "IQLUSION", "UNDERGRUUND", "DESPARATLY", "LAYERTWO", "INVISIBLE"):
    F26_ALPH[w] = keyed(w)
OUTER_KEYS = {"PAL": "PALIMPSEST", "ABS": "ABSCISSA"}
CONTACTS = {"AZ": AZ, "KRY": KRY, "PAL": keyed("PALIMPSEST"), "ABS": keyed("ABSCISSA")}


def enc_f26(pt, st):
    A = F26_ALPH[st["alphabet"]]
    b, u, v = st["b"], st["u"], st["v"]
    if not (b in (5, 7, 9, 11) and 1 <= u < b and 1 <= v < b and u != v):
        raise ValueError("bad F26 setting")
    out = []
    for o in range(0, len(pt), b):
        blk = pt[o:o + b]
        t = len(blk)
        for j in range(t):
            r = A.index(blk[(j + u) % t]) // 13
            h = A.index(blk[(j + v) % t]) % 13
            out.append(A[13 * r + h])
    m = "".join(out)
    o = st["outer"]
    if o is None:
        return m
    U = OUTER_KEYS[o["key"]]
    if o["sign"] not in (1, -1) or not 0 <= o["phase"] < len(U):
        raise ValueError("bad outer setting")
    return "".join(KRY[(KRY.index(ch) + o["sign"] * KRY.index(U[(i + o["phase"]) % len(U)])) % 26]
                   for i, ch in enumerate(m))


def enc_rct(pt, st):
    Ei, Eo, W = CONTACTS[st["ein"]], CONTACTS[st["eout"]], st["wiring"]
    d, m, q = st["d"], st["m"], st["q"]
    if sorted(W) != list(range(26)) or d not in (1, -1) or m not in (2, 3, 4, 5) or not 0 <= q < m:
        raise ValueError("bad RCT setting")
    s, out = 0, []
    for p in pt:
        c = Eo[(W[(Ei.index(p) + s) % 26] - s) % 26]
        out.append(c)
        s += d * (2 if (AZ.index(c) + q) % m == 0 else 1)
    return "".join(out)


def encipher(e):
    return enc_rct(e["text"], e["setting"]) if e["arm"] == "RCT" else enc_f26(e["text"], e["setting"])


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
        for e in r["top"] + list(r["best_by_arm"].values()):
            n += 1
            t = e["text"]
            if e["arm"] == "F26L" and e["setting"]["outer"] is None or e["arm"] == "F26" and e["setting"]["outer"]:
                problems.append(f"{r['id']}: arm label does not match the outer stage")
            try:
                ok = len(t) == 97 and not set(t) - set(AZ) and encipher(e) == ct
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
