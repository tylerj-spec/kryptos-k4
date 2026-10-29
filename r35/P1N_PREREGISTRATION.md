# R35 P1N: post-hoc shuffled-ciphertext null calibration for P1

This is an explicitly **post-hoc** follow-up, designed because P1 K4 best quadgram score (-579.3495047) was 18.4141 higher than one pre-registered shuffled-ciphertext control. It is not an independent confirmatory test chosen without seeing P1. Do not represent its resulting rank or p-value as a formal discovery significance level.

## Fixed experiment

- No new K4 decryption scans. Compare against the frozen K4 best score from P1: exactly -579.3495047 (see `r35/p1_carter_k3_mixed/SUMMARY.json`).
- Twelve new, independently seeded shuffled K4 ciphertext nulls with seeds 35021 through 35032 inclusive. Preserve the exact original 97-letter K4 histogram.
- Every null uses *exactly* the same pre-frozen P1 `routes.txt` (72 opposite-direction K3-shaped route-orders), `key.txt` (282,924 letters from Carter & Mace), 12 alphabet/operation conventions and quadgram model.
- Search all 977,453,568 settings for each null (11,729,442,816 decryptions total). Blind rank top 100 per null.
- Freeze and commit every input, output and compiler/source/scorer SHA before revealing or comparing scores.
- Separate sealed checker independently re-encrypts each top-100 null row. No known K4 plaintext or clue matching is used.
- After the freeze, calculate how many of the twelve null top scores are **at least** -579.3495047. Report the raw rank and empirical one-sided exceedance estimate `(1+exceedances)/13`; note that 1/13 is the lowest attainable estimate.
- Also report the sample mean, standard deviation and full score list, and mark whether the P1 K4 score falls outside the *observed* null range.
- No altered model, tuning, changing seeds, changing cutoffs, or external checker. A high K4 score alone cannot validate a plaintext or rescue a family contradicted by the released 24 letters.

This study is not an attempt to conceal its post-hoc selection.
