#!/usr/bin/env python3
"""R85 design pilot (moved to r87/dev with the R87 pre-registration; DESIGN.md §4 cites it) (SYNTHETIC ONLY; no K4 ciphertext, no published letters). Two measurements for the design:
  chance    the exact check on 50 random ciphertexts with random letters at K4's 24 published POSITIONS, every RX
            setting (16 alphabet pairs x d +-1 x n 1..96 = 3,072): how often a setting passes by chance;
  strength  the true setting's checks on 300 plants with English-frequency letters;
  blind     6 plants from spent development text (Tom Sawyer, r59 dev_pt), setting given, wiring hidden: annealing
            recovery, and the same solver under a wrong step period as a null.
Usage: python3 -I r87/dev/pilot85.py DEV_PT.txt OUT.json"""
import json
import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import rotor87 as R  # noqa: E402

POS = list(range(21, 34)) + list(range(63, 74))       # positions only (layout); no letters
SETTINGS = [(a, b, n, d) for a in R.A4 for b in R.A4 for n in range(1, 97) for d in (1, -1)]


def main():
    rng = random.Random(850002)
    feas, ck = 0, Counter()
    for _ in range(50):
        ct = "".join(rng.choice(R.AZ) for _ in range(97))
        let = [rng.choice(R.AZ) for _ in POS]
        for s in SETTINGS:
            ok, c = R.exact_check(ct, POS, let, *s)
            if ok:
                feas += 1
                ck[c] += 1
    true_ck = Counter()
    for _ in range(300):
        W = list(range(26))
        rng.shuffle(W)
        s = rng.choice(SETTINGS)
        pt = "".join(rng.choice("EEEETTTAAOOIINNSSHHRRDLCUMWFGYPB") for _ in range(97))
        true_ck[R.exact_check(R.encrypt(pt, W, *s), POS, [pt[i] for i in POS], *s)[1]] += 1
    rng = random.Random(850003)
    Q = R.Quad()
    txt = Path(sys.argv[1]).read_text().strip()
    blind = []
    for _ in range(6):
        o = rng.randrange(len(txt) - 97)
        pt = txt[o:o + 97]
        W = list(range(26))
        rng.shuffle(W)
        a, b = rng.choice(R.A4), rng.choice(R.A4)
        n, d = rng.choice((1, 2, 3, 7, 13)), rng.choice((1, -1))
        ct = R.encrypt(pt, W, a, b, n, d)
        sc, _, dec = R.anneal(ct, a, b, n, d, Q, rng, iters=20000, restarts=6)
        scn, _, _ = R.anneal(ct, a, b, n + 1, d, Q, rng, iters=20000, restarts=6)
        blind.append({"ein": a, "eout": b, "n": n, "d": d, "letters_right": sum(x == y for x, y in zip(dec, pt)),
                      "score_per_quad": sc / 94, "true_score_per_quad": Q.score(pt) / 94,
                      "wrong_period_score_per_quad": scn / 94})
    out = {"settings_per_ciphertext": len(SETTINGS), "random_trials": 50 * len(SETTINGS),
           "random_feasible": feas, "random_feasible_checks": dict(ck),
           "true_setting_checks": dict(sorted(true_ck.items())), "blind_pilot": blind}
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "blind_pilot"}))
    for b in blind:
        print(b)


if __name__ == "__main__":
    main()
