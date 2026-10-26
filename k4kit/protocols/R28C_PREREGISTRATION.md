# R28C pre-registration: English search of the R27 "K3 rotation + Gromark" passes (Claude, 26 Oct 2026)

Written before any calibration or K4 English search was run.

**Family.**
- K3's double quarter-turn rearrangement (rows of w1, quarter-turn, rows of w2, quarter-turn), with ChatGPT R27's
  20 route variants, followed or preceded by a 5-digit Gromark substitution with both alphabets free.
- The R27 replay gives 65,968 clue-compatible (route, order, primer) settings: 59,322 with 0 crib cycles, 6,607
  with 1, and 39 with 2.

**What is searched (solver `solver_s2kp`).**
- `solver_s2kp` is S2k with the rearrangement undone before scoring. Same orth dictionary, quadgram term 0.05→0,
  and polish as R21 S2.
- **Tier A:** all 39 two-cycle settings (routes R25x8/CW/inv and R24x9/CW/fwd, both orders) at 64 × 40,000.
- **Tier B:** all passes of **K3's own variant**, R24x8/CW/inv: K3's encryption direction, verified on K3 in
  `two_step.py`, both orders, 3,212 settings.
  - Screen at 16 × 40,000.
  - The 20 best by W are re-run at 64 × 40,000 with new seeds.
- The other 62,717 settings are not searched this round, and that will be stated.

**Calibration (run before K4, same solver and budgets).**
- 20 planted messages: the 20 R21 fresh base passages, each with the clues in place.
- Each is encrypted with R24x8/CW/inv: 10 rearrange-then-substitute, 10 substitute-then-rearrange. Random primer,
  random alphabets.
- The solver is given the true setting. Report readable recovery (≤ 5 wrong letters) at 16 × 40,000 and at
  64 × 40,000.

**Candidate rule (fixed now).** A K4 setting is a candidate only if:
- its best W exceeds **−114.9** (R21's best wrong-key score); and
- the 64 × 40,000 replication with new seeds returns the same text, within 5 letters.

A candidate's raw 97 letters go to Tyler unedited. Otherwise the result is "no candidate in the searched settings".
That is qualified by the calibration recovery rate and is not an exclusion of the family. No Paradigm submission.
