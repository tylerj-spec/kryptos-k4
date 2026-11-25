# R102 run v1: INCOMPLETE (registered budget exceeded)

The registered run (seed 1020901, `run102.py` at SOURCE.sha256 7c7d20f) was stopped by `audit/run_bounded_agg.py` at
**1,800 s wall** (1,784 s CPU, peak 289 MB): wall-clock budget exceeded, exit −9. No `RESULTS.json` was written.
The round registered zero retries, so this is stop condition 6 of `audit/OPERATING_PROCEDURE_ROLLING.md`. R102 is
paused for review, and nothing is re-run.

## Where the time went (development diagnosis, seeds 88 and 89, reduced counts; never the registered seed)
| Check | Cost |
|---|---|
| C3: 240 hypotheses, both solvers | about 0.2 s per hypothesis, about 50 s in all |
| C4: 60 cases | about 0.09 s per case, about 6 s |
| C5: crib-shaped windows | **about 1.2 s per cell** for the primary. 40 windows × 30 cells = 1,200 cells, **about 1,400 s**, plus about 0.2 s per DFS call |

C5 is the cause. Its cells are underdetermined by design: about 22 equations against up to 53 unknowns. The
primary solver enumerates the mod-13 solution space whenever its dimension is ≤ 7, which costs up to 13⁷ vectors
per cell. The registered C5 scale was not timed before registration. That was my error.

No result of any check was seen.
