# R94: structural two-rotor development completed without recovery

Date: 22 November 2026 (America/Chicago).
Status: **COMPLETE_DIAGNOSTIC / SOLVER_NO_POWER on the spent panel**.
Independent execution review: **NONE**. This is new ChatGPT work; internal
ChatGPT source/result checks do not supply a different-model review.

## Decision

The one registered invocation completed all mathematical checks, both finite
unknown-wiring versions, the conditional diagnostics and the archived-result
replay. **Neither version recovered any of the 48 practice messages to the
registered >=95/97-letter threshold**, including among all saved final states.
This closes the two-version R94 development attempt. The two-rotor cipher
family remains OPEN; there was no K4 input, new holdout or formal gate.

The experiment supplies a stronger diagnosis than a search failure alone:
the order-four score admits wrong plaintexts above the true text in 39 of the
48 tested one-swap neighborhoods. Even the separately supplied-one-true-wiring
conditions recover zero cases at the >=95 threshold. A conclusion that only
coupled two-wiring search remains would therefore be unsupported.

## Prospective publication and execution

The preregistration was published at
`567f418961cc18847207008468679115074f4c93`. After the user explicitly approved
the reviewed public payload and bounded execution, the complete reviewed source
was published and fetched at
`3e781d57994a617610db943ea57438759dc6b4ce`. The coordinator confirmed publication
before the sole invocation. All 38 protocol entries and pinned package versions
match the source package. No source, QA or protocol file changed for execution.

The sole command was:

```sh
python3 -I audit/run_bounded_agg.py --manifest r94/QA_MANIFEST.json --log r94/RESOURCE_LOG.json -- python3 -I r94/run_all.py
```

| Resource | Observed | Registered limit |
| --- | ---: | ---: |
| Wall seconds, entire invocation | 6.766 | 1,800 |
| Aggregate CPU seconds | 6.633 | 1,800 |
| Sampled aggregate RSS, MiB | 68.0 | 2,048 |
| Numerical workers | 1 | 1 |
| Retries | 0 | 0 |
| Newly computed saved states | 999 | 1,100 |

The wrapper returned COMPLETE with exit code zero. Phase wall/CPU times were
0.031/0.031 seconds for mathematical checks, 0.343/0.343 for A,
4.635/4.635 for B, and 1.000/1.000 for diagnostics/archival replay. Every phase
completed within its additional cap. The algorithms' finite loops and stopping
conditions ended the run; the unused resource allowance does not authorize
additional versions, restarts or a second invocation.

RSS is sampled over the process group and can miss sub-sample peaks or count
shared mappings more than once. The wrapper also imposes the per-process
address-space limit. These are the declared resource semantics, not a claim
about exact instantaneous physical-memory use.

## What the two versions tested

Version A alternates exact conditional unigram assignments for the two inverse
wirings. Each whole-wiring step solves its additive objective; alternation is
not a global optimizer. Version B starts from the same A final states, uses
order-four assignment/cycle proposals and a fixed legal-swap fallback, and
accepts moves only under the actual order-four score. Its assignment is exact
for the surrogate, not for the full higher-order objective.

Both versions used eight starts on each of the existing 48 supplied-structure
cases. There were no new texts or unknown-structure catalog search. All eight
turnover cells, including the static-second-rotor cell, have six cases and zero
recovery for both versions.

| Unknown-two-wiring measure | Version A | Version B |
| --- | ---: | ---: |
| Cases completed | 48/48 | 48/48 |
| Saved final states | 384 | 384 |
| Top-ranked >=95/97 recovery | 0/48 | 0/48 |
| Any retained >=95/97 recovery | 0/48 | 0/48 |
| Any final-state >=95/97 recovery | 0/48 | 0/48 |
| Exact top-ranked recovery | 0/48 | 0/48 |
| Maximum top-ranked letter matches | 13/97 | 19/97 |
| Maximum over all saved final states | 23/97 | 19/97 |
| Median top-ranked letter matches | 8/97 | 6/97 |

All final states have scalar forward-encryption witnesses. The retention views
contain all eight distinct final plaintexts per row; the zero-recovery result
therefore does not arise from discarding a recovering final state. Intermediate
states were not all retained, so the record does not establish a matching-letter
maximum over every visited state.

A made 3,398 assignments and accepted 2,428 updates, below its 12,288-assignment
bound. B performed 5,038 block updates: 2,907 assignment/cycle acceptances,
809 best-transposition acceptances and 1,322 no-improvement updates. Its
4,110,787 scored strings include non-permutation counterfactuals used to build
the surrogate; those are not cipher candidates. The block-update count is
below the registered 18,432 maximum. The source enforces each block's finite
score-call bound.

Higher order-four score did not produce near-correct unknown-wiring text on
this panel. In particular, B's median top-ranked letter agreement is lower
than A's. This is a descriptive comparison of the frozen versions, not an
estimate of a general success probability.

