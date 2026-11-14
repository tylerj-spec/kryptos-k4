"""R80a synthetic items: r79/items.py's passages, spelling variants, negatives and shuffles, with R80a plants
(r80a/two80.py), plus one near-miss negative.
Positives: free key 1..10 letters (gated); STRETCH plants 11..12 (reported only). L1/L2 listed keys are words of 3..12
letters; X1/X2 keys have 1..3 letters.
NEG_TWO_RANDOM: two keyword stages on the same alphabets and conventions, but both keys random strings of 4..12 letters
(never a list word, never a 1-3 letter key), so outside every R80a family."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "r75"))
sys.path.insert(0, str(ROOT / "r79"))
sys.path.insert(0, str(HERE))
import items as I79  # noqa: E402
import two80 as T  # noqa: E402

shuffles = I79.shuffles


def positives(book, per_fam, n_missp, n_nonstd, n_stretch, rng):
    ws, items = I79.words(book), []
    for fam in T.FAMS:
        for k in range(per_fam):
            kind = "POS_MISSP" if k < n_missp else "POS_NONSTD" if k < n_missp + n_nonstd else "POS"
            p = I79.passage(ws, rng, kind)
            st = T.random_setting(rng, fam)
            items.append({"kind": kind, "fam": fam, "pt": p, "setting": st, "ct": T.encrypt(p, st)})
        for _ in range(n_stretch):
            p = I79.passage(ws, rng, "POS")
            st = T.random_setting(rng, fam, 11, 12)
            items.append({"kind": "STRETCH", "fam": fam, "pt": p, "setting": st, "ct": T.encrypt(p, st)})
    return items


def two_random(book, n, rng):
    ws, items, listed = I79.words(book), [], set(T.word_list())
    for _ in range(n):
        p = I79.passage(ws, rng, "POS")
        while True:
            k1 = "".join(rng.choice(T.AZ) for _ in range(rng.randint(4, 12)))
            k2 = "".join(rng.choice(T.AZ) for _ in range(rng.randint(4, 12)))
            if k1 not in listed and k2 not in listed:
                break
        st = {"fam": "L1", "conv": list(T.CONVS[rng.randrange(len(T.CONVS))]), "word": k1, "free": k2,
              "m_free": len(k2)}
        items.append({"kind": "NEG_TWO_RANDOM", "pt": p, "setting": st, "ct": T.encrypt(p, st)})
    return items


def negatives(neg_pt, neg_key, n_per_arm, nrng, n_two, rng):
    return I79.negatives(neg_pt, neg_key, n_per_arm, nrng) + two_random(neg_pt, n_two, rng)
