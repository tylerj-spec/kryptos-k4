# R118 pre-registration (Claude Code, 28 Nov 2026): how the blind solvers cope with masked English (P9; synthetic)

**Type: synthetic measurement. No K4 input of any kind.**

**Approval:** Tyler, 28 Nov 2026: "I approve all of them", answering the list of P6, P8, P9 and F2's route rounds.
This is proposal P9 of `audit/ROLLING_QUEUE.md`, from F1 §4.

**Independent review: NONE** (one model). R118 joins audit batch C.

## 1. Why
Two K4 results rest on solvers that score candidates with English letter or word models:
- **R111** (L199): the blind S105 run, NO_SIGNAL;
- **R59** (L149): the running-key search, NO SIGNAL.

If Sanborn "masked" the English before enciphering it, a true K4 could score badly and be missed. R118 measures how
much recovery each solver loses on text masked by two fixed rule sets. The solvers and their parameters are
unchanged.

## 2. Texts and masks (`r118/masks118.py`)
**Source:** the Carter OCR, split into word tokens ([A-Z]+) and full stops.
- Plaintext windows come from the **second half**, starting at least 2,000 letters after the midpoint (R114's TEST-C
  region).
- Running keys for the R59 arm come from the **first half**.

**Three forms of each window, built from the same run of words:**
- **U, unmasked:** letters only.
- **G, Germanic/Dutch-like respelling.** These rules apply to each word, in this order:
  1. PH → F
  2. CK → K
  3. QU → KW
  4. C → Z before E, I or Y
  5. remaining C → K
  6. W → V
  7. X → KS
  8. initial Y → J
  9. remaining Y → IJ
  10. SH → SJ
  11. OO → OE
  12. initial F → V
- **T, telegraphese:** drop the words THE, A, AN and OF, and write each full stop as the word STOP.

**Building a window.** A run of words is started at a random word. The first 97 letters of each form are taken, so
the three forms of a window share their opening words. A window is skipped if any of its three forms contains
EASTNORTHEAST, NORTHEAST, BERLIN or CLOCK.

**Scoring.** Recovery is always scored against the form that was **actually enciphered**.

## 3. Arms
| Arm | Solver (unchanged) | Plants | Encryption | Solver run |
|---|---|---|---|---|
| **S** | S105 (`r105/solve105.py`), conditional at the plant's own cell, exactly as R114's arm A1, with fail-closed 97-letter witnesses | 40 base windows (2 per R111 cell: B ∈ {AZ, KRY} × L 1–5 × σ ±1) × 3 forms = 120 | `r100/autokey100.py`, random A, c, primer and signs within σ. The same parameters for all three forms of a window | as R114 |
| **R** | R59's running-key solver (`r59/blind/rk_solve.cpp`, built with `g++ -O2 -std=c++17`), on the plant's own convention only, R59's parameters (beam 100,000, top 2,000, λ 1, polish 3, words 20,000), with R59's pinned letter model (sha256 b1a2a3c7…, checked before use) | 12 base windows × 3 forms = 36. Conventions cycle over AZ_VIG, AZ_BEAU, KRY_VIG and KRY_BEAU. The key is a Carter first-half window, unmasked | R59's plant encryption: c = X[x(p) + x(k)] for VIG, X[x(k) − x(p)] for BEAU | one solver call per convention, with that convention's 9 messages |

**Seeds:**
- S arm: plants 1180901, solver 1180902;
- R arm: plants 1180903.

## 4. Endpoints and labels (fixed now)
**Endpoints:**
- **S arm:** per form, the share recovered at ≥ 90/97 letters (with a valid witness), and the exact share.
- **R arm:** per form, the share with **pair-correct ≥ 60/97** (R59's metric: positions where the output pair
  {p, k} equals the true pair), plus the median pair-correct and the exact-plaintext count.
- **For each mask M ∈ {G, T}:** the drop **U − M** in percentage points, and the paired counts (recovered under U but
  not M, and the reverse).

**Label per arm and mask:**
- **SENSITIVE** if the drop is more than 15 points;
- **ROBUST** otherwise.

**What a label means for the K4 claims:**
- **SENSITIVE:** that K4 NO_SIGNAL (R111 for S, L149 for R) does not cover English masked that way. The ledger row
  gets that qualifier.
- **ROBUST:** the NO_SIGNAL stands for that kind of masking, within this rule set.

**Budget:** two jobs under `audit/run_bounded_agg.py`, zero retries.
- **S job:** 3,600 s / 3,600 s / 2,048 MiB; about 13 minutes expected.
- **R job:** 3,600 s / 3,600 s / 2,048 MiB; about 16 minutes expected. The solver's peak is 1,372 MB in development.

## 5. Development (synthetic only)
- The masks were checked on a Carter first-half sample.
- R59's solver was timed on one synthetic running-key plant: 161 s for four conventions, 26.5 s for one. Peak
  1,372 MB.
- No other result was seen.

## 6. What follows
- The labels qualify R111's and L149's NO_SIGNAL statements in their ledger rows, additively.
- **If G is SENSITIVE,** an orthography-aware scorer (cf. L69) would be the development target for any repeat blind
  run. A repeat run needs its own registration.
- **Not measured:**
  - other rule sets, other languages (L63, L108), and other solvers;
  - masks that change the cipher's alphabet behaviour (F1 §2).
