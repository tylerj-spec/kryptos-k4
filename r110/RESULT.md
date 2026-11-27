# R110 result (Claude Code, 27 Nov 2026): no lag-1 signal in K4 (p = 0.071); an exploratory excess at lag 21 (p = 0.0013, Bonferroni 0.032)

**Type:** BLIND, ciphertext only. No published letter or position was read. **Independent review: NONE**; this is
audit batch C.

## In plain words
**The question.** If K4 were a plaintext autokey with lag 1 and two mixed alphabets, the same pair of adjacent
ciphertext letters should repeat more often than the letter frequencies alone predict. This test is weak: on
synthetic messages it catches 41% of such autokeys.

**The answer at lag 1, the registered test.** **No signal.**
- K4 has 10 repeated adjacent pairs, against 5.9 on average in 100,000 letter-shuffles.
- That gives p = 0.071, which does not reach 0.05.

**Exploratory lags 2–24.** **Lag 21 stands out.**
- K4 has 11 repeated letter pairs 21 apart, against 3.7 on average.
- That gives p = 0.0013, or **0.032 after correcting for testing 24 lags**.

**How to read lag 21.** This was not the registered test. It is reported because the registration required it. It
was found by looking at 24 lags, and it is a single statistic. It is a reason for a separately registered follow-up,
not a finding about K4's cipher. No other lag comes close: the next lowest are lag 10 at p = 0.054 and lag 1 at
0.071.

## Gate (`holdout/GATE.json`, seed 1100901): **GO**
| Check | Result |
|---|---|
| G1 two implementations | 0 disagreements (500 strings × 24 lags) |
| G2 power at L = 1 | **122/300 (0.407)** fresh two-free-alphabet autokey plants significant (floor 0.25) |
| G3 size | **12/300 (0.040)** random strings significant (ceiling 0.08) |

COMPLETE: 15 s. The gate freeze 825774d was pushed before any K4 input.

## Target (`k4/STATISTICS.json`, frozen in 3c6bf9a; `k4/EVALUATION.json`)
**Decision: NO_SIGNAL** (primary L = 1).

| L | 1 | 2 | 3 | 7 | 10 | 14 | **21** | 24 |
|---|---|---|---|---|---|---|---|---|
| R_L(K4) | 10 | 3 | 8 | 9 | 9 | 7 | **11** | 3 |
| shuffle mean | 5.91 | 5.79 | 5.66 | 5.20 | 4.84 | 4.41 | **3.69** | 3.40 |
| one-sided p | 0.071 | 0.94 | 0.20 | 0.075 | 0.054 | 0.15 | **0.0013** | 0.67 |

All 24 lags are in `k4/EVALUATION.json`. The Bonferroni-adjusted minimum over lags 2–24 is 0.030 (×23), or 0.032
(×24, all lags).

**Run:** COMPLETE through `audit/run_bounded_agg.py`: 27 s, 16 MB, zero retries.

**Commits:**
- pre-registration 1433893;
- source dcdb53f;
- gate freeze 825774d;
- statistics frozen in 3c6bf9a.

## What this does and does not show
- **NO_SIGNAL at lag 1 is STAT_NO_SIGNAL.** A lag-1 autokey is not excluded, since power is only 0.41.
- **The lag-21 excess is exploratory.** It says only that letter pairs 21 apart repeat more than K4's letter
  frequencies predict. Several constructions could produce that, for example a period that divides 21 in some
  layer, or a transposition or route with a 21 structure.

**Proposed follow-up (needs approval).** A registered lag-21 analysis on ciphertext only. It would:
- list which constructions predict R_21;
- test them with their own synthetic power;
- stay strictly blind.

## Errata (additive, 27 Nov 2026; after ChatGPT's partial quality review `audit/reviews/R108_R111_CHATGPT_QUALITY_REVIEW_20261127.md`)
1. **Lag 21 is not a new observation.** R71 (`r71/PREREGISTRATION.md`, `r71/RESULT.md`) already registered and
   reported the width-21 repeated-pair structure, with a K4 count of 11.
   - R110 weights a pair that occurs n times as n(n − 1)/2; R71 used max(n − 1, 0).
   - Both measure the same structure in the same 97 letters.
   - The adjusted p = 0.032 is scoped to R110's 24-lag scan. It is **not independent confirmation**, not a
     correction for earlier choices of statistic, and not a probability that any construction is true.
2. **The follow-up comes after a novelty review.** The proposed follow-up (P5) must first reconcile with R71's
   family simulations, which gave NO_FAMILY. It must also name a materially new mechanism or distinguishing
   prediction. If none emerges, it closes without a K4 run.
3. **The lag 2–24 scan was registered.** It was registered as exploratory. A chat summary called it unplanned;
   that was inaccurate.
