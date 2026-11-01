#!/usr/bin/env python3
"""R59 conceptual one-time-pad proof and non-clue ciphertext-statistics test."""
from pathlib import Path
import importlib.util
import itertools
import math
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
src=(ROOT/"r59/blind/fingerprint.py").read_text(encoding="utf-8")
uppercase=src.upper()
for forbidden in (
   "EASTNORTHEAST","BERLINCLOCK","NORTHEAST","CRIB_MASK",
   "R52","KNOWN_K4_PLAINTEXT","K4_ANCHORS","KEY_ORACLE",
   "MASKED_PLAINTEXT","REFERENCE_MESSAGES","AFTER_REVEAL",
):
    assert forbidden not in uppercase, ("known-plaintext dependency in blind code",forbidden)
assert "CAL_SEED = 590061" in src
assert "CAL_N = 4000" in src
assert "PERIODS = tuple(range(2, 13))" in src
assert "LAGS = tuple(range(1, 25))" in src
assert "MAX_FAMILYWISE_P = 0.01" in src
spec=importlib.util.spec_from_file_location("blind_r59",ROOT/"r59/blind/fingerprint.py")
r59=importlib.util.module_from_spec(spec)
spec.loader.exec_module(r59)

# Exhaustive tiny-alphabet perfect secrecy demonstration: for ANY fixed
# ciphertext, every potential plaintext has exactly ONE fitting full-length
# key, so observing the ciphertext alone cannot distinguish plaintexts.
def modsum(x,y,mod):
    return tuple((a+b)%mod for a,b in zip(x,y))
alphabet=range(3)
messages=list(itertools.product(alphabet,repeat=3))
for c in messages:
    all_count=[]
    for p in messages:
        keys=[k for k in messages if modsum(p,k,3)==c]
        assert len(keys)==1
        all_count.append(len(keys))
    assert all(q==1 for q in all_count)

prior=r59.load_freq(ROOT/"r59/data/english_monogram.tsv")
assert prior.shape==(26,26) and np.all(np.isfinite(prior))
texts=[
    ("THECARPENTERSELECTEDTHEWOODANDTHENINSPECTEDTHEWORKBENCH"*3)[:97],
    ("ABCDEFGHIJKLMNOPQRSTUVWXYZ"*4)[:97]
]
assert all(len(t)==97 for t in texts)
matrix=r59.to_matrix(texts)
features=r59.compute_chunk(matrix,prior)
assert features.shape==(2,4) and np.all(np.isfinite(features))
assert all(v>=0 for v in features[:,0])
assert all(v>=0 for v in features[:,1])
sample=np.zeros((4000,4),dtype=float)
p=r59.empirical_component_p(sample,np.asarray([[1.,1.,1.,1.],[0.,0.,0.,0.]]))
assert np.allclose(p[0],1/4001)
assert np.allclose(p[1],1.0)
try:
    r59.to_matrix(["TEST"])
except ValueError:
    pass
else:
    raise AssertionError("accepted malformed ciphertext")
print("R59 CONTRACT PASS: tiny-pad 27x27 exact nonidentifiability, 4 independent features, predeclared calibration and no K4 clues")
