# RX2-O v1–v3 source and resource review

Reviewer: ChatGPT, source review at main
`9e4bd400e64c6aa46ae3afdc9ba0d82a1a927fd1`.
This is a review of Claude-authored historical work, not a fresh multi-model
recovery experiment. The R94 mathematical/self-test and saved-output replay
are prospective at this note's publication. No new candidate job has run.

## Finding: the bounded failure is real, but some wording overstates it

- **v1 remains INCOMPLETE.** `dev/run_v1.py` accumulates completed candidate
  work in memory and creates the full language scorer before saving results.
  Its resource log records a failure. The model loader's whole-file mapping
  plus per-order mappings explain a virtual-address-space limit failure even
  with a small sampled resident set. No saved candidates support a recovery
  numerator or denominator. Treating it as zero recovered out of 48 would be
  unsupported.
- **v2 and v3 report zero recovery among saved final states.** Their kernels
  save each restart only after annealing and greedy polishing. They do not
  save the best-ever state during annealing, nor every visited plaintext.
  Therefore the historical phrase “no restart reached 95” must mean no retained
  final restart state had at least 95 matching letters. It cannot be extended
  to every state visited. A later implementation should explicitly preserve
  the best objective state if it wants that stronger retention claim.
- **The v3 objective is not proved adequate.** Its committed diagnostic has
  the true order 5 score above every saved final state in 47/48 rows, showing a
  missed known feasible score in those rows. One wrong saved state scores
  about 1.06 log10 units above its true text. No global optimum or unique
  plaintext was established. “The objective is now right; remaining failure
  is search” is too strong. Search and scoring limitations can coexist.
- **The full unknown-structure gate remains impractical with this kernel.**
  The v2 annealing job used 1,371.670 CPU seconds for 48 supplied branches;
  v3 used 1,248.559, about 28.58 and 26.01 seconds per branch respectively.
  A 360-item by 16,640-label catalog has 5,990,400 branch solves. A 7,200 CPU-second
  allowance would provide approximately 1.202 milliseconds per branch before
  scoring or orchestration. This extrapolation is roughly 21,600–23,800 times
  below the observed per-branch cost. It describes the current method, not a
  lower bound for every future solver.

The scalar forward witnesses and matching-letter counts can be independently
recomputed from saved keys and texts. The original full R59 language model is
not present here, so this review does not claim a numerical replay of the
original order 5 or order 6 scores or authentic blind generation. R94 uses the
explicitly weaker order 4 construction and reports it as a new objective.

## Complete recorded resource accounting

All 17 committed logs are included, with their digests in
`V1_V3_RESOURCE_REVIEW.json`. Failures consume resources and are included.

| Version | Recorded jobs | Wall seconds summed | CPU seconds summed | Largest sampled aggregate RSS MiB |
| --- | ---: | ---: | ---: | ---: |
| v1 |4 |681.216 |1,337.784 |59.2 |
| v2 |7 |705.573 |1,377.248 |1,092.7 |
| v3 |6 |639.875 |1,254.518 |1,270.5 |
| All versions |17 |2,026.664 |3,969.550 |1,270.5 |

Each version's complete recorded sum is below its own 1,800-second CPU and
wall budget and 2,048 MiB memory cap. The combined three-version sum is not
compared to a single-version allowance. Failed v1 search, the failed v2 model
load, and the failed initial v3 import are all counted. The small v1 speed job
references a temporary script whose exact source was not committed; its
recorded cost is included but that job is not fully reproducible from the tree.

These sums are an ex-post audit of all committed logs, not proof that no
unlogged work occurred. The wrapper enforces a job's process-group limits;
the original separate jobs did not share a persistent cumulative budget
enforcer. R94 instead uses one outer wrapper for its entire work order.

## Structural next step and identifiability

For fixed V, solving U under a sum of per-letter scores is an exact linear
assignment; the same holds with U and V exchanged. Both blocks therefore
admit complete conditional moves. The higher-order linearized assignment
proposals in R94 are explicitly heuristic and accepted only by their actual
score. The distinction matters: adding n-gram interactions destroys the
simple additive assignment objective.

Normalized segment maps satisfy `G_delta = H^delta F`, with
`F = W2 W1` and `H = W2 T1 W2^-1`, a 26-cycle. This is an exact relation
among segments, even across slow-rotor turns, and removes the global
interface-shift gauge. It does not identify unused contacts or guarantee a
unique language interpretation of 97 observations. A raw `(26!)^2` label count
cannot by itself prove an information-theoretic barrier, because many key
labels are gauge-equivalent or unobserved on a finite text.

R94 separates both-unknown results from true-U/true-V conditions and from
true-key local score counterexamples. Each is useful, but none can substitute
for a fresh sealed unknown-structure gate with negative controls. Nothing in
this review authorizes a K4 execution or excludes RX2-O as a family.

## Source references

- `audit/backlog/multirotor/solver/kernel/anneal2.c` and `anneal5.c`: proposals,
  annealing, final polishing and final-state retention.
- `audit/backlog/multirotor/solver/dev/run_v1.py`: v1 output ordering.
- `audit/backlog/multirotor/solver/dev/run_v2.py` and `run_v3.py`: saved raw
  states, retention, reranking, lean model mapping and fixed parameters.
- `audit/backlog/multirotor/solver/dev/v2/DIAG.json`, `EVAL.json` and the
  corresponding v3 files: historical scores and reported recoveries.
- Every `*RESOURCE_LOG.json` under the three version directories: all 17 jobs.
- `r91/MODEL_RECEIPT.json`: exact lower-order reconstruction basis and the
  explicit absence of comparison to the original full-model binary.
