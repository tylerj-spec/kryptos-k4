#!/usr/bin/env python3
"""R110 sealed synthetic gate (PREREGISTRATION section 2). Synthetic only: reads no K4 file.
Usage: python3 -I r110/gate110.py OUT.json"""
import hashlib
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "r100")]
import autokey100 as AK  # noqa: E402
import lagpair110 as LP  # noqa: E402

SEED = 1100901
AZ = AK.AZ
CLUE_WORDS = ("EASTNORTHEAST", "NORTHEAST", "BERLIN", "CLOCK")
TEXT = ROOT / "r33/data/source_carter_mace_1923_google_ocr.txt"
SOURCES = ("lagpair110.py", "gate110.py", "run_target110.py", "evaluate110.py")


def corpus():
    return "".join(ch for ch in TEXT.read_text(errors="ignore").upper() if "A" <= ch <= "Z")


def window(rng, txt, n=97):
    while True:
        s = rng.randrange(0, len(txt) - n)
        w = txt[s:s + n]
        if not any(c in w for c in CLUE_WORDS):
            return w


def main():
    out = Path(sys.argv[1])
    rng = random.Random(SEED)
    txt = corpus()
    t0w, t0c = time.time(), time.process_time()
    rep = {"round": "R110", "gate_type": "STATISTIC_POWER_AND_SIZE", "seed": SEED}
    dis = 0
    for _ in range(500):
        s = "".join(rng.choice(AZ) for _ in range(97))
        dis += sum(LP.R_counter(s, L) != LP.R_sorted(s, L) for L in range(1, 25))
    rep["G1_two_implementations"] = {"strings": 500, "lags": 24, "disagreements": dis, "pass": dis == 0}
    sig = 0
    for _ in range(300):
        A, B = "".join(rng.sample(AZ, 26)), "".join(rng.sample(AZ, 26))
        F = rng.choice(AK.FEEDBACK)
        s1, s2 = rng.choice(AK.SIGNS)
        ct = AK.encrypt(window(rng, txt), A, B, F, 1, s1, s2, rng.randrange(26), [rng.randrange(26)])
        sig += LP.shuffle_p(ct, 1, rng, 1000) < 0.05
    rep["G2_power_L1"] = {"plants": 300, "significant": sig, "share": round(sig / 300, 4), "pass": sig / 300 >= 0.25}
    fp = 0
    for _ in range(300):
        s = "".join(rng.choice(AZ) for _ in range(97))
        fp += LP.shuffle_p(s, 1, rng, 1000) < 0.05
    rep["G3_size_L1"] = {"strings": 300, "significant": fp, "share": round(fp / 300, 4), "pass": fp / 300 <= 0.08}
    rep["status"] = "COMPLETE"
    rep["gate_verdict"] = "GO" if all(rep[g]["pass"] for g in ("G1_two_implementations", "G2_power_L1", "G3_size_L1")) \
        else "NO-GO"
    rep["wall_s"], rep["cpu_s"] = round(time.time() - t0w, 2), round(time.process_time() - t0c, 2)
    rep["source_sha256"] = {f: hashlib.sha256((HERE / f).read_bytes()).hexdigest() for f in SOURCES}
    out.write_text(json.dumps(rep, indent=1) + "\n")
    print(rep["gate_verdict"], json.dumps({g: rep[g] for g in rep if g[:1] == "G"}))


if __name__ == "__main__":
    main()
