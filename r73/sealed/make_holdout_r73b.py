#!/usr/bin/env python3
"""R73b sealed holdout (never read by r73/blind/run_r73b.py). Synthetic only; no K4 data.
  Positives: 100 Family R26 messages; each is consecutive whole words of PT_BOOK totalling exactly 97 letters,
             enciphered with a hidden setting drawn uniformly from R26's 52 settings.
  Negatives: 300 = 40 from each of R71's seven generators (OTP, RUNKEY, PERIODIC, HOMOPHONIC, GROMARK, CTAK, PTAK),
             built on NEG_PT_BOOK with running keys from NEG_KEY_BOOK, plus 20 frequency-preserving shuffles of
             positive ciphertexts.
Ids H_000..H_399 are assigned in a seeded random order, so the blind runner cannot tell kinds apart. The three books
are checked against the sha256 values fixed in r73/R73B_PREREGISTRATION.md.
Usage: make_holdout_r73b.py PT_BOOK NEG_PT_BOOK NEG_KEY_BOOK SEED OUTDIR   (writes blind.tsv and sealed_truth.json)"""
import hashlib
import json
import random
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "r73"))
sys.path.insert(0, str(ROOT / "r71"))
import wordkey as W  # noqa: E402
import generators as G  # noqa: E402

N = 97
BOOK_SHA256 = {
    "pt": "c7603d40299051f8bdde8dfe0e7c7bfb9b414a337fb3b04f5b7ff72342c0ffc0",
    "neg_pt": "03a57076de9eb1fe8143b54d2a795af5600a443c373d72c051603a80e2e038d0",
    "neg_key": "f2ea387ba7cae60ada941bb1b6b4cc1ee960582503eca48b9b602c9cd07dd237",
}


def main():
    pt_book, neg_pt, neg_key, seed, outdir = sys.argv[1:6]
    for role, p in (("pt", pt_book), ("neg_pt", neg_pt), ("neg_key", neg_key)):
        if hashlib.sha256(Path(p).read_bytes()).hexdigest() != BOOK_SHA256[role]:
            raise SystemExit(f"{role} book sha256 mismatch")
    seed, outdir = int(seed), Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    if any(outdir.iterdir()):
        raise SystemExit("refusing to overwrite")
    rng = random.Random(seed)
    words = re.findall(r"[A-Z]+", Path(pt_book).read_text(encoding="utf-8", errors="ignore").upper())
    items = []
    sts = W.settings("R26")
    for _ in range(100):
        while True:
            i = rng.randrange(len(words) - 60)
            msg, n = [], 0
            while n < N:
                msg.append(words[i])
                n += len(words[i])
                i += 1
            if n == N:
                break
        st = sts[rng.randrange(len(sts))]
        items.append({"kind": "R26", "setting": list(st), "words": msg, "ct": W.encrypt(msg, "R26", st)})
    letters = lambda p: np.frombuffer("".join(re.findall(r"[A-Z]", Path(p).read_text(  # noqa: E731
        encoding="utf-8", errors="ignore").upper())).encode(), dtype=np.uint8).astype(np.int16) - 65
    pt, kt = letters(neg_pt), letters(neg_key)
    routes = [[int(x) for x in l.split()[2].split(",")] for l in (ROOT / "r61/routes.txt").read_text().splitlines()]
    nrng = np.random.default_rng(seed + 1)
    for arm in ("OTP", "RUNKEY", "PERIODIC", "HOMOPHONIC", "GROMARK", "CTAK", "PTAK"):
        C, par = G.gen(arm, nrng, 40, pt, kt, routes)
        for r in range(40):
            items.append({"kind": "NEG_" + arm, "param": int(par[r]), "ct": "".join(chr(65 + int(v)) for v in C[r])})
    for p in rng.sample([x for x in items if x["kind"] == "R26"], 20):
        c = list(p["ct"])
        rng.shuffle(c)
        items.append({"kind": "NEG_SHUFFLE", "ct": "".join(c)})
    rng.shuffle(items)
    truth, lines = {}, []
    for k, it in enumerate(items):
        rid = f"H_{k:03d}"
        truth[rid] = it
        lines.append(f"{rid}\t{it['ct']}")
    (outdir / "blind.tsv").write_text("id\tciphertext\n" + "\n".join(lines) + "\n")
    (outdir / "sealed_truth.json").write_text(json.dumps(truth, indent=1, sort_keys=True) + "\n")
    print(f"wrote {len(items)} ciphertexts to {outdir}")


if __name__ == "__main__":
    main()
