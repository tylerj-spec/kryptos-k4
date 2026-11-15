# K4 search hold — in force since 15 November 2026

While this file exists, CI rejects any pull request in which a round adds K4 files
(`audit/check_guardrails.py`, rule 8).

**Still allowed:** additive audits and errata of existing rounds under `rNN/audit/` and `audit/`,
synthetic-only work, preregistrations, and documentation.

## Why

The November 2026 audit confirmed two defects that produced or could produce wrong conclusions
(R83a's one-wrong-plaintext-letter exclusion, L172; R75's F1X int64 overflow, L165). Most historical
exclusions have not been replayed by an independent checker.

## Conditions for lifting

1. The guardrails and the two corrections (PRs #81–#84, or the pull request that combines them) are merged.
2. Tasks T1 and T2 in `audit/NEXT_STEPS.md` are complete and reviewed.
3. Tyler decides to resume.

## How to lift

Tyler approves a pull request that deletes this file and adds an `audit/reviews/` note recording the decision.
An agent must not delete this file on its own initiative.
