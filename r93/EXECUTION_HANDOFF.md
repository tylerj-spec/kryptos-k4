# R93 execution handoff — registered and source-reviewed; not run

## Current state

- **REGISTERED:** preregistration and explicit exact-only mode clarification
  were published at `567f418961cc18847207008468679115074f4c93`.
- **SOURCE_REVIEWED:** the complete implementation, QA metadata and source
  manifest are prepared and internally reviewed. `PROTOCOL.sha256` has SHA-256
  `bffbf215b3366da3cc95d969c21c1b9352030179c7ab6f0c153a95544a3cf234`.
- **NOT_RUN:** neither the formal correctness gate nor the target audit has
  run. The saved scope calculation and small smoke test are development-only.
- **Publication blocked:** automatic approval review twice rejected the public
  source upload as possible sensitive-data egress. The public destination and
  previously public provenance were supplied for re-review, but publication
  remains blocked. The user must explicitly approve the exact reviewed public
  payload before that publication can resume. Do not use another publication
  route or execute around this prerequisite.

This note changes no frozen registration, source, budget or protocol hash.

## After approved source publication

Use the normal approved repository workflow to publish and fetch the reviewed
source package. Record its actual full commit SHA as `R93_SOURCE_SHA`. Confirm
the source bytes and protocol manifest match the reviewed package. Source
publication must precede the formal gate; registration alone is insufficient.

From the repository root, with that actual SHA set:

```bash
mkdir -p r93/holdout
python3 -I audit/run_bounded_agg.py \
  --manifest r93/VALIDATION_BUDGET.json \
  --log r93/holdout/VALIDATION_RESOURCE.json -- \
  python3 -I r93/validate93.py \
    --source-commit "$R93_SOURCE_SHA" \
    --binary /tmp/r93-checker \
    --out r93/holdout/CHECKER_GATE.json
```

Formal gate limits: **180 seconds wall, 120 aggregate CPU seconds, 512 MiB**.
Require the complete 141,793-case oracle, 8,832 parameter plants, all error and
bulk-path checks, and the three-input forecast. The result must say
`gate_type=EXACT_CHECKER_CORRECTNESS`, `gate_verdict=GO`,
`blind_recovery_certified=false`, and the wrapper must say COMPLETE within all
caps. A completed mathematical/forecast failure is NO-GO; a resource,
infrastructure or integrity failure is INCOMPLETE. Either blocks the target.
Preserve failures; do not retry or repair frozen sources silently.

## Publish the gate before any target

Only after complete success:

1. Update the unpinned QA manifest to `stage=gate`, `gate_verdict=GO`, retaining
   the explicit correctness-gate type and all existing bounds.
2. Write `r93/holdout/GATE_FROZEN.sha256` covering the gate result, validation
   resource log, `r93/PROTOCOL.sha256`, and its pinned sources. Do not pin the
   still-staged QA manifest in this gate freeze; it must later record the
   target's frozen stage.
3. Commit and push the gate artifacts in a distinct later commit. Fetch and
   record its actual full SHA as `R93_GATE_SHA`. The coordinator must confirm
   publication before target execution.

## One target execution

Do **not** create `r93/k4` beforehand: the target driver requires a fresh output
directory and refuses to overwrite one. From the repository root:

```bash
python3 -I audit/run_bounded_agg.py \
  --manifest r93/QA_MANIFEST.json \
  --log r93/TARGET_RESOURCE_LOG.json -- \
  python3 -I r93/run_target93.py \
    --source-commit "$R93_SOURCE_SHA" \
    --gate-commit "$R93_GATE_SHA" \
    --binary /tmp/r93-target-checker \
    --out-dir r93/k4
```

Target limits: **1,800 seconds wall, 1,200 aggregate CPU seconds, 512 MiB**;
one invocation, no retry. The exact scan covers 145,728 labels on 201 inputs,
or 29,291,328 base calls and 732,283,200 logical exact/deletion tests.

Expected artifacts are `r93/k4/INPUTS.tsv`, `AGGREGATES.json`,
`SOURCE_RECEIPT.json`, and `r93/TARGET_RESOURCE_LOG.json`. Require COMPLETE,
all 201 input IDs, every full setting count, and all resource caps. Any failure
is INCOMPLETE/UNKNOWN and leaves the exclusion open.

Before interpreting counts, update QA to its frozen stage and write
`r93/k4/FROZEN.sha256` covering all target artifacts, the final QA manifest,
source/protocol receipts, gate evidence and pinned sources. Commit and push
that output freeze separately. Do not change the frozen files afterwards.

## Interpretation after the published freeze

Zero exact-compatible labels supports only the registered all-correct
observation exclusion. Zero DROP-compatible labels supports its separately
stated one-published-observation and one-fixed-length-ciphertext-substitution
bounds. A positive count is **COMPATIBLE / OPEN**; null counts are descriptive.
No LEAD, strength score, plaintext, wiring, surviving setting list or
clue-conditioned target selection is authorized. Nothing enters RX2 engineering.

The legacy QA schema's `max_candidates=1` is an unused positive ceiling; the
stricter limits `max_decoded_candidates=0` and
`max_surviving_setting_outputs=0` remain binding. Aggregate records have their
own cap of 201. Explain this compatibility detail in the result note.

Publish a signed scope/result review with **Independent review: NONE** for this
same-model implementation. A different-model review is required before any
`INDEPENDENTLY VERIFIED` promotion. No current R93 gate, exclusion or K4 result
exists.
