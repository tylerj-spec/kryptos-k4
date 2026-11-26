# R105 pre-registration (Claude Code, 26 Nov 2026): conditional solver for the two-free-alphabet autokey, cipher alphabet supplied, F = A

**Type: C development (solver), synthetic only. No K4 input of any kind.**
- **Batch:** `audit/reviews/BATCH_WORK_ORDER_R102_R107.md`, item R105.
- **Procedure:** `audit/OPERATING_PROCEDURE_ROLLING.md`.
- **Entry conditions** (registered in `r104/PREREGISTRATION.md` §4):
  - R103 is IDENTIFIABLE (L192);
  - R104's prototype for this mode recovered 19/24 (L193);
  - R104's E2 passed.

  All three are **unaudited** (batch B). R105's own gate (G1–G3 below) re-verifies the pieces it uses: the reduction,
  its gauge, the stage-1 statistic and every output's re-encryption. Nothing else rests on R102–R104 being right.
- **Mode:** only "B known, F = A". R104 closed the A-known mode for this batch.

**Independent review: NONE** (one model). R105 is part of audit batch B. **R106 may not start until ChatGPT has
independently verified a GO from this round.**

## 1. Question
The cipher is

    B⁻¹(C_i) = s1·A⁻¹(P_i) + s2·A⁻¹(P_{i−L}) + c   (mod 26)

- **Supplied:** B, L and the signs (s1, s2).
- **Unknown:** the plaintext alphabet A (any of 26!), the constant c, and the L chain starts.

**The question:** does a fixed solver recover the plaintext from 97 letters on fresh synthetic plants at lags 1–5?
If it does, can its score tell a recovery from a wrong hypothesis?

## 2. The solver S105 (fixed here; source `r105/solve105.py`)
**Reduction.** This is R104's reduction (a), with σ = −s1·s2:

    x_i = s1·(B⁻¹(C_i) − c) + σ·x_{i−L},   P_i = A[x_i]

For each trial c′ ∈ Z26, compute x⁰(c′) with every chain start set to 0.

**Gauge.** The true ranks are x⁰(c′) + σ^t·o_r, where t = i div L and r = i mod L, up to a global relabelling of A.
The solver therefore fixes o_0 = 0:
- for σ = +1, the relabelling absorbs o_0 and c′ = c;
- for σ = −1, c′ = c + 2·s1·o_0 absorbs the rest.

The search space is c′ and o_1, …, o_{L−1}: 26^L points, exhaustive.

**Stages:**
1. **Exact pooled histogram.** For every grid point, compute Σ_v n_v², the sum of squares of the letter counts of the
   candidate rank sequence. It is substitution-invariant and equivalent to the index of coincidence. It is computed
   from pairwise cross-correlation tables of the sub-chain histograms:
   - one sub-chain per chain for σ = +1;
   - even and odd t separately for σ = −1.

   Keep the top **N = 4,000** (all, if fewer).
2. **Re-rank.** Rank by z(Σ n_v²) + z(bigram coincidences + 0.5·trigram coincidences), with z-scores taken within the
   pool. Both statistics are substitution-invariant. Keep the top **200**.
3. **Quick anneal.** Run one batched swap anneal of the substitution per candidate: 12,000 proposals, T0 3.5, linear
   cooling, quadgram score. Keep the top **10** by score.
4. **Full anneal.** Run 6 batched restarts per candidate, each 30,000 proposals, T0 3.5.

   **Output:** the best quadgram score, its plaintext, A, c′ and the offsets.

**Shared settings:**
- **Quadgram scores:** `k4kit/data/quad_log10.f32`, rounded to integers in units of 10⁻⁴ so that the sums are exact
  on every platform.
- **Randomness:** the annealer's random stream is numpy PCG64, seeded from the solver's Python stream.

**Development history** (dev seeds 1051–1062, none reused below):

| Version | Dev result |
|---|---|
| R104's P1 with histogram-aligned offsets, L 3–5 | 2/15 |
| Exhaustive IC grid | truth ranked ≤ 147 at L ≤ 5 |
| IC then bigram re-rank, top 8 annealed | 21/25 |
| Three-stage | 23/25 |
| Sum-of-squares fix | 23/30. The 7 failures: 4 scorer counterexamples (the true plaintext scores lower than the output), 1 annealer gap, 2 selection misses |
| Stage-2 statistic comparison | z(IC) + z(n-grams) best: the truth ranked ≤ 38 of 4,000 at L 4–5 over 24 plants |
| Medium-anneal stage | 23/30 |
| Joint offset refinement | 22/30, dropped |
| Batched annealer | 24/30 |
| Final cuts (this registration) | 27/30 and 24/30, so **51/60 at ≥ 90 letters** and 56/60 at ≥ 80 |
| Nulls with the final solver | best score ≤ −461.4 over 15 nulls; recovered plants scored −359 to −426 |

