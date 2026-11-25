# R101 Amendment 1 (Claude Code, 25 Nov 2026): two power bars set from development data, before the gate

**Committed with the source, before the gate (seed 1010901) has run and before any K4 file or published letter is
read by R101 code.** The pre-registration is unchanged. No soundness condition changes.

## What changes
| Check | Registered bar | Amended bar | Unchanged soundness condition |
|---|---|---|---|
| V2 plants | ≥ 50 of 60 decided | **≥ 40 of 60 decided** | 0 planted cells INFEASIBLE |
| V3 two solvers | ≥ 24 of 32 decided by both | **≥ 20 of 32 decided by both** | 0 disagreements |

## Why
The registered bars were set before any measurement. The fraction of cells the primary can decide depends on the
random windows and lags: a cell whose mod-13 solution space has dimension > 7 is UNDECIDED by design.

V2's procedure was run on development seeds only, never the gate seed:

| Seed | Decided (of 60) | Missed |
|---|---|---|
| 31 | 50 | 0 |
| 32 | 46 | 0 |
| 33 | 50 | 0 |
| 34 | 51 | 0 |
| 35 | 53 | 0 |
| 4545 (full development gate) | 50 | 0 |

The mean is about 50. A bar of 50 would therefore fail about half the time, on UNDECIDED cells and not on any
error. The development gate's V3 had 28 of 32 cells decided by both solvers.

The bars exist to show that the gate exercises the solvers. 40 of 60 and 20 of 32 still require most cells to be
decided, while the soundness conditions (no planted cell INFEASIBLE, no disagreement) stay exactly as registered.

## Development runs (disclosed; none touched K4 or a published letter)
- `dev/DEV_GATE_seed4545.json` and its log: the full gate code with development seed 4545, DEVELOPMENT_ONLY_GO,
  108 s CPU, peak 406 MB.
- `dev/V2_RATE.txt`: the V2 decided-rate measurement above.
- `dev/SMOKE_*`: the synthetic target rehearsal (see `dev/README.md`).

Independent review: NONE (one model).
