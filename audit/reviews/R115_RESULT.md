# R115: L203, exact check for linear-recurrence keys with two free alphabets (synthetic), with desk catalogues F1 and F3

Affected ledger IDs: L203

Validation:
- **Order of commits:**
  - pre-registration ad3a123, pushed alone, after the F3 catalogue (ad0fca6);
  - source abc0ac0;
  - run v1 INCOMPLETE, recorded in 4a09125;
  - Amendment 1 (Tyler: "Approve (Recommended)") in 5056cb1;
  - run v2 frozen in 55d9589;
  - then the result note.
- **Resources.** v2 is COMPLETE under `audit/run_bounded_agg.py`: 898 s, 585 MB, zero retries.
- **No K4 input.**
- **CI.** `r115-linrec.yml` re-runs everything and compares every result except timings.
- **Guardrail check:** PASS.

Independent review: NONE. One model (Claude Code) built and ran it. It joins audit batch C.

## Summary
**R115 (L203).** X115 is an exact crib check for a key from an affine linear recurrence mod 26, with both alphabets
free.
- **Correctness:**
  - structure: 0/300 failures;
  - soundness: 0/400 plants, and 0 wrong-letter plants at DROP;
  - against an independent reference: 0 disagreements on 6,828 cells.
- **Chance exclusion:**
  - **0.98 at order 1** (ROBUST; 0.89 with one letter dropped);
  - **0.84 at order 2** (TESTABLE);
  - 0.48 and 0.16 at orders 3 and 4 (WEAK).
- **Next step.** The K4 run is proposed as P8, for approval with P6.

**The catalogues:**
- **F3** ranks the key-generator gaps in the ledger. Rank 1 is R115.
- **F1** sets out two readings of the clues under a masking layer. It shows which exact checks survive which masks:
  - checks that see plaintext letters only through their own free alphabet (L90, L92, X115, R109 with F = A)
    survive any mask that keeps the crib letters' equality pattern;
  - a merge of two crib letters, such as C/K, could cause false exclusions.

  It proposes a masking-scope sentence for every exact round, and P9, a synthetic robustness check of the blind
  solvers.

## Points for the auditor
1. **The mod-2 / mod-13 split of a.** X115 solves the mod-2 system once per a mod 2, and the mod-13 system once per
   a mod 13, then combines them. The reference does not split; it solves for each full a.
   - This rests on the crib equations mod p depending only on a mod p, which holds because every coefficient enters
     linearly.
2. **Shared code.**
   - X115 imports R112's `Sys` (row reduction and signatures). The reference does not use it.
   - Both use the same collision rule, implemented separately.
3. **The superset model.** The recurrence is imposed from the first crib position on, not from position 0.
   - Exclusions therefore cover keys generated from position 0 as well.
   - OPEN cells may be unreachable from position 0 when a_L is not invertible.
4. **Run v1.** It crashed in the report step after all four computations, and nothing was written. The amendment
   changed three lines of `main()` and left the seed unchanged.
5. **The dev estimate at order 3 was low.** It was 0.18 on 6 messages, against the registered 0.48 on 40. Power
   varies widely between masks, so K4's power must come from shuffles in P8.
6. **F1's claim on false exclusions under merges** (§2) is a scope argument, not a computed result. It should be
   checked.
