# Research charter: proposal note

Affected ledger IDs: none. No ledger row, frozen file, guardrail file or CI checker is changed.
Validation: documentation only. Every row, status and number cited in `audit/RESEARCH_CHARTER.md` was read from
`LEDGER.md`, `CURRENT_STATUS.md`, `audit/backlog/CLOSEOUT.md` and `audit/reviews/NEXT_STEPS_AFTER_R94.md` at
`3a48dec` (after PR #105). External facts were taken from pages opened on 22 November 2026 and are linked in the
charter's Sources section. `audit/check_guardrails.py --base origin/main --head HEAD` run locally before push.
Independent review: NONE. Drafted by Claude (research chat); ChatGPT review requested before or after merge.

Date: 22 November 2026 (America/Chicago).

## What is proposed

`audit/RESEARCH_CHARTER.md` adds a strategy layer above the round files. It sits below `r53/BLIND_RULES.md`,
`audit/FUTURE_TEST_GUARDRAILS.md` and `k4kit/CLAUDE.md`, which win any conflict. It adds:

1. a six-test bar for a legitimate answer, restating BLIND_RULES item 6 and the last G4 bullet;
2. eleven lessons from earlier rounds, each tied to the ledger rows that taught it (L23 through L183);
3. three declared round types: A blind search, B exact scope (aggregate-only), C solver development;
4. a five-question rubric for choosing the next family, with a decision test and a budget rule;
5. a K4 evidence budget: a signals register and a contact index;
6. an error-tolerance table of what is covered and what is not;
7. a seven-phase roadmap, a rethink checkpoint, triggers (K5, Paradigm's verifier, contamination) and six
   decisions for Tyler.

## How it reconciles with the earlier Claude drafts

The Claude Docs draft of 22 November and the R83 handoff of 14 November were written before R83–R94 were visible
to the research chat. This version corrects them:

- The "decode a crib-assisted survivor as a LEAD" step is removed. G3 forbids decoding crib-assisted survivors;
  type B rounds emit counts only.
- Claim labels now use the G4 vocabulary rather than new words.
- R80a (R84), the linked key's ±1-per-row schedule (R83a LX) and the single position-stepped rotor through
  period 96 (R87, R92, R93) are recorded as done, not queued.
- The roadmap now leads with the review backlog and solver capability, following
  `NEXT_STEPS_AFTER_R94.md`, because R91 and R94 showed solver power is the binding constraint.
- The proposed `STATUS.md` and top-level `handoffs/` are dropped: `CURRENT_STATUS.md` already exists, and CI
  rule 2 rejects new top-level directories.

## Open items

- Different-model review of the charter itself (ChatGPT or a person).
- The three records in charter Section 9 (contact index, signals register, coverage map) are proposals for
  separate pull requests; none is created here.
