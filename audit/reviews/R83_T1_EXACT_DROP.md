# R83a L172 — T1 exact one-wrong-plaintext-letter re-check of PFX and WPX

Affected ledger IDs: L172
Validation: `python3 -I r83/audit/tests/test_exact_drop.py` (brute force over every key on toy sizes, full-decryption soundness, 42 max-parameter plaintext-error plants, the two `plaintext_drop.py` counterexamples, agreement with R83a's original EXACT engine and containment in the conservative bound); `python3 -I r83/audit/t1_passcheck.py` PASS (exact WPX survivors inside the re-derived 260); K4 job COMPLETE under `audit/run_bounded.py`.
Independent review: NONE. One model (Claude Code) wrote the checker, the tests and this note. Multi-model review has not been run.

## Change to L172
- WPX DROP: was "EXCL", then withdrawn to "UNVERIFIED/OPEN, 260 not eliminated" (conservative bound). Now: exact under R83a's published-positions semantics, 2 settings survive (one up to relabelling), at a level 12/20 shuffles reach: **CHANCE**.
- PFX DROP: was "CHANCE, 17 (not exhaustive)". Now: **CHANCE, 22**, exhaustive under the same semantics; shuffles 12–39.
- EXACT step (all 24 letters right): reproduced, WPX 0 and PFX 0. Unchanged.

## Caveats
- Survivors are an upper bound. Like R83a, the check relaxes the coupling of the runs through decryption of the unpublished letters.
- Nothing was decrypted and no key was completed. Original `r83/` files are untouched.

Details: `r83/audit/EXACT_DROP.md`.
