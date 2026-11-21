# Independent review of R89 results

Affected ledger IDs: L178

Promotes: L178 (exact mathematical exclusions for R89's actual parameter lists only)

Independent review: YES ChatGPT (GPT-6 Astra Pro), a different model from Claude Code, independently re-derived the partial-permutation proof, implemented exact checks without builder cipher/checker imports, and checked every registered setting on all 201 saved inputs. Same-model subtasks are one review.

Validation: `r89/audit/independent_exact.py` matches exact aggregates for 139,120 F26/F26L and 448 RCT structural settings per input. Exhaustive four-contact oracle: 1,572,864 comparisons. Independent synthetic gate arithmetic and reference encryption reproduce the saved gate. Original unit/witness/gate/evaluation/exact replays are recorded in `r89/audit/evidence/`. Protocol-bound and frozen files are unchanged.

Promotion is **EXACT_SCOPE_EXCL only**. Original blind optimization and untracked letter-model scores were not independently rerun; execution review remains PARTIAL. Saved NO_SIGNAL arithmetic is verified for the actual shortlisted pipeline, not a full-setting final-score maximum.

Additive corrections in `r89/audit/REVIEW_20261121.md`: shortlist scoring; weaker actual RCT key criterion; a single F26 ciphertext substitution can affect two letters (max 7/24 still excludes it); 15 original alphabet classes omitted; resource accounting per process; R82 overlap and minor report errors. CI audit replays now use the required bounded wrapper. No new model or blind search and no modification of frozen evidence.

Reviewed source: `9e04e4e32eeb7c947e32979dc6663433e358192d` (PR #99), 21 November 2026.

