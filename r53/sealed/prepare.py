#!/usr/bin/env python3
"""Produce ciphertext-only integration inputs with hidden synthetic truth.

The generator is called OUTSIDE the isolated blind container. The true
plaintext and synthetic Caesar key are written to a separate sealed path,
never copied or mounted into the blind container. These are smoke tests,
NOT a real unknown-key K4 method benchmark or a new blind holdout.
"""
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / "r39" / "ic_gate" / "k4_ciphertext.txt"
EXPECTED_SHA256_WITH_NEWLINE = "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

FRAGMENTS = (
    "THEGARDENERWALKEDACROSSTHEFIELD",
    "THESUNLIGHTSHONETHROUGHTHELEAVES",
    "SHEOPENEDTHEWINDOWTOSEETHEGARDEN",
    "AFRESHBREEZECARRIEDTHEMORNINGSOUNDS",
    "EVERYTRAVELERFOLLOWEDTHEQUIETRIVER",
    "THESMALLVILLAGEWASFULLWITHMUSIC",
    "THEOLDLIBRARYOPENEDBEFORETHENOON",
    "THENEXTDAYBROUGHTANOTHERCHANCE",
    "THETHOUGHTFULREADERENJOYEDTHESTORY",
    "WEWALKEDALONGTHEWIDEFORESTPATH",
    "AFTERTHERAINTHESKYBECAMEBRIGHT",
    "THEMOUNTAINTRAILWASLONGANDNARROW",
    "ANOTHERTRAINARRIVEDBEFOREDAWN",
    "THEFAMILYSHAREDTHEIREVENINGMEAL",
    "THISCHAPTERBEGINSWITHASMALLMYSTERY",
    "THEWRITERFINISHEDTHELASTCHAPTER",
    "SOMEPEOPLEENJOYQUIETAFTERNOONS",
    "THEGOLDENMEADOWSSTRETCHEDFARAWAY",
    "NEWIDEASAPPEAREDINTHERESULTS",
    "THEWINDCARRIEDTHEVOICESOVERTHEHILL",
    "EACHLETTERWASWRITTENWITHCARE",
    "THERESEARCHERREPEATEDEVERYMEASURE",
    "THECHILDRENWATCHEDTHESHIPSSAIL",
    "THEWATERMOVEDBETWEENTHEROUNDSTONES",
)


def encrypt(p, key):
    return "".join(AZ[(AZ.index(c) + key) % 26] for c in p)


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: python3 -I r53/sealed/prepare.py INPUT.ndjson TRUTH.json")
    incoming, sealed_truth = map(Path, sys.argv[1:])
    if incoming.resolve() == sealed_truth.resolve():
        raise ValueError("sealed truth and blind input must have distinct paths")
    original_bytes = ORIGINAL.read_bytes()
    assert hashlib.sha256(original_bytes).hexdigest() == EXPECTED_SHA256_WITH_NEWLINE
    original = original_bytes.decode("ascii").strip()
    assert len(original) == 97 and original.isupper() and original.isalpha()
    rows = [{"id": "K4", "ciphertext": original}]
    truth = {}
    rng = random.Random(531337)
    for i in range(20):
        message = ""
        while len(message) < 97:
            message += rng.choice(FRAGMENTS)
        message = message[:97]
        key = rng.randrange(1, 26)
        ct = encrypt(message, key)
        assert len(message) == len(ct) == 97
        label = f"PLANT_{i:02d}"
        rows.append({"id": label, "ciphertext": ct})
        truth[label] = {"plaintext": message, "caesar_key": key}
    assert len(rows) == 21 and len(truth) == 20
    incoming.parent.mkdir(parents=True, exist_ok=True)
    sealed_truth.parent.mkdir(parents=True, exist_ok=True)
    incoming.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))
    sealed_truth.write_text(json.dumps(truth, indent=2, sort_keys=True) + "\n")
    # Never print plaintext, synthetic keys or any path to the sealed secrets.
    print("R53 prepared one original ciphertext plus 20 hidden-truth smoke controls")


if __name__ == "__main__":
    main()
