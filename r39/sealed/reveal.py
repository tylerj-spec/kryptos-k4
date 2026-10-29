#!/usr/bin/env python3
"""R39 sealed validation: verify freeze, all planted ciphertext, sampled independent IC and truth rank."""
from collections import Counter
import hashlib
import json
import math
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "strictblind/sealed"))
from common import K4, encrypt, make_key  # noqa: E402

exp = Path(sys.argv[1]).resolve()
for line in (exp / "FROZEN.sha256").read_text().splitlines():
    sha, path = line.split(maxsplit=1)
    assert hashlib.sha256((exp / path).read_bytes()).hexdigest() == sha, "frozen output changed: " + path
manifest = json.loads((exp / "manifest.json").read_text())["runs"]
truth = json.loads((exp / "sealed/truth.json").read_text())
result = []

def independent_ic(ct, primer):
    key = [int(c) for c in f"{primer:05d}"]
    for i in range(5, 97):
        key.append((key[i-5] + key[i-4]) % 10)
    groups = [0] * 10
    counts = [[0] * 26 for _ in range(10)]
    for c, k in zip(ct, key):
        groups[k] += 1
        counts[k][ord(c) - 65] += 1
    return (sum(x * (x - 1) for row in counts for x in row)
            / sum(x * (x - 1) for x in groups))

for row in manifest:
    tag = row["tag"]
    ct = "".join(c for c in (exp / row["ct"]).read_text().upper() if "A" <= c <= "Z")
    assert len(ct) == 97
    data = (exp / "out" / f"{tag}.scores.f64").read_bytes()
    assert len(data) == 800000, "each file must encode all 100000 primer scores"
    scores = struct.unpack("<100000d", data)
    for primer in (0, 1, 42, 39000, 54321, 99999):
        assert math.isclose(scores[primer], independent_ic(ct, primer), abs_tol=1e-15)
    best = max(scores)
    entry = {"tag": tag, "max_ic": best,
             "top_primer": min(i for i, s in enumerate(scores) if s == best)}
    if tag == "K4":
        assert ct == K4
        entry["type"] = "K4"
    elif tag.startswith("NULL_"):
        assert Counter(ct) == Counter(K4), "null must preserve ciphertext histogram"
        entry["type"] = "NULL"
    else:
        t = truth[tag]
        primer = int(t["primer"][6:])
        reciphered = encrypt(t["plaintext"], list(range(97)), "ID",
                             make_key("CHAIN", "5", t["primer"]), t["PA"], t["CA"], "VIG")
        assert ct == t["ciphertext"] == reciphered
        score = scores[primer]
        true_rank = 1 + sum(1 for i, s in enumerate(scores)
                            if s > score or (s == score and i < primer))
        entry.update({"type": "PLANT", "true_primer": primer,
                      "true_primer_ic": score, "true_primer_rank": true_rank,
                      "forward_ciphertext_verified": True})
    result.append(entry)
(exp / "REVEAL.json").write_text(json.dumps(result, indent=2) + "\n")
for x in result:
    print(x["tag"], "max IC", x["max_ic"],
          ("true primer rank " + str(x["true_primer_rank"]) if x["type"] == "PLANT" else x["type"]))
