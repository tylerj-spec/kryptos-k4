#!/usr/bin/env python3
"""R40 SEALED input maker. Writes the K4 ciphertext copy, 12 planted ciphertexts and 4 shuffled-K4 nulls into the
experiment directory, and the plant truth into sealed/truth.json (never read by blind/).

Plants: 12 fresh English passages written for R40 (none contains a K4 clue word). Plant i uses key family
FAMS[i % 6] and is in place (i < 6) or transposed by a uniformly random permutation applied before the substitution
(i >= 6). The plaintext alphabet is a uniformly random permutation; the cipher alphabet, operation and key are drawn
uniformly from the declared family. Seeds 40000 + i; nulls are K4 shuffled with seeds 40100 + j.
Usage: make_inputs.py EXPDIR [--dev]   (--dev writes one development plant with seed 49999 and no K4 or nulls)"""
import hashlib
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
CAS = {"AZ": AZ, "KRY": KRY, "PALP": "PALIMSETBCDFGHJKNOQRUVWXYZ", "ABSP": "ABSCIDEFGHJKLMNOPQRTUVWXYZ",
       "ACAKRY": "KAHUOFNPDLXRBIVSGQTEMZYCJW", "ACAPAL": "ACOZEJWIFRLDQMGUPBNYSHVTKX", "ACAABS": "ADJOUZBEKPVCGMRXIHNTYSFLQW"}
K4_SHA = "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
CARTER_SHA = "6761a5075869325f708e1d81f8bd0efeeab5aaaad43206e1551ed53243f13ee0"
FAMS = ["C10b5", "C10b6", "C10b7", "C26b5", "CARTER", "K1K3"]
PASSAGES = [
    "THE OLD FERRY LEFT THE PIER AT DAWN AND THE PASSENGERS WATCHED THE GULLS CIRCLE ABOVE THE GREY WATER AS THE ENGINE HUMMED BELOW",
    "WE FOUND THE LETTER INSIDE A BOX OF SEEDS IN THE GARDEN SHED AND IT DESCRIBED A JOURNEY ACROSS THE DESERT TO A HIDDEN WELL",
    "AFTER THE STORM THE VILLAGERS GATHERED IN THE SQUARE TO COUNT THE FALLEN TREES AND TO REPAIR THE ROOF OF THE SMALL SCHOOL",
    "HER GRANDFATHER KEPT A MAP OF THE RIVER VALLEY PINNED ABOVE HIS DESK WITH EVERY BRIDGE AND MILL MARKED IN FADED RED INK",
    "THE MUSEUM GUARD NOTICED THAT ONE OF THE STATUES HAD BEEN MOVED DURING THE NIGHT THOUGH NO DOOR OR WINDOW WAS EVER OPENED",
    "MANY SAILORS BELIEVED THAT THE LIGHTHOUSE KEEPER COULD PREDICT THE WEATHER BY WATCHING THE COLOUR OF THE EVENING SKY",
    "IN THE LIBRARY BASEMENT THERE IS A SHELF OF ANCIENT LEDGERS RECORDING THE PRICE OF GRAIN AND SALT FOR TWO HUNDRED YEARS",
    "THE EXPEDITION REACHED THE FROZEN LAKE ON THE THIRD DAY AND SET UP CAMP BESIDE A RIDGE OF DARK STONE TO WAIT FOR THE GUIDE",
    "WHEN THE TRAIN STOPPED IN THE MOUNTAINS THE CONDUCTOR WALKED THROUGH EACH CARRIAGE OFFERING HOT TEA AND BLANKETS TO ALL",
    "THE YOUNG ARCHITECT DREW HER FIRST DESIGN ON THE BACK OF A RECEIPT WHILE WAITING FOR THE BUS OUTSIDE THE CITY HALL ONE DAY",
    "A SMALL BOAT DRIFTED INTO THE HARBOUR CARRYING NOTHING BUT A LANTERN A COIL OF ROPE AND A SMALL JOURNAL WRITTEN IN PENCIL",
    "THE FARMERS HAD WAITED ALL SUMMER FOR RAIN AND WHEN IT FINALLY CAME THE CHILDREN RAN OUTSIDE TO DANCE IN THE MUDDY LANES",
]
DEV_PASSAGE = "OUR NEIGHBOUR REPAIRS OLD RADIOS IN HIS KITCHEN AND ON QUIET EVENINGS WE CAN HEAR DISTANT STATIONS PLAYING SLOW MUSIC"


