#!/usr/bin/env python3
"""Independent R60B original-ciphertext monogram-IC diagnostic.

English IID monogram model (historical reference frequencies) and sample size
are preregistered. This script never accesses published K4 plaintext, keys,
codebooks or any K4 candidate plaintext.
"""
import hashlib
import json
import math
import random
import sys
from pathlib import Path

AZ="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KEY_SHA="2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3"
N=97
TRIALS=300000
SEED=600061
PRIOR_PERCENT=(
8.167,1.492,2.782,4.253,12.702,2.228,2.015,6.094,6.966,
0.153,0.772,4.025,2.406,6.749,7.507,1.929,0.095,5.987,
6.327,9.056,2.758,0.978,2.360,0.150,1.974,0.074
)

def ic(counts):
    return sum(n*(n-1) for n in counts)/(N*(N-1))

def main():
    if len(sys.argv)!=3:
        raise SystemExit("english_ic.py CANONICAL_K4_CIPHERTEXT.txt OUTPUT.json")
    _,source,out=sys.argv
    assert not Path(out).exists()
    raw=Path(source).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==KEY_SHA
    c=raw.decode("ascii").strip()
    assert len(c)==97 and set(c)<=set(AZ)
    counts=[c.count(ch) for ch in AZ]
    actual=ic(counts)
    weights=[p/sum(PRIOR_PERCENT) for p in PRIOR_PERCENT]
    expected=sum(w*w for w in weights)
    rng=random.Random(SEED)
    observed_below=0
    seq=range(26)
    for _ in range(TRIALS):
        sample=rng.choices(seq,weights=weights,k=N)
        bc=[0]*26
        for z in sample:bc[z]+=1
        if ic(bc)<=actual+1e-12:
            observed_below+=1
    result={
        "classification":"R60B_PREDECLARED_MONOGRAM_DISTRIBUTION_ONLY",
        "K4_ciphertext_sha256":KEY_SHA,
        "length":N,
        "K4_letter_counts_alphabetical":counts,
        "K4_observed_index_of_coincidence":actual,
        "English_IID_monogram_model_expected_IC":expected,
        "model":"English IID monograms, NOT genuine sentences or all possible covertext",
        "simulations":TRIALS,
        "rng_seed":SEED,
        "simulated_English_IC_at_or_below_K4":observed_below,
        "simulated_English_lower_tail_fraction":observed_below/TRIALS,
        "plus_one_Monte_Carlo_tail":(observed_below+1)/(TRIALS+1),
        "zero_hit_one_sided_95pct_upper_bound":(
            1-math.pow(0.05,1/TRIALS) if observed_below==0 else None
        ),
        "logical_invariant":"letter permutations and a single global alphabet bijection preserve the unordered count multiset and IC, regardless of semantic interpretations",
        "limitation":"A private codebook may choose nonstandard word frequencies; this model is not proof about every possible English covertext or a specific K4 encryptor. No plaintext or decipherment found."
    }
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("x",encoding="ascii") as f:
        json.dump(result,f,indent=2,sort_keys=True);f.write(chr(10))
    print("R60B IC",actual,"English IID expectation",expected,
          "lower-tail observations",observed_below,"/",TRIALS)

if __name__=="__main__":main()
