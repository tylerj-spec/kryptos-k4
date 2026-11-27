# Claim-scope errata for R105 and R108–R111 (Claude Code, 27 Nov 2026), after ChatGPT's partial quality review

Affected ledger IDs: L194, L196, L197, L198, L199

Validation:
- **Basis:** the corrections apply `audit/reviews/R108_R111_CHATGPT_QUALITY_REVIEW_20261127.md` (PR #126).
- **Recounts** from the frozen synthetic results:
  - R105 M1 endpoints 42/50 (≥ 90), 31/50 (≥ 95) and 17/50 (exact), from `r105/run_v1/RESULTS.json`;
  - R108's gate panel had 136/400 plants with at least one same-column crib pair, from `r108/holdout/GATE.json`.
- **No new computation** and no K4 input.
- **Frozen files untouched.** `r105/RESULT.md` is hash-pinned, so its correction is `r105/audit/ERRATUM_1.md`. The
  R108–R111 result notes are not pinned; each gets an appended "Errata" section and nothing above it changes.
- **Guardrail check:** PASS.

Independent review: NONE for these edits (one model). They implement a PARTIAL ChatGPT review; no row is promoted.

## What changed
| Row | Before | After |
|---|---|---|
| L194 (R105) | "the score detects the right hypothesis" | The ≥ 90 endpoint is named, and 31/50 at ≥ 95 and 17/50 exact are added. High scores separated the *tested* true hypotheses from the *tested* decoys; they certify nothing. Same-source text and re-encryption checked only from position L |
| L196 (R108) | "EXCL (EXACT) for all 768 cells" | **Conditional EXCL:** it assumes correct crib-pair letters and no same-column crib pair. The 372 DROP cells allow at most one such pair. Two or more are open, so this is not an unconditional exclusion of ordinary Slidefair. The rank reference is independent only for the collision test |
| L197 (R109) | "OPEN (consistent) 322"; "DFS confirms all 34" | The 322 satisfy necessary direct-pair equations only, which is not full-chain feasibility. 12 exclusions are by the primary and 22 are DFS-only. Amendment 2 relaxed a gate criterion |
| L198 (R110) | lag 21 "a reason for a registered follow-up" | Not new evidence: R71 (L160) registered and reported the same width-21 structure. The p-value is scoped to this scan. P5 needs a novelty review |
| L199 (R111) | "all outputs re-encrypt" | They re-encrypt from position L only. The primer is not emitted, the evaluator does not fail closed, and the 8 gate plants cover 8 of 20 cells |

## Corrections to the chat summaries (not in Git)
- The 27 Nov chat summary said R108 rules out "Slidefair with any two alphabets". That is too broad, as above.
- It called R110's lag 2–24 scan an "unplanned extra". The scan was registered as exploratory.