## 3. Registered computations (in this order)
**Seeds:** plants and nulls use Python `random.Random(1050901)`; the solver uses `random.Random(1050902)`.

**Text:** Carter OCR windows of 97 letters (as R102–R104), skipping windows that contain a published K4 plaintext
word.

**Alphabets:** uniformly random A and B.

| Step | What | Size and pass rule |
|---|---|---|
| **G1a gauge** | The true key, mapped into the solver's gauge, gives exactly x = (A⁻¹(P) − o_0) mod 26 at every position | 100 plants, L 1–8, all four sign pairs, **100/100** |
| **G1b reflection** | (s1, s2, A) and (−s1, −s2, A reflected, A′[v] = A[−v]) give the same ciphertext at every position ≥ L with the same c. This justifies the two-cell scan in E1 | 100 plants, **100/100** |
| **G2 stage-1 reference** | The table value equals Σ_v n_v² computed directly (`np.bincount`) from the candidate sequence | 20 plants × (50 random grid points + the truth), exact equality, **all** |
| **M1 plants (primary)** | S105 on fresh plants with the true B, L and signs. 10 per lag L = 1..5: 5 with σ = +1 and 5 with σ = −1, the sign pair drawn at random within σ. Random c and primer. **Recovered** means ≥ 90/97 letters right | **50 plants** |
| **M2 nulls** | S105 on: (a) 10 uniform random ciphertexts, with random B, cell and L cycling 1–5; (b) 10 fresh plant ciphertexts with an independent random B; (c) 10 fresh plants with the true B but a wrong L′ ≠ L from 1–5 | **30 nulls**. M = the highest null score |
| **G3 re-encryption** | Every S105 output in M1, M2 and E1 re-encrypts exactly to its input ciphertext at positions L…96, under `r100/autokey100.py` `enc_letter` with the output (A, c′) and the supplied B and signs | **all outputs** |
| E1 σ unknown (exploratory) | 10 fresh plants (L cycling 1–5, σ alternating). Solve at (1, −1) and (1, 1) (one cell per σ, by G1b). Record which σ scores higher and whether the higher-scoring output is recovered | 10 plants × 2 |

**Time guard (registered, not an amendment).** If cumulative CPU reaches 1,300 s before E1, E1 is skipped and marked
TRUNCATED with the count so far. G1, G2, M1, M2 and G3 are never truncated, and run first.

**Development estimate:** about 7 s per solve, about 700 s for the whole run.

## 4. Verdict
- **GO** if G1a, G1b, G2 and G3 pass, and both of the following hold:
  - **M1:** ≥ 35/50 recovered, with ≥ 5/10 at every lag;
  - **M1 against M2:** ≥ 90% of the recovered plants score above M.
- **NO_POWER** if the gates pass but either bar fails.
- **GATE_FAILED** if any gate fails. This is a stop condition.

**Also reported:**
- recovery at ≥ 80 letters;
- results per lag and per σ;
- the stage at which each unrecovered plant lost the truth;
- the number of unrecovered plants scoring above M;
- E1.

**What a GO means, and does not mean:**
- It certifies only a conditional solver for one mode on synthetic data. It is not a K4 result.
- Any K4 use (for example, B taken from a registered short list) would be a separately registered round, with its own
  gate and Tyler's approval.
- R106 (both alphabets free) needs this GO verified independently first.

**Budget:** `audit/run_bounded_agg.py`, 1,800 s wall / 1,800 s CPU / 2,048 MiB, zero retries. An INCOMPLETE run is
a stop condition.

## 5. Order
1. This file, `QA_MANIFEST.json` and `PROTOCOL.sha256`, pushed alone.
2. Source (`solve105.py`, `run105.py`) and `SOURCE.sha256`.
3. The run, then `run_v1/OUTPUTS.sha256`.
4. The result note, ledger row, review note and CI workflow.

Nothing from R105 touches K4.
