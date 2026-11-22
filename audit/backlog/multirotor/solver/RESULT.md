# RX2-O solver development (work order Priority 1): stopped after version 3, SOLVER_NO_POWER on development data

Affected ledger IDs: none. This is development evidence only: no cipher exclusion and no K4 run.
Validation: three declared versions on one fixed 48-plant panel (6 per turnover cell, spent books, `dev/panel/`), each
within `dev/BUDGET.json`. Every job ran under `audit/run_bounded_agg.py` with its log committed.
Independent review: NONE. One model (Claude Code) built and ran this, to ChatGPT's work order (`audit/NEXT_STEPS.md`)
as refined in `audit/reviews/NEXT_STEPS_REFINEMENT_20261122.md`.

## What was asked
ChatGPT's work order asked for a blind RX2-O solver, its two-rotor odometer (`../DESIGN.md`):
- with the true structural setting supplied first;
- at most 3 development versions, each within 1,800 s wall, 1,800 s CPU and 2,048 MiB;
- on spent data only;
- **stop after version 3 without a viable prototype**.

The screen it would have to pass next needs ≥ 18/20 top-ranked recoveries in each of 8 turnover cells.

## What the three versions show
| Version | Change | top-1 ≥ 95/97 | Found decodes above the truth | CPU s |
|---|---|---|---|---|
| 1 | joint annealing of both wirings, quadgram objective (32 × 3,000,000) | INCOMPLETE: the letter model could not be mapped under the per-process limit, so no output | — | 1,337.8 |
| 2 | version 1 unchanged, with the stages split | **0/48** | **16/48** by quadgram | 1,377.3 |
| 3 | order-5 letter-model objective (8 × 4,500,000) | **0/48** | **1/48** by order-5 | 1,254.5 |

1. **Not even the easiest cell is solved.** That cell is n = 4 with no slow-rotor turnover: a single rotor followed
   by a fixed arbitrary output substitution. R87's annealer solves the single rotor reliably when the output numbering
   is one of four known alphabets. Making that numbering a free permutation adds about 88 bits of key, and joint
   annealing from random starts does not find the truth.
2. **Quadgrams are the wrong objective for two free wirings.** With about 176 bits of key on 97 letters, the search
   finds non-English decodes that outscore the true text by quadgrams (version 2: 16/48). The order-5 letter model
   ranks the truth above everything the search found in 47/48 plants (version 3).
3. **The remaining failure is search.** At about 36–96 million proposals per plant (28–30 CPU s), no restart of
   1,920 reached 95/97. Version 3's decodes are 4–21 log10 short of the truth's order-5 score.
4. **Throughput.** The full-search gate would allow about 1.2 CPU ms per structural branch. Here 28 CPU s per branch
   fails with the structure supplied. Per-branch annealing is therefore at least four orders of magnitude short.

## What would have to change (not attempted; it needs a new, separately reviewed work order)
- **A different search, not more of the same:**
  - Use the structure: within each step block the fast rotor gives a monoalphabetic cipher, and across blocks the
    substitutions are related by conjugation. That calls for a constraint-propagating or isomorph-based search, not
    random-start annealing.
  - Or a staged search that fixes the output substitution's segment structure first.
- **Then a measured throughput** that can reach 1.2 ms per branch, or a pruning rule frozen before any gate.

These are suggestions. Under the work order's stop rule, this line of work ends here unless Tyler or a reviewer opens
a new one.

## Infrastructure lessons (kept for later rounds)
- `audit/run_bounded_agg.py` sets the per-process address-space limit (RLIMIT_AS) equal to the aggregate memory
  budget. `r75/core.Scorer` briefly maps the 1.29 GB letter-model file twice: a whole-file header map plus the
  per-order maps. So it cannot load under a 2,048 MiB budget.
  - `dev/run_v2.py lean_scorer` builds the same arrays without the header map. It gives identical scores on 20
    reference decodes.
  - A future 2,048 MiB round needs it, or a fix to the wrapper's address-space rule.
- Write expensive intermediate output before loading anything large. Version 1 lost 1,336 CPU s by not doing so.
