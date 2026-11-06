#!/usr/bin/env python3
"""R69 target (sealed side; the blind runner sees only id, ciphertext, set):
  K4 (set A), the unchanged 97-letter ciphertext (sha256-checked);
  SHUF_000-299: 300 fresh frequency-preserving shuffles of K4 (seed 690070), none equal to K4 or to any R64/R65 null;
                SHUF_000-099 get set A (all 78 readings), SHUF_100-299 set F (the 16 F readings);
  R67_CTRL_*: the 192 IC-matched structured-cipher controls of R67 (r69/data/r67_structured.tsv, extracted from
              PR #50 head 14c6690), set F.
Usage: prepare.py OUT.tsv"""
import hashlib
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CT = ROOT / "r39/ic_gate/k4_ciphertext.txt"
CT_SHA256 = "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
STRUCT = ROOT / "r69/data/r67_structured.tsv"
STRUCT_SHA256 = "b4430b3f140d11dc41f27e66d1dfdd8b22da300428ee74ef3350c8db50c64e1c"
SEED, NNULL, NSET_A = 690070, 300, 100


def main():
    raw = CT.read_bytes()
    if hashlib.sha256(raw).hexdigest() != CT_SHA256:
        raise SystemExit("K4 ciphertext hash mismatch")
    if hashlib.sha256(STRUCT.read_bytes()).hexdigest() != STRUCT_SHA256:
        raise SystemExit("structured-control file hash mismatch")
    ct = raw.decode().strip()
    old = set()
    for f in ("r64/k4/TARGET.tsv", "r65/k4/TARGET.tsv"):
        old |= {l.split("\t")[1] for l in (ROOT / f).read_text().splitlines()[1:] if l}
    rng = random.Random(SEED)
    rows, seen = ["id\tciphertext\tset", f"K4\t{ct}\tA"], {ct} | old
    while len(rows) < 2 + NNULL:
        c = list(ct)
        rng.shuffle(c)
        s = "".join(c)
        if s not in seen:
            seen.add(s)
            i = len(rows) - 2
            rows.append(f"SHUF_{i:03d}\t{s}\t{'A' if i < NSET_A else 'F'}")
    for l in STRUCT.read_text().splitlines()[1:]:
        rid, c, _fam = l.split("\t")
        rows.append(f"{rid}\t{c}\tF")
    out = Path(sys.argv[1])
    if out.exists():
        raise SystemExit("refusing to overwrite")
    out.write_text("\n".join(rows) + "\n")
    print(f"wrote K4 + {NNULL} shuffles + 192 structured controls to {out}")


if __name__ == "__main__":
    main()
