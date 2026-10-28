# R42 pre-registration (Claude Code, 28 Oct 2026): strict-blind search with a FREE cipher alphabet

Written before any R42 run on K4. Development used planted data only: 24 messages from `reference_messages.json`
and one development message, seed 49997. None is reused in the run.

## Why this family
- **R40 and R41:** fixed the cipher alphabet and freed the plaintext alphabet.
- **R42 is the mirror image:** the **plaintext alphabet is fixed** (7 choices) and the **cipher alphabet is any**
  of 26!.
- **Classical names covered:**
  - Quagmire II: AZ plaintext alphabet, any keyed cipher alphabet. This includes the ACA's standard Gromark with
    any keyword.
  - Quagmire III/IV with the KRYPTOS tableau (or PALIMPSEST/ABSCISSA, or the ACA alphabets) on the plaintext side.
- **The math:** each ciphertext letter gets one unknown offset t(c), and p_i = PA[t(c_i) − k_i] (Vigenère) or
  PA[t(c_i) + k_i] (Beaufort and variant Beaufort, which are the same up to relabelling).
- **Development finding (planted only):**
  - With the key given, annealing t recovers the text blind at 97 letters: 24/24 readable at 16 restarts, 22/24 at
    8 restarts.
  - Wrong keys score far lower: true keys −377 to −404, wrong keys at or below −475.
  - **Two free alphabets fail (L109, L123); one free alphabet on this side does not.**

## Exact family (one setting = key × PA × operation), in place
- **PA (7):** `AZ`, `KRY`, `PALP`, `ABSP`, `ACAKRY`, `ACAPAL`, `ACAABS` (as in R40).
- **Operation (2):** `VIG` and `BEAU|VARB`.
- **Keys:**
  - `C10b5` and `C10b6`: every primer of base-10 chain addition k_i = k_{i−b} + k_{i−b+1}.
  - `CARTER` and `K1K3`: forward/reversed, letters numbered AZ or KRY, every offset.
- **Size:** 2,235,348 keys, so **31,294,872 settings per ciphertext**.
- **Twins:** a base-10 primer's digit complement, with the other operation, counts as the true setting.

## Blind pipeline (`r42/blind/`, contract-tested)
1. **Stage 1 (`ca_screen`):**
   - For every setting, the best unigram log-likelihood over all cipher alphabets. This is an exact 26 × 26
     assignment, solved with the Hungarian method. English letter frequencies are the quadgram table's marginal.
   - Keep the global top 20,000.
   - Development: the true key's score beat 40 random wrong keys in 21/24 messages and ranked ≤ 4 in all 24.
2. **Stage 2 (`casolve`):** anneal the cipher alphabet for each of the 20,000, 8 restarts × 30,000 swaps.
   Restart 0 starts from the stage-1 assignment.
3. **Stage 3:** re-solve the best 50 with 64 restarts.
4. **Freeze:** `FROZEN.sha256` covers outputs, ciphertexts, copied sources, binaries, the quadgram table, key texts
   and this file. Commit and push before `r42/sealed/` runs.

## Controls
- **Plants (`r42/sealed/make_inputs.py`, seeds 42000–42005):** 6 new English passages, in place, none containing a
  K4 clue word.
  - **Keys:** families C10b5, C10b6, CARTER, K1K3, C10b5, CARTER.
  - **Alphabets:** the PA is drawn from the 7, and the cipher alphabet is uniformly random.
  - **Operation:** drawn from VIG, BEAU and VARB.
- **Nulls:** 2 shuffles of K4 (seeds 42100–42101).

## Decision rules (fixed now)
- **Gate:** if it fails, it is reported and nothing is re-tuned.
  - At least 5 of 6 plants have their true setting (or twin) at final rank 1.
  - All 6 plants' true settings are consistent in the whole-family check.
- **K4 candidate:** either of these makes a candidate:
  - a K4 final row scoring at least T = (best null final score + lowest plant true-row final score) / 2;
  - a K4 top-20 row with at least 20 of the 24 published letters.

  A candidate is re-solved with 256 restarts and reported raw.
- **Whole family (`sealed/whole_family.cpp`, after the freeze):**
  - Exact check over every setting. The 24 published letters fix z_i = PA⁻¹(p_i) ± k_i. **Any** cipher alphabet
    fits exactly when equal ciphertext letters have equal z and different ones different z.
  - **0 consistent K4 settings** means **EXCL** (exact) for in-place decryption with these 7 PA × 2 operations ×
    these keys × **any** cipher alphabet.
  - **Calibration:** the nulls are run with K4's letters, and the plants with their own.
- **No external checker is contacted.**

## Limitations
- **Plaintext alphabet:** fixed, 7 choices.
- **Routes:** in place only.
- **Keys:** these four key families only. C10b7 and base 26 are left out for cost.
- **Language model:** English letter statistics.
