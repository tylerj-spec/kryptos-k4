#!/usr/bin/env python3
"""R111 sealed synthetic gate (PREREGISTRATION section 3). Synthetic only: reads no K4 file and no published plaintext.
Usage: python3 -I r111/gate111.py OUT.json"""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"
import hashlib  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE)]
import cells111 as C  # noqa: E402

SEED_PLANTS, SEED_SOLVER = 1110901, 1110902
AZ = C.AZ
CLUE_WORDS = ("EASTNORTHEAST", "NORTHEAST", "BERLIN", "CLOCK")
TEXT = ROOT / "r33/data/source_carter_mace_1923_google_ocr.txt"
SOURCES = ("cells111.py", "gate111.py", "run_target111.py", "evaluate111.py", "cluecheck111.py")


def corpus():
    return "".join(ch for ch in TEXT.read_text(errors="ignore").upper() if "A" <= ch <= "Z")


def window(rng, txt, n=97):
    while True:
        s = rng.randrange(0, len(txt) - n)
        w = txt[s:s + n]
        if not any(c in w for c in CLUE_WORDS):
            return w


def quagmire3(pt, key, alph):
    return "".join(alph[(alph.index(p) + alph.index(key[i % len(key)])) % 26] for i, p in enumerate(pt))


def main():
    out = Path(sys.argv[1])
    rng, srng = random.Random(SEED_PLANTS), random.Random(SEED_SOLVER)
    txt = corpus()
    t0w, t0c = time.time(), time.process_time()
    rep = {"round": "R111", "gate_type": "BLIND_SOLVER_RECOVERY", "seed_plants": SEED_PLANTS, "seed_solver": SEED_SOLVER,
           "cells": len(C.CELLS)}
    plants, cts = [], []
    for k in range(8):
        b = ("AZ", "KRY")[k % 2]
        L = k % 5 + 1
        sig = (1, 1, -1, -1)[k % 4]
        s1, s2 = rng.choice([sp for sp in [(1, 1), (1, -1), (-1, 1), (-1, -1)] if -sp[0] * sp[1] == sig])
        A = "".join(rng.sample(AZ, 26))
        c = rng.randrange(26)
        pt = window(rng, txt)
        ct = C.AK.encrypt(pt, A, C.B_LIST[b], "A", L, s1, s2, c, [rng.randrange(26) for _ in range(L)])
        cts.append(ct)
        T, rows = C.search(ct, srng, keep_text=True)
        top = max(rows, key=lambda r: r["score"])
        n = sum(x == y for x, y in zip(top["plaintext"], pt))
        right_cell = (top["B"], top["L"], top["sigma"]) == (b, L, sig)
        plants.append({"B": b, "L": L, "sigma": sig, "signs": [s1, s2], "T": T,
                       "top_cell": [top["B"], top["L"], top["sigma"]], "top_letters": n, "right_cell": right_cell,
                       "recovered": right_cell and n >= 90, "reencrypt_all": all(r["reencrypts"] for r in rows),
                       "cell_scores": [r["score"] for r in rows]})
    decoys = []
    for k in range(3):
        lst = list(cts[k])
        rng.shuffle(lst)
        T, rows = C.search("".join(lst), srng)
        decoys.append({"kind": f"shuffle_of_plant_{k}", "T": T, "reencrypt_all": all(r["reencrypts"] for r in rows)})
    for period in (7, 8):
        key = "".join(rng.choice(AZ) for _ in range(period))
        T, rows = C.search(quagmire3(window(rng, txt), key, C.B_LIST["KRY"]), srng)
        decoys.append({"kind": f"quagmire3_KRY_period_{period}", "T": T,
                       "reencrypt_all": all(r["reencrypts"] for r in rows)})
    rec = [p for p in plants if p["recovered"]]
    dmax = max(d["T"] for d in decoys)
    reenc = all(p["reencrypt_all"] for p in plants) and all(d["reencrypt_all"] for d in decoys)
    checks = {"recovered_ge6": len(rec) >= 6, "recovered_above_every_decoy": bool(rec) and min(p["T"] for p in rec) > dmax,
              "reencryption_all": reenc}
    rep.update({"plants": plants, "decoys": decoys, "recovered": len(rec), "decoy_max_T": dmax,
                "recovered_min_T": min(p["T"] for p in rec) if rec else None, "checks": checks})
    rep["status"] = "COMPLETE"
    rep["gate_verdict"] = "GO" if all(checks.values()) else "NO-GO"
    rep["wall_s"], rep["cpu_s"] = round(time.time() - t0w, 2), round(time.process_time() - t0c, 2)
    rep["source_sha256"] = {f: hashlib.sha256((HERE / f).read_bytes()).hexdigest() for f in SOURCES}
    out.write_text(json.dumps(rep, indent=1) + "\n")
    print(rep["gate_verdict"], json.dumps(checks), "recovered", len(rec), "decoy max", dmax)


if __name__ == "__main__":
    main()
