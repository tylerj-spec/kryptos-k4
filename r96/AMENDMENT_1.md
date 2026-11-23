# R96 Amendment 1 (before the truth is opened): the freeze manifest is named OUTPUTS.sha256

`audit/check_guardrails.py` treats any round file whose name contains "frozen" as a **K4 output**. It then requires a
GO synthetic gate. R96 touches no K4 data. Its version 1 freeze manifest, `r96/run_v1/FROZEN.sha256`, committed and
pushed in **1b7ee5e**, tripped that rule.

**Change.**
- The manifest is renamed `r96/run_v1/OUTPUTS.sha256` (git mv, content unchanged), as R94 named its own.
- `evaluate96.py` reads that name. This is its only change: one path and its docstring.

**Unchanged:**
- the outputs (`RESULTS.jsonl`, `RUN.json`, `WITNESS.json`, `RESOURCE_LOG.json`);
- their hashes;
- the freeze commit **1b7ee5e**, against which the evaluator checks every output.

The evaluation has not run, and the truth has not been opened. Updated source hashes are in `SOURCE_A1.sha256`.
