# S105 solver validation plan (Claude Code, 27 Nov 2026): work order, not yet registered or run

Affected ledger IDs: none. This is a plan only.

Validation: desk design. It answers item 2 of §6 of `audit/reviews/R108_R111_CHATGPT_QUALITY_REVIEW_20261127.md`.
It inventories the corpora in the repository: the Carter OCR, `k4kit/data/k1k3_plaintext.txt` and
`k4kit/data/reference_messages.json`, which contain K4 crib words and are therefore unsuitable.

Independent review: NONE (one model).

## Why
R105's GO used one corpus (Carter OCR) with no enforced split. Its endpoint was ≥ 90/97: 42/50 met it, but only
17/50 were exact. Re-encryption was checked from position L only. The quadgram model's training text is
undocumented: `r33/sealed/R33_SOURCE_PROVENANCE.md` says only that it is "unchanged from the preceding local history
bundle". Before S105 is used more widely (R106, or any R111 follow-up), its reliability needs measuring on text it was
not tuned on.

## Design (to be registered as its own round once this plan is accepted)
1. **Enforced text partition.**
   - Split the Carter OCR into a **development half** (the first 50%) and a **test half** (the last 50%). Leave a
     2,000-letter gap between them.
   - Draw test windows only from the test half. Assert in code that every window is disjoint from every
     development window used in R105 and R111; their seeds are known, so they can be regenerated.
   - Add the **K1–K3 plaintext** as a small out-of-style set: overlapping 97-letter windows, reported separately.
2. **A quadgram-overlap sensitivity arm.** Build a second quadgram table from the **development half only**. Run the
   test set under both tables. If recovery drops sharply under the clean table, the undocumented table is suspect for
   overlap. This replaces the impossible task of tracing that table's training text.
3. **Balanced cells.** 10 plants in each of R111's 20 cells (B ∈ {AZ, KRY} × L 1–5 × σ), so 200 plants. R105's lag
   range adds L 1–5 with random B, so 50 more.
4. **Endpoints and witnesses.**
   - **Endpoints:** exact 97/97, ≥ 95, ≥ 90, and the letters-right distribution.
   - **Witnesses:** emit the primer and forward-encrypt all **97** letters with `r100/autokey100.py`. Any failure
     **voids** that plant's recovery, so the round fails closed.
5. **Failure classes.** These are R105's: lost at stage 1, stage 2 or stage 3; annealer gap; scorer counterexample.
   They are counted per cell.
6. **Decoys under the full search.** These decoys get the full 20-cell search:
   - 40 random;
   - 40 letter-shuffles of test plants;
   - 20 periodic Quagmire III;
   - 20 plaintext autokeys with **both** alphabets random.

   The last group is R106's case, which tests whether S105 is fooled when B is not on the list. The calibration is the
   maximum over cells.
7. **Bars, fixed in the registration before any run.** These are proposed:
   - an exact-recovery rate with a 95% lower bound;
   - ≥ 90 recovery in every cell group;
   - no decoy above the lowest recovery.

   Development runs may use only the development half.

## Dependency and scope
- **Synthetic only, with no K4 input.** It measures S105. It does not rely on R105's GO being right, so it could run
  during the batch-B audit, or as part of it.
- **It must not tune S105 toward R111's K4 outputs** or its post-freeze clue counts. Any solver change found here
  becomes a new solver version, with its own registration.
- **If S105 fails these bars,** R111's NO_SIGNAL stays as it is (solver-limited). R106 then needs a better solver
  before it is worth running.
