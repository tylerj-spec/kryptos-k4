"""R81a synthetic items: r79/items.py's passages, spelling variants, negatives and shuffles, with R81a plants
(r81a/families81.py). Keyword lengths 2..10 for gated plants; STRETCH plants 11..12, reported only."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "r75"))
sys.path.insert(0, str(ROOT / "r79"))
sys.path.insert(0, str(HERE))
import families81 as F  # noqa: E402
import items as I79  # noqa: E402

negatives, shuffles = I79.negatives, I79.shuffles


def positives(book, per_fam, n_missp, n_nonstd, n_stretch, rng):
    ws, items = I79.words(book), []
    for fam in F.FAMS:
        for k in range(per_fam):
            kind = "POS_MISSP" if k < n_missp else "POS_NONSTD" if k < n_missp + n_nonstd else "POS"
            p = I79.passage(ws, rng, kind)
            st = F.random_setting(rng, fam)
            items.append({"kind": kind, "fam": fam, "pt": p, "setting": st, "ct": F.encrypt(p, st)})
        for _ in range(n_stretch):
            p = I79.passage(ws, rng, "POS")
            st = F.random_setting(rng, fam, 11, 12)
            items.append({"kind": "STRETCH", "fam": fam, "pt": p, "setting": st, "ct": F.encrypt(p, st)})
    return items
