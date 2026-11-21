# R89 development record (spent books only; NOT gate evidence)

**Texts.** All spent: Peter Pan (R87 holdout), Northanger Abbey (R87 holdout) and White Fang (R88 holdout) stand in for
the three genres; Black Beauty (R87) is used for running keys; all with `--raw`. The seed is 890300 and the set has
the gate's full size: 96 positives, 9 extras and 150 negatives. No fresh book, no K4 ciphertext and no published
letter was used.

**Parameters.**
- **F26L:** exhaustive (no parameters).
- **RCT:** R87's measured schedule (`r87/dev/DEV.md`), unchanged.
- **Cuts:** R59's.
- **Nothing was tuned on this run.** The only change during development came before it: the alphabet-list fix in
  `r89/REVIEW_PR98.md` §2a, prompted by a PALIMPSEST-reversed plant in a 6-item smoke test.

## Result (`DEV_SUMMARY.json`)
| Arm | ok (≥ 95/97, right arm, confident) | Exact | S1 / S2 / S3 / S4 | G1 / G2 / G3 | Masked | Setting right | Recovered min lm |
|---|---|---|---|---|---|---|---|
| F26L | **48/48** | 48 | 12 / 12 / 12 / 12 | 16 / 16 / 16 | 12/12 | 48/48 | −1.169 |
| RCT | **45/48** | 44 | 12 / 11 / 12 / 10 | 15 / 15 / 15 | 10/12 | 48/48 | −1.114 |

**Both arms clear every pre-set bar:** 42 ok, 36 exact, 9 per stratum, 12 per genre and 8 masked.

**Negatives:** **0/150 confident**, and no family was declared on any negative.

| Generator | Best letter-model score |
|---|---|
| ANAGRAM | −1.337 |
| SUBTRANS | −1.375 |
| PERIODIC | −1.380 |
| RX | −1.386 |
| RQ | −1.402 |
| RUNKEY | −1.403 |
| PTAK | −1.413 |
| RCTX | −1.414 |
| RANDOM | −1.419 |
| F26X | −1.425 |

Max word score: −1.773. The frequency-preserving English anagrams come closest to the cut (−1.30): the free RCT wiring
has English letter frequencies to work with.

**RCT misses:**
- H_010: masked, 76/97, not confident;
- H_034: masked, 94/97;
- H_188: 91/97, confident.

All have the right setting, so they are scorer limits on masked or unusual text.

**Extras (reported):**
- **F26L:** all four recovered. A ciphertext error costs one letter (96/97), as the design states.
- **RCT:** plaintext errors 2/2; ciphertext errors 1/2; missed update 0/1.
  - The failed ciphertext-error item decodes 7/97: the wrong letter changed every later offset.
  - The missed update decodes 76/97: only the part before it is right.
  - This is RCT's designed error propagation. A carving error in K4 under RCT would hide a true solution with
    probability of roughly one half.

**Witness:** 1,844/1,844 stored decodes re-encrypt.

**Cost:** 255 items in 749 s on 4 cores (48.5 core-minutes). The gate has the same size; K4 + 200 shuffles is about
10 minutes.

## Files
| File | sha256 |
|---|---|
| Development input | 8d93747f53e9737e05182afda80fb1fc703f5978b0556edad8d4c8e832445ce7 |
| Development results | 30d20ef7fdc9cc6c382a4151aaa3e2cb376e82bf54800ca24c8f31f464e829e1 |

**Isolation:** the first 2 development items run through `make_sandbox89.py` and `run_isolated89.sh` (both arms, 2
processes) reproduce the open run **byte for byte**.
