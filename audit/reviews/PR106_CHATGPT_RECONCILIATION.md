# PR #106 review and reconciliation with active ChatGPT work

Affected ledger IDs: none changed; L181, L182 and L183 are discussed only at their recorded scopes.
Validation: documentary comparison against the pinned sources below; no new cryptographic computation.
Independent review: YES ChatGPT — review of Claude's planning document only, not mathematical re-derivation or ledger promotion.

Date: 22 November 2026 (America/Chicago).

PR #106 is already merged; this is an additive planning correction.
The immediate 25-meter target is to finish the existing R95 evidence chain.
R93's different-model review proceeds separately.
No R95 pass/fail or new K4 exclusion is claimed.
Tyler has explicitly authorized publication to Git; no further publication decision is needed.

## 1. Scope and authority

Tyler requested: “Can you review the recent planning doc in pr106. Ensure the work you were doing is
incorporated into it”, followed by “You have permission to push anything to git”.

The reviewed charter was added by PR #106 and merged as
`a8f29c0b94c9a7f6fbfbe6252a54e2e162358bf5`. Its research snapshot stopped at the PR #105 merge,
`3a48dec3414560c0d26de6b1558e3dbf05ab772c`. R95 was already a separate active workstream.
The adopted charter's own precedence table makes `r53/BLIND_RULES.md`,
`audit/FUTURE_TEST_GUARDRAILS.md` and `k4kit/CLAUDE.md` controlling; explicit owner instructions
take precedence over repository defaults.

This review changes only `audit/RESEARCH_CHARTER.md`, the current portion of `CURRENT_STATUS.md`
and this note. Original proposal notes, historical status snapshots, frozen evidence, registrations,
solver/checker code, workflow rules and ledger rows are preserved. No experiment, optimizer, target
checker, K4 candidate generation or external solution submission was performed.

ChatGPT reviewed Claude's strategy document. Same-model agents separately checked prior-work coverage,
R95 provenance and the revised wording; they count as one ChatGPT review, not multiple independent
reviewers. Nothing here promotes R93, R94 or R95, or extends the existing finite R92 promotion.

## 2. Missing active work: R95

### Repository evidence