## Truth-assisted diagnostics, kept separate from recovery

Both unknown-wiring files closed and their hashes were written before the
program opened the public spent truth. The saved event indices are A close
54, B close 106 and truth open 108, counted from zero. Postrun hashes match the
pre-truth receipt. This is the registered file-read-order convention; the
process had ordinary filesystem access and does not claim operating-system
blind isolation.

The following conditions deliberately receive one true inverse wiring. They
are diagnostic assistance, not unknown-two-wiring recoveries or a substitute
formal gate.

| Supplied true inverse wiring | Version | >=95/97 | Exact | Median matches | Maximum matches | Wrong found text above truth's order-four score |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| U | A | 0/48 | 0/48 | 49 | 65 | 0/48 |
| U | B | 0/48 | 0/48 | 51.5 | 94 | 6/48 |
| V | A | 0/48 | 0/48 | 43 | 72 | 0/48 |
| V | B | 0/48 | 0/48 | 45.5 | 93 | 3/48 |

Truth's order-four score exceeds the found B state in 42/48 true-U cases and
45/48 true-V cases. Those are concrete optimization gaps to a known feasible
point. The remaining six and three cases are concrete scoring counterexamples.
No conclusion of global optimality, uniqueness or information-theoretic
impossibility follows from either observation.

At the true pair, the registered local check evaluated all 650 individual
transpositions across the two blocks for each row: **31,200 legal neighbor
scores**. In **39/48 cases**, at least one distinct wrong plaintext scores
above the true plaintext. The per-row counts sum to 117 wrong-text instances.
The best saved wrong neighbor has 90–96 matching letters: **25 of the 39 are
below 95**, while 14 remain near-correct at 95–96. Thus the observed defects
include both exact-text misranking and misranking across the chosen recovery
threshold. This is a finite local counterexample panel, not exhaustive search
or a universal claim about language models.

The 999 newly saved states comprise 768 unknown-wiring finals, 192 conditional
states and 39 best-neighbor witnesses. Duplicate retention views are not counted
as newly computed states.

## Mathematical and archived-evidence checks

The invocation's mathematical checks passed: 24 exhaustive conditional
assignment cases, 54 cycle-parameterization checks, 24 independent reference
round trips, 24 scalar/batch score comparisons and 144 replacement-objective
checks. These establish the tested implementation invariants. They do not
supply recovery or false-positive evidence.

The archived witness/count replay independently checked 1,536 v2 and 384 v3
saved final restart states, plus the retained forward witnesses. Neither
archive has a saved state at >=95/97; the maxima are 20/97 for v2 and 18/97
for v3. Top-ranked maxima are 15/97 and 12/97. The v1 designation remains
INCOMPLETE with no saved candidate recovery rate.

All 17 committed resource logs, including failed jobs, were recounted:

| Archived version | Logs | Sum of wall seconds | Sum of aggregate CPU seconds |
| --- | ---: | ---: | ---: |
| v1 | 4 | 681.216 | 1,337.784 |
| v2 | 7 | 705.573 | 1,377.248 |
| v3 | 6 | 639.875 | 1,254.518 |
| Total | 17 | 2,026.664 | 3,969.550 |

Each version's committed sum falls below its own allowance. This does not
prove there was no unlogged work or that the historical jobs shared a single
cumulative enforcer. No old optimizer or original order-five/order-six score
was rerun. R94 uses the declared, pinned R91 order-one-through-four model.

## Scope and next decision

This work order terminates at SOLVER_NO_POWER on the spent panel. Do not enlarge
its starts or budgets after seeing the result. The observations justify
requiring both better scoring behavior and demonstrated conditional recovery
before another full two-unknown-wiring attempt. The normalized single-cycle
relation remains a structural design fact; R94 did not implement a separate
cycle-based solver, so that avenue is neither tested nor excluded here.

A future proposal needs a separately reviewed work order and its own finite
development bounds. It should first demonstrate conditional recovery and
measure wrong-text scoring counterexamples, then establish full unknown-wiring
recovery, and only subsequently use fresh sealed controls with negative
calibration. These are research prerequisites, not authorization of another
R94 version or a K4 run.

Evidence: `development/RESULT.json`, `RECOVERY.json`,
`CONDITIONAL_DIAGNOSTICS.jsonl`, `CONDITIONAL_SUMMARY.json`, `ARCHIVED_REPLAY.json`,
`TESTS.json`, `EVENTS.jsonl`, both version files and their pre-truth receipt;
`RESOURCE_LOG.json`; `audit/EXECUTION_RECEIPT.json`; and
`audit/RUN_FROZEN.sha256`. The raw output manifest remains unchanged.

**Signed: ChatGPT — completed bounded development result; no cipher exclusion,
fresh-gate pass or independent-model promotion.**
