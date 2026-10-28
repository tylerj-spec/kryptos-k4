#!/usr/bin/env python3
"""SEALED side: build the R32 planted controls (PREREGISTRATION_R32.md). Writes the ciphertexts the blind scanner may
read (runs/plant_*_ct.txt) and the ground truth it may NOT read (sealed/plants_truth.json)."""
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
R32 = HERE.parent
sys.path.insert(0, str(R32.parent / "tools"))
from k4common import AZ, KRY, R27_ROUTES, inv, route  # noqa: E402

TEMPL = json.loads((R32.parent / "data" / "reference_messages.json").read_text())["r20_templates"]
SRC = {"CARTER": (R32 / "runs" / "carter_az.txt").read_text().strip(),
       "K1K3": "".join(c for c in (R32.parent / "data" / "k1k3_plaintext.txt").read_text().upper() if "A" <= c <= "Z")}


def chain(p, b):
    k = [int(x) for x in f"{p:0{b}d}"]
    while len(k) < 97:
        k.append((k[-b] + k[-b + 1]) % 10)
    return k[:97]


def encrypt(P, perm, order, key, pa, ca, op):
    q = inv(perm)
    src = list(range(97)) if order == "ID" else q
    kix = q if order == "T_then_S" else list(range(97))
    ct = [None] * 97
    for t in range(97):
        k, x = key[kix[t]], pa.index(P[t])
        c = (x + k) % 26 if op == "VIG" else ((k - x) % 26 if op == "BEAU" else (x - k) % 26)
        ct[src[t]] = ca[c]
    return "".join(ct)


def make(i, P, rng, routes, fam):
    name, order = rng.choice(routes)
    perm = list(range(97)) if order == "ID" else route(name)
    pa, ca, op = rng.choice([AZ, KRY]), rng.choice([AZ, KRY]), rng.choice(["VIG", "BEAU", "VARB"])
    if fam in ("CARTER", "K1K3"):
        d, num = rng.choice(["fwd", "rev"]), rng.choice(["AZ", "KRY"])
        s = SRC[fam] if d == "fwd" else SRC[fam][::-1]
        off = rng.randrange(len(s) - 96)
        al = AZ if num == "AZ" else KRY
        key, spec = [al.index(c) for c in s[off:off + 97]], f"{d}/{num}/off{off}"
    else:
        b = 5 if fam == "G5" else 6
        p = rng.randrange(10 ** b)
        key, spec = chain(p, b), f"primer{p:0{b}d}"
    ct = encrypt(P, perm, order, key, pa, ca, op)
    return ct, {"plant": i, "family": fam, "route": name, "order": order, "key": spec, "PA": "KRY" if pa == KRY else "AZ",
                "CA": "KRY" if ca == KRY else "AZ", "OP": op, "plaintext": P, "ciphertext": ct}


if __name__ == "__main__":
    f1 = [("ID", "ID")] + [(n, o) for n in R27_ROUTES for o in ("S_then_T", "T_then_S")]
    f2 = [(f"R{a}x{b}/{d}/{k}", o) for a in range(4, 29) for b in range(4, 29) for d in ("CW", "CCW")
          for k in ("fwd", "inv") for o in ("S_then_T", "T_then_S")]
    truth = []
    rng = random.Random(32001)
    for i, fam in enumerate(["CARTER", "K1K3", "G5", "C6", "CARTER", "G5"]):
        ct, meta = make(i, TEMPL[i], rng, f1, fam)
        (R32 / "runs" / f"plant_f1_{i}_ct.txt").write_text(ct + "\n")
        truth.append(meta)
    rng = random.Random(32002)
    ct, meta = make(6, TEMPL[6], rng, f2, "G5")
    (R32 / "runs" / "plant_f2_6_ct.txt").write_text(ct + "\n")
    truth.append(meta)
    (HERE / "plants_truth.json").write_text(json.dumps(truth, indent=1) + "\n")
    for m in truth:
        print(m["plant"], m["family"], m["route"], m["order"], m["key"], m["PA"], m["CA"], m["OP"])
