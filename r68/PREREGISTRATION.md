# R68 pre-registration (Claude Code, 5 Nov 2026): classic keyed ciphers whose key advances along a path through the carved text

Written before the holdout plants are generated and before any K4 run. Follows `r53/BLIND_RULES.md` as clarified by
Tyler: the **algorithm reads only the ciphertext and generic models**, and the published letters are used only as a
check after everything is frozen and pushed. Tyler asked for this follow-up to R67 and authorised running it through to
K4 candidates.

## Why
- **The anomaly:** R65 and R67 established that K4's letters read along SNAKE_L carry structure that neither shuffles
  nor six structured cipher families reproduce. SNAKE_L reads the 4+31+31+31 engraved rows in alternating directions.
  R65b showed it is not a German running key.
- **The ciphers not yet tried on paths:** the classic keyed ciphers a 1989 hand cipher would use, whose key advances
  letter by letter along such a path.
- **Sanborn's wording:** Sanborn stated his clues as carved letters decoding to plaintext letters ("NYPVTT, letters 64–69,
  decode to BERLIN"). Taken literally, each carved letter decodes in place. That fits a cipher whose **key** follows the
  path while each letter stays where it is carved (model M2 below). The R61/R64 transposition model (M1) puts the
  published letters at plaintext positions instead. R68 tests both.

## Hypotheses (exactly what is tested)
- **Paths:** the carved order (ID) and the 10 frozen R61 routes (`r61/routes.txt`). For a path perm, the path-order text
  Y satisfies CT[j] = Y[perm[j]].
- **Models:**
  - **M1** (substitute, then transpose; R61/R64): the plaintext is in path order. Published letters at path-order positions
    21–33 and 63–73.
  - **M2** (position-aligned; key along the path): carved letter j is enciphered in place at path step perm[j]:
    CT[j] = E(P[j], k_{perm[j]}). The plaintext is in carved order, and the published letters sit at carved positions
    21–33 and 63–73, literally as Sanborn stated them.
  - For ID, M1 = M2 = in place.
- **Conventions (12):** plaintext alphabet Ap and ciphertext alphabet Ac each AZ or KRYPTOS, with op VIG (y = x + k),
  BEAU (y = k − x) or VARB (y = x − k), where x = Ap⁻¹(p), y = Ac⁻¹(c).
- **Families** (k_t = shift at path step t):

  | Family | Key | Range |
  |---|---|---|
  | PER | periodic shifts s[t mod p] | p = 1–20 |
  | GRO | Gromark: 5-digit primer, d_t = d_{t−5} + d_{t−4} mod 10 | all 100,000 primers |
  | CTAK | ciphertext autokey, k_t = Ac⁻¹(Y[t−L]), free primer for t < L | L = 1–24 |
  | PTAK | plaintext autokey, k_t = Ap⁻¹(Q[t−L]), free primer for t < L | L = 1–24 |

## Blind pipeline (frozen: `r68/blind/run.py`, `r68/blind/keyed_solve.cpp`)
- **Rows:** for each ciphertext, all 21 (path, model) rows (ID once, 10 routes × 2 models) are solved under every family,
  convention and parameter.
- **Search:**
  - **PER:** coordinate ascent, 6 seeded restarts.
  - **GRO:** exhaustive over all 100,000 primers.
  - **CTAK and PTAK:** coordinate ascent over the primer (PTAK with 6 seeded restarts).
  - **Scoring:** the order-4 slice of the R59 English model during search; every candidate rescored with the order-6
    model + 1 × the R59 word score (the total).
- **Answer per family:** the best total over rows, conventions and parameters.
- **Raw evidence:** every row's best per family and convention (21 × 48 per ciphertext) is kept in `work/` and hashed.
- **No tuning after this file is committed.**

## Development record (development sources only; K4 never run)
- **Routed development run** (`r68/dev/`): 8 plants (`make_plants.py dev_pt.txt 8 68001 DEV`, *Tom Sawyer*) and
  8 shuffled nulls (seed 68002), run with 6 restarts:

  | Family | Recovered | Setting exact (path, model, convention, parameter) | Letters | Null maximum |
  |---|---|---|---|---|
  | PER (p 6, 6) | 2/2 | 2/2 | 97, 97 | −344.5 |
  | GRO | 2/2 | 2/2 | 97, 97 | −467.3 |
  | CTAK (L 11, 6) | 2/2 | 2/2 | 91, 91 | −421.3 |
  | PTAK (L 24, 15) | 0/2 | 0/2 | 9, 5 | −322.9 |

  - Both models and four different routes were recovered, including SNAKE_L and SNAKE_R.
  - All 16,464 raw witnesses are valid.
