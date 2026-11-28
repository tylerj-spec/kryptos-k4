# R116–R119: L204–L207. The approved proposals P8, P6 and P9, and F2 rank 1 (Tyler, 28 Nov 2026: "I approve all of them")

Affected ledger IDs: L204, L205, L206, L207 (new). L149 and L199 receive an additive qualifier through L206.

Validation:
- **Order of commits.** Every round pushed its pre-registration alone. Then its source; then its sealed gate, which is
  the pilot for R119; then its frozen outputs; then evaluation and cross-checks. The commits:

  | Round | Pre-registration | Source | Gate | Freeze |
  |---|---|---|---|---|
  | R116 | 755b0e8 | 2e8b53d | c8bd391 | 61b7e78 |
  | R117 | 97bc78f | ae50c98 | 2c7e4bf | bb0e108 |
  | R118 | 707b8af | 21e333a | none (synthetic) | 266773b |
  | R119 | 9ba6dd7 | d96e94e | 421dfd5 | b72038d |
- **Resources.** Every job is COMPLETE under `audit/run_bounded_agg.py`, with zero retries.
- **K4 input.** R116, R117 and R119 read K4 only through their registered target scripts, after their gate GO was
  pushed. R118 has no K4 input.
- **Cross-checks** (post-freeze, independent references): 0 disagreements in every one.
  - R116: ref115 on 708 K4 cells, plus 300 order-3 vectors.
  - R117: brute-force ref112 on **all 768** K4 cells.
  - R119: brute force on a 312-cell sample.
- **CI.** Each round has a workflow that re-checks the manifests, recounts from the frozen inputs, and repeats part of
  the reference check. The R118 and R119 checks were run locally before the PR.
- **Guardrail check:** PASS.

Independent review: NONE. One model (Claude Code) built and ran all four. They join audit batch C.

## Summary
- **R116 (P8, L204): linear-recurrence keys with two free alphabets.**
  - **Order 1 is EXCLUDED_DROP for K4,** 26 of 26 vectors. That covers every progressive and multiplicative key, with
    both alphabets free.
  - **Order 2:** 668 of 676 vectors are excluded, and 8 are OPEN. Fibonacci, period 2 and linear progression are
    excluded.
  - **Orders 3–4:** WEAK, as registered.
  - **No lead.**
- **R117 (P6, L205): free-alphabet Slidefair with exact same-column handling.**
  - **All 768 cells are excluded,** including any key. 356 are also excluded with one bad pair.
  - R108's no-same-column assumption is no longer needed.
  - **No lead.**
- **R118 (P9, L206): blind solvers on masked English (synthetic).**
  - Germanic/Dutch-like respelling is **SENSITIVE** for both S105 (−72.5 points) and R59's solver (−75 points).
  - Telegraphese is ROBUST.
  - So the K4 NO_SIGNAL of R111 (L199) and of R59 (L149) **does not cover respelled plaintext**.
- **R119 (F2 rank 1, L207, exploratory): a route, then Slidefair, over L161's 26 routes.**
  - **8 routes are excluded in every cell.**
  - **Periods 1, 2 and 4 are excluded for all 26 routes,** and period 3 for 25.
  - The other 18 routes are PARTIAL, within the shuffle range.
  - **No lead.**

## Points for the auditor
1. **R116's mod-2 / mod-13 split.**
   - X115 solves each coefficient vector's system separately mod 2 and mod 13, and combines the forced-equal pairs.
   - The reference ref115 does not split (R115 point 1).
   - The superset model (the recurrence imposed from the first crib position) makes exclusions conservative.
2. **R117's 16 cells moving from DROP to exact-only.**
   - These are cells where a same-column branch, combined with one dropped pair, opens a way out.
   - They should be checked against R108's DROP list: VIG/BEAU_0_0_1 and _1_1_1, at p 7, 9, 18 and 21.
3. **R117's exclusion is stronger on K4 than on shuffles.**
   - K4 leaves 0 cells open, against a shuffle median of 224.
   - R108 saw the same. It is a property of K4's ciphertext letters at the crib positions, not a lead. The LEAD flag
     concerns *more* open cells.
4. **R118's rule set G is a single strong respelling.**
   - The label tells you about this rule set only.
   - The R arm ran on each plant's own convention, so it measures scoring robustness, not convention identification.
5. **R119's null.**
   - R119 reuses R117's 200 frozen shuffles, because a fixed route applied to a uniform shuffle is again uniform.
   - The family-wise false-alarm rate of its LEAD flag (up to about 13%) was stated before the run. The flag did not
     fire.
6. **Shared code.**
   - R119 imports R117's frozen `scan_input` and `ref_verdict`.
   - R116 imports R115's X115 and ref115.
   - R117 and R119 use R112's X112 and ref112 unchanged.
   - Every reference still differs from its check in elimination method and branch handling.
