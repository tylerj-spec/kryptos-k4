# R94 execution handoff

**REGISTERED / SOURCE_REVIEWED / NOT_RUN**

The preregistration and resource/work-order Markdown files were published at
`567f418961cc18847207008468679115074f4c93`. The source/QA/input package has passed
static review and Python AST parsing only. No module execution, mathematical
self-test, candidate search, new control generation or truth-assisted
diagnostic has run for R94.

Automatic approval review rejected publication of the source package as
possible sensitive egress, including on re-review after the public repository
and byte-identical public synthetic input provenance were documented. The
publication did not complete. Do not execute R94 or use another publication
route to evade that rejection. Resume only after the user explicitly approves
the exact public payload, publication is approved and succeeds, and the
published source tree is fetched and verified against the local protocol.

## Fixed source package

- `r94/PROTOCOL.sha256`
- `r94/QA_MANIFEST.json`
- `r94/SOURCE_RECEIPT.json`
- `r94/audit/V1_V3_RESOURCE_REVIEW.json`
- `r94/audit/V1_V3_REVIEW.md`
- `r94/inputs/PANEL.tsv`
- `r94/inputs/PANEL_TRUTH.json`
- `r94/reference.py`
- `r94/run_all.py`
- `r94/selftest.py`
- `r94/structured.py`

The additive `r94/audit/STATIC_SOURCE_REVIEW.md` documents the static check;
it is not an execution dependency. `SOURCE_RECEIPT.json` binds the exact copied
inputs to their already-public source at
`9e4bd400e64c6aa46ae3afdc9ba0d82a1a927fd1`. These are synthetic cipher-test
wirings and public spent test plaintexts, not account credentials.

Final runner SHA256:
`a01b60af02041a2a2be60cea52954fc02d37be81b0bd14a82ba38f4cc05c6d2b`.
Protocol SHA256:
`d16853b5c70885897e026a99d2d63f1e655bd12e7bf2c142074b19f7937011b1`.
Do not edit frozen source or regenerate the protocol to change the experiment.

## Sole execution command, after approved source publication

Run from the repository root. **Do not pre-create `r94/development`:** the
runner requires exclusive directory creation and refuses any existing path.

```sh
python3 -I audit/run_bounded_agg.py --manifest r94/QA_MANIFEST.json --log r94/RESOURCE_LOG.json -- python3 -I r94/run_all.py
```

One attempt, one worker, zero retries. The entire invocation has a cumulative
1,800-second wall limit, 1,800 aggregate CPU-second limit and 2,048 MiB memory
limit. Additional wall/CPU phase ceilings are 60 seconds for mathematical
checks, 300 for version A, 900 for version B, and 300 for diagnostics and the
archival replay. There is no budget reset between phases or versions.

Expected artifacts are `r94/RESOURCE_LOG.json` and files under
`r94/development/`: `TESTS.json`, `VERSION_A.jsonl`, `VERSION_B.jsonl`,
`UNKNOWN_OUTPUTS_BEFORE_TRUTH.json`, `EVENTS.jsonl`,
`CONDITIONAL_DIAGNOSTICS.jsonl`, `CONDITIONAL_SUMMARY.json`,
`ARCHIVED_REPLAY.json`, `RECOVERY.json`, `RESULT.json`, and `OUTPUTS.sha256`.
An exceptional exit writes `INCOMPLETE.json` only if this invocation created
the results directory; it cannot overwrite evidence when a repeat is refused.

Verify the aggregate resource log says COMPLETE before accepting a complete
diagnostic. Keep both-unknown-wiring recovery separate from the true-U/true-V
oracle conditions. Partial output after failure remains INCOMPLETE. Do not
retry automatically, create a third version, replace inputs, promote a fresh
gate, infer a false-positive rate, run K4, or claim a cipher-family exclusion.
Any success remains a spent-data development observation.
