# R44 holdout result (evaluated after the freeze at 5006be8)

**Gate FAILED: 14/20 exact; the pre-registered bar is 16/20.** Nothing has been run on K4.

| Measure | Result |
|---|---|
| Exact 97/97 | **14/20** |
| ≤ 3 letters wrong | 19/20 |
| Median errors | 0 |
| Invalid forward witnesses | 0 (checked by `r43/sealed/evaluate.py`) |
| Plaintext alphabet identified | 19/20 exactly; the 20th (H_05, GAZING) took another keyword alphabet that gives the identical plaintext |
| Margin of the best answer over the next keyword | 10–60 points in 19/20 |

## The six misses
Each has the right plaintext alphabet and 1–4 wrong letters. Every error sits on a **rare ciphertext letter**
(1–3 occurrences), whose cipher-alphabet position the quadgram score barely constrains. Examples: L→I, B→T, F→S, R→N,
W→H.

| Message | Errors |
|---|---|
| H_00 | 2 |
| H_01 | 2 |
| H_02 | 1 |
| H_08 | 4 |
| H_11 | 1 |
| H_18 | 1 |

## What this means
- **The hard part works.** Identifying a keyword plaintext alphabet with a fully free cipher alphabet worked 20/20.
- **The last letters do not.** The gap is a last-mile polish: the inner solve uses quadgrams only.
- **Proposed next step (R44b):** after the inner solve, re-optimise the cipher alphabet by swaps on quadgrams +
  word score (L138: the word model identifies text). Develop it on this, now-seen, holdout. Then pre-register and
  test on a **new** 20-message holdout. Per the protocol, no change is counted against this holdout.