- **Long periods and lags** (true row only, *Tom Sawyer*):
  - With 6 restarts, PTAK was solved perfectly for L = 2–12 and failed for L ≥ 14. PER was only partly solved at p ≥ 12.
  - **20 restarts** gave:

    | | PER | PTAK |
    |---|---|---|
    | Letters at period / lag 12, 14, 16, 18, 20 | 97, 69, 97, 54, 35 | — |
    | Letters at lag 14, 16, 20, 24 | — | 69, 43, 54, 24 |

  - The search is the limit at long periods and lags, not the model. Restarts fixed at **20** (about 2.8× the cost).
  - Long periods and lags stay only partly powered; the gate reports them separately.

## Holdout gate (fixed now)
- **Plants:** 24, generated only after this file is pushed:
  `r68/sealed/make_plants.py hold_pt.txt 24 68100 HOLD OUTDIR`.
  - Plaintext from the R64 holdout books (*Call of the Wild*, *Hound of the Baskervilles*).
  - 6 plants per family, in a random order.
  - PER p uniform 2–20; CTAK and PTAK L uniform 1–24; random primer.
  - Convention, path and model random.
- **Nulls:** 24 shuffles, `r63/sealed/make_nulls.py BLIND.tsv 68101`.
- **Order:** one blind run → freeze and push → `r68/sealed/verify.py` → sealed `r68/sealed/gate.py … 60 3 5 5 2`.
- **Per-family gate:** recovered = above the family's null maximum **and** ≥ 60/97 letters. Bars: **PER ≥ 3/6, GRO ≥ 5/6,
  CTAK ≥ 5/6, PTAK ≥ 2/6**, and every witness valid.
- **K4 runs if at least one family passes;** a family that fails is INCONCLUSIVE for K4.
- **Also reported:** recovery for parameters ≤ 12 and > 12.

## K4 (only if a family passes)
- **Input:** `r68/sealed/prepare_k4.py`: the unchanged K4 (sha256 2797de14…) plus 100 frequency-preserving shuffles,
  seed 680070.
- **Order:** one blind run → freeze and push → `verify.py` → commit and push → only then `r68/sealed/reveal_k4.py`.
- **Primary, per passing family f:**

  | Outcome | Condition |
  |---|---|
  | **SIGNAL (f)** | K4's family-f best total exceeds all 100 nulls' **and** that decode matches ≥ 10/24 published letters |
  | **Score anomaly (f)** | the first condition without the second (STAT; not a candidate) |
  | **NO SIGNAL (f)** | otherwise |

  - Published letters are compared at plaintext positions: path order for M1, carved order for M2.
- **Contender screen:** **any** frozen K4 decode (each row's best per family and convention: 21 × 48) matching **≥ 12/24**
  published letters is listed raw.
  - **Alignment:** for M1, the literal carved-position reading (P[perm[j]] against the letter published for carved j)
    is also checked.
  - **Calibration:** reported with the number of null ciphertexts having any decode that reaches the same count.
- **A contender is not a solution.** It must also read as coherent English beyond the published letters, have a
  stated key and path, and re-encrypt exactly. No external checker without Tyler's go-ahead.

## Exact family check (after the K4 freeze; `r68/sealed/exact.py`)
- **What it checks:** for every path × model × convention, which settings can produce the 24 published letters, as exact
  necessary-and-sufficient conditions:
  - PER p = 1–48;
  - GRO all 100,000 primers;
  - CTAK L = 1–96;
  - PTAK L = 1–96 (constraints only where both steps carry published letters).
- **Run on:** K4 and the same 100 nulls.
- **Reported:**
  - EXCL for every infeasible setting;
  - the number of non-vacuous feasible settings (≥ 1 constraint) and strong ones (≥ 8 constraints), compared with the
    nulls.
- **Feasible settings are not candidates.** Their frozen blind decode is reported if they lie inside the blind search
  range.

## What a negative would and would not mean
- **Would argue against:**
  - **STAT, where the gate shows power:** K4 = ordinary English through one of these four keyed families, any of the 12
    conventions, with the key advancing along the carved order or one of the 10 R61 routes, under either model.
  - **EXCL:** every exactly infeasible setting.
- **Would not exclude:**
  - other keyed families (running keys are R59–R64; two free alphabets);
  - other paths;
  - long periods and lags beyond the measured power;
  - irregular key resets;
  - masking or non-English plaintext.
