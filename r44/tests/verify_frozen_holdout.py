#!/usr/bin/env python3
"""Independently verify R44b's archived known-key holdout; never attempt K4."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
H = ROOT / "r44" / "holdout_b"
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Freeze checks against the hashes committed before any sealed truth evaluation.
frozen = {}
for line in (H / "FROZEN.sha256").read_text().splitlines():
    pieces = line.split(maxsplit=1)
    assert len(pieces) == 2
    frozen[pieces[1].lstrip("*")] = pieces[0]
for rel in ("r44/holdout_b/RESULTS.jsonl", "r44/holdout_b/SOLVER.jsonl",
            "r44/holdout_b/blind.tsv"):
    assert rel in frozen, ("missing frozen SHA", rel)
    assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == frozen[rel], rel

rows = {}
for ln in (H / "blind.tsv").read_text().splitlines()[1:]:
    lab, ct, ks = ln.split("\t")
    assert lab not in rows
    key = [int(v) for v in ks.split(",")]
    assert len(ct) == len(key) == 97
    assert set(ct) <= set(AZ) and all(0 <= v < 26 for v in key)
    rows[lab] = (ct, key)
truth = json.loads((H / "sealed_truth.json").read_text())
assert len(rows) == len(truth) == 20

def replay(filename):
    outputs = {}
    for ln in (H / filename).read_text().splitlines():
        candidate = json.loads(ln)
        lab = candidate["id"]
        assert lab in rows and lab not in outputs
        p = candidate["plaintext"]
        pa = candidate["plaintext_alphabet"]
        ca = candidate["ciphertext_alphabet"]
        assert len(p) == 97 and set(p) <= set(AZ)
        assert len(pa) == len(ca) == 26
        assert set(pa) == set(ca) == set(AZ)
        ct, key = rows[lab]
        actual = "".join(ca[(pa.index(ch) + k) % 26] for ch, k in zip(p, key))
        assert actual == ct, ("failed independent forward-encryption", lab)
        outputs[lab] = p
    assert outputs.keys() == rows.keys()
    return sum(outputs[lab] == truth[lab]["plaintext"] for lab in outputs)

pre = replay("SOLVER.jsonl")
post = replay("RESULTS.jsonl")
assert pre == 16 and post == 20, (pre, post)
print("PASS: frozen bytes match SHA256; known-key R44b solver-only 16/20, polished 20/20, all 40 forward witnesses exact")
print("LIMITATION: the real 97-position key is SUPPLIED for each control; no unknown-key K4 solve is claimed")
