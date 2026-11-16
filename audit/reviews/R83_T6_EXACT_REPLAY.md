# R83a L172 — T6 item 1: independent replay of the EXACT step

Affected ledger IDs: L172
Validation: `python3 -I r83/audit/tests/test_replay_exact.py` (toy brute force over every key, 33 max-parameter plants, agreement with exact83 on random ciphertexts); replay plan committed before any K4 run (`r83/audit/REPLAY_EXACT_PLAN.md`, e97aa0c); all jobs COMPLETE under `audit/run_bounded.py`; 0 disagreements (`r83/audit/REPLAY_EXACT.md`).
Independent review: NONE. One model (Claude Code) wrote the checker, ran it and wrote this note. Multi-model review has not been run.

## Change to L172
The EXACT verdicts are now independently reproduced:
- WPX, PFX, SLX, SLX-A and SSX in full on K4 and 20 shuffles;
- LX in full on K4, and as a sampled replay on 5 shuffles.

No verdict changes. The DROP and SHIFT steps of SLX, SLX-A, SSX and LX are not covered.
