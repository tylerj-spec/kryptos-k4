#!/usr/bin/env python3
"""R103 registered run (PREREGISTRATION section 3): identifiability of the two-free-alphabet plaintext autokey at 97
letters, by the false-consistency rate of unrelated English passages under R102's exact test. Synthetic only.
Usage: python3 -I r103/run103.py OUT.json"""
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
sys.path[:0] = [str(ROOT / "r102"), str(ROOT / "r100")]
import autokey100 as AK  # noqa: E402
import s3b102 as S  # noqa: E402
import dfs102 as D  # noqa: E402

SEED = 1030901
AZ = AK.AZ
CLUE_WORDS = ("EASTNORTHEAST", "NORTHEAST", "BERLIN", "CLOCK")
LAGS = (1, 2, 3, 5, 8, 13, 21, 40)
CELLS = [(s1, s2, F) for s1, s2 in AK.SIGNS for F in AK.FEEDBACK]
GUARD_CPU = 1400.0
TEXT = ROOT / "r33/data/source_carter_mace_1923_google_ocr.txt"


def corpus():
    return "".join(ch for ch in TEXT.read_text(errors="ignore").upper() if "A" <= ch <= "Z")


def window(rng, txt, n=97):
    while True:
        s = rng.randrange(0, len(txt) - n)
        w = txt[s:s + n]
        if not any(c in w for c in CLUE_WORDS):
            return w, s


def decide(ct, hyp, L, cell):
    st, d, wit = S.solve(ct, hyp, L, *cell)
    if st == "UNDECIDED":
        st = D.solve(ct, hyp, L, *cell, node_cap=100_000)
    return st, wit


def hit(ct, hyp, L, cells):
    """A hit: some cell CONSISTENT, or UNDECIDED (conservative)."""
    for cell in cells:
        if decide(ct, hyp, L, cell)[0] != "INCONSISTENT":
            return True
    return False


def witness_ok(ct, pt, L, s1, s2, F, wit):
    A, B, c = wit
    return all(AK.enc_letter(pt[i], pt[i - L], A, B, F, s1, s2, c) == ct[i] for i in range(L, len(ct)))


def main():
    out = Path(sys.argv[1])
    rng = random.Random(SEED)
    txt = corpus()
    t0w, t0c = time.time(), time.process_time()
    cpu = lambda: time.process_time() - t0c  # noqa: E731
    plants = []
    for k in range(300):
        L = LAGS[k % len(LAGS)]
        A, B = "".join(rng.sample(AZ, 26)), "".join(rng.sample(AZ, 26))
        F = rng.choice(AK.FEEDBACK)
        s1, s2 = rng.choice(AK.SIGNS)
        pt, start = window(rng, txt)
        ct = AK.encrypt(pt, A, B, F, L, s1, s2, rng.randrange(26), [rng.randrange(26) for _ in range(L)])
        plants.append({"L": L, "cell": (s1, s2, F), "pt": pt, "ct": ct, "start": start})

    def unrelated(p):
        while True:
            w, s = window(rng, txt)
            if abs(s - p["start"]) >= 97:
                return w

    rep = {"round": "R103", "seed": SEED}
    bad = 0
    for p in plants[:100]:
        st, wit = decide(p["ct"], list(p["pt"]), p["L"], p["cell"])
        bad += st != "CONSISTENT" or not witness_ok(p["ct"], p["pt"], p["L"], *p["cell"], wit)
    rep["G1_soundness"] = {"plants": 100, "failures": bad, "pass": bad == 0}

    both = dis = 0
    for k in range(40):
        p = plants[100 + k]
        src = p["pt"] if k < 20 else unrelated(p)
        n = 97 if k % 2 else 60
        hyp = list(src[:n]) + [None] * (97 - n)
        a = S.solve(p["ct"], hyp, p["L"], *p["cell"])[0]
        b = D.solve(p["ct"], hyp, p["L"], *p["cell"])
        dec = a in ("CONSISTENT", "INCONSISTENT") and b in ("CONSISTENT", "INCONSISTENT")
        both += dec
        dis += dec and a != b
    rep["G2_two_solvers"] = {"cases": 40, "both_decided": both, "disagreements": dis, "pass": dis == 0 and both >= 30}

    hits, by_lag = 0, {}
    for p in plants:
        for _ in range(10):
            h = hit(p["ct"], list(unrelated(p)), p["L"], CELLS)
            hits += h
            r = by_lag.setdefault(str(p["L"]), [0, 0])
            r[0] += h
            r[1] += 1
    rep["M2_primary"] = {"trials": 3000, "hits": hits, "by_lag_hits_trials": by_lag, "cpu_after_s": round(cpu(), 1)}

    m1 = {}
    for n in (30, 45, 60):
        h = t = 0
        lag = {}
        for p in plants:
            if cpu() >= GUARD_CPU:
                break
            hyp = list(unrelated(p)[:n]) + [None] * (97 - n)
            x = hit(p["ct"], hyp, p["L"], [p["cell"]])
            h += x
            t += 1
            r = lag.setdefault(str(p["L"]), [0, 0])
            r[0] += x
            r[1] += 1
        m1[str(n)] = {"trials": t, "hits": h, "by_lag_hits_trials": lag, "truncated": t < len(plants)}
    rep["M1_curve"] = m1

    h = t = 0
    for p in plants[:100]:
        if cpu() >= GUARD_CPU:
            break
        hyp = list(unrelated(p))
        x = any(hit(p["ct"], hyp, L, CELLS) for L in range(1, 25))
        h += x
        t += 1
    rep["M3_unknown_lag"] = {"trials": t, "hits": h, "truncated": t < 100}

    if not (rep["G1_soundness"]["pass"] and rep["G2_two_solvers"]["pass"]):
        verdict = "GATE_FAILED"
    elif hits == 0:
        verdict = "IDENTIFIABLE"
    elif hits / 3000 >= 0.01:
        verdict = "NOT_IDENTIFIABLE"
    else:
        verdict = "UNCLEAR"
    rep["verdict"] = verdict
    rep["wall_s"], rep["cpu_s"] = round(time.time() - t0w, 2), round(cpu(), 2)
    rep["source_sha256"] = {"run103.py": hashlib.sha256((HERE / "run103.py").read_bytes()).hexdigest()}
    out.write_text(json.dumps(rep, indent=1) + "\n")
    print(verdict, json.dumps({k: v for k, v in rep.items() if k[:1] in "GM"}))


if __name__ == "__main__":
    main()
