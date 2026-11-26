# R107: L195, Slidefair with free alphabets and a periodic key, testable at p 1–8, 10 and 11 by an exact crib check

Affected ledger IDs: L195

Validation:
- **Order of commits:**
  - pre-registration f76e520, pushed alone;
  - source d45aa0e;
  - CI workflow ad5909a, committed during the run; it does not touch any input of the run;
  - outputs frozen in 7818586.
- **T1 structure:** 0 failures on 19,200 pairs.
- **T2 soundness:** 0 unsound on 400 plants.
- **T3 two implementations:** 0 disagreements on 2,960 cells.
- **Resources:** COMPLETE under `audit/run_bounded_agg.py`, 254 s, zero retries.
- **CI:** `.github/workflows/r107-slidefair-periodic.yml` checks the hashes, re-runs `run107.py` (standard library
  only) and compares every result except timings.

Independent review: NONE. One model (Claude Code) built and ran R107. It opens audit batch C.

## Summary
- **Algebra, verified against R98's reference cipher:**
  - Slidefair maps each pair (u, w) to (σ_k(w), σ_k⁻¹(u));
  - the upper letter never maps to itself;
  - each known pair gives two homogeneous equations mod 26 in the two alphabets and the key letter.
- **The check X107.** It uses the letter identity and forced collisions in the null space mod 2 and mod 13. It is
  sound, and it allows one dropped pair.
- **Power.** Allowing one dropped pair, X107 rules out a random hypothesis with probability ≥ 0.50 at p 1–8, 10 and
  11 (1.00 at p 1). At longer periods, and with any key, the probability is 0.18–0.47. Without the drop allowance it
  is still ≥ 0.59 everywhere.
- **Proposal P4.** A crib-assisted, exclusion-only K4 run of X107, over 16 conventions × p 1–48 and any key, is
  proposed for approval.

## Points for the auditor
1. **The same-column equations** (the table in `r107/PREREGISTRATION.md` §2), and the claim that a DROP branch covers
   any same-column rule or any error at one pair.
2. **Soundness of the collision rule.** Can three letters forced equal mod 13 still be injective mod 26? The claim is
   no: each residue mod 13 has only two lifts mod 26.
3. **The T4 powers come from random masks and letters.** The K4 cell results will differ.
