# R93 independent review and narrow ledger promotion

Affected ledger IDs: L182
Promotes: L182
Validation:
- My own partial-bijection proof.
- A separately coded checker that re-checks every omission from scratch, with step-event offsets.
- A synthetic gate (GO): 33,483 complete-key toy lists (q 2–5), plants at all 145,728 labels, 27,324 error checks,
  24,000 second-implementation comparisons, a planted-positive sensitivity check, and every R93 scope count
  reproduced.
- One target replay on all 201 frozen inputs, with byte-for-byte regeneration of the shuffles: every per-input count
  equals `r93/k4/AGGREGATES.json`, and all are zero.
- Plan 44dfb52, source b33e248 and gate 529e90f were published before the target replay, which was frozen at
  5771533.

Independent review: YES Claude Code, reviewing ChatGPT's R93. Claude Code subtasks are one review.

## Decision
Promote **L182's finite exact exclusion only** to INDEPENDENTLY VERIFIED: zero feasible wirings for all 145,728
labels (n 5–96, every nonzero boundary phase, d ±1, 16 contact pairs) on K4.
- This holds with all 24 published observations and with any one omitted, so it covers one wrong published plaintext
  letter, or one ciphertext substitution at a published position, separately.
- All 200 frozen shuffles are also zero.
- With L181 (independently verified by ChatGPT), every nonzero boundary phase of this rotor is independently verified
  as excluded through period 96. The zero-phase labels have independent review only for n ≤ 4 (R92's review). R87's
  n 5–96 zero-phase labels in L176 remain single-model.

**Cost:** gate 9.3 s wall / 9.2 s CPU / 35 MB; target 13.3 s / 13.2 s / 30 MB. Both COMPLETE under
`audit/run_bounded_agg.py`, with zero retries.

The signed review, evidence and limits are in `r93/audit/independent_review/`. Nothing in this review alters R93's
frozen files.
