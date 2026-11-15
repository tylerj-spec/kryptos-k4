# Guardrails v2 and integration of the November 2026 audit — review note

Affected ledger IDs: L165, L172
Validation: on 15 Nov 2026 the four audit branches (PRs #81–#84) were merged into one branch without conflict and every audit suite was re-run locally: guardrail fixtures (35 tests), R53 blind contract, R75 safe F1X checker (6 tests), R83 plaintext-error synthetic counterexamples, historical scan fixtures (10 tests), the full ledger and hash scan, the L01–L04 recheck (832 settings, 1 survivor, as reported) and the L167 invariant (sums 7, 12, 7, 14; 14,400 synthetic checks). All passed and all reported figures reproduced.
Independent review: PARTIAL. The audit was written by one model (ChatGPT). A second model (Claude Code) re-ran its tests and reviewed and hardened the guardrail checker. Nobody has reviewed the mathematics of the R75 and R83 corrections line by line, and no multi-model council review has been run.

## Ledger content

This pull request carries the L165 qualifier and the L172 erratum exactly as written in PRs #83 and #82. No other ledger row is changed.

## Gaps found in the first guardrail checker (PR #81) and closed here

| Gap | Consequence | Fix |
|---|---|---|
| `FROZEN.sha256` only had to be non-empty | A freeze manifest with wrong or no hashes passed | Every line is verified; every output must be listed or committed later |
| A manifest was required only for files under `rNN/k4/` | A round using `results/`, `runs/` or `frozen/` (as R78 and R80 do) needed no preregistration or manifest | Any new round adding non-Markdown files, and any round adding K4 files, needs a manifest |
| Only three exact file names were immutable | `PREREG_*.md`, `P1_PROTOCOL.sha256`, `runs/`, `frozen/` and solver code pinned by a protocol hash could be rewritten | Name patterns widened; any file whose content is pinned by a committed SHA-256 manifest is immutable |
| Experiments outside `rNN/` were not checked at all | A new top-level directory bypassed everything | New non-round top-level directories are rejected |
| The gate file only had to exist | K4 could run after a failed gate, or with the gate added in the same commit | `gate_verdict` must be GO and the gate must be in an earlier commit than any K4 file |
| Freeze-before-reveal order was not checked | Reveal files could be committed with the frozen outputs | Outputs not listed in the freeze manifest must be in a later commit |
| The resource budget was declared, never enforced | The R83a runaway job could recur | `audit/run_bounded.py` enforces the budget; K4 outputs need COMPLETE, in-budget logs |
| Blind inputs were screened by file name only | A word list containing a published word passed | Content is screened for the published words as well |
| Any new review note satisfied a ledger change | A note about a different row passed | Changed rows must be named; the note must state the independent-review status |
| A pull request could weaken the checker it shipped | Guardrails could be removed in the same change as a violation | CI also runs the base branch's checker; guardrail files need a review note |
| The check ran only on pull requests | A direct push to main was never checked | Also runs on pushes to main (detects, does not prevent) |
| No way to suspend searches | The recommended pause was advice only | `audit/SEARCH_HOLD.md` blocks new K4 files until the owner removes it |

## Not covered

Listed under "What CI cannot enforce" in `audit/FUTURE_TEST_GUARDRAILS.md`. In short: CI checks structure and order. It cannot tell whether a test measures its hypothesis.
