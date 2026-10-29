#!/usr/bin/env python3
"""R44b SEALED holdout generator (second, fresh holdout) (never read by r44/blind/). 20 passages written for R44b; none used before (the first R44 holdout is now development data)
(development used R43's D0_10, D0_11, D0_15 texts and L109's plants). Each passage is encrypted with a KEYWORD plaintext
alphabet (keyword drawn uniformly from the solver's candidate words), a uniformly random cipher alphabet and a uniformly
random 5-digit Gromark primer: c_i = CA[(PA_index(p_i) + k_i) mod 26]. Seeds 44300 + i.
Usage: make_holdout.py OUTDIR   (writes OUTDIR/blind.tsv and OUTDIR/sealed_truth.json; refuses to overwrite)"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
PASSAGES = [
    "The lighthouse keeper climbed the spiral stairs every evening to clean the great lens and watch the ships pass slowly along the rocky coast.",
    "My uncle grew tomatoes on the balcony of his apartment and every summer he gave baskets of them to the neighbors who lived on his floor.",
    "The orchestra rehearsed in a cold hall all afternoon and the conductor stopped them many times to repeat a difficult passage in the second part.",
    "A group of hikers followed the river upstream until they found a waterfall hidden behind the trees and stopped there to eat their lunch.",
    "The village blacksmith worked from sunrise to sunset shaping horseshoes and tools while children gathered at the door to watch the sparks.",
    "Every winter the town organized a race across the frozen lake and the winner received a wooden trophy carved by the oldest man in the town.",
    "The young doctor walked through the snow to visit a family on a distant farm and arrived just as the mother began to prepare a hot meal.",
    "We found an old map in the attic that showed the original streets of the town before the railway station and the new bridge were built.",
    "The painter set up her easel near the harbor each morning and tried to capture the changing colors of the water before the fog lifted.",
    "When the power failed during the storm the whole family gathered in the kitchen and told stories by the light of a single candle until dawn.",
    "The farmer repaired the stone wall around his field after the spring rains and found an ancient coin buried in the mud near the gate.",
    "Our school took a trip to the science museum where we watched a model of the planets moving slowly around a bright lamp in a dark room.",
    "The mail carrier knew every dog on her route by name and always kept a few biscuits in her pocket to make sure the morning went smoothly.",
    "A strong wind carried the kite high above the beach and the little boy laughed as he ran along the sand holding tightly to the string.",
    "The tailor measured the groom carefully and promised that the suit would be finished in time for the wedding at the end of the month.",
    "After many years abroad the sailor returned to his village and found that the old tavern by the river had become a busy bakery and shop.",
    "The scientists camped on the glacier for three weeks to measure how quickly the ice was moving toward the valley far below their tents.",
    "Every Sunday morning the market square filled with farmers selling cheese and honey while musicians played old songs near the fountain.",
    "The firefighters practiced on the empty field behind the station and the neighbors came out to watch them climb the tall metal ladder.",
    "She planted a small garden of herbs outside the kitchen window so that she could pick fresh leaves while she cooked dinner for her family.",
]


def clean(t):
    return "".join(c for c in t.upper() if "A" <= c <= "Z")


def candidate_words(kcand=5000):
    """Same rule as the blind solver: top KCAND exact ORTH words of length 5-10 (ties by word)."""
    ws = []
    for ln in (ROOT / "k4kit/data/word_model_orth.tsv").read_text().splitlines():
        w, ex, ed = ln.split()
        if float(ex) > -1e90 and 5 <= len(w) <= 10:
            ws.append((-float(ex), w))
    ws.sort()
    return [w for _, w in ws[:kcand]]


def kw_alpha(w):
    out = ""
    for ch in w + AZ:
        if ch not in out:
            out += ch
    return out


def main():
    out = Path(sys.argv[1]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    if any(out.iterdir()):
        raise SystemExit("refusing to overwrite an existing holdout")
    words = candidate_words()
    rows, truth = ["id\tciphertext\tkey_digits"], {}
    for i, text in enumerate(PASSAGES):
        p = clean(text)
        assert len(p) >= 97, (i, len(p))
        p = p[:97]
        for w in ("NORTHEAST", "BERLIN", "CLOCK"):
            assert w not in p
        rng = random.Random(44300 + i)
        kw = rng.choice(words)
        pa = kw_alpha(kw)
        ca = list(AZ)
        rng.shuffle(ca)
        ca = "".join(ca)
        k = [rng.randrange(10) for _ in range(5)]
        while len(k) < 97:
            k.append((k[-5] + k[-4]) % 10)
        ct = "".join(ca[(pa.index(ch) + k[j]) % 26] for j, ch in enumerate(p))
        lab = f"HB_{i:02d}"
        rows.append(f"{lab}\t{ct}\t{','.join(map(str, k))}")
        truth[lab] = {"plaintext": p, "keyword": kw, "plaintext_alphabet": pa, "ciphertext_alphabet": ca,
                      "primer": "".join(map(str, k[:5]))}
    (out / "blind.tsv").write_text("\n".join(rows) + "\n")
    (out / "sealed_truth.json").write_text(json.dumps(truth, indent=1) + "\n")
    print(f"wrote {len(truth)} holdout ciphertexts to {out}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        print([len(clean(t)) for t in PASSAGES])
    else:
        main()
