# R63 independent raw-work integrity and optional alternative witness check

**Review-only addition; does not alter Claude's running R63 solver, thresholds, source files or preregistration. Do not merge this PR or modify the in-flight R63 experiment.**

## The reproducibility gap this closes

`r63/blind/run.py` resumes a chunk if its existing `.jsonl` has the *expected number of lines*, without matching its IDs, ciphertexts, solver and model parameters. A same-length stale chunk can be carried into the combined output. The existing R63 postfreeze reveal will usually detect an incorrect ciphertext via forward encryption, but that happens late.

More importantly, `r63/blind/rk2_solve.cpp` emits **`best`, `per_convention` (six), and `top` (eight)** full 97-letter plaintext/key candidates for each ciphertext. `r63/blind/run.py` copies only `best` into `RESULTS.jsonl`; the original `FROZEN.sha256` does **not** cover the raw `work/*.jsonl` alternatives. Without an additional remote freeze, those alternatives cannot be validly treated as previously committed independent candidates during a later clue check. This could cause a top-score-only review to overlook alternatives already produced by the blind solver.

## Safe sequence (only AFTER the existing R63 run finishes)

1. **Before any published K4 plaintext check**, use the unchanged solver output and run:

   ```bash
   python3 r63/audit/seal_work.py /path/to/R63_FROZEN_DIR --expected-nulls 100
   ```

   This creates `WORK_FREEZE.sha256` containing the original `FROZEN.sha256`, `RESULTS.jsonl`, and all raw `work/{CLOCK,GERMAN}_NNN.{tsv,jsonl}` files. No published clue text is read.

2. Commit and **successfully push `WORK_FREEZE.sha256` and every listed raw work file** to remote Git before revealing known plaintext. Confirm the exact Git commit URL on GitHub, that its tree contains every file listed, and that the frozen source/preregistration commit predates generation. If the published-letter comparison has already run before this remote freeze, these alternative checks are **not** independently blind; disclose them as post-exposure exploratory results instead. Do not rewrite history.

3. From a checkout of the frozen source commit, against the original unchanged files and exact binaries/models named in `FROZEN.sha256`, run:

   ```bash
   python3 r63/audit/verify_frozen.py \
     --input /path/TARGET.tsv \
     --frozen /path/R63_FROZEN_DIR \
     --root /path/kryptos-k4 \
     --solver-binary /path/rk2_solve \
     --english-lm /path/lm6_en.bin \
     --keydir /path/R63_MODELS \
     --report /path/REPORTS/independent_audit.json
   ```

   It checks every original source hash, all 101 original/shuffled inputs, all 202 combined 97-character forward-encryption witnesses, every cached input/result chunk, plus every `best`/`per_convention`/`top` candidate. It reports per-model empirical ranks with the `(ge + 1) / 101` calculation and an explicit two-model Bonferroni bound. It does **not** access published K4 plaintext.

4. **Only after that audit passes and a successful remote Git freeze is independently verified**, Claude may separately invoke the optional check:

   ```bash
   python3 r63/audit/reveal_alternates.py \
     --input /path/TARGET.tsv \
     --frozen /path/R63_FROZEN_DIR \
     --root /path/kryptos-k4 \
     --solver-binary /path/rk2_solve \
     --english-lm /path/lm6_en.bin \
     --keydir /path/R63_MODELS \
     --remote-freeze-commit FULL40HEXGITSHA \
     --report /path/REPORTS/alternative_check.json
   ```

   The optional script runs the same independent audit **before** loading the existing sealed `r63/sealed/reveal_k4.py` postfreeze checker. It tests previously frozen alternatives only; it does not generate plaintext, adjust model weights, request new keys, or send clue data to the solver. It reports only threshold-qualified candidates, not a clue-driven ranking of failures. The remote SHA is operator evidence; this local script cannot independently attest GitHub's remote state.

## Interpretation limits

- A six-convention or top-eight alternative is **not** a pre-registered R63 primary candidate. Its clue-check result is an *exploratory postfreeze secondary analysis*, and must not be called a preregistered `SIGNAL` or used to revise the original primary decision rule.
- Forward-encryption success means only mathematical reversibility, not that the plaintext is authentic.
- Null shuffles are not automatically a complete null model for every possible structured cipher; two tested models have familywise multiple-testing concerns. The report's Bonferroni bound assumes the shuffle-rank calibration is valid; it does not adjust for the larger historical search across R1-R63 or the alternatives examined post hoc.
- `WORK_FREEZE.sha256` does not itself prove remote provenance, a source freeze predating the run, or that the historical executable can be rebuilt bit-for-bit. Check these separately and report any gap.
- Do not merge any PR as part of this audit. Do not use known K4 text in generation or tune models from failed clue checks.

## Local regression tests (all synthetic, no actual K4 plaintext)

```bash
python3 -m unittest -v r63.audit.test_verify_frozen
```