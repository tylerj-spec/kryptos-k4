# R75 L165 — T2 setting-by-setting F1X replay

Affected ledger IDs: L165
Validation: `python3 -I r75/audit/replay_f1x.py --replay` on K4 + 20 shuffles (R75 target) and 20 shuffles (R83 target), all 692,224 settings each, with `r75/audit/f1x_safe.py` (its own exhaustive toy oracle in `r75/audit/tests/test_f1x_safe.py` passes); `--compare` against `r75/k4/EXACT.json`, `r83/k4/run/R83A.json` and the original `f1x()` re-run with its decode branch off: 0 feasibility disagreements, 5,670 count disagreements, all true counts ≥ 2^63; `t2_overflow_17.py` confirms R83a's NULL_010/NULL_011 account. All jobs COMPLETE under `audit/run_bounded.py`.
Independent review: NONE. One model (Claude Code) wrote the driver and this note; the checker `f1x_safe.py` was written earlier by another model (ChatGPT).

## Change to L165
The audit qualifier gains a T2 line: feasibility and tallies confirmed independently. Only solution counts ≥ 2^63 were wrong, and none of the archived listed settings has one. The blind NO_SIGNAL and the "no readable decode" statement are not replayed here.
