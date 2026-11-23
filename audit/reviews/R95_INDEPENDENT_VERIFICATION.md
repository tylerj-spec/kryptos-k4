# R95 independent verification: GO on the registered score check (1/48), by different-model replication

Affected ledger IDs: L184
Validation:
- Plan a09f16b, source 5d9fae2 and Amendment 1 7b27d64 were published before computation; outputs frozen at 03ef90f.
- The model was rebuilt to R95's registered digest e9c0848f… with a correctly rounded `log10f`.
- All 48 true and 31,200 neighbor forward witnesses pass.
- R95's chronology and its 22 protocol hashes are checked.
- The recovered primary shard D_000 agrees 650/650.
- **Primary endpoint:** order-5 candidate 1/48, order-4 baseline 32/48. Baseline wrong-text-above-truth is 39/48,
  equal to R94.
- **Runs:** build 2.3 s wall / 2.1 s CPU / 219 MB; run 4.8 s / 4.7 s / 200 MB. Both COMPLETE under
  `audit/run_bounded_agg.py`, with zero retries. No K4 input.

Independent review: YES Claude Code (different-model replication of ChatGPT's R95 question). R95's own primary
evidence remains unpublished, and its registered same-model verifier was not run.

The signed review is `audit/reviews/r95_independent/REVIEW.md`. Under R95's fixed rule the order-5 objective passes
the objective check (GO_FOR_CONDITIONAL_DEVELOPMENT).
- That permits only a separately specified conditional-recovery work order (charter §6.3).
- It does not authorize any K4 run, and it excludes no cipher family. RX2-O remains OPEN.
