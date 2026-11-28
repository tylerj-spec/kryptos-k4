# R115 Amendment 1 (APPROVED): fix the report step and re-run once as v2

**Status: APPROVED.** Tyler, 28 Nov 2026, answering the question in this session: "Approve (Recommended)". The option
read: "Commit the 3-line report fix as Amendment 1 and re-run once as run v2 with the same seed, computation and
budget. Run v1 stays on record as INCOMPLETE."

## What happened
Run v1 finished all four registered computations inside its budget (`run_v1/RESOURCE_LOG.json`, `run_v1/CONSOLE.log`,
commit 4a09125):
- T1 0.14 s, T2 0.54 s, T3 192.9 s, T4 655.5 s;
- 849 s wall in total, with an aggregate peak of 585 MB.

**The crash.** `main()` stored each stage's wall time **inside** that stage's own dictionary. The label loop over
T4's entries then met a float and raised `TypeError`. `RESULTS.json` is written only after that loop, so **no result
was produced or seen**. Only the four stage timings were printed. The run is synthetic, with no K4 input.

## The change (report step only)
- Stage timings now go in their own top-level field, `stage_wall_s`. Three lines of `main()` change.
- **Unchanged:** T1–T4, their code, the seed (1150901, a single stream used in the same order), the thresholds,
  the labels and the budget (3,600 s / 3,600 s / 2,048 MiB, zero retries).
- **Checked before the run:** the report path was exercised with T3 and T4 replaced by stubs. That dev check
  produced no registered output.
- **v2 is the only run with results.** v1 stays recorded as INCOMPLETE.
- **CI** compares every field except `wall_s`, `cpu_s` and `stage_wall_s`.
