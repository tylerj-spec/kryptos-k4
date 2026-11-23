# R95 closeout: CLOSED, GO_FOR_CONDITIONAL_DEVELOPMENT on the registered score check (by independent replication)

Affected ledger IDs: L184
Validation:
- Tyler's decision, quoted below.
- The independent replication in `audit/reviews/r95_independent/` (PR #109). It used:
  - the model rebuilt to R95's registered digest e9c0848f…;
  - all 48 true and 31,200 neighbor forward witnesses;
  - the recovered primary shard D_000, which agrees 650/650.
- R95's registration files are kept verbatim, with their git blob ids, in
  `audit/reviews/r95_independent/r95_registration_snapshot/`.

Independent review: YES Claude Code (different-model replication of ChatGPT's R95 question)

## Decision
On 23 Nov 2026 Tyler, asked whether the independent replication should count as closing R95, answered: **"Yes, that
is fine with closing 95"**.

**R95 is CLOSED.**
- **Recorded outcome** of its registered rule: **GO_FOR_CONDITIONAL_DEVELOPMENT**.
- **Order-5 objective:** 1/48 cases have a below-95/97 one-swap neighbor above truth, against the bar of ≤ 2.
- **Order-4 baseline:** 32/48.

## What closing means
- **Evidence basis.** The outcome rests on the different-model replication, not on R95's own primary outputs. Those
  were lost with ChatGPT's workspace; 47 of 48 shards were never published.
- **Determinism.** The computation is fully determined. If the originals ever surface, they must equal the
  replication, and a disagreement would be a defect to report.
- **Unused verifier.** R95's registered same-model verifier was never run and is no longer required.
- **No more invocations.** The primary allowance is spent and is not reopened.
- **The branch** `chatgpt/r95-fixed-score-challenge-20261122` (8f59313) is left as ChatGPT left it. It is not merged.
  Its CI would rebuild the model from downloads and compare against a review file that was never produced.
- **What GO permits.** Only a separately specified **conditional-recovery work order** (charter §6.3):
  - at most two fixed optimizer variants;
  - 48 true-U and 48 true-V conditions;
  - at least 44/48 recoveries at ≥ 95/97 in each condition;
  - at least 5/6 in each of the eight turnover cells;
  - its own budget inside one cumulative cap.
- **Not authorized:** no K4 run, fresh gate or blind search. RX2-O stays **OPEN**.
