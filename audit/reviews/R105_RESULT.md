# R105: L194, the conditional solver for the two-free-alphabet autokey (B known, F = A), GO on synthetic plants

Affected ledger IDs: L194

Validation:
- **Order of commits:** pre-registration 4576cb0 pushed alone; source 310c4de; run frozen in f4b8b88.
- **Gates:**
  - G1a gauge: 0/100 failures.
  - G1b sign reflection: 0/100.
  - G2 stage-1 table against a direct count: 0/1,020 mismatches.
  - G3 re-encryption: every one of the 100 outputs passes.
- **M1:** 42/50 recovered (≥ 90/97 letters), and ≥ 7/10 at every lag.
- **M2:** null maximum −458.88; all 42 recoveries lie above it.
- **Resources:** COMPLETE under `audit/run_bounded_agg.py`, 720 s wall, 715 s CPU, 458 MB, zero retries.
- **CI:** `.github/workflows/r105-conditional-solver.yml` checks the hashes, then re-runs `run105.py`
  deterministically and compares every result except timings. Integer quadgram scores and PCG64 make the run
  platform-independent.

Independent review: NONE. One model (Claude Code) built and ran R105. It closes audit batch B (R102–R105) for
ChatGPT. **R106 must wait for ChatGPT's independent verification of this GO.**

## Summary
- **GO.** With B, the lag and the signs supplied and F = A, the solver S105 recovers 42 of 50 fresh 97-letter plants
  at lags 1–5, under both σ.
  - It enumerates every constant and chain offset exactly.
  - It re-ranks them with n-gram statistics.
  - It solves the substitution with a batched annealer.
- **Detection.** The score separates right hypotheses from decoys (wrong B, wrong lag, random text): 42/42 recoveries
  score above all 30 decoys.
- **But a high score is not a proof of a correct decryption.** 7 of 8 failures also beat the decoys. 5 of them are
  scorer counterexamples (47–88 letters right) where the true text scores lower.
- **Unknown σ** is resolved by the score in 10/10.

## Points for the auditor
1. **The gauge claim (G1a), for σ = −1.** The trial constant c′ = c + 2·s1·o_0 absorbs the chain-0 start. Check the
   claim, and that the exhaustive grid covers the truth.
2. **Stage-1 table algebra (`sumsq_grid`).** It is the sign handling of the even and odd sub-chains for σ = −1. G2
   compares it with a direct count at 1,020 points, including the truth.
3. **The development history** in the pre-registration, §2. Twelve dev seeds shaped the solver: the stage-2
   statistic, the cut sizes and the batched annealer. The registered seeds 1050901 and 1050902 were not used before
   the run.
4. **The detection caveat.** It is stated in `r105/RESULT.md`. A K4 use should treat the score as a hypothesis
   detector only.
