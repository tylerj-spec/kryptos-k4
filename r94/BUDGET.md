# R94 cumulative resource budget

One invocation, one worker, zero retries. The entire work order has a hard
**1,800-second wall limit, 1,800 aggregate CPU-second limit and 2,048 MiB aggregate
sampled resident-memory limit** under `audit/run_bounded_agg.py`. The same memory
number is the per-process address-space limit. Imports, tests, both candidate
versions, truth-assisted diagnostics, archival replay and report writing count
toward this one allowance. Separate jobs do not receive new 1,800-second budgets.

| Phase | Additional wall/CPU ceiling | Finite search/computation bound |
| --- | ---: | --- |
| Mathematical checks |60 s each |24 exhaustive conditional assignments at q3–6; finite reference/model checks |
| Version A |300 s each |48 rows ×8 starts ×16 sweeps ×2 blocks =12,288 assignments maximum |
| Version B |900 s each |48 ×8 ×24 ×2 =18,432 block proposals maximum |
| Diagnostics and archival replay |300 s each |96 conditional assignments,2,304 higher-order block proposals,31,200 true-key neighbors, saved v2/v3 witness recount |

Internal phase checks occur at finite loop boundaries and raise an error when
either phase limit is exceeded. The outer wrapper is the hard cumulative kill
boundary. Every higher-order block evaluates at most 1,015 strings, including
nonlegal one-entry counterfactuals used only to build its surrogate. At most
1,008 new final/key-witness records are saved; QA's explicit cap is1,100.

The runner writes version A and version B candidates incrementally by row.
Both complete files are hashed before truth is opened. Partial files after a
failure provide audit evidence but do not make a complete recovery result.

At most 2 versions are authorized by this work order. Version B has the fixed
implementation and validity/resource trigger in the preregistration; it is not
selected by true plaintext matches. Any exceptional exit, failed invariant,
phase-cap exhaustion or global kill is INCOMPLETE. There is no automatic retry.
