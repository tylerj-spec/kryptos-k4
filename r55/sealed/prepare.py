#!/usr/bin/env python3
"""SEALED R55 control and target input preparation. Never mount this in blind runtime."""
import hashlib
import json
import random
import sys
from pathlib import Path

N = 97
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ORIGINAL_SHA256 = "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
MULTIPLIERS = (1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25)

# Twenty independently written ordinary-English passages. This is a limited synthetic
# test distribution, not evidence for the unknown style or construction of original K4.
PASSAGES = (
    "The caretaker unlocked the garden gate before sunrise and followed a winding trail beside the silent river until the old bridge came into view.",
    "In the kitchen the baker carefully measured flour and butter while her youngest brother stacked clean plates beside the window overlooking the orchard.",
    "Every autumn a small group of hikers climbed the grassy ridge and watched the clouds gather over the distant mountains before returning to camp.",
    "The repairman examined the cracked wooden frame and replaced the broken hinges before the shopkeeper opened the doors to her first customers.",
    "At the local museum the guide described how early travelers navigated by watching constellations appear above the desert long after sunset.",
    "A sudden storm scattered the fishing boats across the harbor and sent the market vendors hurrying to protect their baskets of fresh produce.",
    "During the afternoon the librarian rearranged several shelves of history books and discovered a handwritten note tucked inside an old atlas.",
    "The engineer tested the mechanical instrument once again and listened as each small brass gear slipped smoothly into place beneath the glass cover.",
    "The family packed blankets and a picnic lunch before driving through the countryside to visit a quiet lake surrounded by pine trees.",
    "When the theater lights dimmed the audience grew silent and the musicians began playing a gentle melody that filled the crowded hall.",
    "The gardener spent the entire morning trimming rose bushes and sweeping dry leaves from the stone path that led to the greenhouse.",
    "Under a bright blue sky the children launched paper kites from the meadow and chased them across the field whenever the wind shifted.",
    "The old railroad station became a lively gathering place where travelers exchanged stories while waiting for the last train of the evening.",
    "After finding a faded photograph the historian searched through several handwritten diaries to identify the names of the people pictured.",
    "Our neighbors built a wooden table beneath the tall maple tree and invited everyone to share supper after the community festival ended.",
    "A curious fox emerged from the forest at dawn and moved carefully toward the stream where several birds were searching for insects.",
    "The carpenter selected a length of polished oak and began shaping the delicate curved handle of a chair commissioned for the town hall.",
    "On a cold winter evening the children gathered around the fireplace and listened as their grandfather told stories from his travels overseas.",
    "The university students mapped the coastline with simple instruments and carefully recorded the changes in the shape of each rocky inlet.",
    "Before the sun reached the horizon the farmer checked the irrigation pipes and closed the gates that carried water between the orchard rows.",
)

def mod26(x):
    return x % 26

def clean(s):
    return "".join(ch for ch in s.upper() if ch in AZ)

def encrypt(p, mode, lag, mult, sign, offset, step):
    plain = [ord(ch) - 65 for ch in p]
    c = []
    for i, value in enumerate(plain):
        feedback = (plain[i - lag] if mode == "plaintext" else c[i - lag]) if i >= lag else 0
        c.append(mod26(mult * value + offset + step * i + sign * feedback))
    return "".join(chr(65 + v) for v in c)

def write_new(path, contents):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="ascii") as fh:
        fh.write(contents)

def controls(input_path, truth_path):
    if Path(input_path).resolve() == Path(truth_path).resolve():
        raise ValueError("truth and blind input cannot share a path")
    rng = random.Random(550551)
    lines = []
    truth = {}
    assert len(PASSAGES) == 20
    for i, passage in enumerate(PASSAGES):
        raw = clean(passage)
        assert len(raw) >= N, (i, len(raw))
        p = raw[:N]
        mode = rng.choice(("plaintext", "ciphertext"))
        lag = rng.randrange(1, 9)
        mult = rng.choice(MULTIPLIERS)
        sign = rng.choice((-1, 1))
        offset = rng.randrange(26)
        step = rng.choice((-1, 0, 1))
        ct = encrypt(p, mode, lag, mult, sign, offset, step)
        id_ = f"PLANT_{i:02d}"
        lines.append(f"{id_}\t{ct}\n")
        truth[id_] = {
            "plaintext": p, "mode": mode, "lag": lag, "multiplier": mult,
            "sign": sign, "offset": offset, "step": step,
        }
    assert len(truth) == 20
    write_new(input_path, "".join(lines))
    write_new(truth_path, json.dumps(truth, sort_keys=True, indent=2) + "\n")
    print("R55 controls prepared: 20 ciphertext-only blind examples; truths kept outside solver")

def target(ciphertext_file, input_path):
    raw = Path(ciphertext_file).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == ORIGINAL_SHA256
    text = raw.decode("ascii").strip()
    assert len(text) == N and text.isalpha() and text.isupper()
    rows = [f"K4\t{text}\n"]
    rng = random.Random(550088)
    seen = {text}
    for i in range(12):
        letters = list(text)
        rng.shuffle(letters)
        ct = "".join(letters)
        assert ct not in seen and sorted(ct) == sorted(text)
        seen.add(ct)
        rows.append(f"NULL_{i:02d}\t{ct}\n")
    write_new(input_path, "".join(rows))
    print("R55 target prepared: unchanged original K4 ciphertext and 12 frequency-preserving nulls")

if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "controls":
        controls(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 4 and sys.argv[1] == "target":
        target(sys.argv[2], sys.argv[3])
    else:
        raise SystemExit("usage: prepare.py controls INPUT.tsv TRUTH.json | target ORIGINAL_K4.txt INPUT.tsv")
