# L172 — corrected WPX one-wrong-letter strength, recalibrated against the shuffles

Affected ledger IDs: L172
Validation:
- PR #90's claim reproduced independently with T1's checker: witnesses 1, 1, 2, 2.
- `python3 -I r83/audit/tests/test_wpx_drop_strength.py` passes (survivors equal T1's; strength equals direct enumeration on 1,152 toy settings).
- Plan pushed before the run (32dc662).
- Scan COMPLETE under `audit/run_bounded.py`.
Independent review: PARTIAL. ChatGPT found the defect (PR #90, merged). Claude Code reproduced it and ran the recalibration. Not a multi-model council review.

## Change to L172
The withdrawn "eff 4, 12/20 shuffles" comparison is replaced by the calibrated statistic:
- K4 max s = 2;
- no setting at s ≥ 3 (NO_WITNESS_S_GE_3);
- p_family 0.38.
