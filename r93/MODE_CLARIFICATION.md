# R93 prospective mode clarification: exact-checker correctness

## Authorization and scope

On 21 November 2026 (the user's displayed date) the user requested the remaining follow-ups after merged
PR #104, explicitly including the wider published-letter timing check after
review and registration. The coordinating agent confirmed that this authorizes
an **exclusion-only audit**, rather than commissioning a blind decoder for this
task. R93 implements that instruction as **CRIB_ASSISTED / AGGREGATE_ONLY**.

This is a prospective clarification for R93 only. It does not edit or weaken the
frozen R92 registration, `audit/NEXT_STEPS.md`, the rotor design, or any BLIND
experiment requirement. It does not treat R92's narrow recovery gate as evidence
of recovery over the wider R93 domain.

## The policy distinction is explicit

G0 and G4 of `audit/FUTURE_TEST_GUARDRAILS.md` allow narrowly stated crib-assisted
mathematical exclusions backed by independent code or proof and exhaustive toy
controls. G1 and G2 also contain unqualified sealed blind-recovery requirements.
An exact compatibility checker is not a decoder and cannot honestly satisfy
unknown-family, key, or plaintext recovery requirements.

For this user-authorized exact-only round, the prerequisite is therefore named
**EXACT_CHECKER_CORRECTNESS**, with its own preregistered all-or-nothing tests.
Its `GO` means only that the specified mathematical compatibility test passed
those tests. It does **not** mean blind recovery, family recognition, language
power, calibration of a plaintext candidate, or permission for an RX2 search.

The gate requires a complete-key brute-force toy oracle independent of the
production criterion; all-parameter boundary plants; independently implemented
97-character forward/inverse checks; distinct plaintext, ciphertext and state
error tests; false-exclusion and false-feasibility challenges; exact schedule
accounting; pinned sources; and successful aggregate resource logs. Its complete
criteria are in `PREREGISTRATION.md`.

The existing QA schema supports `mode: crib_assisted` and requires a prior `GO`
gate artifact but does not encode the gate type. R93 therefore adds explicit
`gate_type: EXACT_CHECKER_CORRECTNESS` and
`blind_recovery_certified: false` fields to both its QA manifest and gate result.
No guardrail code change or fabricated recovery result is needed. The type and
limitations must remain visible in all summaries.

## Required separation and publication

1. Publish this note and the preregistration before formal validation or target
   input. Publish the source/protocol manifest and QA manifest in a later commit.
2. Run the declared synthetic correctness gate. Publish its complete result,
   source hashes and resource log in a separate commit. A failure blocks K4.
3. Only after the coordinator confirms the gate commit is pushed, run the exact
   aggregate audit under its declared cap. Freeze its inputs, aggregates and
   provenance before interpreting the counts or changing the ledger.
4. Publish a separate signed result review. This ChatGPT implementation and its
   same-model internal review are **Independent review: NONE**. A future
   independent-model review is required for an independently verified promotion.

No decoded plaintext, completed or partial wiring, candidate ranking, surviving
structural label, strength score or clue-conditioned setting selection is
published. R93 outputs must not enter RX2 engineering, a blind candidate
generator or another target-selection procedure. Nonzero feasible counts mean
only `COMPATIBLE / OPEN` for this necessary check, never a lead or a solution.

All original BLIND gate, isolation, output-freeze and post-freeze clue-check
requirements remain unchanged for any future recovery experiment.