def letters(s):
    return "".join(ch for ch in s.upper() if ch.isalpha())


def chain(primer_digits, base, n=97):
    k = list(primer_digits)
    b = len(k)
    while len(k) < n:
        k.append((k[-b] + k[-b + 1]) % base)
    return k[:n]


def draw_key(fam, rng, texts):
    symbols = "0123456789ABCDEFGHIJKLMNOP"
    if fam not in texts:   # chain families C10b5, C10b6, C10b7, C26b5
        base, b = int(fam[1:fam.index("b")]), int(fam[fam.index("b") + 1:])
        digits = [rng.randrange(base) for _ in range(b)]
        return chain(digits, base), f"{fam}/primer{''.join(symbols[d] for d in digits)}"
    src = texts[fam]
    d, num = rng.randrange(2), rng.randrange(2)
    s = src[::-1] if d else src
    off = rng.randrange(len(s) - 97 + 1)
    al = KRY if num else AZ
    return [al.index(ch) for ch in s[off:off + 97]], f"{fam}/{'rev' if d else 'fwd'}/{'KRY' if num else 'AZ'}/off{off}"


def encrypt(P, key, pa, ca, op, perm):
    X = [P[perm[j]] for j in range(97)]
    out = []
    for j in range(97):
        a = pa.index(X[j])
        v = {"VIG": a + key[j], "BEAU": key[j] - a, "VARB": a - key[j]}[op] % 26
        out.append(ca[v])
    return "".join(out), "".join(X)


def make_plant(P, fam, transposed, seed, texts):
    rng = random.Random(seed)
    pa = list(AZ)
    rng.shuffle(pa)
    ca_name = rng.choice(sorted(CAS))
    op = rng.choice(["VIG", "BEAU", "VARB"])
    key, label = draw_key(fam, rng, texts)
    perm = list(range(97))
    if transposed:
        rng.shuffle(perm)
    ct, X = encrypt(P, key, "".join(pa), CAS[ca_name], op, perm)
    setting = f"{label}|CA={ca_name}|OP={'VARB' if op == 'VARB' else 'VIG|BEAU'}"
    return ct, {"plaintext": P, "transposed_plaintext": X, "pa": "".join(pa), "ca": ca_name, "op": op, "key": key,
                "setting": setting, "perm": perm, "transposed": transposed, "family": fam, "seed": seed}


def main():
    exp = Path(sys.argv[1]).resolve()
    dev = "--dev" in sys.argv
    exp.mkdir(parents=True, exist_ok=True)
    carter = (REPO / "r34/carter_az.txt").read_text()
    assert hashlib.sha256(carter.encode()).hexdigest() == CARTER_SHA, "Carter text hash"
    texts = {"CARTER": letters(carter), "K1K3": letters((REPO / "k4kit/data/k1k3_plaintext.txt").read_text())}
    truth = {}
    if dev:
        P = letters(DEV_PASSAGE)[:97]
        ct, t = make_plant(P, "C10b6", False, 49999, texts)
        (exp / "DEV_ct.txt").write_text(ct + "\n")
        (exp / "dev_truth.json").write_text(json.dumps(t) + "\n")
        print("dev plant", t["setting"])
        return
    k4 = (REPO / "r38/p4_aca_gromark/k4_ciphertext.txt").read_text()
    assert hashlib.sha256(k4.encode()).hexdigest() == K4_SHA, "K4 ciphertext hash"
    (exp / "K4_ct.txt").write_text(k4)
    for i, raw in enumerate(PASSAGES):
        P = letters(raw)
        assert len(P) >= 97, (i, len(P))
        P = P[:97]
        for w in ("NORTHEAST", "BERLIN", "CLOCK"):
            assert w not in P, (i, w)
        ct, t = make_plant(P, FAMS[i % 6], i >= 6, 40000 + i, texts)
        tag = f"PLANT_{i:02d}"
        (exp / f"{tag}_ct.txt").write_text(ct + "\n")
        truth[tag] = t
    k4l = letters(k4)
    for j in range(4):
        s = list(k4l)
        random.Random(40100 + j).shuffle(s)
        (exp / f"NULL_{j:02d}_ct.txt").write_text("".join(s) + "\n")
    (HERE / "truth.json").write_text(json.dumps(truth, indent=1) + "\n")
    print("wrote K4, 12 plants, 4 nulls to", exp)


if __name__ == "__main__":
    main()
