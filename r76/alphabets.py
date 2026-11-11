"""R76 alphabet sets for H1 (no K4 data). An alphabet is a 26-letter ordering of A-Z built from a word:
  asc   the word's letters (repeats dropped), then the rest of A-Z ascending (the K1/K2 construction, core.keyed);
  desc  the word's letters, then the rest descending;
  aca   the ACA transposition-block alphabet (r38/aca_alphabet.py).
small_tier(): every word of r75/data/kryptos_words.txt, all three variants, plus A-Z.
large_tier(): every word of 4-15 letters in the R59 word model (k4kit/data/word_model_orth.tsv), all three
variants, plus A-Z. Duplicates (same 26-letter ordering) are merged; the first name is kept."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _d in ("r75", "r38"):                       # appended, so modules of the same name in r76/ keep priority
    if str(ROOT / _d) not in sys.path:
        sys.path.append(str(ROOT / _d))
import core  # noqa: E402
from aca_alphabet import aca_alphabet  # noqa: E402

AZ = core.AZ


def variants(w):
    head = "".join(dict.fromkeys(w))
    return {"asc": head + "".join(c for c in AZ if c not in head),
            "desc": head + "".join(c for c in AZ[::-1] if c not in head),
            "aca": aca_alphabet(w)}


def build(words):
    out, seen = [("AZ", AZ)], {AZ}
    for w in words:
        for kind, a in variants(w).items():
            assert sorted(a) == list(AZ)
            if a not in seen:
                seen.add(a)
                out.append((f"{w}/{kind}", a))
    return out


def kryptos_words():
    ws = []
    for line in (ROOT / "r75/data/kryptos_words.txt").read_text().splitlines():
        if not line.startswith("#"):
            ws += line.split()
    return ws


def small_tier():
    return build(kryptos_words())


def large_tier():
    words = sorted(w for w in core.load_words(maxlen=15) if 4 <= len(w) <= 15)
    return build(kryptos_words() + words)
