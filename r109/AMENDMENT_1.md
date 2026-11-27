# R109 Amendment 1 (Claude Code, 27 Nov 2026): primary enumeration limit dmax 7 → 5 (before any source or gate)

**Status:** PROPOSED. It is committed before the source and before the gate, and is reported to Tyler at once under
the rolling procedure §4.2. It applies only if approved.

## What changes
In §2 of `PREREGISTRATION.md`, the primary solver `s3b102.solve` runs with **dmax = 5** instead of its default 7.
A cell whose mod-13 solution space has dimension 6 or 7 becomes primary-UNDECIDED. Then:
- **EXACT verdict:** the DFS (node cap 100,000, unchanged) decides it, as for any primary-UNDECIDED cell, or it stays
  UNDECIDED.
- **DROP variants and the shuffle counts:** the primary alone is used, so such a variant counts as not excluded.

Everything else is unchanged.

## Why
**Development timing** (dev seeds 1091–1093; random ciphertexts and random 13 + 11 masks; no K4 data):
- With dmax 7, one primary call with a 6- or 7-dimensional space enumerates up to 13⁷ ≈ 6.3·10⁷ points. A dev run
  stalled for over 8 minutes on a few such cells.
- The registered budget (3,600 s) covers about 2,000 primary calls on K4 plus the shuffles. It cannot absorb such
  calls.
- With dmax 5 over 60 dev cells:
  - the primary took a median 0.00 s and a maximum 0.06 s;
  - the DFS (cap 20,000) took a median 0.001 s and a maximum 0.34 s.

## Effect on the conclusions
The change can only move a cell from a decided verdict to UNDECIDED, or leave it to the DFS. Both solvers are sound
in each direction: INCONSISTENT is a proof, and CONSISTENT comes with a witness. So:
- the change cannot create an exclusion;
- it cannot turn an exclusion into a consistency claim.

At worst, some exclusions that dmax 7 would have found are missed.
