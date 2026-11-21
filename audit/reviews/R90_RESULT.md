# R90 — L179: the 15 F26L alphabet classes R89 left open, gate GO, K4 blind NO_SIGNAL, exact EXCL

Affected ledger IDs: L179
Validation:
- Pre-registration cd411e9 (`r90/PREREGISTRATION.md`, `r90/PROTOCOL.sha256`). It follows the requirements of ChatGPT's R89 review (`r89/audit/REVIEW_20261121.md`):
  - the actual catalog, taken from its `ALPHABET_SCOPE.json`;
  - an explicit retention rule;
  - a key-equivalence definition;
  - an aggregate budget;
  - fresh controls;
  - the ≥ 22/24 ciphertext-error screen.
- Development on spent books (`r90/dev/DEV.md`); nothing tuned. `python3 -I r90/tests/test_r90.py` passes (10 groups).
- Sealed gate on four fresh genre books, truth committed only as a sha256 before the run: GO.
  - 48/48 with the right key;
  - retained 48/48;
  - 0/150 negatives confident.
- Runs under `audit/run_bounded_agg.py`: COMPLETE.
  - Amendment 1: the first gate launch was killed by the aggregate memory budget before any output.
  - Witness 1,259/1,259 and 1,302/1,302; determinism 8/8 twice.
- Freezes pushed before the truth (167afe6) and before any published letter (ab3447b).
- K4: NO_SIGNAL, p_family 0.751, 1/24.
- Exact: no setting at ≥ 22/24 (K4 max 6/24); cross-checked by full decryption.
- Guardrail check PASS.
Independent review: NONE. One model (Claude Code) built and ran R90. No `Promotes:` line.
