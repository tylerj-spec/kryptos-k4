#!/usr/bin/env python3
"""R44 SEALED holdout generator (never read by r44/blind/). 20 passages written for R44, not used in development
(development used R43's D0_10, D0_11, D0_15 texts and L109's plants). Each passage is encrypted with a KEYWORD plaintext
alphabet (keyword drawn uniformly from the solver's candidate words), a uniformly random cipher alphabet and a uniformly
random 5-digit Gromark primer: c_i = CA[(PA_index(p_i) + k_i) mod 26]. Seeds 44200 + i.
Usage: make_holdout.py OUTDIR   (writes OUTDIR/blind.tsv and OUTDIR/sealed_truth.json; refuses to overwrite)"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
PASSAGES = [
    "On the first cold morning of winter the shepherd led his flock down from the hills and counted every animal twice before closing the gate.",
    "The old clockmaker kept a drawer full of tiny brass wheels and he could tell from the sound of a ticking watch exactly which part was worn.",
    "Our neighbors planted sunflowers along the fence and by the end of summer the flowers were taller than the roof of their small garden shed.",
    "When the ferry reached the island the passengers carried their bags along a stone pier and searched for the road that led up to the village.",
    "My sister learned to play the violin in an empty church because the walls made every note sound larger and more beautiful than at home.",
    "The fishermen returned before noon with nets full of silver fish and the whole harbor smelled of salt and smoke from the cooking fires.",
    "After the snow melted the children found a family of ducks living in the pond behind the school and fed them bread every afternoon.",
    "A traveling musician stopped in the square and played a cheerful song while the shopkeepers stepped outside their doors to listen.",
    "The museum guard walked slowly through the empty halls each night checking the locks and pausing in front of his favorite painting.",
    "We rented a small cabin beside the lake and spent the evenings reading by candlelight while the wind moved through the tall pine trees.",
    "Before dawn the bakers lit the ovens and filled the narrow street with the smell of bread that drew hungry workers from every direction.",
    "The captain studied the old chart for an hour and then ordered the crew to turn the ship south toward the warmer waters of the bay.",
    "Every spring the farmers gathered in the village hall to share seeds and stories and to argue about which field would yield the most grain.",
    "The student carried a heavy bag of books up the hill to the library and spent the whole day copying notes from a rare history of the city.",
    "During the festival the streets were decorated with paper lanterns and families walked together until midnight to watch the fireworks.",
    "A young fox appeared at the edge of the meadow each evening and watched the farmhouse until the lights were turned off for the night.",
    "The carpenter measured the board three times before cutting it and explained that patience was the most important tool in his workshop.",
    "Grandmother kept her recipes in a worn notebook and each page was marked with flour and small notes about who had eaten at her table.",
    "The mountain guide warned us that the weather could change quickly so we carried extra coats and food in case we had to stay overnight.",
    "At the end of the long road there was a quiet inn where travelers could rest their horses and share news from distant towns over dinner.",
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
        rng = random.Random(44200 + i)
        kw = rng.choice(words)
        pa = kw_alpha(kw)
        ca = list(AZ)
        rng.shuffle(ca)
        ca = "".join(ca)
        k = [rng.randrange(10) for _ in range(5)]
        while len(k) < 97:
            k.append((k[-5] + k[-4]) % 10)
        ct = "".join(ca[(pa.index(ch) + k[j]) % 26] for j, ch in enumerate(p))
        lab = f"H_{i:02d}"
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
