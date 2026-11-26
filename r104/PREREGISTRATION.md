# R104 pre-registration (Claude Code, 26 Nov 2026): feedback-chain decomposition and solver architecture for the two-free-alphabet autokey

**Type: synthetic measurement and prototype study. No K4 input of any kind.**
- **Batch:** `audit/reviews/BATCH_WORK_ORDER_R102_R107.md`, item R104.
- **Procedure:** `audit/OPERATING_PROCEDURE_ROLLING.md`.
- **Dependencies:** none on unverified results. R103's IDENTIFIABLE verdict is one of R105's entry conditions, not
  R104's.

**Independent review: NONE** (one model). R104 is part of audit batch B.

## 1. Questions
1. **Does the feedback chain spread key errors?** If a decryption alphabet has a few wrong entries, what fraction of
   the plaintext is still right? This decides whether key-space local search can have a basin.
2. **Do the conditional problems reduce to known solvable forms?** There are two exact reductions (R102's algebra):
   - **(a) B known, F = A.** The plaintext A-ranks satisfy x_i = s1·(B⁻¹(C_i) − c) + σ·x_{i−L}, with σ = −s1·s2.
     This is a known linear recursion, so P = A[x]: a simple substitution of a known sequence, once c and the L
     chain offsets are fixed.
   - **(b) A known, F ∈ {A, AZ}.** b′(C_i) = g(P_{i−L}, P_i), with b′ = B⁻¹ − c and g a known pair function. The
     ciphertext is then a simple substitution of a *code* sequence.
3. **Can simple prototypes solve them on fresh synthetic plants?** The answer sets R105's entry gate.

## 2. Data
- **Text:** Carter OCR windows (as R102/R103, clue-word windows skipped).
- **Ciphers:** uniformly random alphabets.
- **Scorer:** the quadgram model `k4kit/data/quad_log10.f32` (sha256 in `PROTOCOL.sha256`).
- **Seed:** 1040901.

## 3. Registered computations
| Step | What | Size and rule |
|---|---|---|
| E1 landscape | Swap 1 or 2 random pairs in A, or in B; decrypt with the true c and primer; record the fraction of plaintext letters right | 120 plants (F cycling A, B, AZ; L in {1, 2, 3, 5}). Prediction: F = A with A-swaps ≥ 0.80 mean; every other combination ≤ 0.60 |
| E2 identities | Reduction (a) reproduces the plaintext ranks, given the true c and primer. Reduction (b) holds for F = A and for F = AZ | 100 plants each, 100/100 required |
| E3 prototype P1 | **B known, F = A**, L ∈ {1, 2, 3}. For each c ∈ Z26, set the chain offsets by two coordinate-ascent sweeps maximising the index of coincidence (IC) of x. Rank the (c, offsets) candidates by IC and keep the top 3. Solve each as a simple substitution by annealing (T0 3.5, 30,000 proposals, 6 restarts, quadgram score). Output the best | 24 fresh plants (8 per lag). Recovered = ≥ 90/97 letters |
| E4 prototype P2 | **A known, F = A, L = 1.** Code-trigram model computed from the quadgram probabilities. Anneal the code map b′ (T0 3.5, 30,000, 6 restarts). Decode with each of the 26 first letters, keep the best quadgram score. Also record whether the true map outscores the found map (a search gap) or not (an objective counterexample) | 24 fresh plants |

## 4. R105 entry gate (registered here)
R105, the conditional solver, may start **for a given mode** only if all of the following hold:
1. R103 is IDENTIFIABLE. It is (L192).
2. The R104 prototype for that mode recovers **≥ 12/24** fresh plants.
3. E2 passes.

Otherwise that mode is closed for this batch, with the evidence recorded. The development figures (not this run)
were P1 11/16 and P2 0/10. A failure of E2 is a stop condition.

**Budget:** `audit/run_bounded_agg.py`, 1,800 s / 1,800 s / 2,048 MiB, zero retries. Development estimate about 300 s.

## 5. Order
1. This file, `QA_MANIFEST.json` and `PROTOCOL.sha256`, pushed alone.
2. Source and `SOURCE.sha256`.
3. The run, then `OUTPUTS.sha256`.
4. The result note.

Nothing from R104 touches K4.
