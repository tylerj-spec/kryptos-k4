#!/usr/bin/env python3
"""strictblind SEALED plant maker (run BEFORE the blind experiment; writes only ciphertexts where the scanner looks).
  make_plants.py EXP TAG ROUTES KIND ARG TEMPLATE_INDEX SEED
Encrypts reference_messages.json r20_templates[TEMPLATE_INDEX] under a random route-order from ROUTES, a random key of
KIND/ARG and random conventions; writes EXP/TAG_ct.txt and appends the truth to EXP/sealed/truth.json."""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import AZ, KRY, N, encrypt, letters, make_key, read_routes  # noqa: E402

exp, tag, routes, kind, arg, ti, seed = sys.argv[1:8]
exp = Path(exp)
rng = random.Random(int(seed))
P = json.loads((Path(__file__).resolve().parents[2] / "k4kit/data/reference_messages.json").read_text())["r20_templates"][int(ti)]
R = read_routes(exp / routes)
name, order = rng.choice(sorted(R))
karg = str(exp / arg) if kind == "TEXT" else arg
if kind == "TEXT":
    L = len(letters(karg))
    spec = f"{rng.choice(['fwd', 'rev'])}/{rng.choice(['AZ', 'KRY'])}/off{rng.randrange(L - N + 1)}"
else:
    spec = f"primer{rng.randrange(10 ** int(arg)):0{int(arg)}d}"
pa, ca, op = rng.choice(["AZ", "KRY"]), rng.choice(["AZ", "KRY"]), rng.choice(["VIG", "BEAU", "VARB"])
ct = encrypt(P, R[name, order], order, make_key(kind, karg, spec), AZ if pa == "AZ" else KRY, KRY if ca == "KRY" else AZ, op)
(exp / f"{tag}_ct.txt").write_text(ct + "\n")
(exp / "sealed").mkdir(exist_ok=True)
tf = exp / "sealed" / "truth.json"
truth = json.loads(tf.read_text()) if tf.exists() else {}
truth[tag] = {"plaintext": P, "route": name, "order": order, "key": spec, "PA": pa, "CA": ca, "OP": op, "ciphertext": ct}
tf.write_text(json.dumps(truth, indent=1) + "\n")
print(tag, "planted")