The inspected branch is
[`chatgpt/r95-fixed-score-challenge-20261122`](https://github.com/tylerj-spec/kryptos-k4/tree/chatgpt/r95-fixed-score-challenge-20261122),
pinned for this review at
[`8f59313c7d4fa6327e0cee41a39f092ebbeb23aa`](https://github.com/tylerj-spec/kryptos-k4/commit/8f59313c7d4fa6327e0cee41a39f092ebbeb23aa).

| Stage | Published commit |
| --- | --- |
| Registration | `c02b7a92404c2c18d41e7d2a13d75099ab8764bc` |
| Source and separately coded verifier | `f81ceaf79e41f161efb41a3127ba9afdf6ecb194` |
| Executed source, including QA schema correction | `b3471306d15b61489d9630b4fee079d89c8d1b6f` |
| Interrupted-publication record and first recovered shard | `8f59313c7d4fa6327e0cee41a39f092ebbeb23aa` |

Primary sources on that pinned commit:

- [R95 work order](https://github.com/tylerj-spec/kryptos-k4/blob/8f59313c7d4fa6327e0cee41a39f092ebbeb23aa/r95/WORK_ORDER.md)
- [R95 preregistration](https://github.com/tylerj-spec/kryptos-k4/blob/8f59313c7d4fa6327e0cee41a39f092ebbeb23aa/r95/PREREGISTRATION.md)
- [R95 execution handoff](https://github.com/tylerj-spec/kryptos-k4/blob/8f59313c7d4fa6327e0cee41a39f092ebbeb23aa/r95/EXECUTION_HANDOFF.md)
- [R95 interruption status](https://github.com/tylerj-spec/kryptos-k4/blob/8f59313c7d4fa6327e0cee41a39f092ebbeb23aa/r95/INTERRUPTION_STATUS.json)
- [Publication-interruption review](https://github.com/tylerj-spec/kryptos-k4/blob/8f59313c7d4fa6327e0cee41a39f092ebbeb23aa/audit/reviews/R95_PUBLICATION_INTERRUPTION_20261122.md)

The work order expressly defines “25m” as the 25-meter immediate-priority target, not a 25-minute cap.
R95 compares one fixed rebuilt order-five language objective against the lower-order baseline on
48 spent RX2-O practice cases and their complete 31,200 legal one-swap neighbors. Its pass endpoint
is **at most two cases with any below-95/97 neighbor above truth**, after complete verification.
The previous 25/48 saved-best count is only a lower bound and cannot substitute for that endpoint.

The rebuilt order-five model differs from the unavailable historical RX2-O v3 model. “K5” in a
model filename denotes order five, not Kryptos K5. R95 is not unknown-key recovery, a fresh sealed
gate, an optimizer run, a false-positive estimate or a K4 family test.

The remote interruption record reports one primary invocation with exit 0 and COMPLETE stdout,
but explicitly says the full freeze is unpublished, the separately coded verifier has not run,
and the scientific verdict is NOT_READ_OR_VERIFIED. The retained remote evidence contains one
neighbor shard. The process summary is not a substitute for its original resource log.

### Later session report, not yet reconciled to Git

The recovered conversation record includes a 22 November 2026 23:41:48 UTC update (17:41:48
America/Chicago): original outputs reportedly recovered; 55/55 output hashes and 22/22 source/input
hashes matched; the 48 public practice plaintexts/wirings matched their public copies; publication
was accepted and upload was continuing; the verifier had not yet run.

This is **reported recovery**, not a newly inspected complete evidence freeze. The branch inspected
during this review still ends at the interruption commit. The plan therefore preserves both facts,
without treating an upload authorization, process completion or matching hashes as a scientific
GO/NO-GO result.

### Carried-forward action and stop rule

The charter now makes this the immediate task: reconcile original artifacts and pending operations,
publish the complete preserved primary freeze, complete the one already registered scalar verifier,
and record the actual scoped result and closeout. Missing evidence remains INCOMPLETE; no silent
primary rerun is permitted. Verify whether a previously pending invocation completed before invoking
anything again.

The registered primary ceiling is 300 wall seconds, 240 aggregate CPU seconds and 1,024 MiB; the
verifier has 300 wall seconds, 240 aggregate CPU seconds and 512 MiB. Each has one worker and zero
retries. A verified GO_FOR_CONDITIONAL_DEVELOPMENT permits only a separate conditional-development
proposal. SCORE_NO_GO rejects this objective under its finite diagnostic, leaving RX2-O OPEN.
The separately coded verifier remains same-model work.

## 3. Completed work preserved

| Work | Scope retained in the plan | Remaining boundary |
| --- | --- | --- |
| R92 / L181 | Independently reviewed finite exact exclusion: 192 R92 labels plus 128 registered R87 zero-phase labels through n=4; saved blind result NO_SIGNAL | No blanket promotion of all R87 results; original optimizer/full-model scoring and raw-book freshness not independently certified; overrun remains disclosed |
| R93 / L182 | 145,728 n=5..96 nonzero-phase labels; exact and single-observation-omission results closed at the registered scope | Different-model derivation and complete aggregate replay outstanding; no decoding, surviving-label list or feed into blind engineering |
| Combined single rotor | 148,992 labelled settings through n=96 under the stated position-only model | Labels are not distinct cipher functions; combined coverage is not complete independent certification |
| R94 / L183 | A/B and both one-true-wiring conditions 0/48; 39/48 higher-scoring wrong local neighbors; 25 saved best counterexamples below the recovery threshold | Finished finite procedures remain stopped; no K4 run or rotor-family exclusion |
| RX2-O / RX2-D design | Reversible definitions, feasibility kernel, clock/gauge analysis remain reusable | RX2-D has design/correctness work only; RX2-O's recovery failures do not establish RX2-D solver failure |
| Conditional and joint development | >=44/48 top-ranked recovery at >=95/97 and >=5/6 in each of eight turnover cells before a fresh full-pipeline gate | Proposed bars need a new complete work order; a score pass alone cannot authorize K4 |
| R82 / PTAK and period expansion | Unchanged failed/redundant procedures remain parked; finite-window clock equivalence precedes larger label enumeration | No new exclusions or reopened budgets from this planning update |

Sources: `audit/reviews/NEXT_STEPS_AFTER_R94.md`, `CURRENT_STATUS.md`,
`r92/audit/independent_review/REVIEW.md`, `audit/reviews/R92_INDEPENDENT_REVIEW.md`,
`r93/RESULT.md`, `r94/RESULT.md`, `audit/backlog/CLOSEOUT.md` and
`audit/backlog/multirotor/DESIGN.md` at the PR #106 merge.

## 4. Planning defects corrected

| Finding | Correction and governing evidence |
| --- | --- |
| §5 allowed a crib-assisted survivor to enter a later blind round if exposure was disclosed | Ban survivor-fed seeding, filtering, ranking and scope selection; retain R93's aggregate-only contract and other type B rounds' registered evidence contracts. Disclosure does not cure forbidden information flow. `r53/BLIND_RULES.md` items 2/5 and record correction; G3; R93 handoff |
| §1.3 labelled L165's implied-key statistics ciphertext-only | Separate and quarantine them as published-letter-derived audit material; exclude them from the selection rubric and prediction pipeline. G3 |
| The whole charter could be handed to a generator despite containing clues | Mark it coordination/reviewer-only; require a separate reviewed generator input allowlist. G3 |
| §2 allowed exact-encryption or published-letter mismatches to count as a solution through declared errors | Restore the binding exact tests. Error-tolerant exclusions/reconstruction hypotheses remain separate; no automatic exception from charter adoption. BLIND_RULES items 4/6; G4 |
| §12 said to finish a run after discovering a wrong rule | Stop affected invalid computation, preserve evidence, document the defect, repair additively and satisfy fresh required controls. G1 fail-fast and mandatory reviewer checklist |
| Shared fresh benchmark/public CTF wording could recycle exposed controls | Share the specification, use newly sealed controls per decisive gate, label reusable/public material development-only. G1/G2 |
| A failed required stratum was merely labelled WEAK | Required-stratum failure is NO-GO; narrowing afterward needs a new registration and fresh controls. G1/G2 |
| Synthetic-only error mapping implied wider K4 exclusions | Record OPEN tolerance gaps; require a valid implication proof or separately registered exhaustive target check for an extension |
| E1-sub omitted R92/R93 scope | Include their position-only, fixed-length one-substitution implication and review limits; do not combine error classes without proof. R93 RESULT §3; R92 independent review |
| RX2-D design was conflated with RX2-O's SOLVER_NO_POWER | Split their coverage rows |
| The rubric could indefinitely prioritize general bookkeeping over the user's current target | Make R95 explicit now, with R93 review parallel; bounded registers remain later/parallel work |
| Roadmap implied eventual exhaustion of all plausible ciphers at an undefined E1 | Use a versioned finite queue, precise error classes and explicit OPEN/INCOMPLETE outcomes, with a finite rethink checkpoint |
| Second-observable wording implied automatic independence on the same 97 letters | Require joint selection/calibration disclosure; otherwise retain exploratory status; support is not family identification |
| K5 trigger proposed applying every existing exact checker | Require independent input provenance and applicability review; forbid transfer of K4 cribs and clue-conditioned survivors |
| Charter remained PROPOSED after its stated adoption trigger | Record the actual PR #106 merge; preserve the historical proposal note |
| External source URL and custody language were imprecise | Rechecked [Paradigm's official announcement](https://www.paradigm.xyz/writing/kryptos), dated 12 June 2026: SHA-256/HMAC verification without staff seeing plaintext; distinguish the dated announcement from live release/competition status |

The answer-bar key requirement now emphasizes reproducible independent derivation. Historical
plausibility remains useful evidence, without falsely equating a long independently sourced key
with an arbitrary key fitted to a guessed plaintext. Scorer-failure statements are restricted to
the actual tested scopes.

## 5. Validation and limits

The changes are documentation only. The relevant review is source/provenance comparison, checking
the revised document for contradictory priorities, preserving the R95 endpoint/budgets and checking
the repository's immutable-evidence and review rules. No old experiment needs rerunning for this edit.

Repository validation results are recorded in the follow-up PR. Both the baseline guardrail checker
and the unchanged branch checker must pass against the complete planning diff, and `git diff --check`
must pass before publication. This note makes no assertion that CI proves scientific validity.

Outstanding research work remains explicit: finish R95's saved-evidence chain; obtain a genuinely
different-model R93 review; demonstrate conditional/joint recovery and a fresh gate before any new
K4 search. No new candidate, plaintext, key or cipher identification resulted from this review.
