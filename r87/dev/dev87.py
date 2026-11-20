#!/usr/bin/env python3
"""R87 development check on SPENT text (Tom Sawyer = r59 dev_pt; Dorian Gray = r59 dev_key). Synthetic only.
Positives: RX plants with random settings; reports the true setting's pass-1 rank, final letters right, timing.
Usage: python3 -I r87/dev/dev87.py DEV_PT.txt N OUT.json"""
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "blind"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import rotor87 as R  # noqa: E402
import solve87 as S  # noqa: E402


def main():
    txt = Path(sys.argv[1]).read_text().strip()
    n_items = int(sys.argv[2])
    rng = random.Random(850201)
    rows = []
    for k in range(n_items):
        o = rng.randrange(len(txt) - 97)
        pt = txt[o:o + 97]
        W = list(range(26))
        rng.shuffle(W)
        st = (rng.choice(R.A4), rng.choice(R.A4), rng.randint(1, S.PARAMS["NMAX"]), rng.choice((1, -1)))
        ct = R.encrypt(pt, W, *st)
        t0 = time.time()
        out, rank1, nset = S.solve(ct)
        best = out[0]
        rows.append({"setting": list(st), "pass1_rank_true": rank1[st],
                     "letters_right": sum(a == b for a, b in zip(best["text"], pt)),
                     "best_quad": best["quad"] / 94, "true_quad": R.Quad().score(pt) / 94, "seconds": time.time() - t0})
        print(rows[-1], flush=True)
    Path(sys.argv[3]).write_text(json.dumps(rows, indent=1) + "\n")


if __name__ == "__main__":
    main()
