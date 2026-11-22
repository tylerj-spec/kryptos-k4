#!/usr/bin/env python3
"""RX2-O development panel (SPENT books only; no K4, no clues). 6 plants per turnover cell (rx2o.CELLS) = 48, fixed
for all three solver versions. Within a cell: phases r balanced (n=2: 3/3; n=3: 2/2/2; n=4: 2/2/1/1), the four
direction pairs cycled, h uniform over the cell's range, contact pair and both wirings uniform; plaintext a random
97-letter window of a random spent book (letters only). Writes PANEL.tsv (id, label, ciphertext: supplied structure,
no wirings) and PANEL_TRUTH.json (development truth, opened by the evaluator).
Usage: make_panel.py BOOK1,BOOK2,... SEED OUTDIR"""
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path[:0] = [str(HERE.parents[1]), str(HERE.parents[5] / "r89" / "sealed")]
import rx2o as X  # noqa: E402
import make89 as M89  # noqa: E402


def main():
    books, seed, out = sys.argv[1].split(","), int(sys.argv[2]), Path(sys.argv[3])
    rng = random.Random(seed)
    T = [M89.letters(b, True) for b in books]
    rows, truth = [], {}
    k = 0
    for cell, (n, hr) in X.CELLS.items():
        phases = [i % n for i in range(6)] if n < 4 else [0, 1, 2, 3, 0, 1]
        dirs = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for j in range(6):
            r, (d1, d2), h = phases[j], dirs[(j + k) % 4], rng.choice(list(hr))
            label = (rng.choice(X.A4), rng.choice(X.A4), n, r, h, d1, d2)
            assert X.cell_of(n, r, h) == cell
            W1, W2 = list(range(26)), list(range(26))
            rng.shuffle(W1)
            rng.shuffle(W2)
            pt = M89.window(rng, T[rng.randrange(len(T))])
            ct = X.encrypt(pt, W1, W2, *label)
            rid = f"D_{k:03d}"
            rows.append(f"{rid}\t{','.join(map(str, label))}\t{ct}")
            truth[rid] = {"cell": cell, "label": label, "W1": W1, "W2": W2, "pt": pt, "ct": ct,
                          "turnovers": X.turnovers(97, n, r, h)}
            k += 1
    out.mkdir(parents=True, exist_ok=False)
    (out / "PANEL.tsv").write_text("id\tlabel\tciphertext\n" + "\n".join(rows) + "\n")
    (out / "PANEL_TRUTH.json").write_text(json.dumps(truth, indent=1) + "\n")
    print(len(rows), "plants")


if __name__ == "__main__":
    main()
