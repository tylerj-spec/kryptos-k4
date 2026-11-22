# R82/PTAK backlog closure through R91 fresh power screens

Affected ledger IDs: L157, L180

Validation: preregistered supplied-structure screen on 600 fresh controls, complete outputs committed and pushed before truth opening, all 600 forward witnesses, all fixed per-stratum decisions, immutable protocol/freeze checks, aggregate resource logs, and a separately coded post-freeze verifier importing neither solver nor original evaluator. The separate verifier passed in 0.754 s wall / 0.626 s CPU / 15.7 MB sampled aggregate RSS.

Independent review: NONE for the new R91 execution. ChatGPT built, ran and internally reviewed this round. Same-model subtasks and separately written code improve verification but do not provide an independent-model council vote. This note promotes no K4 exclusion.

## Terminal decisions

The R82 broad linked-key baseline and archived R68 long-lag PTAK baseline both fail the registered criterion of at least 18/20 exact messages with true or proved-equivalent keys in every stratum. R82 achieves 250/360 exact, with 8/18 passing strata. PTAK achieves 32/240, with 0/12 passing lag strata. Both attempts close as **SOLVER_NO_POWER / NO-GO for advancement**; their cipher families remain OPEN.

This is a supplied-structure eligibility screen. It establishes failure of the specified per-true-branch capability requirement for the pinned score, seed schedule, effort and one-key retention rule. It does not prove that every unknown-structure classifier fails; equivalent alternative branches or a different optimizer may behave differently. The full unknown-family/negative-control stage was not eligible and was not executed. No false-positive rate or new K4 result is claimed.

L157 gains a cross-reference documenting the demonstrated long-lag limitation. Its prior GRO/PER/CTAK exclusions are unchanged. New L180 records the synthetic R91 experiment and its actual scope, rather than converting solver failure into a cipher-family exclusion.

## Separate result audit

`audit/backlog/verify_r91_result.py` was published in the output-freeze commit before truth was opened. It independently implements forward encryption and linked-key functional equivalence. After reveal it confirmed:

- All 18 linked and 12 PTAK cells have exactly 20 cases.
- All 600 true keys satisfy the primitive-period sampling rule.
- All 600 saved outputs and all 600 truth records re-encrypt correctly.
- Every exact/near/key count and both terminal decisions agree with `r91/RESULT.json`.
- All 600 plaintexts are distinct; the 200 windows from each source do not overlap.
- All 39 protocol entries, 60 output-freeze entries and five input-freeze entries match.
- Every critical input, source, model, output and resource record was present with matching bytes at output-freeze commit `600747049a1537378e7843d93b356ddbe8d4390a`.
- Truth and result files were absent from that commit, and the revealed truth matches its earlier commitment.
- Both candidate arms completed once within the registered limits. No retries or outcome-based tuning occurred.

Evidence: `audit/backlog/R91_RESULT_REVIEW.json`, its resource log, and `r91/RESULT.md`. The historical order-six model was not rebuilt or byte-compared; the shipped lower-order model follows the pinned corpus/builder construction, as explicitly qualified in R91.

The post-result `check_r91_public_provenance.py` audit reproduced the entire answer file and both input files byte for byte from the pinned public-source books and public random seed. `R91_PUBLIC_PROVENANCE.json` records this verification. The payload consists of synthetic cipher-test keys and public-source text windows, not account credentials. This was a separate provenance audit, not a formal candidate-kernel retry or a fresh holdout.

R91's frozen QA correctly remains at the output-stage `PENDING_TRUTH_REVEAL` value. The subsequent terminal decisions are in the separate result files. No frozen evidence was rewritten to update that field.

Signed: ChatGPT.
