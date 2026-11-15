#!/usr/bin/env python3
"""Independent ciphertext-only audit of R78/L167 self-key sum invariant.

No published K4 plaintext letters, positions, candidate decryption,
or key inference. Reads hash-verified original ciphertext only.
"""
import hashlib
import json
import random
import sys
from pathlib import Path

AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALPH = {
    "AZ": AZ,
    "KRY": "".join(dict.fromkeys("KRYPTOS" + AZ)),
    "PAL": "".join(dict.fromkeys("PALIMPSEST" + AZ)),
    "ABS": "".join(dict.fromkeys("ABSCISSA" + AZ)),
}
OPS={"VIG":(1,1),"BEAU":(-1,1),"VARB":(1,-1)}
ROOT=Path(__file__).resolve().parents[2]


def sum_mod26(ct, alphabet):
    return sum(alphabet.index(x) for x in ct) % 26


def synthetic_controls():
    rng = random.Random(7800018)
    for n in (1,2,5,26,97,101):
        for _ in range(200):
            plain_idx = [rng.randrange(26) for _ in range(n)]
            key_idx = plain_idx.copy()
            rng.shuffle(key_idx)
            for ca in ALPH.values():
                for name,(s,t) in OPS.items():
                    ct = "".join(ca[(s*plain_idx[i]+t*key_idx[i])%26]
                                 for i in range(n))
                    total=sum_mod26(ct,ca)
                    assert (total%2==0 if name=="VIG" else total==0)
    return {"synthetic_plant_sizes":[1,2,5,26,97,101],
            "plants_each_size":200,"tableaux":4,"operations":3,
            "assertions":6*200*4*3,
            "status":"PASS"}


def run():
    controls=synthetic_controls()
    target=ROOT/"r83/k4/TARGET.tsv"
    frozen=ROOT/"r83/k4/run/FROZEN.sha256"
    expected=[line.split()[0] for line in frozen.read_text().splitlines()
              if line.endswith("r83/k4/TARGET.tsv")]
    assert expected==[hashlib.sha256(target.read_bytes()).hexdigest()]
    d=dict(line.split("\t") for line in target.read_text().splitlines()[1:] if line)
    ct=d["K4"]
    assert len(ct)==97 and set(ct)<=set(AZ)
    outcomes={}
    for name,a in ALPH.items():
        v=sum_mod26(ct,a)
        outcomes[name]={
            "sum_mod26":v,
            "beau_and_variant_possible":v==0,
            "vig_possible":v%2==0,
        }
    assert {k: v["sum_mod26"] for k,v in outcomes.items()}=={
        "AZ":7,"KRY":12,"PAL":7,"ABS":14}
    return {
        "type":"CIPHERTEXT_ONLY_NECESSARY_INVARIANT",
        "scope":"Self-key from arbitrary permutation of full plaintext; same PLAINTEXT and KEY alphabet, ciphertext tableau one of four named charts",
        "source":"R83 SHA-frozen original K4, no published letters read",
        "synthetic_controls":controls,
        "L167":outcomes,
        "interpretation":"Beaufort/variant ruled out under stated formula for all four ciphertext charts. Vigenere ruled out for AZ/PAL ciphertext charts only; KRY/ABS remain OPEN. Arbitrary different plain/key alphabets NOT covered.",
    }


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: ciphertext_invariants.py OUTPUT.json")
    o=run()
    p=Path(sys.argv[1]);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"L167":o["L167"],"synthetic":o["synthetic_controls"]},sort_keys=True))
