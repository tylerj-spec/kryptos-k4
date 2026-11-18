# T6 item 2 — R79 (L169) and R81a (L170) keyword exclusions replayed

Affected ledger IDs: L169, L170
Validation:
- `python3 -I r79/audit/tests/test_replay_kw.py` passes: slot rules equal the originals' encryption-side state machines; counts equal the pre-registered totals; feasibility equals exhaustive keyword search; 24/24 one-wrong-plaintext-letter plants flagged at the right position.
- Plan pushed before the run (`r79/audit/REPLAY_KW_PLAN.md`).
- Both replays COMPLETE under `audit/run_bounded.py`.
- 132/132 comparisons equal (`r79/audit/REPLAY_KW_COMPARE.json`).
Independent review: NONE. One model (Claude Code) wrote the checker, ran it and wrote this note.

## Change to L169, L170
A T6 REPLAY qualifier is appended. Status: **replayed, one model**. Under guardrail rule 10 these rows are not promoted. Neither the H11 routes (L169) nor G5X (L170) was replayed.
