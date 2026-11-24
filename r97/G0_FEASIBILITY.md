# R97 G0: what joint recovery can lead to, and the throughput of a full pipeline

Written before any R97 source. It answers the mandatory reviewer challenges in
`audit/reviews/POST_R96_NEXT_STEPS_20261123.md` (ChatGPT, PR #113).

## 1. Can a true-wiring-free full pipeline search the structural labels within its cap? **No.**
RX2-O has 16,640 structural labels, and 16,256 distinct (contact pair × 97-position schedule) combinations
(computed from `audit/backlog/multirotor/solver/rx2o.py`).
- Without a structure-pruning method, every one must be solved jointly per input.
- At R96's measured 1.34 million order-5 proposals per CPU second:

| Effort per label | CPU s per input | Fresh gate, 360 inputs (cap 7,200 CPU s) | K4 + 200 shuffles |
|---|---|---|---|
| One conditional anneal, 230,000 proposals (a floor; joint must cost more) | 2,790 | 1.0 M s: **140× over** | 6.5 CPU-days |
| R96's per-condition effort (16 anneals) | 44,600 | 16 M s: **2,200× over** | 104 CPU-days |
| R97 version 1's planned per-case effort | 140,000 | 50 M s: **7,000× over** | 325 CPU-days |

**Consequence, fixed now and independent of R97's outcome.** No RX2-O fresh gate and no RX2-O K4 run will be
designed unless a **structure-pruning method** is first shown on synthetic data. That means ciphertext-only
statistics, or a staged search, that cut the labels needing a joint solve by at least the factor above, without
losing the true label. This is the prospective revision the challenge requires ("STOP before K4 and revise").

## 2. Is R97 still worth running? Yes, by the charter's decision test
| R97 outcome | Next action |
|---|---|
| **GO** (joint recovery works with the structure supplied) | Structure-pruning research becomes the RX2-O bottleneck. It gets its own type C work order and synthetic test. No fresh gate yet |
| **SOLVER_NO_POWER** | Stop the RX2-O solver line. Effort moves to the construction-discovery lane |

The two outcomes lead to different actions. Cost: under 30 CPU minutes.

## 3. The other challenges
- **"Does joint alternation have a path to success, or does it cycle among local optima?"**
  - Version 1 is alternating conditional optimization with fresh-start and warm-start anneals at every step.
    Version 2 adds kicks between fixed points (iterated local search).
  - After the freeze, two truth-assisted diagnostics measure the path directly, reported and not gated:
    - D1: is the true key a fixed point of the alternation?
    - D2: from U = the true U with 4, 8 or 12 random swaps and V random, does alternation reach the truth? That
      gives the size of the basin a future initializer would need to hit.
  - Prior evidence is candid: random-start joint annealing found 0/48 (RX2-O dev v2/v3, and R94).
- **"Objective failure or optimization failure?"** Every top-1 is diagnosed (search gap / objective counterexample /
  alias), as in R96. R96's 4 conditional misses were objective counterexamples, and they bound what any joint solver
  can reach (≤ 44–47/48 per condition).
- **"Is the panel too familiar?"** Yes, it is spent. Every R97 result is labelled **spent-panel development**, never
  generalization.
- **"Keep K4 known letters out."** R97 reads no K4 file, no published letter and no clue-derived input.
