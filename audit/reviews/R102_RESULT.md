# R102: L191, S3b algebra VERIFIED (synthetic), and an exact S3b crib check exists

Affected ledger IDs: L191
Validation:
- **Order of commits:**
  - pre-registration 529680c;
  - source a7ae384;
  - Amendment 1 (Tyler, "Go with the recommended") 7c7d20f;
  - run v1 INCOMPLETE on the wall cap, recorded in be3a43f;
  - Amendment 2 (Tyler, "Do recommend") b591c20;
  - run v2 COMPLETE, frozen in bc7374d.
- **Checks:** C1 400/400; C2 200/200; C3 0/240 true hypotheses rejected; C4 0 disagreements on 58.
- **C5:** 57.9% consistent among decided cells, which refutes the prediction.
- **C6:** lag-1 power 0.41.
- **Resources:** COMPLETE under `audit/run_bounded_agg.py`, zero retries. Guardrail check PASS.
- **CI:** `.github/workflows/r102-algebra.yml` re-runs `run102.py` and compares every result except timings.

Independent review: NONE. One model (Claude Code) built and ran R102. It is part of audit batch B (ChatGPT).

## Summary
R102 is the algebraic base for the S3b line, the plaintext autokey with two free alphabets.
- **Reduction:** every ciphertext letter is a Latin-square entry at the plaintext pair L apart.
- **Consistency test:** whether a closed plaintext hypothesis fits is decided exactly, by linear algebra mod 26 with
  bijectivity, and comes with a witness.
- **Correction:** the published letters do give an exact crib check for the family; about 42% of random cells are
  infeasible. This corrects the S3 status note.

Two new rounds are proposed for approval in `audit/ROLLING_QUEUE.md`:
- **P1:** the exact S3b crib check on K4;
- **P2:** a ciphertext-only lag-1 test on K4.
