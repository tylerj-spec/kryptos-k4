# R90 Amendment 1 (22 Nov 2026): gate launch 1 killed by the aggregate memory budget; relaunch with 2 workers

**Written before any blind output existed and before the truth was opened.**

## What happened
The first gate launch used 4 workers under `audit/run_bounded_agg.py`. The wrapper killed it after 3.5 s:
**aggregate resident memory 4,184 MB, above the pre-registered 4,096 MB** (status INCOMPLETE). The log is kept in
`r90/holdout/launch1_aborted/RESOURCE_LOG.json`.

The cause: each worker loads its own copy of the R59 letter model, about 1 GB. The kill came before any item finished.
The runner writes `RESULTS.jsonl` only at the end, so **no blind output was produced or seen**, and the truth file was
not opened.

## What changes
- **Both runs (gate and K4) use 2 worker processes instead of 4.** The pre-registration does not fix the worker count.
- **The budget is unchanged:** 4,096 MB aggregate, 28,800 s CPU, 7,200 s wall.
- **Every item's result is independent of the worker count:** each is a deterministic, exhaustive computation, which
  the determinism check verifies.
- **The relaunch uses a fresh sandbox.**

## What it shows about earlier rounds
This is the first measurement of a 4-worker run's aggregate memory. R87, R88 and R89 also ran 4 workers, each loading
the same letter model, under `audit/run_bounded.py`. That wrapper limited and logged memory per process only, so their
aggregate memory was probably above 4 GB. The figure was never measured or enforced, as ChatGPT's R89 review noted
(correction E). None of those rounds' results depends on memory. The point concerns how their budgets were described.
