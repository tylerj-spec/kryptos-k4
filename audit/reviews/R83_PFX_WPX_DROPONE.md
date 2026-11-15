# R83a L172 — independent post-freeze audit and disposition

Affected ledger IDs: L172
Validation: GitHub Actions run 43734350994; the frozen historical R83a results were not changed.
Independent review: PARTIAL. Found and written by one model (ChatGPT). A second model (Claude Code) re-ran `r83/audit/plaintext_drop.py --synthetic` on 15 Nov 2026 and reproduced both false rejections by the original test. The 260-survivor K4 figure was not re-derived, and the exact one-error checker is outstanding (`audit/NEXT_STEPS.md`, T1).
Review status: confirmed single-model mathematical counterexample and deterministic CI; requires independent external review before any claim of exhaustive corrected feasibility.

## What was tested

A fresh, fully reversible 97-letter **synthetic** PFX plant and WPX plant were created with artificial known-position runs; one **plaintext** letter (not ciphertext) was altered. The original R83a DROP test falsely rejected both true settings because it removed just one constraint while still using the corrupted letter to determine future feedback or key-pointer steps. Independent necessary-only checkers retained the planted truth.

An additive *post-freeze* crib-assisted WPX consistency screen on the already frozen real K4 record was then run with the suspect plaintext removed from both the local equation and its future pointer-state computation. For safety it allows independent phases on newly split known-letter segments. On this permissive screen 260 unique WPX structural settings remained not eliminated across all 24 choices for the one bad published plaintext letter; 21 of those drop choices had nonzero survivors.

This is an **upper bound**, NOT 260 valid full-length decryptions or keys. The global pointer continuity and unread positions can still eliminate the candidates.

## Correct ledger interpretation

- RETAIN R83a WPX all-24-letters exact EXCL under its fixed in-place alphabets, transcription, and state rules; that checker does not perform a one-error substitution.
- WITHDRAW the former WPX claim of EXCL under any one inaccurate published plaintext letter. Correct classification is **UNVERIFIED/OPEN**, with at least one necessary-only survivor for 21 of 24 choices.
- PFX one-error DROP was already CHANCE, but its published count (17) is not an exhaustive correct plaintext-one-error count. Label as not established until propagation-aware recomputation.
- Keep SLX/SLX-A/SSX DROP and independently tested shifted-run conclusions separate; this counterexample does not invalidate those models.
- Original pre-registration, protocol hashes, K4 ciphertext, raw R83a results and freeze hashes remain immutable.

## Provenance and follow-up

- Source: r83/audit/plaintext_drop.py
- Documentation: r83/audit/ERRATUM.md
- CI: https://github.com/tylerj-spec/kryptos-k4/actions/runs/43734350994
- Original: r83/RESULT.md, r83/k4/run/R83A.json and r83/k4/run/FROZEN.sha256 (unmodified)
- Next: independent **exact** PFX/WPX one-error state-aware solver, toy brute-force comparison, held-out max-size controls, and reviewer signoff; do not promote a new exact exclusion before this passes.
