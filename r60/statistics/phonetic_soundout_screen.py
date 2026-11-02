#!/usr/bin/env python3
"""Exploratory AFTER-R60 phonetic direct-reading sensitivity check.
This is NOT pre-registered, NOT an encryption attack, and not a language model.
It never sees any published K4 plaintext letters, crib positions or true pad.
It is ONLY a bounded demonstration that plausible English sound-out respellings
do not automatically produce uniform-looking letter frequencies.
"""
from pathlib import Path
import hashlib, importlib.util, json, random, statistics
ROOT=Path(__file__).resolve().parents[2]
sp=importlib.util.spec_from_file_location("r60sealed_fixture",ROOT/"r60/sealed/prepare.py")
gen=importlib.util.module_from_spec(sp)
sp.loader.exec_module(gen)
# Handpicked, partly Germanic/NL-like grapheme substitutions, for illustration.
# No source establishes any of them as genuine K4 masking rules.
RULES=(("TH","D"),("W","V"),("SH","SJ"),("CH","TSJ"),
       ("OO","OE"),("EA","EE"),("PH","F"),("QU","KW"),
       ("CK","K"),("Y","IJ"))
EXTRA=" The visitors walked quietly toward the station and waited for a message near the garden."
SEED=600061
EXPECTED_SHA="2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
def clean(s):return "".join(c for c in s.upper() if "A"<=c<="Z")
def ic(s):
    n=len(s)
    assert n==97
    return sum(s.count(chr(i))*(s.count(chr(i))-1) for i in range(65,91))/(n*(n-1))
def main():
    k4file=ROOT/"r39/ic_gate/k4_ciphertext.txt"
    raw=k4file.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==EXPECTED_SHA
    k4=raw.decode("ascii").strip()
    assert len(k4)==97
    target=ic(k4)
    rng=random.Random(SEED)
    original=[]; respelled=[]
    for coverword,s in gen.PASSAGES:
        q=clean(s)[:97]
        assert len(q)==97 and coverword in q
        original.append(ic(q))
        for _ in range(100):
            variant=(s+EXTRA).upper()
            for a,b in RULES:
                if rng.random()<0.55:variant=variant.replace(a,b)
            variant=clean(variant)[:97]
            assert len(variant)==97
            respelled.append(ic(variant))
    assert len(original)==20 and len(respelled)==2000
    res={
      "classification":"POSTHOC_EXPLORATORY_DIRECT_GERMANIC_GRAPHEME_SCREEN_NOT_K4_DECRYPTION",
      "K4_original_ciphertext_IC":target,
      "English_covertext_samples":20,
      "English_IC_median":statistics.median(original),
      "English_IC_min":min(original),
      "English_IC_leq_K4":sum(x<=target for x in original),
      "toy_phonetic_samples":2000,
      "toy_phonetic_IC_median":statistics.median(respelled),
      "toy_phonetic_IC_min":min(respelled),
      "toy_phonetic_IC_5pct_95pct":[sorted(respelled)[100],sorted(respelled)[1900]],
      "toy_phonetic_IC_leq_K4":sum(x<=target for x in respelled),
      "seed":SEED,
      "rules":[[a,b] for a,b in RULES],
      "limitations":[
         "These are convenience spellings, not independently evidenced real K4 rules.",
         "The 2,000 draws share only 20 source sentences and are not independent.",
         "The screen measures letter-frequency effects without an encryption layer.",
         "It cannot reject layered phonetic masking and is not a formal K4 p-value."
      ]
    }
    print(json.dumps(res,sort_keys=True,indent=2))
if __name__=="__main__":main()
