#!/usr/bin/env python3
"""Calibration for E4 (diagnostic, after the run): 20 R21 passages encrypted under random Carter-book windows (random
direction, numbering, offset; seed 30007) with random alphabets; true key given; ORTH at 64 restarts."""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e4_book as eb  # noqa: E402
from r30lib import ANCH, AZ, DATA, HERE, RUNS, encrypt, possible, run_solver, seed, solver_line, verify_row  # noqa: E402

BOOK = HERE.parents[1] / "archive" / "sources" / "carter_mace_1923_v1_doran_google_ocr.txt"
text, _ = eb.normalise(BOOK.read_bytes().decode("utf-8", errors="replace"))
bases = json.loads((DATA / "reference_messages.json").read_text())["calibration"]
rng = random.Random(30007)
items = []
for i, P in enumerate(bases):
    d, a = rng.choice(["fwd", "rev"]), rng.choice(["AZ", "KRY"])
    k = eb.key_of(text, d, a, rng.randrange(len(text) - 97))
    pa, ca = list(AZ), list(AZ)
    rng.shuffle(pa)
    rng.shuffle(ca)
    ct = encrypt(P, k, pa, ca)
    assert possible(k, ct=ct)
    items.append((f"C4_{i:02d}_{d}_{a}", P, k, ct))
best, _ = run_solver([solver_line(l, k, ct, ANCH, seed(f"c4|{l}")) for l, P, k, ct in items], "c4_bookplant", 64)
rows = {}
for l, P, k, ct in items:
    assert verify_row(best[l], k, ct)
    rows[l] = {"W": best[l]["W"], "wrong_letters": sum(x != y for x, y in zip(best[l]["plaintext"], P))}
n = sum(v["wrong_letters"] <= 5 for v in rows.values())
json.dump({"readable": n, "of": 20, "rows": rows}, open(RUNS / "c4_bookplant.json", "w"), indent=1)
print(f"planted Carter-key recovery at 64 restarts: {n}/20 readable")
