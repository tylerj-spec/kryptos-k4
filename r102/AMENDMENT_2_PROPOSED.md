# R102 Amendment 2, PROPOSED (not applied): a C5 scale that fits the budget, and a v2 run

**Status: PROPOSED; review requested.** These are stop conditions 2 and 6: run v1 exceeded its registered budget
(`run_v1/INCOMPLETE.md`), and the remedy changes the registered computation. Nothing has been re-run.

## Proposed change (recommended)
- **C5 uses the DFS solver alone** (node cap 50,000) to decide each crib-shaped cell.
  - The primary solver is skipped there. Its enumeration is the expensive part, and C5 asks only whether these
    underdetermined systems usually *have* a solution, which the DFS shows quickly by finding one.
  - The mod-13 dimension is still reported for each cell, from elimination only.
- **Run v2 once,** seed 1020902, as a new seed so that v1's interrupted stream is not reused. Same budget: 1,800 s /
  1,800 s / 2,048 MiB.
  - Expected: C1–C4 about 100 s; C5 1,200 cells at about 0.3 s each, about 360 s; C6 about 30 s.
  - That is well under the cap.

## Alternative
Keep C5 on the primary solver but reduce it from 40 to 10 windows (300 cells, about 400 s). It covers fewer cells
but keeps the same solver.

Everything else (C1–C4, C6, the verdict rule and Amendment 1) is unchanged.
