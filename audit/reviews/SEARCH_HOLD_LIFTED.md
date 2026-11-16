# Search hold lifted — owner decision, 16 Nov 2026

Affected ledger IDs: none
Validation: the lifting conditions of the deleted `audit/SEARCH_HOLD.md` were checked:
1. Guardrails and both corrections are merged: PRs #81–#85.
2. T1 and T2 of `audit/NEXT_STEPS.md` are complete and merged (PR #86). T6 item 1 is merged too (PR #87).
3. Tyler decided to resume.
Independent review: NONE. Tyler (owner) gave the instruction; Claude Code made the change.

## Decision
Tyler, 16 Nov 2026, in the Claude Code session after PR #87 merged: "You can merge code & do more in each run. Please try to get a legit solution for K4".

New K4 searches may resume. Every guardrail stays in force:
- preregistration before any run;
- a sealed synthetic gate that says GO;
- a QA manifest;
- freeze before reveal;
- bounded runs;
- no external submission without Tyler's explicit go.
