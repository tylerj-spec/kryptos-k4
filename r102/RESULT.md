# R102 result (Claude Code, 26 Nov 2026): the two-free-alphabet autokey, algebra VERIFIED, and one prediction refuted

**Type:** analysis with synthetic verification. No K4 input.
**Verdict:** **VERIFIED.** C1–C4 all pass. C5 refutes the round's own prediction T4.

## In plain words
**Why the family can be analysed exactly.** Every ciphertext letter is fixed by a table lookup on the pair of
plaintext letters L places apart, and the table has a simple group structure. That makes it possible to decide
exactly whether a proposed plaintext could have produced a given ciphertext, for any pair of alphabets. The test is
a set of linear equations mod 26 in which both unknown alphabets must be genuine permutations.

**What we learned:**
1. **A full plaintext guess is checked exactly and cheaply.** True plaintexts always pass, with a reconstructed key
   that re-encrypts. Unrelated English passages fail, both at full length and at 60 letters (C4). R103 measures this
   properly.
2. **The published letters have more exclusion power than expected.** On random inputs shaped like K4's two clue
   windows, only about 58% of (lag, signs, F) cells admit any pair of alphabets. That is against the predicted
   ≥ 90%. So an exact crib check **does** exist for this family, and it excludes roughly 4 cells in 10 by chance
   alone. This corrects `audit/reviews/S3_STATUS_20261125.md`, which said there was none.
3. **There is a weak ciphertext-only signature at lag 1.** Repeated adjacent ciphertext pairs are more common than
   in shuffles: a mean of 13.3 against 7.9, detected 41% of the time at a 5% false-positive rate. At lags 2–3 it is
   too weak to use (9–11%).

## Results (`run_v2/RESULTS.json`, frozen in bc7374d)
| Check | Result |
|---|---|
| C1 Latin-square reduction (T1) | 400/400 |
| C2 gauge invariance (T2) | 200/200 |
| C3 soundness (T3; Amendment 1) | 240 true hypotheses: **0 INCONSISTENT** under either solver; 16 left UNDECIDED by the primary, all CONSISTENT under the DFS; 0 bad witnesses |
| C4 two solvers | 58/60 decided by both, **0 disagreements** |
| C5 crib-shaped windows (T4; Amendment 2) | 1,200 cells: 512 CONSISTENT, 372 INCONSISTENT, 316 UNDECIDED. Share consistent 0.579, so the prediction of ≥ 0.90 is **refuted**. At most 22 equations; mod-13 dimension ≥ 2 |
| C6 lag-L repeated pairs (T5) | L 1: mean 13.3 against 7.9, power 0.41. L 2: 9.0 against 7.1, power 0.11. L 3: 7.7 against 7.0, power 0.09 |

**Runs:**
- **v1** (seed 1020901) was **INCOMPLETE**: stopped at the 1,800 s wall cap, with no output (`run_v1/INCOMPLETE.md`).
  The cause was C5's cost on the primary solver.
- **v2** (seed 1020902, under Amendment 2) **COMPLETE**: 213 s wall, 212 s CPU, peak 256 MB, zero retries.

**Amendments, both approved by Tyler before the run they affect:**
- **Amendment 1:** C3 judges soundness over both solvers.
- **Amendment 2:** C5 is decided by the DFS alone, and v2 uses a new seed.

## What follows
- **R103 (identifiability)** can use the exact consistency test. Its own gate re-verifies the test.
- **A new exact round on K4** becomes possible: the S3b direct-pair crib check, for every pair of alphabets. It is
  outside the approved batch, so it is proposed in `audit/ROLLING_QUEUE.md` for approval.
- **A ciphertext-only lag-1 test** of K4 becomes possible too, with power about 0.4. It would be a blind round and is
  also proposed for approval.

## Review
**Independent review: NONE.** One model (Claude Code) built and ran R102. It is part of ChatGPT's next audit batch.
