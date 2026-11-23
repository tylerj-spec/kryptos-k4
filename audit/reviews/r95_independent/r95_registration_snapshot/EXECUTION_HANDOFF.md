# R95 execution and reproduction

The preregistration is published at
`c02b7a92404c2c18d41e7d2a13d75099ab8764bc`. Its scope is one fixed candidate
objective on spent public synthetic examples. This is not a new cipher,
unknown-key search, blind holdout or K4 experiment.

## Original bounded primary invocation

Use a fresh output directory. In the actual workspace, the existing external
model and training inputs reside under
`/workspace/scratch/4f425b909cf8/backlog_gate_dev/r59_rebuild/`.
Their exact bytes, not their location, identify the inputs. From repo root:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
python3 -I audit/run_bounded_agg.py --manifest r95/QA_MANIFEST.json \
  --log r95/RESOURCE_LOG.json -- \
  python3 -I r95/score_challenge.py \
  --repo /workspace/scratch/4f425b909cf8/r89_review_repo \
  --model5 /workspace/scratch/4f425b909cf8/backlog_gate_dev/r59_rebuild/lm5.bin \
  --training-text /workspace/scratch/4f425b909cf8/backlog_gate_dev/r59_rebuild/corpus/train.txt \
  --protocol /workspace/scratch/4f425b909cf8/r89_review_repo/r95/PROTOCOL.sha256 \
  --out /workspace/scratch/4f425b909cf8/r89_review_repo/r95/development
```

The primary stores 48 neighbor shards of 650 records, each at most512KiB.
Total controlled output is at most32MiB. All labels are retained; this is
only storage partitioning. It records Python/NumPy versions rather than
requiring a particular NumPy build. Exact model bytes and a separate scalar
verifier constrain scientific portability. No primary run into an existing
output directory is allowed; the work order permits zero retries.

Publish the complete output, resource log and freeze before interpretation.
Then invoke the independent-code verifier once under `REVIEW_BUDGET.json`:

```bash
python3 -I audit/run_bounded_agg.py --manifest r95/REVIEW_BUDGET.json \
  --log r95/REVIEW_RESOURCE_LOG.json -- \
  python3 -I r95/verify_score_challenge.py \
  --repo /workspace/scratch/4f425b909cf8/r89_review_repo \
  --model5 /workspace/scratch/4f425b909cf8/backlog_gate_dev/r59_rebuild/lm5.bin \
  --training-text /workspace/scratch/4f425b909cf8/backlog_gate_dev/r59_rebuild/corpus/train.txt \
  --protocol /workspace/scratch/4f425b909cf8/r89_review_repo/r95/PROTOCOL.sha256 \
  --run /workspace/scratch/4f425b909cf8/r89_review_repo/r95/development \
  --out /workspace/scratch/4f425b909cf8/r89_review_repo/r95/review
```

The two original jobs together have600wall/480aggregateCPU seconds, with the
per-job memory caps in their manifests. The user's25-meter priority is not a
runtime limit and does not alter these scientific stop rules.

## Reconstruct dependencies for independent reproduction

`rebuild_model.py` downloads only the19 already-pinned public training assets,
checks every digest, uses the original corpus and C++ model builders, and
requires the final training/model digests to match `MODEL_SPEC.json`. It reads
no practice panel, true key, plaintext diagnostic, or K4 input. Run it under
`CI_REBUILD_BUDGET.json` with `--repo REPO --out FRESH_DIRECTORY`. The output
contains `lm5.bin` and `corpus/train.txt` for the verifier command above.

This dependency reconstruction and later saved-evidence CI are verification
replications, not extra attempts at the original experiment. CI does not run
the primary scorer/neighbor producer or an optimizer. Changed upstream bytes,
failed downloads or different generated model digests stop reproduction;
they never permit replacing the registered model with a convenient one.

The review is a separate implementation within ChatGPT. It must retain
`independent_model_review: NONE`. R93's pending independent-model review is
not fulfilled by this work.
