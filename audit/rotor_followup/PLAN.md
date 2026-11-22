# R93/R94 post-freeze internal result review

This is a same-model artifact and arithmetic review. Independent-model review:
**NONE**. It cannot promote either new round to INDEPENDENTLY VERIFIED.

Run only after the coordinator confirms that both complete result freezes are
published and fetched. The checker requires full immutable source, gate and
freeze commit IDs and verifies their ancestry and committed bytes. It records
the review source and budget hashes. Git proves commit relations; the
coordinator's publication record establishes that pushes preceded execution.

## Scope

- R93: verify protocol/gate/target hashes and chronology, gate counts and
  resource limits, the 201-input shuffled panel, the complete aggregate schema,
  exact/deletion count bounds, absence of decoded candidates, and the derived
  bounded verdict. The complete target scan is **not rerun**.
- R94: independently code the event-clock cipher, inverse mapping, unigram
  and scalar order-four scores. Recheck every saved final state, retention
  order, recorded monotone traces, start convention, forward/inverse witness,
  recovery summary and key-equivalence diagnostic. Check output hashes and
  event ordering before truth access. Recount the 96 one-true-wiring conditions
  separately, verify all 31,200 finite true-key neighbors, and recheck saved
  archival witnesses and all 17 historical resource logs. No optimizer is
  invoked and no new candidate is saved.
- Verify the sole cumulative R94 resource log, individual phase limits and
  finite state/update counts. A failed/incomplete original job cannot become
  a complete experimental result through this review.

The review uses only Python's standard library. Its cipher and scorer do not
import the original reference, candidate core, evaluator or optimizer.
It preserves the distinction between unknown-two-wiring recovery, conditional
diagnostics, local scoring counterexamples and statistical generalization.

## Budget and command

One review invocation: 300 seconds wall, 180 aggregate CPU seconds, 512 MiB;
zero automatic retries. The bound is for a separate postrun verification job,
not a reset of either experiment's search allowance.

```sh
python3 -I audit/run_bounded_agg.py --manifest audit/rotor_followup/BUDGET.json --log audit/rotor_followup/RESOURCE_LOG.json -- python3 -I audit/rotor_followup/check_postrun.py --source-commit SOURCE_SHA --r93-gate-commit GATE_SHA --r93-freeze-commit R93_FREEZE_SHA --r94-freeze-commit R94_FREEZE_SHA --out audit/rotor_followup/REVIEW_RESULTS.json
```

R93 freeze: `r93/k4/FROZEN.sha256`. R94 freeze:
`r94/audit/RUN_FROZEN.sha256`, supplemented by the runner's complete
`r94/development/OUTPUTS.sha256` manifest.

The verifier emits counts, hashes and review dispositions only. It does not
publish plaintexts, keys, surviving R93 labels or rankings, and nothing from
R93 is supplied to R94. A later human/model assessment must retain the stated
scope and independent-review limits.
