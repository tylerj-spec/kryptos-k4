# R104: L193, the autokey's error propagation, and the solver architecture; R105 entry met for B known, F = A

Affected ledger IDs: L193
Validation:
- **Order of commits:** pre-registration 2709df3, pushed alone; source b27e4d1; run frozen in 913bd86.
- **E1:** prediction holds.
- **E2:** 0 failures in 300 identity checks.
- **E3 (P1):** 19/24, gate met.
- **E4 (P2):** 0/24, with 17 objective counterexamples; gate not met.
- **Resources:** COMPLETE under `audit/run_bounded_agg.py`, 69 s, zero retries. Guardrail check PASS.
- **CI:** `.github/workflows/r104-architecture.yml` re-runs `run104.py` and compares all results except timings.

Independent review: NONE. One model (Claude Code) built and ran R104. It is part of audit batch B (ChatGPT).

## Summary
- **Errors spread except in one case.** With feedback numbered in the plaintext alphabet (F = A), plaintext-alphabet
  errors stay local. Every other alphabet error propagates along the autokey chain.
- **Mode 1 is solvable.** B known with F = A reduces exactly to a simple substitution once c and the chain offsets
  are fixed. A prototype recovers 19/24 fresh plants, so **R105 may proceed for this mode**.
- **Mode 2 is not, yet.** A known reduces exactly to a substitution of a code sequence, but the code-trigram
  objective is fooled (0/24), so that mode is closed for this batch.
