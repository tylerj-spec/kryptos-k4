#!/usr/bin/env python3
"""Create an independent planted control without K4-related plaintext templates.
Usage: make_controls.py EXP TAG ROUTES KIND ARG TEMPLATE_INDEX SEED.
Plaintext is the first 97 alphabetic letters of the selected original paragraph in r35/controls.json.
Runs ONLY before the blind experiment. Never imported from strictblind/blind.
"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "strictblind/sealed"))
from common import ALPHABETS, ALPHABETS_ACA, N, encrypt, letters, make_key, read_routes  # noqa: E402

exp, tag, routefile, kind, arg, ti, seed = sys.argv[1:8]
exp = Path(exp)
rng = random.Random(int(seed))
paragraphs = json.loads((ROOT / "r35/controls.json").read_text())["texts"]
P = "".join(c for c in paragraphs[int(ti)].upper() if "A" <= c <= "Z")[:N]
assert len(P) == N, "control must be 97 letters"
R = read_routes(exp / routefile)
name, order = rng.choice(sorted(R))
karg = str(exp / arg) if kind == "TEXT" else arg
if kind == "TEXT":
    L = len(letters(karg))
    spec = f"{rng.choice(['fwd', 'rev'])}/{rng.choice(['AZ', 'KRY'])}/off{rng.randrange(L - N + 1)}"
elif kind == "CHAIN":
    spec = f"primer{rng.randrange(10 ** int(arg)):0{int(arg)}d}"
elif kind in ("CHAINBASE", "CHAINALPH", "CHAINACA"):
    base, b = map(int, arg.split(","))
    value = rng.randrange(base ** b)
    symbols = "0123456789ABCDEFGHIJKLMNOP"
    chars = []
    for _ in range(b):
        chars.append(symbols[value % base])
        value //= base
    spec = "primer" + "".join(reversed(chars))
else:
    raise ValueError("unknown key family")
choices = ["AZ", "KRY", "PAL", "ABS"] if kind in ("CHAINALPH", "CHAINACA") else ["AZ", "KRY"]
alph = ALPHABETS_ACA if kind == "CHAINACA" else ALPHABETS
pa, ca, op = rng.choice(choices), rng.choice(choices), rng.choice(["VIG", "BEAU", "VARB"])
ct = encrypt(P, R[name, order], order, make_key(kind, karg, spec),
             alph[pa], alph[ca], op)
(exp / f"{tag}_ct.txt").write_text(ct + "\n")
(exp / "sealed").mkdir(exist_ok=True)
tf = exp / "sealed/truth.json"
truth = json.loads(tf.read_text()) if tf.exists() else {}
if tag in truth:
    raise ValueError("duplicate planted control")
truth[tag] = {"plaintext": P, "route": name, "order": order, "key": spec,
              "PA": pa, "CA": ca, "OP": op, "ciphertext": ct, "seed": int(seed),
              "template_index": int(ti), "control_source": "r35/controls.json"}
tf.write_text(json.dumps(truth, indent=1) + "\n")
print(f"{tag}: independent control planted, only ciphertext passed to blind runner")
