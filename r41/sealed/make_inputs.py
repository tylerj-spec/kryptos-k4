#!/usr/bin/env python3
"""R41 SEALED input maker. Writes the K4 ciphertext copy, 6 planted ciphertexts and 2 shuffled-K4 nulls into the
experiment directory, and the plant truth into sealed/truth.json (never read by blind/).

Plants: 6 fresh English passages written for R41 (none contains a K4 clue word), encrypted with a uniformly random
plaintext alphabet, a cipher alphabet and operation drawn uniformly from the declared family, a key drawn uniformly
from the plant's key family, and then transposed (S_then_T: CT[j] = X[perm[j]]) by a route drawn uniformly from
the plant's route part. Seeds 41000 + i; nulls are K4 shuffled with seeds 41100 + j.
Usage: make_inputs.py EXPDIR"""
import hashlib
import json
import random
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
CAS = {"AZ": AZ, "KRY": KRY, "PALP": "PALIMSETBCDFGHJKNOQRUVWXYZ", "ABSP": "ABSCIDEFGHJKLMNOPQRTUVWXYZ",
       "ACAKRY": "KAHUOFNPDLXRBIVSGQTEMZYCJW", "ACAPAL": "ACOZEJWIFRLDQMGUPBNYSHVTKX", "ACAABS": "ADJOUZBEKPVCGMRXIHNTYSFLQW"}
K4_SHA = "2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
CARTER_SHA = "6761a5075869325f708e1d81f8bd0efeeab5aaaad43206e1551ed53243f13ee0"
PLANTS = [("A", "C10b5"), ("A", "C10b6"), ("A", "CARTER"), ("A", "K1K3"), ("B", "C10b5"), ("B", "K1K3")]
PASSAGES = [
    "THE BAKER OPENED HIS SHOP BEFORE SUNRISE AND THE SMELL OF FRESH BREAD DRIFTED DOWN THE NARROW STREET TOWARD THE RIVER",
    "OUR TEACHER TOLD US THAT THE OLD BRIDGE WAS BUILT BY HAND OVER MANY YEARS USING HEAVY STONES CARRIED FROM THE NEARBY HILLS",
    "SHE KEPT EVERY LETTER HER BROTHER SENT FROM THE ISLAND AND READ THEM AGAIN EACH WINTER WHEN THE COLD NIGHTS GREW VERY LONG",
    "THE SURVEYORS MEASURED THE FIELD TWICE BECAUSE THE FIRST RESULT DID NOT AGREE WITH THE MAP DRAWN BY THE PREVIOUS OWNER",
    "A TRAVELLING CIRCUS ARRIVED IN THE TOWN ONE AUTUMN AND THE CHILDREN WATCHED THE ELEPHANTS WALK SLOWLY PAST THE CHURCH",
    "WHEN THE SNOW MELTED THE SHEPHERDS LED THEIR FLOCKS UP TO THE HIGH PASTURES AND BUILT SMALL HUTS FROM BRANCHES AND MUD",
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
    al = KRY if num else AZ
    return [al.index(ch) for ch in s[off:off + 97]], f"{fam}/{'rev' if d else 'fwd'}/{'KRY' if num else 'AZ'}/off{off}"


def routes(part):
    """S_then_T route-orders of a part, generated with the blind route maker (reading blind code is allowed here)."""
    mk = [sys.executable, "-I", str(HERE.parent / "blind/routes.py")]
    with tempfile.TemporaryDirectory() as td:
        if part == "A":
            subprocess.run(mk + ["r27", f"{td}/a.txt"], check=True, capture_output=True)
            subprocess.run(mk + ["columnar", "KRYPTOS,PALIMPSEST,ABSCISSA", f"{td}/b.txt"], check=True, capture_output=True)
            lines = Path(f"{td}/a.txt").read_text().splitlines() + Path(f"{td}/b.txt").read_text().splitlines()
        else:
            subprocess.run(mk + ["rot", "4", "28", f"{td}/a.txt"], check=True, capture_output=True)
            subprocess.run(mk + ["rot-mixed", "4", "28", f"{td}/b.txt"], check=True, capture_output=True)
            lines = Path(f"{td}/a.txt").read_text().splitlines() + Path(f"{td}/b.txt").read_text().splitlines()
    out = []
    for ln in lines:
        name, order, p = ln.split()
        if order == "S_then_T":
            out.append((name, [int(v) for v in p.split(",")]))
    return out


def main():
    exp = Path(sys.argv[1]).resolve()
    exp.mkdir(parents=True, exist_ok=True)
    carter = (REPO / "r34/carter_az.txt").read_text()
    assert hashlib.sha256(carter.encode()).hexdigest() == CARTER_SHA, "Carter text hash"
    texts = {"CARTER": letters(carter), "K1K3": letters((REPO / "k4kit/data/k1k3_plaintext.txt").read_text())}
    k4 = (REPO / "r38/p4_aca_gromark/k4_ciphertext.txt").read_text()
    assert hashlib.sha256(k4.encode()).hexdigest() == K4_SHA, "K4 ciphertext hash"
    (exp / "K4_ct.txt").write_text(k4)
    R = {"A": routes("A"), "B": routes("B")}
    assert len(R["A"]) == 116 and len(R["B"]) == 5000, (len(R["A"]), len(R["B"]))
    truth = {}
    for i, (raw, (part, fam)) in enumerate(zip(PASSAGES, PLANTS)):
        P = letters(raw)
        assert len(P) >= 97, (i, len(P))
        P = P[:97]
        for w in ("NORTHEAST", "BERLIN", "CLOCK"):
            assert w not in P, (i, w)
        rng = random.Random(41000 + i)
        pa = list(AZ)
        rng.shuffle(pa)
        ca = rng.choice(sorted(CAS))
        op = rng.choice(["VIG", "BEAU", "VARB"])
        key, label = draw_key(fam, rng, texts)
        rname, perm = rng.choice(R[part])
        X = []
        for t in range(97):
            a = pa.index(P[t])
            X.append(CAS[ca][{"VIG": a + key[t], "BEAU": key[t] - a, "VARB": a - key[t]}[op] % 26])
        ct = "".join(X[perm[j]] for j in range(97))
        tag = f"PLANT_{i:02d}"
        (exp / f"{tag}_ct.txt").write_text(ct + "\n")
        truth[tag] = {"plaintext": P, "pa": "".join(pa), "ca": ca, "op": op, "key": key, "route": rname, "perm": perm,
                      "part": part, "family": fam, "seed": 41000 + i,
                      "setting": f"{label}|ROUTE={rname}|CA={ca}|OP={'VARB' if op == 'VARB' else 'VIG|BEAU'}"}
    k4l = letters(k4)
    for j in range(2):
        s = list(k4l)
        random.Random(41100 + j).shuffle(s)
        (exp / f"NULL_{j:02d}_ct.txt").write_text("".join(s) + "\n")
    (HERE / "truth.json").write_text(json.dumps(truth, indent=1) + "\n")
    print("wrote K4, 6 plants, 2 nulls to", exp)


if __name__ == "__main__":
    main()
