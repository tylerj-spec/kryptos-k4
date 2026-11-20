# T6 item 3, part 1 — R40 (L134) and R42 (L136) one-free-alphabet exclusions replayed

Affected ledger IDs: L134, L136
Validation:
- `python3 -I r40/audit/tests/test_onefree.py` passes: pure-Python reference; fresh plants in both modes found at V = 0; minimum settings re-verified.
- The kernel's sampled brute-force self-check never fired.
- Plan pushed before the run.
- 20/20 jobs equal the archived REVEAL.json whole-family results (`r40/audit/REPLAY_ONEFREE.json`).
- Run COMPLETE under `audit/run_bounded.py`.
Independent review: NONE. One model (Claude Code).

## Change
A T6 REPLAY qualifier is appended to L134 and L136. Status: replayed, one model. Not promoted (rule 10). L135 (R41) is not yet replayed.
