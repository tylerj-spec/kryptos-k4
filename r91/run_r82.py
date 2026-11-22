#!/usr/bin/env python3
"""Known-structure R82 power gate. Secret key and plaintext are never read.

Every library, public input record and output stream is loaded/opened before
seccomp. During candidate search, new file reads and network calls are denied.
"""
import argparse
import ctypes
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "vendor/r82"))
import pairwise_pilot as P
sys.path.insert(0, str(HERE))
import reference as R


def seed(row):
    public = {k: row[k] for k in ("ciphertext", "m", "w")}
    data = "R91_R82_12x100|" + json.dumps(public, sort_keys=True, separators=(",", ":"))
    return int(hashlib.sha256(data.encode()).hexdigest()[:15], 16)


def solve(row):
    P.RNG = np.random.default_rng(seed(row))
    c = np.array([ord(x)-65 for x in row["ciphertext"]], dtype=int)
    unary, edges = P.factors(c, row["m"], row["w"])
    key, score = P.solve(unary, edges, restarts=12, steps=100)
    key = "".join(R.AZ[int(v)] for v in key)
    plain = R.linked_decrypt(row["ciphertext"], key, row["w"])
    assert R.linked_encrypt(plain, key, row["w"]) == row["ciphertext"]
    return {"id": row["id"], "arm": "R82_LINKED", "key": key, "plaintext": plain,
            "objective": float(score), "seed": seed(row), "witness": True}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    args = ap.parse_args()
    rows = [json.loads(line) for line in Path(args.input).read_text().splitlines() if line]
    assert 0 < len(rows) <= 360 and len({r["id"] for r in rows}) == len(rows)
    for r in rows:
        assert set(r) == {"id", "arm", "ciphertext", "m", "w"}
        assert r["arm"] == "R82_LINKED" and len(r["ciphertext"]) == 97
        assert set(r["ciphertext"]) <= set(R.AZ)
    # Exercise first-use NumPy initialization using a fixed arbitrary dummy.
    dummy = {"id": "DUMMY", "arm": "R82_LINKED", "ciphertext": "A" * 97, "m": 3, "w": 3}
    solve(dummy)
    lib = ctypes.CDLL(str(HERE / "seccomp_io.so"))
    lib.r91_python_lock_io.restype = ctypes.c_int
    with Path(args.output).open("x") as out:
        for fd in os.listdir("/proc/self/fd"):
            n = int(fd)
            if n > 2 and n != out.fileno():
                try:
                    os.close(n)
                except OSError:
                    pass
        assert lib.r91_python_lock_io() == 0, "required input isolation unavailable"
        for i, row in enumerate(rows, 1):
            result = solve(row)
            out.write(json.dumps(result, sort_keys=True) + "\n")
            out.flush()
            if i % 20 == 0:
                print(f"R82 completed {i}/{len(rows)}", flush=True)


if __name__ == "__main__":
    main()
