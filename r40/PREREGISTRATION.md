# R40 pre-registration (Claude Code, 28 Oct 2026): strict-blind search with a FREE plaintext alphabet

Written before any R40 run on K4. Development so far used planted data only (one development message, seed 49999,
never used in the real run).

## Why this family
- **What earlier blind rounds fixed:** R32–R38 fixed both alphabets (12–48 conventions).
- **Why that left a gap:** two unknown alphabets cannot be solved blind at 97 letters (L109, L112, L116, L123). A
  new nested solver prototype this round also fails, even though the true text scores best.
- **Why one free alphabet is different:**
  - Fix the cipher alphabet CA and the key, and let the plaintext alphabet PA be **any** of the 26! orders. Then
    y = CA⁻¹(c) − k (Vigenère or Beaufort), or y = CA⁻¹(c) + k (variant Beaufort), is a **simple substitution**
    of the plaintext.
  - Simple substitutions of 97 English letters can be solved.
  - y's letter counts are unchanged by any transposition applied *before* the substitution. So the stage-1
    statistic also detects "any transposition, then this substitution", though only in-place texts can be read.
- **Classical names covered:**
  - Quagmire I: AZ cipher alphabet, any plaintext alphabet.
  - Quagmire III/IV with the KRYPTOS tableau as cipher alphabet and any plaintext alphabet.
  - The same with PALIMPSEST/ABSCISSA alphabets, and with ACA Gromark alphabets.

## Exact family (one setting = key × CA × operation)
- **Ciphertext:** K4, the original 97 letters (sha256 `2797de14…a5a3` with newline).
- **CA (7):**
  - `AZ`
  - `KRY` (`KRYPTOSABCDEFGHIJLMNQUVWXZ`)
  - keyword-prefix `PALP`, `ABSP` (as in R37)
  - ACA columnar `ACAKRY`, `ACAPAL`, `ACAABS` (as in R38)
- **Operation (2):**
  - `VIG|BEAU`: y = x − k. Vigenère and Beaufort give the same y up to a substitution.
  - `VARB`: y = x + k.
- **Keys (24,131,248 keys; 337,634,136 settings per ciphertext):**
  - chain addition k_i = k_{i−b} + k_{i−b+1} mod base, every primer:
    - base 10, b = 5, 6, 7 (`C10b5`, `C10b6`, `C10b7`);
    - base 26, b = 5 (`C26b5`).
  - running key `CARTER`: Carter & Mace vol. I, sha256 `6761a507…3ee0`.
  - running key `K1K3`: the K1–K3 plaintext, `k4kit/data/k1k3_plaintext.txt`.
  - For both running keys: forward and reversed, letters numbered AZ or KRY, every offset.
- **Known twins:**
  - **Base-10 chains:** the digit-complement primer with the other operation gives the same y except where the
    key digit is 0.
  - **Base-26 chains:** the complement primer with the other operation gives an **identical** y.
  - A twin counts as the true setting in every rule below.

## Blind pipeline (`r40/blind/`, contract-tested: no clue words, positions, masks or sealed files)
1. **Stage 1 (`pafree_scan`):**
   - For every setting, L1 is the best unigram log-likelihood of y under any substitution: sorted counts of y
     against sorted English log-frequencies. The frequencies are the marginal of `k4kit/data/quad_log10.f32`.
   - Keep the global top 5,000, with ties broken by (family, key, CA, operation).
   - Record a histogram of L1 over every setting.
2. **Stage 2 (`subsolve`):**
   - Solve each of the 5,000 as a simple substitution in reading order: English quadgrams, 8 restarts × (20,000
     annealing + 3,000 greedy swaps).
   - Seeds come from the setting string.
3. **Stage 3:** re-solve the 50 best stage-2 rows with 64 restarts. The final score is the better of the two.
4. **Freeze:** `FROZEN.sha256` covers all outputs, ciphertexts, the copied blind sources, binaries, the quadgram
   table, both key texts and this file. Commit and push before anything in `r40/sealed/` runs.

## Controls
- **Plants (`r40/sealed/make_inputs.py`, seeds 40000–40011):** 12 English passages written for R40, none
  containing a K4 clue word.
  - **Key families:** plant *i* uses family [C10b5, C10b6, C10b7, C26b5, CARTER, K1K3][i mod 6].
  - **Alphabets, operation, key:** a uniformly random PA, with CA, operation and key drawn uniformly from the
    family.
  - **Routes:** plants 0–5 are in place; plants 6–11 are first transposed by a uniformly random permutation.
- **Nulls:** 4 shuffles of K4 (seeds 40100–40103), letter counts kept.
- **Same pipeline:** every control goes through the identical pipeline as K4.

## Decision rules (fixed now)
- **Gate:** the gate passes only if all three hold. If it fails, the failing part of the K4 result is reported
  as not interpretable, and nothing is re-tuned.
  1. All 6 in-place plants have their true setting (or twin) at final rank 1.
  2. At least 5 of 6 transposed plants have their true setting (or twin) in the stage-1 top 5,000.
  3. Each in-place plant's true setting is consistent in the whole-family check below.
- **K4 candidate:** either of these makes a candidate:
  - a K4 final row scoring at least T, where T = (best null final score + lowest in-place plant true-row final
    score) / 2;
  - a K4 top-20 row with at least 20 of the 24 published letters.

  A candidate is re-solved with 256 restarts and reported raw. It counts only if it reads as language and keeps
  at least 20/24 letters.
- **Whole family, in place (`sealed/whole_family.cpp`, after the freeze):**
  - For each in-place setting, the 24 published letters are checked for consistency with any plaintext alphabet
    (equal letters ⇔ equal y). This is exact.
  - **0 consistent settings** means **EXCL** (exact) for in-place decryption with these 7 CA × 2 operations × 6
    key families and **any** plaintext alphabet.
  - **Chance level:** about 26⁻¹¹ per setting, so about 0 expected.
  - **Calibration:** the nulls are run with K4's letters. Each in-place plant is run with its own letters at the
    same positions.
- **Transposition-first detection (descriptive):**
  - **Signal:** K4's best L1 is above every null's best L1 **and** at or above the lowest true L1 of the
    transposed plants.
  - Otherwise there is **no signal** for "any transposition, then this substitution".
- **No external checker is contacted.**

## Development record (planted only)
Development message: seed 49999, C10b6, KRY, VIG.
- **Stage 1:** the true setting ranked **3** of 337,634,136.
- **Stage 2:** #1, with 1 letter wrong.
- **Wrong rows:** they score ≤ −455; the true row scores −400.4; its base-10 twin is #2 at −410.7.
- **Whole family:** 2 consistent settings, the true one and its twin.

**Simulation:** for English 97-letter windows at their 5th percentile of L1, 2 × 10⁻⁶ of random strings score
higher (about 700 of 3.4 × 10⁸).

## Limitations
- **Cipher alphabet:** fixed, 7 choices. A free CA is not covered.
- **Keys:** only the six key families.
- **Reading:** only in-place texts can be read. Transposition-first texts are detection only, through unigram
  counts.
- **Language model:** assumes English-like letter frequencies.
