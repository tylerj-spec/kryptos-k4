#!/usr/bin/env python3
"""R65 target: the unchanged 97-letter K4 ciphertext plus 300 FRESH frequency-preserving shuffles (seed 650070),
none equal to K4 or to any of R64's 100 shuffles (seed 640070). Reads only the ciphertext file (sha256-checked).
Usage: prepare.py OUT.tsv"""
import hashlib
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CT = ROOT / "r39/ic_gate/k4_ciphertext.txt"
CT_SHA256 = "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
SEED, NNULL = 650070, 300


def main():
    raw = CT.read_bytes()
    if hashlib.sha256(raw).hexdigest() != CT_SHA256:
        raise SystemExit("K4 ciphertext hash mismatch")
    ct = raw.decode().strip()
    old = {l.split("\t")[1] for l in (ROOT / "r64/k4/TARGET.tsv").read_text().splitlines()[1:] if l}
    rng = random.Random(SEED)
    rows, seen = ["id\tciphertext", f"K4\t{ct}"], {ct} | old
    while len(rows) < 2 + NNULL:
        c = list(ct)
        rng.shuffle(c)
        s = "".join(c)
        if s not in seen:
            seen.add(s)
            rows.append(f"NULL_{len(rows) - 2:03d}\t{s}")
    out = Path(sys.argv[1])
    if out.exists():
        raise SystemExit("refusing to overwrite")
    out.write_text("\n".join(rows) + "\n")
    print(f"wrote K4 + {NNULL} fresh nulls to {out}")


if __name__ == "__main__":
    main()
