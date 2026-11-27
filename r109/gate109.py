#!/usr/bin/env python3
"""R109 sealed synthetic gate (PREREGISTRATION section 3). Synthetic only: reads no K4 file and no published letter or
position. Usage: python3 -I r109/gate109.py OUT.json"""
import hashlib
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE)]
import check109 as K  # noqa: E402

SEED = 1090901
AZ = K.AZ
CLUE_WORDS = ("EASTNORTHEAST", "NORTHEAST", "BERLIN", "CLOCK")
TEXT = ROOT / "r33/data/source_carter_mace_1923_google_ocr.txt"
LAGS_V1 = list(range(1, 13)) + list(range(30, 53))
SOURCES = ("check109.py", "gate109.py", "run_target109.py", "evaluate109.py", "AMENDMENT_1.md", "AMENDMENT_2.md")


def corpus():
    return "".join(ch for ch in TEXT.read_text(errors="ignore").upper() if "A" <= ch <= "Z")


def window(rng, txt, n=97):
    while True:
        s = rng.randrange(0, len(txt) - n)
        w = txt[s:s + n]
        if not any(c in w for c in CLUE_WORDS):
            return w


def mask(rng):
    while True:
        a0, b0 = rng.randrange(0, 85), rng.randrange(0, 87)
        pos = set(range(a0, a0 + 13)) | set(range(b0, b0 + 11))
        if len(pos) == 24:
            return sorted(pos)


def main():
    out = Path(sys.argv[1])
    rng = random.Random(SEED)
    txt = corpus()
    t0w, t0c = time.time(), time.process_time()
    rep = {"round": "R109", "gate_type": "EXACT_CHECKER_CORRECTNESS", "seed": SEED}
    f1 = f2 = badw = noeq = 0
    mix = {}
    for _ in range(150):
        A, B = "".join(rng.sample(AZ, 26)), "".join(rng.sample(AZ, 26))
        F = rng.choice(K.FEEDBACK)
        s1, s2 = rng.choice(K.SIGNS)
        L = rng.choice(LAGS_V1)
        pt = window(rng, txt)
        ct = K.AK.encrypt(pt, A, B, F, L, s1, s2, rng.randrange(26), [rng.randrange(26) for _ in range(L)])
        pos = mask(rng)
        hyp = [pt[i] if i in pos else None for i in range(97)]
        v, prim, wit = K.exact(ct, hyp, L, s1, s2, F, with_witness=True)
        mix[v] = mix.get(v, 0) + 1
        noeq += v == "NO_EQUATIONS"
        f1 += v == "INCONSISTENT" or (v != "NO_EQUATIONS" and K.dfs_crosscheck(ct, hyp, L, s1, s2, F) == "INCONSISTENT")
        badw += prim == "CONSISTENT" and not K.witness_ok(ct, hyp, L, s1, s2, F, wit)
        j = rng.choice(pos)
        h2 = list(hyp)
        h2[j] = rng.choice([x for x in AZ if x != pt[j]])
        v2 = K.exact(ct, h2, L, s1, s2, F)[0]
        f2 += v2 == "INCONSISTENT" and K.drop(ct, h2, L, s1, s2, F)
    rep["V1_soundness"] = {"plants": 150, "verdicts": mix, "no_equations": noeq, "inconsistent_true_hypotheses": f1,
                           "bad_witnesses": badw, "pass": f1 == 0 and badw == 0}
    rep["V2_one_error"] = {"plants": 150, "excluded_drop_with_one_error": f2, "pass": f2 == 0}
    both = dis = n = 0
    while n < 600:                                       # AMENDMENT_2 (approved): 600 cases
        L = rng.choice(LAGS_V1)
        F = rng.choice(K.FEEDBACK)
        s1, s2 = rng.choice(K.SIGNS)
        pos = mask(rng)
        ct = "".join(rng.choice(AZ) for _ in range(97))
        hyp = [rng.choice(AZ) if i in pos else None for i in range(97)]
        a = K.primary_only(ct, hyp, L, s1, s2, F)
        if a == "NO_EQUATIONS":
            continue
        n += 1
        b = K.dfs_crosscheck(ct, hyp, L, s1, s2, F)
        dec = a in ("CONSISTENT", "INCONSISTENT") and b in ("CONSISTENT", "INCONSISTENT")
        both += dec
        dis += dec and a != b
    rep["V3_two_solvers"] = {"cases": 600, "both_decided": both, "disagreements": dis, "pass": dis == 0 and both >= 40}
    rep["status"] = "COMPLETE"
    rep["gate_verdict"] = "GO" if all(rep[v]["pass"] for v in ("V1_soundness", "V2_one_error", "V3_two_solvers")) else "NO-GO"
    rep["wall_s"], rep["cpu_s"] = round(time.time() - t0w, 2), round(time.process_time() - t0c, 2)
    rep["source_sha256"] = {s: hashlib.sha256((HERE / s).read_bytes()).hexdigest() for s in SOURCES}
    out.write_text(json.dumps(rep, indent=1) + "\n")
    print(rep["gate_verdict"], json.dumps({v: rep[v] for v in rep if v[:1] == "V"}))


if __name__ == "__main__":
    main()
