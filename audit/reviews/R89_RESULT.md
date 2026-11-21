# R89 — L178: F26L and RCT, per-arm gates GO, K4 blind NO_SIGNAL, both exact EXCL

Affected ledger IDs: L178
Validation:
- Design by ChatGPT (PR #98), reviewed by a different model (Claude Code) in `r89/REVIEW_PR98.md`. That review found:
  - the finite F26L space could be enumerated in full;
  - two F26 equivalences, including reversed alphabets;
  - an exact check for each arm.
- Pre-registration 935a403 (`r89/PREREGISTRATION.md`, `r89/PROTOCOL.sha256`). Development on spent books at the gate's full size (`r89/dev/DEV.md`); nothing tuned.
- `python3 -I r89/tests/test_r89.py` passes (11 groups):
  - round trips, every final-block length and the K1/K2 openings;
  - witness vs reference;
  - 20 distinct alphabet classes;
  - exhaustive solver vs reference, and the kernel frame;
  - three-way exact-check agreement;
  - error propagation;
  - witness failures;
  - the holdout maker;
  - the per-arm bars;
  - sandbox refusals.
- Sealed gate on four fresh genre books, truth committed only as a sha256 before the run: F26L GO 47/48, RCT GO 42/48, 0/150 negatives confident.
- Both runs isolated under `audit/run_bounded.py`: COMPLETE.
  - Independent stdlib witness 1,833/1,833 and 1,428/1,428.
  - Determinism 8/8 twice; kernel identical to a clean compile.
- Freezes pushed before the truth (59a6a91) and before any published letter (60a5b77).
- K4: NO_SIGNAL, p_family 0.453 over 200 shuffles, 1/24.
- Exact checks:
  - F26L/F26: no setting at 24/24 or ≥ 23/24 (K4 max 7/24);
  - RCT: 0 of 448 feasible, also with any one or (extra) any two letters set aside;
  - cross-checked with second implementations.
- Guardrail check PASS.
Independent review: NONE for the execution. The design had a second-model review (Claude Code reviewing ChatGPT's design), which does not count as independent review of this run. No `Promotes:` line.
