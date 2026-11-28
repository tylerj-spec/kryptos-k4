# R114: L202, S105 validation on held-out text (synthetic). 4 of 5 bars pass; bar 3 on its boundary

Affected ledger IDs: L202

Validation:
- **Order of commits:** pre-registration 62a9747 pushed alone; source fee7038; job 1 frozen in f54fa56 before
  anything was read; both jobs frozen in 0b26783 before evaluation.
- **Resources:** both jobs COMPLETE under `audit/run_bounded_agg.py`, with zero retries.
- **No K4 input.**
- **CI:** `r114-validation.yml` checks the manifests and witnesses, then re-runs the first 10 A1 plants and the first
  A4 plant deterministically.
- **Guardrail check:** PASS.

Independent review: NONE (one model). R114 joins audit batch C.

## For the reviewer
1. **Bar 3 is exactly at its limit.** The inherited table gave 85/100; the first-half table gave 70/100. That is a
   difference of 15 percentage points, against a registered limit of "within 15".
   - The frozen code evaluates `abs(0.85 - 0.70) <= 0.15` as False (0.15000000000000002), so the frozen verdict is
     FAIL.
   - On the registered integer counts, the difference is exactly 15, which is a PASS.
   - I did not change the frozen output. Please decide which reading governs.
2. **Bar 3 confounds two things.** The first-half table comes from about half the text the inherited table may have
   had, so the drop mixes smaller training data with any overlap effect.
3. **R105's GO is not verified here.** It remains with the batch-B audit. R114 measures the solver only in its
   tested scope.
