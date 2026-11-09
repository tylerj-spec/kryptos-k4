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

## K4 run (pre-registered in `r73/R73B_PREREGISTRATION.md`; run because the gate passed)
| Step | Commit | Result |
|---|---|---|
| Target: K4 + 100 shuffles (seed 731300) | 6c93788 | — |
| Blind run (about 1.5 min) and freeze | 34ed8a3 | all 52 R26 settings per ciphertext kept |
| Verify (no published letters) | a93b0aa | **PASSED**: 5,252 decodes re-encrypt |
| Sealed reveal (`r73/k4_r73b/REVEAL.json`) | this commit | **NO_SIGNAL** |

**Blind result:**
- **Score:** K4's best R26 decode scores −1.802 per letter (AZ tableau, phase 6). Against the −1.40 cut:
  - Real R26 messages in the holdout scored −0.92 or better.
  - The shuffled copies of K4 score the same as K4: median −1.804, best −1.736, and 45 of 100 at or above K4.
- **Published letters:** the best decode matches 0 of 24. The best of all 52 settings matches 4/24; the nulls'
  median is 3 and their maximum 5.
- **Contenders:** none out of K4's 52 decodes (≥ 12/24 needed).
- **Raw decode** (unedited; 11 of its words are unknown-word fragments):
  `HTBHJCKARRDTI KFBXTONH WBGJDCABWORYXSWYU GHXDEDOTH OKNFUUUCKOFA WARM AKA HE EWIN ZTENJ THE BQIIMJ RAMY GZINEBR`

**R26X (crib-assisted, post-freeze; not part of the blind outcome): EXCLUDED under both alphabets.**
- **The check:** whether any phase, word numbering and word division (words of 1–18 letters, unknown plaintext
  between the two blocks) makes R26 encipher the published letters to K4's letters.
- **K4's answer is no** for the AZ tableau and for the KRYPTOS tableau.
  - Neither published block on its own has a single consistent word division, so the plaintext between the blocks
    cannot rescue it.
  - None of the 100 shuffles is consistent either, as expected from the validation: the true alphabet and division
    were found in 40/40 synthetic plants, and 0 of 2,000 random ciphertexts were consistent.

## Conclusion
- **K4 is not R26 as defined**: y = x + word number + position in word + phase (mod 26), enciphered in place on the
  AZ or KRYPTOS tableau.
  - The blind run finds nothing: K4 scores like its own shuffles, with no published letters.
  - The published letters rule the family out on their own.
- **The solver now works for this family:** 100/100 on a fresh sealed holdout. A ciphertext really enciphered this
  way would have stood out.
- **Not tested:**
  - the subtractive form (y = x − word number − position − phase);
  - other increments or alphabets;
  - a transposition before or after;
  - word divisions the solver cannot see (e.g. words longer than 18 letters).
- The ledger row is L163.
