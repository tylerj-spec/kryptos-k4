# T3 — R81a (L170) drop-one soundness, and other one-letter-wrong claims

Affected ledger IDs: L172
Validation: source review only (`r81a/audit/DROP_ONE_REVIEW.md`, with file and line citations); R81a's existing post-freeze power control `r81a/sealed/control_validate81.py` already re-encrypts from an altered plaintext letter. Nothing was run on K4.
Independent review: NONE. One model (Claude Code) did the review.

## Outcome
- L170: no change. Every R79/R81a family it covers is plaintext-state-free (ciphertext feedback, fixed text streams, positional or cipher-letter-driven slot rules), and each published letter enters exactly one validator equation, so its drop-one is exact for one wrong plaintext letter.
- L172: only the Changes-section summary line for R83a was touched. A note was added that its "walking key also excluded with one published letter wrong" is superseded (WPX DROP = CHANCE after T1). The L172 row itself was updated under `audit/reviews/R83_T1_EXACT_DROP.md`.
- L35: flagged UNVERIFIED, not changed. Its source `one_error.py` is not in the repository. Its Hill 2×2/3×3 one-error claim would share the R83a defect if it meant plaintext errors, because one plaintext letter enters every equation of its block.
