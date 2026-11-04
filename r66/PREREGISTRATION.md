# R66 pre-registration (Claude Code, 4 Nov 2026): homophonic substitution (a frequency-masking cipher) with a transposition

Written before the holdout plants are generated and before any K4 run. Follows `r53/BLIND_RULES.md` as clarified by
Tyler: the **algorithm reads only the ciphertext and generic models**, and the published letters are used only as a
check after everything is frozen and pushed.

## Why
- **Scheidt** said K4's plaintext is English with its statistics deliberately masked. ChatGPT's dossier (PR #46)
  recommends moving from key dictionaries to **masking-method identification**.
- **Homophonic substitution** is the classical cipher built for exactly this job: frequent letters get several cipher
  letters, which flattens the counts. `docs/CIPHER_TYPES_TESTED.md` §17 lists it as fitting K4's flat counts and
  **never tested**.
- **In place it is already exactly excluded:** any fixed letter-to-letter decode sends the two Q's at positions 26–27
  to one letter, but the published plaintext there is N, O (the L02 argument).
- **So R66 tests it combined with a transposition.** The decode is the same at every position, so "substitute then
  transpose" and "transpose then substitute" give the same relation. One search covers both.

## Hypothesis H-HOM (exactly what is tested)
- **Plaintext:** P is ordinary English, 97 letters.
- **Decode map:** f sends each cipher letter to one plaintext letter. Several cipher letters may share a plaintext letter
  (homophones), **at most 4 per plaintext letter** (the cap; see the development record). Some plaintext letters may
  have no cipher letter at all.
- **Transposition:** CT[j] = X[perm[j]] and P[i] = f(X[i]).
- **Part A (blind, with measured power):** perm is one of the **10 frozen R61 routes** (`r61/routes.txt`).
- **Part B (exact, after the freeze):** large permutation families, checked against the published letters (below).

## Part A blind pipeline (frozen: `r66/blind/run.py`, `r66/blind/hom_solve.cpp`)
- **Solver:** for each ciphertext, undo each of the 10 routes and solve each un-routed text with `hom_solve`:
  - simulated annealing over f under the R59 English letter model (order 6, `r59/blind/LM_SHA256`);
  - 30 restarts × 1,000,000 moves, temperature 5 → 0.05 (log10 units), homophone cap 4, fixed seed 66;
  - then a hill-climb polish of f under letter model + 1 × the R59 word-segmentation score.
- **Answer:** the best total over the 10 routes (ties: lower route index).
- **Raw evidence:** every route's best and top 8 decodes in `work/`, hashed in `WORK.sha256`.
- **Cache:** a finished ciphertext is reused only if its digest (ciphertext, model, routes, binary, parameters) matches.
- **No tuning after this file is committed.**

## Development record (development sources only; K4 never run)
- **The cap.** Without a cap, the letter model's smoothing rewards degenerate decodes: 97 × "A" scores −24.9, while
  real English windows score −62 to −83, and the search found such strings. Real homophonic tables give each letter
  only a few cipher letters (the plant tables here give at most 3). The cap of 4 is part of the cipher model.
- **Search settings.** In-place tests on 6 homophonic plants from *Tom Sawyer* (seed 66001), with the run that
  produced each conclusion:

  | Annealing (restarts × moves, temperature) | Plants solved | What it showed |
  |---|---|---|
  | 20 × 20k–60k, start 0.3–2.0 | 0–2/6 | too cold and too short: found decodes scored below the true text (search failure, not model failure) |
  | 10 × 1M, start 5, order 6 | 3/6, and 3/3 simple substitutions | longer, hotter runs on the full model work |
  | **30 × 1M, start 5, order 6** | **6/6 (91–97/97)** | adopted |

  - Annealing on order-4/5 models was worse.
  - In-place shuffled copies scored −209 to −228, against plants at −132 to −177.
- **Routed development run** (`r66/dev/`): 8 plants, `make_plants.py dev_pt.txt 8 66001 DEV`, plus 8 nulls
  (seed 66002), through the full 10-route pipeline:
  - **recovered 7/8**: median 95/97 letters, route right 7/8;
  - recovered plants scored −134 to −186; the null maximum was −196.7;
  - one plant (DEV_04) had IC 0.0363, as flat as K4, and was recovered (76/97);
  - **the miss (DEV_06)** was a search failure on its true route: it scored −199.4 on a wrong route, below the null
    maximum;
  - all 1,437 raw witnesses valid.
- **Runtime:** about 19 s per route, so about 3.2 min per ciphertext on one core.

## Holdout gate (fixed now)
- **Plants:** 20, generated only after this file is pushed:
  `r66/sealed/make_plants.py hold_pt.txt 20 66100 HOLD OUTDIR`.
  - Plaintext windows from the R64 holdout books (*The Call of the Wild*, *The Hound of the Baskervilles*;
    `r64/corpus/build_sources.py`, sha256-pinned). The R66 solver never saw them.
  - Homophone tables, cipher choices and routes random.
- **Nulls:** 20 shuffles, `r63/sealed/make_nulls.py BLIND.tsv 66101`.
- **Order:** one blind run → freeze and push → `r66/sealed/verify.py` → sealed `r66/sealed/gate.py … 60 14`.
- **Pass:** at least **14/20 plants recovered**, and every witness valid. Recovered = above the maximum null **and**
  ≥ 60/97 plaintext letters correct.
- **If the gate fails:** record **INCONCLUSIVE**, do not run Part A on K4, and still run Part B (which needs no power).

## K4, Part A (only if the gate passes)
- **Input:** `r66/sealed/prepare_k4.py`: the unchanged K4 (sha256 2797de14…) plus 100 frequency-preserving shuffles,
  seed 660070.
- **Order:** one blind run → freeze and push → `verify.py` → commit and push → only then
  `r66/sealed/reveal_k4.py`.
- **Decision:**

  | Outcome | Condition |
  |---|---|
  | **SIGNAL** | K4's total exceeds all 100 nulls' totals **and** K4's frozen plaintext matches ≥ 10/24 published letters |
  | **Score anomaly** | the first condition without the second (STAT; not a candidate) |
  | **NO SIGNAL** | otherwise |

- **Secondary (exploratory):** the best published-letter match over all frozen alternatives of K4, with the same number
  for every null.

## Part B: exact family check (after the K4 freeze; `r66/sealed/hom_feas.cpp`)
- **The exact condition:** for a fixed permutation, a homophonic decode matching the 24 published letters exists if and
  only if no cipher letter would have to stand for two different plaintext letters at the published positions. The cap
  of 4 never binds on 24 letters.
- **Families:**
  1. **2,538 distinct explicit permutations** (`r66/data/feas_routes.txt`, sha256 in `r66/data/FEAS_ROUTES.sha256`):
     - R61's 10 routes;
     - the strictblind r27 set (identity + 20 K3-style routes);
     - every double rotation with widths 4–28 (`routes.py rot 4 28`);
     - keyed columnar for KRYPTOS, PALIMPSEST, ABSCISSA (32 variants each).
  2. **Every complete columnar transposition of widths 2–11, every column order**, in both directions (fill rows and
     read columns in key order, and its inverse): 43,954,712 orders per direction.
- **Run on K4 and on the same 100 nulls.**
- **Reported:**
  - **EXCL** for every infeasible permutation;
  - the number of **feasible** permutations for K4, compared with the nulls' counts;
  - K4's feasible permutations listed raw.
- **Feasible permutations are not candidates.** They are not solved with the published letters, and no crib-selected
  solving is done without Tyler's go-ahead.

## What a negative would and would not mean
- **Would argue against:**
  - **STAT, with power:** K4 = ordinary English through a homophonic table (≤ 4 cipher letters per plaintext letter)
    with one of the 10 routes.
  - **EXCL:** the same for every infeasible permutation in the Part B families, with no cap at all.
- **Would not exclude:**
  - other transpositions;
  - homophonic tables keyed by position (polyalphabetic homophonic);
  - nulls or padding;
  - more than 4 homophones per letter in Part A (Part B has no cap);
  - non-English or phonetically spelled plaintext;
  - a true one-time pad.

## Context recorded now (no published letters)
- K4's index of coincidence is 0.0361.
- The 6 in-place development homophonic plants had IC 0.042–0.053 (`r66/sealed/homophonic.py` tables, 20–22 distinct
  plaintext letters, so only 4–6 spare cipher letters).
- A 26-letter homophonic system flattens only partly. K4's very flat counts are not specifically predicted by it.
