# R73b result (Claude Code, 9 Nov 2026): R26 passes its sealed synthetic gate with the letter-model solver

**Synthetic gate.** No K4 ciphertext or published letters were used in it. Pre-registration:
`r73/R73B_PREREGISTRATION.md` (136418d).

## Steps
| Step | Commit | Result |
|---|---|---|
| Pre-registration (POOV −3, cut −1.40/letter, fixed on development books) | 136418d | — |
| Holdout (seed 731200; truth sha256 eb5f4c96… withheld) | 5f54cd7 | 400 ciphertexts |
| Blind run (about 5 min on 4 cores) and freeze | 81ef506 | all 52 R26 settings per ciphertext kept |
| Verify (truth not opened) | this commit | **PASSED**: 20,800 decodes re-encrypt to their ciphertexts |
| Gate (truth hash matched) | this commit | **PASS** |

## Gate (`r73/holdout_r73b/GATE.json`)
| | Recovered and confident | Bar | Setting exact | Exact plaintext | Fewest letters right | Worst score per letter | Result |
|---|---|---|---|---|---|---|---|
| R26 positives (*The Moonstone*) | **100/100** | 90 | 100/100 | 88/100 | 92 | −0.915 | **PASS** |
| Negatives | **0/300 confident** | 0 | — | — | — | best −1.721 (cut −1.40) | pass |

- **Negatives' best score by kind:** −1.72 (running key) to −1.76 (shuffles). Every kind is at least 0.32 per letter
  below the cut.
- **The 12 inexact decodes** (unedited; found ← true):
  - Contractions: C ANY ← CAN T; WOULD RS ← WOULDN T; DID UP DID UP ← DIDN T DIDN T; HER GO ← HERE S; I ← IT S;
    RS ← COULDN T.
  - Names and possessives: T IPPOOR ← TIPPOO; BETTER JILJO ← BETTEREDGE S; GOOSEBERR DO ← GOOSEBERRY S.
  - Short words: A SHE ← AS IF; HE ← HER IF; C LACKEY ← CLACK IS.
  - Each is local: the setting stayed exact and at least 92 of 97 letters were right.
- **Compared with Phase B**, where the flat unknown-word penalty gave 88/100 recovered, 93/100 setting exact and as
  few as 67 letters right, the name failures are gone.

## What follows
Under the pre-registration, R26 now goes to K4: K4 + 100 shuffles (seed 731300), freeze and push, verify, then the
sealed reveal and the crib-assisted R26X check. The K4 section is added below when it is done.
