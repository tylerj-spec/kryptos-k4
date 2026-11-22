#!/usr/bin/env python3
"""RX2-O development tests (synthetic only). 1 rx2o.encrypt equals ChatGPT's rotor_constraints.encrypt with its
odometer (contact alphabets applied outside), round trips; 2 16,640 labels; every label's turnover count matches its
cell; 3 the kernel's per-restart score equals the quadgram score of rx2o.decrypt of the returned wirings.
Usage: python3 -I audit/backlog/multirotor/solver/tests/test_rx2o.py"""
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path[:0] = [str(HERE.parent), str(ROOT / "audit/backlog/multirotor"), str(ROOT / "r87")]
import rx2o as X  # noqa: E402
import rotor_constraints as RC  # noqa: E402
import solve_v1 as S  # noqa: E402
import rotor87  # noqa: E402

CELL_TURN = {"n1t3": 3, "n1t4": 4, "n2t1": 1, "n2t2": 2, "n3t1": 1, "n3t2": 2, "n4t0": 0, "n4t1": 1}


def main():
    rng = random.Random(930901)
    for _ in range(300):
        W1, W2 = list(range(26)), list(range(26))
        rng.shuffle(W1)
        rng.shuffle(W2)
        lab = rng.choice(X.LABELS)
        pt = "".join(rng.choice(X.AZ) for _ in range(97))
        ct = X.encrypt(pt, W1, W2, *lab)
        ein, eout, n, r, h, d1, d2 = lab
        ref = RC.encrypt([X.IDX[ein][p] for p in pt], W1, W2, RC.odometer(97, n, r, h, d1, d2))
        assert ct == "".join(X.ALPH[eout][v] for v in ref)
        assert X.decrypt(ct, W1, W2, *lab) == pt
    print("1 ok: 300 random labels equal rotor_constraints.encrypt + odometer; round trips")
    assert len(X.LABELS) == 16640 == len(set(X.LABELS))
    for lab in X.LABELS:
        _, _, n, r, h, _, _ = lab
        assert X.turnovers(97, n, r, h) == CELL_TURN[X.cell_of(n, r, h)]
    print("2 ok: 16,640 labels; every label's turnover count matches its cell")
    Q = rotor87.Quad()
    for _ in range(6):
        W1, W2 = list(range(26)), list(range(26))
        rng.shuffle(W1)
        rng.shuffle(W2)
        lab = rng.choice(X.LABELS)
        ct = X.encrypt("".join(rng.choice(X.AZ) for _ in range(97)), W1, W2, *lab)
        for sc, A, B, text in S.restarts(ct, lab, 2, 2000, 2.0, rng.randrange(1, 2 ** 60)):
            assert abs(Q.score(text) - sc) < 1e-2
    print("3 ok: kernel scores equal the quadgram score of rx2o.decrypt")
    print("RX2-O TESTS OK")


if __name__ == "__main__":
    main()
