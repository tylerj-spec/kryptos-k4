# R109 Amendment 2 (Claude Code, 27 Nov 2026): the two-solver gate check counts decided cases, not a share (before the gate)

**Status:** PROPOSED. It is committed before the gate has run, and is reported to Tyler at once under the rolling
procedure §4.2. It applies only if approved.

## What changes
In §3 of `PREREGISTRATION.md`, V3 changes from

> 200 random masked hypotheses … 0 disagreements where both decide, and ≥ 50% both decided

to

> **600** random masked hypotheses … **0 disagreements where both decide, and at least 40 cases where both decide.**

Nothing else changes.

## Why
- The 50% figure came from R102 and R103. There, the primary ran with dmax 7, and most hypotheses were longer than 24
  letters.
- After Amendment 1 (dmax 5), the primary decides only a minority of random 24-letter masked hypotheses.
  - In a development smoke run (seed 96, 20 cases), both solvers decided 2 of the 20, with 0 disagreements.
  - In dev seed 1093, the primary decided 16 of 60 cells.
- The 50% share therefore measures the primary's coverage, not whether the two solvers agree. It would fail the gate
  for a reason unrelated to correctness.

**What the new rule keeps:**
- **The check itself:** agreement wherever both solvers decide, with zero disagreements allowed.
- **A minimum of evidence:** 40 decided cases.

Soundness of the INCONSISTENT verdicts is still tested directly by V1 (true hypotheses) and V2 (one error).

**Cost:** about 600 × 0.5 s, or about 300 s, inside the gate budget of 1,800 s.

## Effect on the conclusions
None on K4. The gate is the same kind of check, with a bar the solver configuration can meet. A failure of V1 or V2,
or any disagreement in V3, still means NO-GO.
