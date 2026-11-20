#!/usr/bin/env python3
"""Tests for r40/audit/onefree.c (T6 item 3). Synthetic only: no K4 ciphertext, no published letters.
1 a pure-Python reference (keys from their definitions, V by brute force over all pairs, and a constructive
  partial-bijection test) agrees with itself on random cases, and V = 0 iff a consistent alphabet exists;
2 fresh planted messages, one per key family and mode (free PA with a random plaintext alphabet; free CA with a
  random cipher alphabet), enciphered by an independent encryptor here: the kernel reports the true setting at V = 0;
3 for every setting the kernel lists at its minimum V, the Python reference recomputes the same V.
The kernel's own sampled brute-force self-check (ONEFREE_SELFCHECK) must not fire.
Usage: python3 -I r40/audit/tests/test_onefree.py"""
import random
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
AL = {"AZ": AZ, "KRY": "KRYPTOSABCDEFGHIJLMNQUVWXZ", "PALP": "PALIMSETBCDFGHJKNOQRUVWXYZ",
      "ABSP": "ABSCIDEFGHJKLMNOPQRTUVWXYZ", "ACAKRY": "KAHUOFNPDLXRBIVSGQTEMZYCJW",
      "ACAPAL": "ACOZEJWIFRLDQMGUPBNYSHVTKX", "ACAABS": "ADJOUZBEKPVCGMRXIHNTYSFLQW"}
POS = list(range(21, 34)) + list(range(63, 74))
SYM = "0123456789ABCDEFGHIJKLMNOP"


def letters(p):
    return "".join(ch for ch in Path(p).read_text().upper() if "A" <= ch <= "Z")


TEXTS = {"CARTER": letters(ROOT / "r34/carter_az.txt"), "K1K3": letters(ROOT / "k4kit/data/k1k3_plaintext.txt")}


def key_of(label):
    fam, rest = label.split("/", 1)
    if re.fullmatch(r"C[0-9]+b[0-9]+", fam):
        base, b = map(int, fam[1:].split("b"))
        pr = rest.replace("primer", "")
        k = [SYM.index(ch) for ch in pr]
        while len(k) < 97:
            k.append((k[-b] + k[-b + 1]) % base)
        return k
    d, num, off = rest.split("/")
    t = TEXTS[fam][::-1] if d == "rev" else TEXTS[fam]
    o = int(off[3:])
    return [AL[num].index(ch) for ch in t[o:o + 97]]


def V_ref(mode, ct, want, alpha, op, key):
    idx = [i for i in range(97) if want[i] != "?"]
    vals, labs = [], []
    for i in idx:
        if mode == "PA":
            v = AL[alpha].index(ct[i]) + (-key[i] if op == 0 else key[i])
            lab = want[i]
        else:
            v = AL[alpha].index(want[i]) + (key[i] if op == 0 else -key[i])
            lab = ct[i]
        vals.append(v % 26)
        labs.append(lab)
    V = sum((vals[x] == vals[y]) != (labs[x] == labs[y]) for x in range(len(idx)) for y in range(x + 1, len(idx)))
    fwd, bwd, ok = {}, {}, True                          # constructive bijection test
    for l, v in zip(labs, vals):
        if fwd.setdefault(l, v) != v or bwd.setdefault(v, l) != l:
            ok = False
    assert (V == 0) == ok
    return V


def encrypt(mode, pt, alpha, op, key, rng):
    """Independent encryptor. PA mode: CA = alpha fixed, PA random; CA mode: PA = alpha fixed, CA random."""
    free = list(AZ)
    rng.shuffle(free)
    free = "".join(free)
    out = []
    for i, p in enumerate(pt):
        if mode == "PA":                     # CA^-1(c) = PA^-1(p) + k  (op 0)  or  PA^-1(p) - k  (op 1)
            x = free.index(p) + (key[i] if op == 0 else -key[i])
            out.append(AL[alpha][x % 26])
        else:                                # CA^-1(c) = PA^-1(p) + k (op 0) or - k (op 1), CA free
            x = AL[alpha].index(p) + (key[i] if op == 0 else -key[i])
            out.append(free[x % 26])
    return "".join(out)


def run(exe, mode, ct, want, tmp):
    out = Path(tmp) / "o.tsv"
    r = subprocess.run([str(exe), mode, ct, want, str(ROOT / "r34/carter_az.txt"),
                        str(ROOT / "k4kit/data/k1k3_plaintext.txt"), str(out)], capture_output=True, text=True,
                       env={"ONEFREE_SELFCHECK": "1"})
    assert r.returncode == 0, r.stderr
    meta, mins = {}, []
    for line in out.read_text().splitlines():
        f = line.split("\t")
        if f[0] == "min_setting":
            mins.append(f[1])
        elif f[0] != "V":
            meta[f[0]] = int(f[1])
    return meta, mins


def main():
    rng = random.Random(400619)
    for _ in range(300):                        # 1: reference consistency on random small cases
        mode = rng.choice(("PA", "CA"))
        ct = "".join(rng.choice(AZ) for _ in range(97))
        want = "".join(rng.choice(AZ) if i in POS else "?" for i in range(97))
        V_ref(mode, ct, want, rng.choice(list(AL)), rng.randrange(2), [rng.randrange(26) for _ in range(97)])
    print("1 ok: reference V and constructive bijection test agree on 300 random cases")
    with tempfile.TemporaryDirectory() as tmp:
        exe = Path(tmp) / "onefree"
        subprocess.run(["gcc", "-O3", "-march=native", "-Wall", "-Wextra", "-Werror", "-o", str(exe),
                        str(ROOT / "r40/audit/onefree.c")], check=True)
        cases = [("PA", "C10b6/primer418230", "KRY", 0), ("PA", "C26b5/primer3K0AB", "ACAPAL", 1),
                 ("PA", "CARTER/rev/AZ/off5123", "ABSP", 0), ("CA", "C10b7/primer9031775", "PALP", 1),
                 ("CA", "K1K3/fwd/KRY/off301", "AZ", 0)]
        for mode, label, alpha, op in cases:
            pt = "".join(rng.choice("ETAOINSHRDLUCMWFGYPB") for _ in range(97))
            ct = encrypt(mode, pt, alpha, op, key_of(label), rng)
            want = "".join(pt[i] if i in POS else "?" for i in range(97))
            meta, mins = run(exe, mode, ct, want, tmp)
            opname = (("VIG|BEAU", "VARB") if mode == "PA" else ("VIG", "BEAU|VARB"))[op]
            tag = f"{label}|{'CA' if mode == 'PA' else 'PA'}={alpha}|OP={opname}"
            assert meta["min_V"] == 0 and tag in mins, (tag, meta, mins[:5])
            for s in mins:                      # 3: reference recomputes V at every listed minimum
                m = re.fullmatch(r"(.*)\|(?:CA|PA)=([A-Z]+)\|OP=(.*)", s)
                lab, al, opx = m.group(1), m.group(2), m.group(3)
                o = 0 if opx in ("VIG|BEAU", "VIG") else 1
                assert V_ref(mode, ct, want, al, o, key_of(lab)) == meta["min_V"], s
            print("2-3 ok:", mode, label, "true setting found at V = 0;", len(mins), "minimum settings re-checked")
    print("T6 R40/R42 ONE-FREE-ALPHABET TESTS OK")


if __name__ == "__main__":
    main()
