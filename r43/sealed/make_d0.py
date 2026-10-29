#!/usr/bin/env python3
"""Sealed D0 control generator. NEVER imported by the blind word solver.
All prose authored for this round, before any solver results; no ciphertext or text from K4.
"""
import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "r43" / "d0"
OUT.mkdir(parents=True, exist_ok=True)
if any(OUT.iterdir()):
    raise RuntimeError("refuse to overwrite existing D0 results")
SENTENCES = [
    "The morning rain had stopped and the people came out of their houses to walk along the river and talk about the new bridge which would open soon.",
    "My father found an old wooden box under the stairs and inside it were letters that his grandmother had written to her family many years before.",
    "When the train arrived at the little station the children ran outside and waved to their friends who had been waiting beside the long platform.",
    "We could hear the gentle sound of water moving through the stones while the distant hills were covered by the soft light of the evening sun.",
    "The young teacher opened the classroom door and asked the students to write about a place they had visited during their summer holidays.",
    "After the long journey we stopped at a small village where a kind woman offered us fresh bread and a warm place to sit beside the fire.",
    "There was a narrow path through the garden that led to a wooden gate and behind it stood an enormous tree with branches reaching the sky.",
    "Every morning the baker placed the warm loaves on the table and watched the people hurry down the street on their way to work.",
    "A sudden storm brought heavy clouds over the valley and the farmers hurried to bring their animals home before the first drops of rain fell.",
    "I remember the day we climbed the highest hill near our town and found a quiet place where we could watch the ships sailing across the sea.",
    "The librarian showed us a small book with a faded blue cover and explained that it had belonged to a famous explorer nearly a century ago.",
    "As the sun went down the old man lit the lamps in his shop and carefully counted the coins before locking the wooden door for the night.",
    "They followed the winding road through the forest until they reached a clear stream where they filled their bottles with cold fresh water.",
    "The little dog waited at the front window each day and ran to the door whenever he heard the familiar sound of his owner coming home.",
    "At the end of the market a friendly merchant showed us a beautiful painting of a harbor filled with fishing boats and bright white sails.",
    "The children gathered around the kitchen table to hear their mother tell a story about a strange light that once appeared above the mountain.",
    "Our family decided to leave early in the morning so we would have enough time to visit the old castle and explore the rooms inside the tower.",
    "She spent the afternoon writing a long letter to her brother and telling him about the wonderful things she had seen during her travels.",
    "The gardener planted a row of small trees near the road and promised that one day they would give shade to everyone walking into the town.",
    "We watched the workers lift the last stone into place and the entire crowd began to cheer when the new building was finally completed.",
]
def clean(t):
    return "".join(c for c in t.upper() if "A" <= c <= "Z")
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
seen = set()
truth = {}
inputs = ["id\tciphertext\tkey_digits"]
for i, sentence in enumerate(SENTENCES):
    p = clean(sentence)
    assert len(p) >= 97, (i, len(p))
    p = p[:97]
    assert p not in seen
    seen.add(p)
    rng = random.Random(43000 + i)
    pa = list(AZ); ca = list(AZ)
    rng.shuffle(pa); rng.shuffle(ca)
    primer = [rng.randrange(10) for _ in range(5)]
    k = primer[:]
    for j in range(5, 97):
        k.append((k[j-5] + k[j-4]) % 10)
    ct = "".join(ca[(pa.index(letter) + k[j]) % 26] for j, letter in enumerate(p))
    label = f"D0_{i:02}"
    inputs.append(label + "\t" + ct + "\t" + ",".join(map(str, k)))
    truth[label] = {"plaintext": p, "plaintext_alphabet": "".join(pa),
                    "ciphertext_alphabet": "".join(ca), "primer": "".join(map(str, primer))}
(OUT / "blind.tsv").write_text("\n".join(inputs) + "\n")
(OUT / "sealed_truth.json").write_text(json.dumps(truth, indent=2) + "\n")
(OUT / "INPUT.sha256").write_text(
    hashlib.sha256((OUT / "blind.tsv").read_bytes()).hexdigest() + "  blind.tsv\n")
print(f"Created {len(truth)} new D0 plants with independent random alphabets, true key supplied")
