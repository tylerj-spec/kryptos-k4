# R32 historical closeout plan

Scope: post-freeze, crib-assisted audit of L117's archived fixed-alphabet whole-family counts at `k4kit/r32/runs/WHOLE_FAMILY.json`. No candidate generator, plaintext output, missing-key completion or new family. Original evidence remains unchanged.

The independent kernel turns each published plaintext equality under a fixed route/convention into an expected numeric key symbol. It counts those equalities for every fixed keystream, avoiding full-text reconstruction. Every histogram bin is compared with the archive, not merely the maximum. Counts are interpreted as labeled settings, including duplicates and equivalent conventions.

Five jobs: F1 CARTER, K1K3, G5 and C6 over 41 route-orders and 12 conventions; F2 G5 over 5,000 route-orders and 12 conventions. Every text window, forward/reversed direction and AZ/KRY numbering is included. Every chain primer is included. Routes are independently reconstructed from coordinate orderings and compared with the archived F1 routes and the historical constructor for F2. Input/source bytes and all generated route files are hashed.

Before reading K4: exhaustive small-alphabet route/order/tableau oracle; independently encrypted planted messages at first/last running-key offsets and first/last 5/6-digit primers; complete short/final-block route permutations. Compare the compiled match counter with direct Python decryption on synthetic inputs. A synthetic-only benchmark over fixed route/key counts estimates the full job cost.

Budget: one process, at most 1,800 wall seconds and 1,200 aggregate CPU seconds for the five target count jobs combined; 2,048 MB aggregate resident memory. No retry after target-result inspection. Synthetic development/benchmark is separately capped at 180 wall/120 CPU seconds. Every target-reading job is launched through the current bounded wrapper and the aggregate budget is independently monitored.

Decision before target input: if the synthetic benchmark projects more than 80% of either full-run cap, run only a fixed diagnostic sample: every 100th route-order plus the first and last route-order, all conventions and all keys. That outcome is SAMPLED_REPLAY and does not close the original aggregate-count item. Otherwise run all five jobs. Interrupted/failed work is INCOMPLETE and never a negative cryptographic result. A mismatch or any full 24-letter match is a stop-and-report event; no automatic extension or retuning.

Full-count closure requires exact equality of all five histograms, their total settings and maxima. A sampled result or a replay of only the retained top100 rows cannot close it. This ChatGPT audit reviews the historical Claude implementation, but promotion still requires the coordinating review note and explicit scope.
