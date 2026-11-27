# Lag 21: novelty review against R71, and a finite work order (Claude Code, 27 Nov 2026)

Affected ledger IDs: none. This is a planning note: no ledger row changes, and nothing is computed on K4.

Validation: desk review of `r71/PREREGISTRATION.md`, `r71/RESULT.md`, `r71/features.py` and `r71/generators.py`,
and of the ledger rows L17, L157, L160, L161 and L198. The arithmetic below is analytic. Nothing was run.

Independent review: NONE (one model). This answers item 1 of §6 of
`audit/reviews/R108_R111_CHATGPT_QUALITY_REVIEW_20261127.md`.

## 1. What is already known (R71, L160)
- **The structure was already found.** R71 scanned widths 2–48 and found K4's repeated vertical pairs at width 21:
  R₂₁ = 11, its statistic T2. Against K4's own shuffles it is matched at 0.99% after the width scan. It is jointly
  rare with the width-7 doubled-letter column (8 × 10⁻⁵).
- **R71's seven families were not enriched** for the joint signature (NO_FAMILY). The families were:
  - one-time pad, running key;
  - periodic, for periods 2–30;
  - homophonic followed by one of the **10 fixed R61 routes**;
  - Gromark;
  - ciphertext autokey, for lags 1–30;
  - plaintext autokey, for lags 1–30.
- **R110 re-measures the same pairs.** R₂₁ = 11 again, with weight n(n − 1)/2 in place of max(n − 1, 0). Its adjusted
  p = 0.032 adds no independent evidence.

## 2. Mechanisms that predict excess repeats at lag 21, and their coverage
For K4's letter frequencies, the expected count under the shuffle null is about 3.7. A mechanism explains R₂₁ = 11
only if it makes a ciphertext pair (C_j, C_{j+21}) a function of something that repeats in English.

| Mechanism | Why it would raise R₂₁ | Coverage |
|---|---|---|
| Ciphertext autokey, lag 21: C_j = f(C_{j−21}, P_j) | A pair repeats when (C_{j−21}, P_j) repeats. The expected R₂₁ is about 2,850 × (1/26) × 0.066 ≈ 7 | **Excluded by exact checks:** L17 (free alphabet, lags 1–67) and L157 (carved order and routes, L ≤ 71). Also simulated in R71 |
| Plaintext autokey, lag 21 | A pair depends on the triple (P_{j−21}, P_j, P_{j+21}). English has no structure at spacing 21 | Predicts **no** excess. R109 cannot test lag 21 (no crib equations) |
| Periodic substitution, period dividing 21 | The pairs are (σ(P_j), σ(P_{j+21})). English has no lag-21 bigram structure | Predicts no excess. R71's periodic family was not enriched |
| **A transposition that puts plaintext neighbours 21 apart, then a polyalphabetic substitution** | Plaintext bigrams land at ciphertext lag 21, so English bigram repeats survive whenever the two occurrences share alphabets | **Not covered.** R71's route family used only 10 fixed routes, followed by homophonic substitution. The L06–L09 transposition exclusions do not produce 21-letter columns. The K3-style decimations of L161 put neighbours at lags 25, −7, 4, 46, 28, −2, 14, 49 and −1 mod 99, never 21 |
| A physical or layout artefact (a sheet or line 21 wide) | Copying or arrangement, not encryption | Outside cryptanalysis. That is R71's own recommendation |

**Examples of the open mechanism:**
- a decimation C_j = X_{(a·j) mod n} with a⁻¹ ≡ 21 (mod n), for example a = 37 for n = 97;
- a grid with 21-letter columns read by columns: 5 columns, 97 of 105 cells, with column orders and reading
  variants;
- in either case, followed by a periodic or similar substitution.

**A rough size check.** English 97-letter text has about C(96, 2) × 0.006 ≈ 27 repeated bigram pairs. Under a period-p
substitution, about 27/p of them survive, so the expected R₂₁ is about 3.7 + 27/p. Reaching 11 suggests a small p.
But K4's index of coincidence (0.0361, below random) argues for a strong, near-uniform substitution, which suppresses
those repeats. Whether the family can match **both** at once is the genuine open quantitative question. Only
simulation can settle it.

## 3. What a new experiment would add
It would answer one question R71 could not: **does a lag-21-adjacency transposition followed by a polyalphabetic
substitution, matched to K4's index of coincidence, make R₂₁ ≥ 11 substantially more likely than shuffles and R71's
baselines?**

**What would distinguish this family from the alternatives.** It also predicts repeats in the chained pairs and
triples (C_j, C_{j+21}, C_{j+42}), which inherit English trigrams and skip-grams. Ciphertext autokey and the R71
families do not predict that. A follow-up would also lead somewhere concrete: each transposition hypothesis moves the
published letters to known plaintext positions. That gives exact crib-assisted checks, as L06 does for columnar plus
periodic.

## 4. Proposed finite work order (P5, replacing the earlier wording; needs approval)
1. **Step 1, synthetic only, with no K4 input.** For lag-21-adjacency transpositions (the decimation and grid forms
   above) with periodic substitution at p 2–30 and random alphabets, simulate IC-matched messages (as R71 did).
   Estimate:
   - P(R₂₁ ≥ 11);
   - the ratio of that probability to R71's running-key baseline;
   - the predicted rates for the chained triples.

   **Stop rule:** if the conservative lower bound of the ratio is below R71's bar of 10×, close P5. No K4 run follows.
2. **Step 2, only if step 1 passes, separately registered.** A crib-assisted exact check of these transposition plus
   periodic families, in place of a blind search. Any K4 statistic on the chained triples would be a new feature on
   already inspected text. It would be registered and reported as exploratory.

Nothing here uses K4 letters, positions or survivors of earlier crib checks to choose parameters for a blind search.
