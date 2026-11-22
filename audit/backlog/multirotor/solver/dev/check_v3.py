#!/usr/bin/env python3
"""Version-3 kernel check (synthetic; random texts, no panel truth): (1) every restart score the kernel returns equals
97 x core.Scorer.lm_score truncated at order 5 (lean_scorer with order 5) on the explicit decrypt of its wirings;
(2) the throughput in proposals per CPU second.  Usage: check_v3.py LM.bin"""
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
import run_v2  # noqa: E402
import solve_v3 as S  # noqa: E402
import rx2o as X  # noqa: E402


def main():
    lm = sys.argv[1]
    import core
    sc = run_v2.lean_scorer(lm)
    sc.order = 5
    rng = random.Random(930902)
    for _ in range(6):
        W1, W2 = list(range(26)), list(range(26))
        rng.shuffle(W1)
        rng.shuffle(W2)
        lab = rng.choice(X.LABELS)
        ct = X.encrypt("".join(rng.choice(X.AZ) for _ in range(97)), W1, W2, *lab)
        for v, A, B, text in S.restarts(ct, lab, 2, 3000, 2.0, rng.randrange(1, 2 ** 60), lm):
            ref = 97 * float(sc.lm_score(core.codes(text)[None])[0])
            assert abs(ref - v) < 1e-3, (ref, v)
    print("1 ok: kernel scores equal 97 x the order-5 letter-model score of rx2o.decrypt (12 restarts)")
    lab = ("AZ", "KRY", 2, 1, 5, 1, -1)
    ct = X.encrypt("".join(rng.choice(X.AZ) for _ in range(97)), W1, W2, *lab)
    t = time.process_time()
    S.restarts(ct, lab, 2, 500000, 4.0, 7, lm)
    print("2 speed:", round(1e6 / (time.process_time() - t)), "proposals per CPU second")


if __name__ == "__main__":
    main()
