# R64 pre-registration (Claude Code, 3 Nov 2026): World Clock or German running key, THEN a transposition

Written before the holdout plants are generated and before any K4 run. Follows `r53/BLIND_RULES.md` as clarified by
Tyler (R63 Amendment 2): clue-motivated hypotheses are fine; the **algorithm reads only the ciphertext and generic
models**, and the published letters are used only as a check after everything is frozen and pushed.

Built from ChatGPT's research (PR #46, `research/k4_2026-11-03/`, priority A1) and its R64 proposal (PR #45,
`r64/PROPOSED_PROTOCOL.md`). Their requests and how R64 meets them are listed at the end.

## Why
- **R61 (L150):** English running key, then one of 10 transpositions. No signal.
- **R63 (L152):** World Clock or German running key, in place. No signal, with 10/10 power for each.
- **Their combination was never tested.** If Sanborn took a Berlin-clock or German key and then transposed the result
  as in K3, R61 and R63 would both miss it.

## Hypothesis H-NEKT (exactly what is tested)
- **Plaintext:** ordinary English, P.
- **Key:** K from R63's frozen CLOCK model (any sequence of the 107 World Clock city names) or GERMAN model (German
  prose), `r63/blind/MODELS.sha256`.
- **Substitution:** X[i] = S(P[i], K[i]) under one of 6 conventions: AZ or KRYPTOS alphabet × VIG / BEAU / VARB.
- **Transposition:** CT[j] = X[perm[j]] for one of the **10 frozen R61 routes** in `r61/routes.txt` (K3's four 24×8
  rotations; the six 4+31+31+31 engraving-site routes), unchanged.
- **All 10 routes are searched symmetrically.** The R61/R62C COL_LT oddity is not given any extra weight.

## Blind pipeline (frozen: `r64/blind/run.py`)
- **Solver:** the R63 two-model solver `r63/blind/rk2_solve.cpp`, unchanged (binary sha256 f171dbe5…), with the R59
  English model (`r59/blind/LM_SHA256`).
- **For each ciphertext and each key model m (CLOCK, GERMAN) separately:**
  1. undo all 10 routes;
  2. **stage 1:** solve each un-routed text **without polish**: beam B1 = 15,000, TOPN 2000, LAMBDA 1, all 6
     conventions, POLISH_M 0;
  3. **stage 2:** the 2 best routes by stage-1 total (ties: lower route index) are re-solved with the **unchanged R63
     parameters** (beam 50,000, TOPN 2000, LAMBDA 1, all, POLISH_M 2, POLISH_WORDS 20000);
  4. **answer for m:** the best stage-2 total (ties: lower route index), with route, convention and both texts in
     plaintext order.
- **Raw evidence kept:** every solver output of both stages (10 + 2 route rows, each with the best, the 6
  per-convention bests and the top 8) in `work/`, hashed in `WORK.sha256`. Code, models, input and results are hashed
  in `FROZEN.sha256`.
- **Cache:** a finished (ciphertext, model) job is reused after an interruption only if its digest matches the
  ciphertext, model, every model-file hash, the routes hash, the solver-binary hash and the parameters.
- **No tuning after this file is committed.**

DEVELOPMENT_RECORD_PLACEHOLDER
