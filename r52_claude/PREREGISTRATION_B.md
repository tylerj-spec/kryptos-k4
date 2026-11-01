# R52b (Claude Code) pre-registration, 31 Oct 2026: blind solve of the single R52 survivor

Written after R52's screen and before any blind solve on K4.

## The survivor
R52 found **one** keyword-feasible K4 setting, a base-26 twin pair (`R52_RESULT.tsv`):
- **Key:** base-26 chain addition, primer `34DCA` (1450342) with sign −, which is identical to primer `NMDEG`
  (10906288) with sign +.
- **Route:** `R24x8/CCW/inv`, substitute then transpose.
- **Plaintext alphabet:** `DECABFGHIJKLMNOPQRSTUVWXYZ`; the cipher alphabet is free.

It was **selected using the 24 published letters**, so by itself it is crib-feasible only. Coincidental survivors
are expected at this family size: the B10/b8 control family had 12.

## Blind test (no clue letters, no mask)
- **Input:** X = the K4 ciphertext un-transposed by the route (X_i = CT[perm⁻¹(i)]), and the key in plaintext order
  (the NMDEG stream, which absorbs the sign).
- **Solver:** the frozen R44b pipeline, `r44/blind/kwpa_solve.cpp` (4,749 keyword alphabets; the cipher alphabet
  annealed) plus `r44/blind/polish.cpp` (λ = 1), unchanged.
- **The solver is not told the surviving alphabet:** it enumerates all 4,749.
- **Controls:** 4 planted messages in the same family (base-26 5-digit primer, R24x8/CCW/inv S_then_T, keyword PA,
  random CA), solved the same way. Each must come back exact.
- **Freeze:** the K4 output is frozen and committed before it is compared with the 24 letters.

## Decision
- **Real lead:** the blind best plaintext reads as English **and** carries EASTNORTHEAST and BERLINCLOCK at
  22–34 / 64–74. It would then be reported raw for independent review; no external checker without Tyler.
- **Coincidental survivor:** the blind output is non-English or misses the clue letters. The family is then excluded
  at the blind level too.
