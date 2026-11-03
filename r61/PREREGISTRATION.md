# R61 pre-registration (Claude Code, 2 Nov 2026): running key from an unknown English text, then a K3-style transposition

Written before the holdout plants are generated and before any K4 run. Follows `r53/BLIND_RULES.md`:
- the solver never sees K4's published letters or their positions;
- outputs are frozen and pushed before a separate reveal.

## Why
- **What R59 left open.** R59 (L149) found no sign of an **in-place** running key with an English key. The most natural
  extension is that the running-key output was then transposed, as K3 was by a 24×8 double rotation. K4 would then be
  "K1/K2 tableau + K3 transposition".

## Hypothesis H-RKT (exactly what is tested)
- **Substitution:** X = the running-key encryption of English plaintext P with an English key K, exactly as in R59
  (AZ or KRY × VIG / BEAU (= VARB), indices in the alphabet, both texts ordinary English).
- **Transposition:** CT[j] = X[perm[j]] for one of the **10 routes** in `r61/routes.txt` (`r61/blind/make_routes.py`):
  - **K3's own grid:** R24x8/CW/fwd, R24x8/CW/inv, R24x8/CCW/fwd, R24x8/CCW/inv (strictblind route maker; K3 itself
    is R24x8/CW/inv);
  - **the six 4+31+31+31 engraving-site routes of R58:** COL_LT, COL_LB, COL_RT, COL_RB, SNAKE_L, SNAKE_R. These are
    byte-identical to `r58/blind/solve.py`.
- **Not tested: transposition first, then substitution.** The plaintext and the key would then be scrambled relative to
  each other, and no letter-by-letter solver can follow both.

## Blind pipeline (frozen: `r61/blind/run.py`, B1 = 30000, TOP_ROUTES = 2)
- **Solver:** the R59 solver (`r59/blind/rk_solve.cpp`) and model (`r59/blind/LM_SHA256`), unchanged.
- **For each ciphertext:**
  1. Undo all 10 routes.
  2. **Stage 1:** solve each un-transposed text with the R59 solver **without polish** (beam 30,000, TOPN 2000,
     LAMBDA 1, 4 conventions).
  3. **Stage 2:** the 2 best routes by stage-1 total are re-solved with the **full R59 parameters** (beam 100,000,
     POLISH_M 3, POLISH_WORDS 20000).
  4. **Answer:** the best stage-2 total, with its route, convention and both texts in plaintext order.
- **Resume:** finished ciphertexts are cached and reused after an interruption. The solver is deterministic: a rerun
  matched byte for byte.
- **No tuning after this file is committed.**

## Development record (development books only; K4 never run)
- **Data:** 8 plants (`r61/sealed/make_plants.py`, *Tom Sawyer* × *Dorian Gray*, seed 61001), routes and conventions
  random, plus 8 shuffled nulls (seed 61002).
- **Results:**

  | Measure | Result |
  |---|---|
  | Detected (above the maximum null, −310.2) | 6/8 |
  | Route identified | 6/8, rank 1 at stage 1 each time; the 2 misses are the 2 undetected plants |
  | Convention | 7/8 |
  | Letter pairs correct | median 59/97; ≥ 60 in 3/8; detected plants 51–86 |
  | Witnesses | all valid |
- **Effect of the route search:** taking the best over 10 routes raises the null scores slightly compared with R59
  (8 nulls −326 to −310).

## Holdout gate (fixed now)
- **Plants:** 20, generated only after this file is pushed:
  `r61/sealed/make_plants.py hold_pt.txt hold_key.txt 20 61100 HOLD OUTDIR` (the R59 holdout books; new windows, keys,
  conventions and routes).
- **Nulls:** one shuffle per plant, `r59/sealed/make_nulls.py BLIND.tsv 61101`.
- **Run:** plants and nulls in one blind run, frozen and pushed before `r61/sealed/gate.py` runs.
- **Pass (all of):**
  - **detected ≥ 12/20:** best total above the maximum over the 20 nulls;
  - **route identified ≥ 12/20;**
  - **convention ≥ 14/20;**
  - **letter pairs correct ≥ 60/97 in ≥ 8/20;**
  - **all witnesses valid:** re-encryption through the chosen route.

  These bars sit about 20% below the development rates, so a method that works is unlikely to fail by chance. Each one
  still requires real recovery.
- **If it fails:** record it, and do **not** run K4.

## K4 test (only if the gate passes)
- **Input:** `r61/sealed/prepare_k4.py` writes the unchanged K4 (sha256 `2797de14…`) plus 100 shuffles (seed 610070).
- **Run, freeze, reveal:** the same pipeline; freeze and push; then `r61/sealed/reveal_k4.py`. The reveal is the only
  code holding the published letters. They are compared in plaintext order, after the route is undone.
- **Decision, fixed now (s = K4's best total; r = number of nulls ≥ s):**

  | Outcome | Condition |
  |---|---|
  | **SIGNAL** | r = 0 **and** K4's frozen best output matches ≥ 10/24 published letters in one of its texts |
  | **Score anomaly** | r = 0 with fewer than 10/24 (STAT; not a candidate) |
  | **NO SIGNAL** | r ≥ 1 |

  - **NO SIGNAL** is evidence against H-RKT, with power equal to the holdout detection rate.
  - **A SIGNAL** still needs coherent raw English, exact re-encryption and Tyler's decision. No external checker.
