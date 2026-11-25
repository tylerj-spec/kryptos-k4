# R102 Amendment 1, PROPOSED (not applied): C3 must not count UNDECIDED cells as soundness failures

**Status: PROPOSED; review requested.** This is stop condition 2 of `audit/OPERATING_PROCEDURE_ROLLING.md`: a
pre-registered pass condition needs changing. The registered run (seed 1020901) has **not** been run, and nothing
has touched K4.

## The issue
Registered C3: "The true plaintext (full, and the first 60 letters) is CONSISTENT … 240/240."

The primary solver is registered to return UNDECIDED when its mod-13 solution space has dimension > 7. Some C3 cells
are underdetermined by design. A 60-letter prefix at lag 40 has only 20 equations, against up to 53 unknowns, so
those cells come out UNDECIDED, not CONSISTENT, and C3 would fail on them. Nothing would be wrong in the algebra or
the solvers. This was an oversight in writing C3.

**Development evidence** (seed 77, `dev/DEV_SMOKE.txt`):
- 2 of 32 true hypotheses were UNDECIDED (L 40, n 60, dimensions 9 and 12);
- the DFS second solver decides both CONSISTENT;
- no true hypothesis was INCONSISTENT under either solver.

## Proposed change (soundness is unchanged)
**C3 passes iff all of the following hold:**
- **(a)** no true hypothesis is INCONSISTENT under either solver;
- **(b)** every true hypothesis the primary leaves UNDECIDED is CONSISTENT under the DFS solver with node cap
  2,000,000;
- **(c)** every CONSISTENT verdict of the primary comes with a witness that re-encrypts to C at every constrained
  position.

The number of primary-UNDECIDED cells is reported. Nothing else changes.

## Alternative
Keep C3 as registered and drop lag 40 from C3's lag list, so that every C3 cell has at least 37 equations. This is
also a change to the registered computation, so it needs the same review.
