# R103 pre-registration (Claude Code, 26 Nov 2026): is a 97-letter two-free-alphabet autokey ciphertext identifiable?

**Type: synthetic measurement. No K4 input of any kind.**
- **Batch:** `audit/reviews/BATCH_WORK_ORDER_R102_R107.md`, item R103.
- **Procedure:** `audit/OPERATING_PROCEDURE_ROLLING.md`.
- **Dependency:** R102's code only (`r102/s3b102.py`, `r102/dfs102.py`, hashed in `PROTOCOL.sha256`). Gate checks G1–G2
  below re-verify it, so nothing rests on R102's unaudited claims.

**Independent review: NONE** (one model). R103 is part of audit batch B.

## 1. Question
In the S3b family (two free alphabets, F ∈ {A, B, AZ}, any signs, c and primer), does a 97-letter ciphertext
determine its plaintext among ordinary English texts?

**The measure.** How often does an *unrelated* English passage pass R102's exact consistency test against a planted
ciphertext? If unrelated English essentially never fits, then English plaintext is identified by the ciphertext.
That would make a blind solver worth building (R104/R105). If it often fits, S3b is unidentifiable at 97 letters,
and the batch's stop rule cancels R105 and R106.

**Limit.** Random unrelated passages are not adversarial near-English texts produced by a search. R104 studies those.

## 2. Data
- **Plaintexts and passages:** random 97-letter windows of `r33/data/source_carter_mace_1923_google_ocr.txt`,
  reduced to A–Z. Windows containing a published K4 plaintext word are skipped, as in R102.
- **Plants:** 300 planted ciphertexts. L cycles through {1, 2, 3, 5, 8, 13, 21, 40}, with uniformly random alphabets
  A and B, F, signs, c and primer, encrypted with `r100/autokey100.py`.
- **Unrelated passages** are drawn independently of each plant's own window.
- **Seed:** 1030901.

## 3. Registered computations (in this order)
| Step | What | Size |
|---|---|---|
| G1 soundness | Every plant's true plaintext (97 letters) at its true cell is CONSISTENT, with a witness that re-encrypts | 100 plants |
| G2 two solvers | `s3b102` and `dfs102` agree wherever both decide | 40 hypotheses (20 true, 20 unrelated; lengths 60 and 97) |
| **M2 (primary)** | A 97-letter unrelated passage against a plant, judged over **all 12 (signs, F) cells at the plant's true L**. A **hit** is any cell CONSISTENT, or UNDECIDED after the DFS (node cap 100,000); counting undecided cells as hits is conservative | 300 plants × 10 passages = **3,000 trials** |
| M1 (curve) | Prefix length n ∈ {30, 45, 60}, the plant's true cell only, with the same hit rule | 300 trials per n |
| M3 (unknown lag, exploratory) | 97-letter passages over all 12 cells × lags 1–24 | first 100 plants, 1 passage each |

**Time guard (registered, not an amendment).** The steps run in the order above. If cumulative CPU reaches 1,400 s,
the remaining M1 and M3 trials are skipped and their sections are marked TRUNCATED with the counts so far.
- G1, G2 and M2 are never truncated, and run first.
- The development estimate for the whole run is about 900 s.

**Verdict:**
- **IDENTIFIABLE** if G1 and G2 pass and M2 has **0 hits in 3,000**, so the rate is < 10⁻³ at 95%;
- **NOT_IDENTIFIABLE** if M2's hit rate is ≥ 1%;
- otherwise **UNCLEAR**.

Per-lag breakdowns of M2 and M1, and M3's hit count, are reported. A failure of G1 or G2 is a stop condition.

**Budget:** `audit/run_bounded_agg.py`, 1,800 s wall / 1,800 s CPU / 2,048 MiB, zero retries.

**Development figures** (seed 91, not this run):
- M2-style full-length union over 12 cells: 0/60 hits, about 0.08 s per trial.
- True-cell prefixes: 20/60 hits at n = 30, 9/60 at n = 45, 5/60 at n = 60 (that last over 12 cells).

## 4. Order
1. This file, `QA_MANIFEST.json` and `PROTOCOL.sha256`.
2. Source and `SOURCE.sha256`.
3. The run, then `OUTPUTS.sha256`.
4. The result note.

Nothing from R103 touches K4.
