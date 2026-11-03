# R61 result (Claude Code, 2 Nov 2026): no sign of a running key followed by a K3-style or engraving-route transposition

**No K4 solution. NO SIGNAL under the pre-registered rule.**
- **Rule followed:** the solver never saw K4's published letters. Every output was frozen and pushed before the
  separate reveal.
- **Not done:** no external checker was contacted.

## Plain words
- **The question:** could K4 be the K1/K2-style tableau with a key from an unknown English text (as R59 tested), but
  with the letters then rearranged? The rearrangements tested were K3's own 24×8 rotation, in 4 variants, and the 6
  ways of reading the sculpture's 4/31/31/31 rows (from ChatGPT's R58).
- **The solver works:** on 20 hidden test messages from books it had never seen, it:
  - found the running-key structure in 18;
  - identified the right rearrangement in 15 and the right tableau in 19;
  - recovered most letters (median 64 of 97 letter pairs correct).
- **On K4 it found nothing usable:**
  - K4's best score sits near the top of its 100 shuffled copies, but 5 of them scored as high or higher (p ≈ 0.06).
    The pre-registered bar was all 100.
  - Its frozen output is word salad matching only 2–3 of the 24 published letters, which is chance level.
  - A real hit at the holdout's recovery level would have matched about 15 or more.

## Pre-registered steps (`r61/PREREGISTRATION.md`, commit 5b51a00)
| Step | Commit | Result |
|---|---|---|
| Development code | 9648ebb | — |
| Pre-registration | 5b51a00 | — |
| Holdout generated (truth withheld, sha256 recorded) | 3370837 | 20 plants + 20 nulls |
| Holdout freeze | e6b6325 | — |
| Holdout gate (truth hash matched) | 3178f50 | **PASSED**: detected 18/20 (bar 12), route 15/20 (12), convention 19/20 (14), pair-correct ≥ 60 in 11/20 (8), witnesses valid; median pair-correct 64/97 |
| K4 target (K4 + 100 shuffles, seed 610070) | c7b6891 | — |
| K4 freeze | 4276033 | — |
| Reveal (`r61/k4/REVEAL.json`) | this commit | **NO SIGNAL** |

**Holdout note:** 3 of the 18 detected plants had the wrong route; a closely related rotation kept enough structure to
score high. Detection means "running-key structure present", and the route is identified separately.

## K4 numbers
| Measure | Value |
|---|---|
| K4 best total F | −310.01 (route COL_LT, convention KRY_BEAU) |
| 100 shuffled-K4 nulls: min / median / max | −326.9 / −318.2 / −301.0 |
| Nulls scoring ≥ K4 | **5 / 100** (empirical p = 0.059). The rule needed 0 |
| Holdout plants scoring above K4 | 19 / 20 |
| Holdout plants above K4's null maximum (power of the strict rule) | 13 / 20 (65%) |
| Published letters, compared in plaintext order (pre-registered) | 2/24 in text A, 0/24 in text B |
| Same, comparing the letters at their *ciphertext* positions through the route (post-hoc, labelled) | 3/24 |
| The same counts for the nulls' best outputs | median 2, max 6–7 |
| Re-encryption witnesses checked | 202 / 202 exact |

**Raw K4 output (best pair, unedited).** It is word salad of the same kind as on shuffled letters, so it is **not** a
decryption:
```
route COL_LT, KRY_BEAU
text A  ISHEROLLEDPROBLEMSOFBECAMEONHISMISSEDASCLAYNEATALLBUTTHECARBONANDDEATHTHATAMERESTARTINGREADMETAND
text B  ONCESSIONREGRETLIFEFORTHETRELYORIGINOFRISINGFACEAWAYTHEWEEKBILLHOLEFLOCKTORELOOKISOUTBUTINAMINUTE
```

## Post-hoc observation (NOT pre-registered; not evidence of a decryption)
- **What was seen:** in K4's stage-1 table, one route stands far ahead of the others. COL_LT scored −313.8; the next
  best was −335.0, a gap of 21.2.
  - Among the 100 nulls, the gap between their best and second-best route has median 4.1, 95th percentile 16.7 and
    maximum 20.0. So K4's gap is larger than every null's.
- **Why this is not evidence:**
  - The statistic was chosen **after** seeing K4's table, so the 1-in-101 figure does not account for the other
    statistics that could have been noticed.
  - The COL_LT output does not read as English.
  - It matches the published letters only at chance.
- **What it could mean:** something in K4's letter order interacts with this column-wise reading of the 4/31/31/31
  layout. Un-transposing by COL_LT roughly interleaves ciphertext letters 3–4 positions apart.
- **What would test it:** a fresh pre-registered test of a *specific* structural statistic for that layout, with its
  own nulls. Nothing here supports a running key.

## What this rules out, and what it does not
- **Evidence against (STAT, about 65% power with the strict rule):** a running key with English plaintext and English
  key, under AZ or KRYPTOS × Vigenère / Beaufort / variant Beaufort, **substituted and then transposed** by K3's 24×8
  rotations or by the R58 engraving routes. K4 scored below 19 of 20 test messages.
- **Together with R59 (in place, about 80% power):** the simplest running-key versions of "readable English plus a
  flattening layer" are now disfavoured.
- **Not covered:**
  - transposition **before** substitution;
  - other routes or grid sizes;
  - other alphabets;
  - non-English or numeric keys;
  - masking;
  - autokey.

## Reproduce
- **Solver and model:** the R59 solver and language model (`r59/RESULT.md`).
- **Run:** `python3 -I r61/blind/run.py IN.tsv OUTDIR lm6.bin rk_solve 4 30000 2`.
- **Score:** `r61/sealed/gate.py` for the holdout and `r61/sealed/reveal_k4.py` for K4.
