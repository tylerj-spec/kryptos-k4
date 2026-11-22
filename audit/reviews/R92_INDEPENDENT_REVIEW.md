# R92 independent review and narrow ledger promotion

Affected ledger IDs: L181
Promotes: L181
Validation: Independent conflict-graph proof and exhaustive toy oracle; full
replay of all 192 R92 labels and all 128 registered R87 n<=4 zero-phase labels
on K4 and all 200 frozen shuffles; saved forward witnesses, gate/evaluation
arithmetic, hashes and public commit ordering.
Independent review: YES ChatGPT, reviewing Claude Code's R92. ChatGPT subtasks
constitute one review and do not supply additional independent votes.

The signed evidence and its explicit limitations are in
`r92/audit/independent_review/REVIEW.md`. The machine-readable evidence is
`r92/audit/independent_review/REVIEW_RESULTS.json`, with the sole target job's
aggregate resource log alongside it. The review plan was published at
`76d9a013c3dd3c2aff9c0144c8a9ebf22ba6d361`, and the final checker and synthetic
PASS were published at `567f418961cc18847207008468679115074f4c93` before that job.

## Decision

Promote **L181's finite exact exclusion only** to INDEPENDENTLY VERIFIED.
There are zero feasible wirings for every one of its 192 phase/contact/direction
labels, with all 24 prescribed observations or with any one observation
omitted. The independent replay also verifies the registered 128 zero-phase
labels for n=1..4, completing independently checked all-phase coverage through
period four. It does not promote the remaining 2,944 labels or other claims
in L176.

The audit independently checked 2,015 saved candidate re-encryptions, 52
positive/extra truth witnesses and 101 hash-manifest entries. Saved arithmetic
gives 47/48 confident recoveries to at least 95/97 letters, 44/48 exact texts,
44/48 used-contact wiring agreements and 0/150 confident negatives. The saved
K4 result remains NO_SIGNAL: 50/200 shuffles are at least as high, giving
51/201 with the add-one convention. No optimizer, original full letter-model
rescoring, historical execution isolation or raw-book freshness certification
was independently rerun.

The target audit completed in 1.754 seconds wall and 1.628 seconds aggregate
CPU, with 34.8 MiB sampled aggregate RSS, within its 300/180-second and 1,024-MiB
limits. It had zero retries. The original disclosed development budget overrun
remains a deviation.

## Additive corrections

`r92/audit/independent_review/SCOPE_CORRECTIONS.md` supplies the derivations.
RX2-O with identity second wiring embeds R92's phased single rotor. Distinct
schedules need not define disjoint cipher functions. The remaining nonzero
phases for n=5..96 contain **145,728** labels, not 145,920. The blind statistic
is a maximum from a fixed pruned pipeline, not an exhaustive letter-model
optimum. Exact compatibility is independent of the language of the unknown
text. The one-error conclusion covers one observation error, not an insertion,
deletion, lost update or simultaneous errors at different observed positions.

These corrections are additive. Original frozen source and evidence are
unchanged. R92 scores, settings and constraints are not inputs to the new
two-rotor development work.

**Signed: ChatGPT, 21 November 2026 (America/Chicago).**
