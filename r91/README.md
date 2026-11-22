# R91: archived solver power gates

This round contains **synthetic-only known-structure power screens** for the
archived R82 linked-tableau key solver and R68 plaintext-autokey primer solver.
The complete plan and fixed bounds are in `PREREGISTRATION.md`.

The secret key and message are concealed. True structural settings are
deliberately supplied. Failure can reject the specified bounded solver
attempt; success does not certify unknown-family recognition. **No outcome
of this round authorizes a K4 run.**

## Provenance

- `vendor/r82/`: unchanged files from draft PR77 at
  `1550736de568abdf442686e4a15b8889c585f2f3`.
- `vendor/r68/keyed_solve.cpp`: unchanged source from main
  `bef9e7d7bcbecc1ca870fa46f0dd78d8a0805d77`.
- `derive_ptak_screen.py`: checked, exact-text adaptation selecting one
  supplied branch and preserving the original primer optimizer.
- `R59_LOWER4_FROM_K5.bin`: reconstructed original order-1 through order-4
  scoring tables, not a replacement scorer. Its receipt and raw acquisition
  digests are retained in `MODEL_RECEIPT.json` and `model_build/`.
- `dev/REPORT.json`: spent-data checks. These are not gate results.

`PROTOCOL.sha256` pins the source, model, plan and provenance artifacts.
`QA_MANIFEST.json` is bound to the actual published preregistration commit
before fresh inputs are generated. It later records the public input paths
and execution evidence. The final holdout freeze covers the complete outputs,
models, code, binaries, resource records and independent forward witnesses.

## Execution sequence

All commands below run from the repository root. Execute each stage only
after the preceding commit has been published. The private truth directory
stays outside the repository and is not read by either candidate kernel.

1. Commit and publish the complete source/preregistration; bind its actual
   commit and SHA-256 in `QA_MANIFEST.json` in a subsequent commit. Only then
   generate the holdout, under `audit/run_bounded_agg.py`:

   ```bash
   python3 -I audit/run_bounded_agg.py --manifest r91/QA_MANIFEST.json --log r91/GENERATION_RESOURCE_LOG.json -- python3 -I r91/make_gate.py --sources RAW_SOURCE_DIRECTORY --training REBUILT_R59_TRAINING_TEXT --public r91/holdout --private PRIVATE_DIRECTORY
   ```

   Commit and publish the two public input files and truth commitment. Never
   publish or open private truth at this stage.

2. Verify `sha256sum --check r91/PROTOCOL.sha256`, derive and compile:

   ```bash
   python3 -I r91/derive_ptak_screen.py
   g++ -O3 -std=c++17 r91/ptak_r68_screen.cpp -o r91/ptak_r68_screen
   g++ -O3 -std=c++17 -shared -fPIC r91/seccomp_io.cpp -o r91/seccomp_io.so
   ```

   Check the source manifest again after derivation; the generated source
   must be byte-identical. Record compiler, binary hashes and environment.
   Create `r91/holdout/run/` once, and prepare the public PTAK TSV:

   ```bash
   python3 -I r91/prepare_ptak.py r91/holdout/PTAK_INPUT.jsonl r91/holdout/run/PTAK_INPUT.tsv
   ```

3. Run each candidate arm once, with no retries or changes:

   ```bash
   python3 -I audit/run_bounded_agg.py --manifest r91/QA_MANIFEST.json --log r91/holdout/run/R82_RESOURCE_LOG.json -- python3 -I r91/run_r82.py r91/holdout/R82_INPUT.jsonl r91/holdout/run/R82_OUTPUT.jsonl
   python3 -I audit/run_bounded_agg.py --manifest r91/QA_MANIFEST.json --log r91/holdout/run/PTAK_RESOURCE_LOG.json -- r91/ptak_r68_screen r91/R59_LOWER4_FROM_K5.bin r91/empty_words.tsv r91/holdout/run/PTAK_INPUT.tsv r91/holdout/run/PTAK_OUTPUT.jsonl 0 24 20 68
   ```

4. Before opening truth, run `verify_witnesses.py` with `--round r91` and
   `--output r91/holdout/run/WITNESSES.json`, under the same resource wrapper.
   Freeze every relevant artifact in `r91/holdout/FROZEN.sha256`, commit and
   publish the complete output freeze. The independent scalar verifier must
   pass all 600 records.

5. After that push is observed, evaluate with `evaluate_gate.py --round r91
   --truth PRIVATE_DIRECTORY/TRUTH.json --freeze-commit ACTUAL_FREEZE_SHA
   --output r91/RESULT.json`, under the same resource wrapper. Publish the
   truth and narrow report in a later commit. A missing record, failed
   witness, isolation failure, hash mismatch or resource failure is
   **INCOMPLETE**, never a method rejection.

## Model reconstruction

The shipped 1.9 MB binary is sufficient for candidate execution. To rebuild,
use `model_build/acquire.py REPO` to fetch the 19 pinned original external
files, copy the original `r34/carter_az.txt` to `model_build/carter_az.txt`,
then run `model_build/build_lower4.py REPO`, under an aggregate resource cap.
Both original builders remain in `r59/` and are hash-identified in the
receipt. The generated training text is used only by the control generator
to reject exact 97-letter overlaps, and never enters a candidate process.

## Interpretation

The main criterion is at least 18/20 exact messages with the true or proved
equivalent key **in every declared stratum**. Any failed stratum yields
`SOLVER_NO_POWER` for that broad bounded attempt. An all-stratum pass yields
`SCREEN_PASS_ONLY`. Neither status closes the cipher family, proves
impossibility, passes the omitted unknown-family/negative-control gate, or
authorizes a K4 experiment. One ChatGPT team performs this execution;
internal review is not independent-model review.
