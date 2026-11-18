# Guardrail rule 10 — promotion of exclusions needs a named independent reviewer

Affected ledger IDs: none
Validation: `python3 -I audit/tests/test_guardrails.py`, 40 tests, all pass. Five new tests:
- a single-model (NONE) promotion is rejected;
- a PARTIAL promotion is rejected;
- a row marked `INDEPENDENTLY VERIFIED` without a promoting note is rejected;
- a named YES review is accepted;
- a single-model replay that promotes nothing is still accepted.
Independent review: NONE. Claude Code wrote the rule. It implements Tyler's 18 Nov 2026 instruction ("I would make independent review a required condition for promoting major historical exclusions, rather than treating a note that says NONE as sufficient").

## Change
- `audit/FUTURE_TEST_GUARDRAILS.md`, G4: replays by the builder stay "replayed, one model". Promotion needs `Promotes:` plus `Independent review: YES <reviewer>`, where the reviewer is a different model or a person. Same-model roles and subagents count as NONE.
- `audit/check_guardrails.py`, rule 10: enforces that form.

No ledger row is promoted by this change. Earlier replays (T1, T2, T6) stay "replayed, one model" until independently reviewed.
