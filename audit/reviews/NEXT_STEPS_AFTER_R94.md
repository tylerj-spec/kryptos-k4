# Next steps after the R92–R94 closeout

Affected ledger IDs: L181, L182, L183
Validation: Completed R92 independent review; frozen R93 exact result; completed
R94 development and bounded postrun review. The decisions below follow those
outcomes and do not alter their registrations or frozen evidence.
Independent review: PARTIAL. R92 has the separate signed independent review.
R93/R94 remain same-model work with independent-model review NONE.

Date: 22 November 2026 (America/Chicago).

## Decisions now in force

1. **Close the requested R92 independent review.** L181's finite exact
   exclusion qualifies for promotion. The original blind result remains
   NO_SIGNAL and its limitations/development overrun remain disclosed.
2. **Close the deferred R93 timing audit.** All 145,728 registered labels fail
   both exact and single-observation-omission compatibility. Do not rescan this
   unchanged domain. Its independent-model review is still outstanding.
3. **Stop the R94 two-version procedures.** Both finished with zero recovery
   on the spent panel. Do not convert unused resource ceilings into additional
   restarts, a third version or a K4 attempt. The cipher family remains open.
4. **Keep the earlier R82/PTAK decisions parked.** All R91 linked-key cells
   lie in archived R83 LX, and the unchanged long-lag PTAK optimizer failed its
   prerequisite power screen. Nothing in R93/R94 reopens those old work orders.

The earlier `audit/NEXT_STEPS.md`, multi-rotor design and PR #104 refinement are
hash-pinned historical work orders. They remain unchanged. This additive note
and `CURRENT_STATUS.md` identify the active decisions.

## Priority 1: independent-model R93 review

Prepare a different-model reviewer to assess L182 before promotion. Required
work is the exact formula/error proof, independent feasibility implementation,
complete registered label coverage and aggregate replay, not another English
solver. Preserve the distinction between a second code path and an independent
model. The current internal postrun verifier checks saved arithmetic and
provenance; it does not independently regenerate R93's complete target scan.

The review should publish its plan and source before target computation, use a
different consistency formulation, validate it with complete-key toy oracles
and full-size plants, and record explicit aggregate wall/CPU/RAM limits. A
reasonable ceiling is the existing R93 target allowance of 1,800 wall seconds,
1,200 aggregate CPU seconds and 512 MiB, with zero automatic retries. Its exact
implementation and synthetic throughput gate must be frozen first. Emit only
compatibility counts and evidence metadata; no plaintexts, completed wirings,
surviving labels or input to a blind solver.

The source, gate and target freeze commits are respectively `3e781d5`,
`2621a5e` and `542165b`; full SHAs and commands are in `r93/RESULT.md`.
If an independent reviewer disagrees, preserve the current files and add an
erratum. No independent-model reviewer has yet performed this task.

## Priority 2: a better objective and conditional solver before joint search

R94 establishes two distinct obstacles. Its order-four objective prefers a
wrong local plaintext in 39/48 cases, with 25 saved counterexamples below the
chosen recovery threshold. Its conditional optimizer also fails when one full
true wiring is supplied. Increasing the same joint search's runtime alone
does not resolve either finding.

The next development proposal should select and freeze both its score and its
optimization method before execution. The normalized relation
`G_delta=H^delta F`, where H is a single 26-cycle, is available for a different
parameterization; R94 did not implement a cycle-based solver. Reparameterizing
is not itself evidence of better recovery or identification.

Proposed finite decision sequence for a future work order:

| Stage | Benchmark and bound | Suggested continuation bar |
| --- | --- | --- |
| Objective check | At most two fully specified scores on the existing 48 spent cases and their fixed 650 legal one-swap neighbors each | Report exact-text misrankings separately; at most two cases with a below-95 competitor scoring above truth before advancing |
| Conditional recovery | At most two fixed optimizer variants, 48 true-U and 48 true-V conditions, with seeds/starts/retention frozen | At least 44/48 >=95 recovery in each condition and at least 5/6 in each turnover cell |
| Both wirings unknown, supplied structure | One selected method on the same 48 spent cases | At least 44/48 top-ranked >=95 recovery and at least 5/6 per cell; record candidate recall separately |
| Fresh full-pipeline gate | New concealed texts/keys, unknown structural labels, registered negative calibration, model-overlap/key-equivalence handling and whole-search throughput | Must satisfy a separately reviewed complete gate before any K4 search |

These are proposed development selection bars, **not an executed or complete
preregistration**. Objective definitions, source/corpus provenance, exact
algorithms, keys/labels, seeds, retention and failure rules still need to be
fixed in that future work order. Both positive-only spent-data success and
truth-assisted conditions remain development evidence.

A proposed development ceiling is one cumulative 1,800-wall/1,800-CPU-second,
2,048-MiB invocation, one worker, at most two versions and zero automatic
retries. Each stage must have an explicit smaller cap inside that total; it
cannot reset the allowance. Stop at the first failed continuation bar and
record SOLVER_NO_POWER or INCOMPLETE as appropriate. These limits do not extend
R94 or authorize another invocation of its runner.

## Avoid redundant period expansion

Before proposing periods above 96, audit finite-length clock equivalences
analytically. Over 97 characters, such a period can produce at most one step
after the initial phase under the current position-only rule. This observation
may reduce future scope accounting, but this note makes no new exclusion for
that domain. A larger number of parameter labels is not automatically new
cipher-function coverage.

No current result identifies K4's method, key or plaintext. The next useful
milestones are an independently reviewed exact scope and demonstrated solver
power on fresh controls, not another unqualified family-exclusion claim.
