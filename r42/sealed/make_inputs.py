#!/usr/bin/env python3
"""R42 SEALED input maker. Writes the K4 ciphertext copy, 6 planted ciphertexts and 2 shuffled-K4 nulls into the
experiment directory, and the plant truth into sealed/truth.json (never read by blind/).

Plants: 6 fresh English passages written for R42 (none contains a K4 clue word), in place, with a plaintext alphabet
drawn uniformly from the 7 declared ones, a uniformly random cipher alphabet (free), an operation drawn uniformly
from VIG/BEAU/VARB and a key drawn uniformly from the plant's key family. Seeds 42000 + i; nulls are K4 shuffled
with seeds 42100 + j.
Usage: make_inputs.py EXPDIR"""
import hashlib
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
PAS = {"AZ": AZ, "KRY": KRY, "PALP": "PALIMSETBCDFGHJKNOQRUVWXYZ", "ABSP": "ABSCIDEFGHJKLMNOPQRTUVWXYZ",
       "ACAKRY": "KAHUOFNPDLXRBIVSGQTEMZYCJW", "ACAPAL": "ACOZEJWIFRLDQMGUPBNYSHVTKX", "ACAABS": "ADJOUZBEKPVCGMRXIHNTYSFLQW"}
K4_SHA = "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
CARTER_SHA = "6761a5075869325f708e1d81f8bd0efeeab5aaaad43206e1551ed53243f13ee0"
FAMS = ["C10b5", "K1K3", "C10b5", "K1K3", "C10b5", "K1K3"]
PASSAGES = [
    "EVERY SPRING THE OLD GARDENER PLANTED BEANS ALONG THE SOUTH WALL AND TOLD THE CHILDREN STORIES ABOUT HIS YEARS AT SEA",
    "THE CAPTAIN ORDERED THE CREW TO LOWER THE SAILS WHEN THE FOG ROLLED IN AND THEY ALL WAITED QUIETLY FOR THE MORNING TIDE",
    "AT THE END OF THE MARKET DAY THE TRADERS PACKED THEIR CARTS WITH UNSOLD APPLES AND WALKED SLOWLY HOME ALONG THE DUSTY ROAD",
    "MY AUNT FOUND A BUNDLE OF PHOTOGRAPHS HIDDEN BEHIND THE KITCHEN STOVE SHOWING PEOPLE NOBODY IN THE FAMILY COULD NAME",
    "THE STUDENTS SPENT THE AFTERNOON COPYING OLD MAPS IN THE ARCHIVE AND COMPARING THE COASTLINES WITH THE MODERN CHARTS",
    "A HEAVY SNOW FELL OVERNIGHT AND BY DAWN THE VILLAGE WAS SILENT EXCEPT FOR THE BELLS OF THE SLEIGHS CARRYING THE WINTER MAIL",
]


def letters(s):
    return "".join(ch for ch in s.upper() if ch.isalpha())


def draw_key(fam, rng, texts):
    if fam not in texts:   # base-10 chains C10b5, C10b6
        b = int(fam[-1])
        k = [rng.randrange(10) for _ in range(b)]
        primer = "".join(map(str, k))
        while len(k) < 97:
            k.append((k[-b] + k[-b + 1]) % 10)
        return k, f"{fam}/primer{primer}"
    d, num = rng.randrange(2), rng.randrange(2)
    s = texts[fam][::-1] if d else texts[fam]
    off = rng.randrange(len(s) - 97 + 1)
    return [(KRY if num else AZ).index(ch) for ch in s[off:off + 97]], f"{fam}/{'rev' if d else 'fwd'}/{'KRY' if num else 'AZ'}/off{off}"


def main():
    exp = Path(sys.argv[1]).resolve()
    exp.mkdir(parents=True, exist_ok=True)
    carter = (REPO / "r34/carter_az.txt").read_text()
    assert hashlib.sha256(carter.encode()).hexdigest() == CARTER_SHA, "Carter text hash"
    texts = {"CARTER": letters(carter), "K1K3": letters((REPO / "k4kit/data/k1k3_plaintext.txt").read_text())}
    k4 = (REPO / "r38/p4_aca_gromark/k4_ciphertext.txt").read_text()
    assert hashlib.sha256(k4.encode()).hexdigest() == K4_SHA, "K4 ciphertext hash"
    (exp / "K4_ct.txt").write_text(k4)
    truth = {}
    for i, (raw, fam) in enumerate(zip(PASSAGES, FAMS)):
        P = letters(raw)
        assert len(P) >= 97, (i, len(P))
        P = P[:97]
        for w in ("NORTHEAST", "BERLIN", "CLOCK"):
            assert w not in P, (i, w)
        rng = random.Random(42000 + i)
        pa_name = rng.choice(sorted(PAS))
        pa = PAS[pa_name]
        ca = list(AZ)
        rng.shuffle(ca)
        ca = "".join(ca)
        op = rng.choice(["VIG", "BEAU", "VARB"])
        key, label = draw_key(fam, rng, texts)
        ct = "".join(ca[{"VIG": pa.index(P[t]) + key[t], "BEAU": key[t] - pa.index(P[t]), "VARB": pa.index(P[t]) - key[t]}[op] % 26]
                     for t in range(97))
        tag = f"PLANT_{i:02d}"
        (exp / f"{tag}_ct.txt").write_text(ct + "\n")
        truth[tag] = {"plaintext": P, "pa": pa_name, "ca": ca, "op": op, "key": key, "family": fam, "seed": 42000 + i,
                      "setting": f"{label}|PA={pa_name}|OP={'VIG' if op == 'VIG' else 'BEAU|VARB'}"}
    k4l = letters(k4)
    for j in range(2):
        s = list(k4l)
        random.Random(42100 + j).shuffle(s)
        (exp / f"NULL_{j:02d}_ct.txt").write_text("".join(s) + "\n")
    (HERE / "truth.json").write_text(json.dumps(truth, indent=1) + "\n")
    print("wrote K4, 6 plants, 2 nulls to", exp)


if __name__ == "__main__":
    main()
