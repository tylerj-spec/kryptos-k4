# R87 — L176: one stepping rotor with an unknown wiring, gate GO, K4 blind NO_SIGNAL, exact EXCL

Affected ledger IDs: L176
Validation:
- Pre-registration 5af6212 (`r87/PREREGISTRATION.md`, `r87/PROTOCOL.sha256`); development on spent books only (`r87/dev/DEV.md`).
- `python3 -I r87/tests/test_r87.py` passes:
  - witness vs reference on 400 settings;
  - kernel vs explicit decrypt;
  - three exact-check implementations agree on 26,340 cases;
  - witness and sandbox refusals;
  - holdout maker;
  - gate bars.
- Sealed gate on fresh books, truth committed only as a sha256 before the run: GO, 45/48 positives, 0/90 negatives confident, 10/12 one-ciphertext-letter-wrong.
- Both runs in the isolated sandbox under `audit/run_bounded.py`: COMPLETE.
  - Independent stdlib witness: 750/750 (gate) and 505/505 (K4).
  - Determinism 8/8 for each run; sandbox kernel identical to a clean compile (Amendment 1, the compile race).
- Freezes pushed before the truth (a0b2fa9) and before any published letter (a204614).
- K4 evaluation: NO_SIGNAL, p_family 0.228, 2/24.
- Exact check (`r87/sealed/exact87.py`): 0 of 3,072 settings feasible, also with any one letter set aside. Cross-checked with `rotor87.exact_check`; extra two-letter set-aside also 0.
- Guardrail check PASS.
Independent review: NONE. One model (Claude Code) designed, built, ran and audited R87. No `Promotes:` line. ChatGPT's PR #95 (R85 pilot, R86) is a separate single-model run of an 8-setting subset, which this exact check now covers; I re-checked #95's archived outputs for internal consistency only.
