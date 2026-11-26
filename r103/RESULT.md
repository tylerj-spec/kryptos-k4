# R103 result (Claude Code, 26 Nov 2026): the two-free-alphabet autokey is IDENTIFIABLE at 97 letters

**Type:** synthetic measurement. No K4 input.
**Verdict:** **IDENTIFIABLE.** 0 of 3,000 unrelated English passages fit a planted ciphertext.

## In plain words
**The question.** If K4 were enciphered with a plaintext autokey using two unknown alphabets, would its 97 letters
be enough to pin down the plaintext? Or could many different English texts fit the same ciphertext?

**The test.** We took 300 synthetic ciphertexts and asked, 3,000 times, whether an unrelated 97-letter English
passage could have produced one of them. The exact test of R102 was used, over every sign and feedback convention at
the true lag.
- **Answer:** never, in 3,000 tries. The false-fit rate is below 1 in 1,000 at 95% confidence.
- **Meaning:** for this family, the ciphertext determines the English plaintext. A blind solver is worth building,
  and the batch's stop rule does **not** cancel R105/R106.
- **Shorter prefixes are another matter.** At 30 letters many unrelated texts fit, mostly at long lags, where 30
  letters give only a handful of equations. So partial-plaintext methods cannot rely on the exact test early on.

## Results (`run_v1/RESULTS.json`, frozen in 0bb4817)
| Step | Result |
|---|---|
| G1 soundness | 100/100 true plaintexts CONSISTENT, with valid witnesses |
| G2 two solvers | 36/40 decided by both, **0 disagreements** |
| **M2 (primary)** | **0 hits in 3,000 trials.** By lag, hits/trials: L 1 0/380; L 2 0/380; L 3 0/380; L 5 0/380; L 8 0/370; L 13 0/370; L 21 0/370; L 40 0/370 |
| M1 curve, n = 30 (true cell) | 74/214 hits. By lag: L 1 4/27, L 2 3/27, L 3 4/27, L 5 5/27, L 8 2/27, L 13 6/27, L 21 24/26, L 40 26/26. **TRUNCATED** by the registered time guard |
| M1, n = 45 and n = 60 | not run (TRUNCATED) |
| M3 unknown lag (exploratory) | not run (TRUNCATED) |

**Run:** COMPLETE through `audit/run_bounded_agg.py`. 1,790 s wall, 1,780 s CPU, peak 316 MB (cap 1,800 / 1,800 /
2,048), zero retries.

**Disclosures:**
1. **The time guard truncated M1 and M3, as registered.** M1's n = 30 trials cost about 5.7 s each, against about
   0.5 s in development: the primary solver enumerates large solution spaces when a short prefix leaves few
   equations. The guard is checked only between trials, so a single slow trial ran past the 1,400 s guard, and the
   run came within 10 s of the wall cap. Future guards should bound each trial.
2. **The pre-registration (b03793f) and source (6b01776) commits were pushed together.** The pre-registration commit
   precedes the source in history, but the two were not pushed separately.

## Limits
- **Unrelated passages are not adversarial texts.** A search could produce near-English that fits better than random
  English does. R104 examines search behaviour.
- **The lag was taken as known** (the true lag). The unknown-lag exploratory test (M3) did not run.
- **Nothing here touches K4.**

## Review
**Independent review: NONE.** One model (Claude Code) built and ran R103. It is part of audit batch B (ChatGPT).
