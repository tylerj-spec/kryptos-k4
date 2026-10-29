# R41 pre-registration (Claude Code, 28 Oct 2026): free plaintext alphabet, substitution THEN K3-style transposition

Written before any R41 run on K4, after R40's reveal. R41 uses the same method as R40; development used planted
data only (one message, seed 49998).

## Why this family
- **What R40 covered:**
  - in place: decrypted, plus an exact whole-family exclusion;
  - "any transposition, then substitution": detected, since letter counts are unchanged.
- **What R40 could not reach:** **substitution first, then a transposition** (`S_then_T`, CT[j] = X[perm[j]]), the
  order of a substitution followed by K3's method. There the route decides which key letter meets which
  ciphertext letter.
- **The R41 method:** for a fixed route, X_i = CT[q_i] (q = perm⁻¹) and y_i = CA⁻¹(X_i) ∓ k_i. That y is again a
  simple substitution of the plaintext, in reading order, so it can be both detected and solved.
- **Earlier fixed-alphabet coverage of the same routes:** R32, R33, R34 and R35 tested them with fixed alphabets
  (12–48 conventions). R41 allows **any** plaintext alphabet.

## Exact family (one setting = key × route × CA × operation)
- **CA (7):** as R40. `AZ`, `KRY`, `PALP`, `ABSP`, `ACAKRY`, `ACAPAL`, `ACAABS`.
- **Operation (2):** `VIG|BEAU` (y = x − k) and `VARB` (y = x + k).
- **Part A: 116 routes, all S_then_T.**
  - **Routes:** `routes.py r27` (20) plus `routes.py columnar KRYPTOS,PALIMPSEST,ABSCISSA` (96).
  - **Keys:** `C10b5`, `C10b6` (every primer); `CARTER` and `K1K3` (forward/reversed × AZ/KRY numbering × every
    offset).
  - **Size:** 3,630,205,152 settings per ciphertext.
- **Part B: 5,000 routes, all S_then_T.**
  - **Routes:** `routes.py rot 4 28` (2,500 same-direction double rotations) plus `routes.py rot-mixed 4 28`
    (2,500 opposite-direction).
  - **Keys:** `C10b5` and `K1K3` only (for cost).
  - **Size:** 7,282,520,000 settings per ciphertext.
- **Twins:** a base-10 primer's digit complement, with the other operation, is its declared twin, as in R40.

## Blind pipeline (`r41/blind/`, contract-tested)
- **Stage 1 (`route_pafree_scan`):**
  - L1 is computed as in R40.
  - Each part keeps its top 20,000, and the two lists are merged to a top 20,000.
  - **Speed change from R40:** the count-sorting and modular arithmetic are table- and histogram-based. They gave
    byte-identical output to the direct version on the development message.
- **Stage 2:** solve all 20,000 as simple substitutions, 8 restarts each (`subsolve`, unchanged from R40).
- **Stage 3:** re-solve the best 50 with 64 restarts.
- **Freeze:** `FROZEN.sha256` covers outputs, ciphertexts, the copied blind sources, route files, binaries, the
  quadgram table, key texts and this file. Commit and push before `r41/sealed/` runs.

## Controls
- **Plants (`r41/sealed/make_inputs.py`, seeds 41000–41005):** 6 new English passages, none containing a K4 clue
  word.
  - Plants 0–3 use part A, with keys C10b5, C10b6, CARTER and K1K3.
  - Plants 4–5 use part B, with keys C10b5 and K1K3.
  - Alphabets: a random PA, with CA, operation, key and route drawn uniformly from that part.
- **Nulls:** 2 shuffles of K4 (seeds 41100–41101).

## Decision rules (fixed now)
- **Gate:** if the gate fails, it is reported and nothing is re-tuned.
  - At least 5 of 6 plants have their true setting (or twin) at final rank 1.
  - All 6 plants' true settings are consistent in the whole-family check.
- **K4 candidate:** either of these makes a candidate:
  - a K4 final row scoring at least T = (best null final score + lowest plant true-row final score) / 2;
  - a K4 top-20 row with at least 20 of the 24 published letters.

  A candidate is re-solved with 256 restarts and reported raw.
- **Whole family (`sealed/whole_family.cpp`, after the freeze):**
  - Exact consistency of the 24 published letters with **any** plaintext alphabet, over every setting of both
    parts.
  - **0 consistent K4 settings** means **EXCL** (exact) for S_then_T with these routes × 7 CA × 2 operations ×
    these keys × any plaintext alphabet.
  - **Calibration:** the nulls are run with K4's letters, and the plants with their own.
- **No external checker is contacted.**

## Development record (planted only)
Development message: seed 49998, C10b5 primer 31415, route R24x8/CW/inv, KRY, VIG. Scanned over 4 R27 routes ×
C10b5 + K1K3.
- **Stage 1:** the true setting ranked 1 of 5,826,016.
- **Whole family:** only the true setting is consistent.

## Limitations
- **Cipher alphabet:** fixed, 7 choices.
- **Routes:** only the declared sets. Part B uses fewer key families than part A.
- **Language model:** assumes English-like letter frequencies.
