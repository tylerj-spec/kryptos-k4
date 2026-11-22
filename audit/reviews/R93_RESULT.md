# R93 exact-only result and scope review

Affected ledger IDs: L182
Validation: Published preregistration, source and complete exact-checker
correctness gate before the sole target run; 145,728 labels on each of 201
inputs; complete output/resource freeze before interpretation; both freeze
manifests and aggregate accounting verified against published bytes.
Independent review: NONE. ChatGPT implementation and execution, reviewed by
same-model subtasks. The independent synthetic oracle is a separate code path,
not another model. No independent-model promotion is requested.

## Disposition

Record **EXACT_SCOPE_EXCL** for the all-correct and single-observation-error
conditions within R93's registered finite scope. K4 has **zero EXACT-compatible
labels, zero DROP-compatible labels and zero label/omission pairs** among all
145,728 labels. Every one of the 200 frozen shuffles also has zero for all
three counts. These are descriptive compatibility counts; no p-value, strength
ranking or candidate claim is made.

The scope is one position-only stepping rotor with arbitrary 26-symbol wiring,
16 independently selected AZ/KRYPTOS/PALIMPSEST/ABSCISSA contact pairs,
`s_i=d*floor((i+r)/n)`, n=5..96, r=1..n-1 and d=+/-1, in place. All labels,
including finite-clock overlaps, were retained. The 145,728-label count is the
correct remainder after R92's 192 labels; 145,920 would include those again.

The full outcome, proof, caveats and evidence hashes are in `r93/RESULT.md`.
Primary machine-readable evidence is `r93/k4/AGGREGATES.json`, frozen at
`542165b77806917d17dd4f3f8314685fd2d1e55a` before this interpretation.

## Gate, resources and integrity

The gate type is explicitly **EXACT_CHECKER_CORRECTNESS**, with
`blind_recovery_certified=false`. It passed all 141,793 exhaustive toy-oracle
cases, 8,832 full-size plants, 44,160 plant/error setting checks, 17,664
forward/inverse round trips, both bulk-catalog boundary plants, adversarial
cases and the registered resource forecast. The plant panel covers every
period and the three preregistered phases per period, not every nonzero phase.

The gate completed once in 6.011 seconds wall, 5.943 aggregate CPU and 92.6 MiB
sampled aggregate RSS under its 180/120-second and 512-MiB caps. The target
completed once in 6.273 seconds wall, 7.972 aggregate CPU and 94.5 MiB under
1,800/1,200 seconds and 512 MiB. No source change, retry or budget extension
occurred.

Publication order is registration `567f418`, source `3e781d5`, gate `2621a5e`,
target freeze `542165b`, then this review. The driver validates source/gate
hashes and commits before target input. The 15-entry gate freeze and 21-entry
target freeze match both local and published bytes. All 201 expected IDs have
145,728 settings and satisfy the exact/drop/deletion-pair count inequalities.
Totals account for 29,291,328 setting/input calls and 732,283,200 logical
exact-or-one-deletion decisions, using Python integer accumulation.

## Interpretation boundaries

The partial-bijection criterion is necessary and sufficient for a wiring at a
fixed structural label. The one-deletion mask covers one wrong reported
plaintext symbol or one fixed-length ciphertext substitution separately; it
does not cover insertion/deletion, altered alignment, lost updates or
simultaneous errors at different positions. Exact compatibility does not depend
on English, but the observation symbols must be correct within the declared
error tolerance.

No decoder, partial/completed wiring, surviving structural setting list,
plaintext ranking or candidate was emitted. The legacy positive QA candidate
ceiling of 1 is unused; stricter limits of zero decoded candidates and zero
surviving-setting outputs apply. Aggregate records are separately limited to
201. No global guardrail code was changed.

Combining the recorded R87/R92/R93 domains accounts for all boundary phases
through period 96 for these fixed contacts and directions. This does not
independently certify the unreviewed remainder of R87 or promote R93. Other
alphabets, stepping laws, transpositions, multiple rotors, n>=97 and wider
error models remain outside this result. R93 outputs do not enter RX2 work.

**Signed: ChatGPT, 22 November 2026 (America/Chicago).**
