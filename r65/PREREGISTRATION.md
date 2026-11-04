# R65 pre-registration (Claude Code, 4 Nov 2026): fresh-null retest of R64's German stage-1 route gap

Written before the fresh nulls are generated or run. Ciphertext-only: **no published K4 letters are used anywhere in
R65**, not even in the evaluation.

## Why
- **What R64 saw:** under the GERMAN key model, K4's best stage-1 route (SNAKE_L, −320.86) was 28.4979 ahead of the
  second (R24x8/CCW/fwd, −349.36). That is just above all 100 R64 nulls (maximum 27.99).
  - Frozen in `r64/k4/run/RESULTS.jsonl` (efc5ad0) and `r64/k4/EXPLORATORY_STAGE1_GAP.json`.
- **Why it is not yet evidence:**
  - it was noticed **after** the reveal;
  - the statistic was not pre-registered;
  - it is one of several things that could have been looked at (2 models; gap vs total).
- **The cure:** fix the statistic and the threshold now, and test it on **fresh** shuffles, as R62C did for R61's
  COL_LT gap.

## Statistic (fixed now)
- **G** = (best stage-1 route total) − (second-best stage-1 route total).
- **How it is computed:** under the GERMAN key model with R64's stage 1 exactly: `r64/blind/run.py` functions, the
  10 R61 routes, the R63 solver (binary sha256 f171dbe5…), beam 15,000, TOPN 2000, LAMBDA 1, all 6 conventions,
  POLISH_M 0, WORDS 20000. Ties go to the lower route index. Runner: `r65/blind/run.py`.
- **K4's value:** G_K4 = **28.4979**, the R64 frozen value. K4 is re-run as a reproducibility check; the result must
  reproduce within 0.001 with best route SNAKE_L, or R65 is **INVALID**.

## Nulls
- **300 fresh frequency-preserving shuffles of K4** (`r65/sealed/prepare.py`, seed 650070), none equal to K4 or to
  any R64 null. Generated only after this file is pushed.

## Decision (fixed now)
- **Primary:** p = (1 + #{fresh nulls with G ≥ 28.4979}) / 301.
  - **REPLICATED** if p ≤ 0.01, i.e. at most 2 of the 300 fresh nulls reach G_K4.
  - **NOT REPLICATED** otherwise.
- **Secondary (reported, not decisive):**
  - the same count restricted to nulls whose best route is SNAKE_L;
  - the count pooled with R64's 100 nulls;
  - the gap quantiles.
- **What REPLICATED would mean:** K4, un-routed by its best route, is unusually well fit by an English-plaintext /
  German-key decomposition compared with shuffled K4. It would be a **structural anomaly, not a decryption.** R64's
  output on that route is word salad with 3/24 published letters.
  - **Next step if replicated:** a separately pre-registered test with a period-appropriate (pre-1996, literary)
    German key model, which R64 showed the current model lacks.
- **Order:** run (K4 + 300) → freeze and push → `r65/sealed/evaluate.py`.
  - The evaluator checks the manifests, the K4 reproduction and every raw re-encryption witness, then computes the
    above.
