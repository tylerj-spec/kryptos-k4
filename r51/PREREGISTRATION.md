# R51 pre-registration — ciphertext-feedback keystream with K3 transposition first
**30 October 2026, written before any R51 K4 ciphertext feasibility results.**

## Why this is NOT another Gromark round
R45/R46/R50 exactly excluded narrow keyword/free substitution models under direct or four K3 quarter-turn Gromark constructions. A Gromark decimal recurrence is not required by K4. R17's old ciphertext-autokey screen covered **in-place models**; this round tests ciphertext-autokey after the four pre-declared **K3-style transposition-before-substitution** routes, a meaningfully different mechanism. Neither Berlin clock city names nor K4 story/landmark guesses appear in the key generator.

## Locked cipher hypothesis
Original 97-character K4, exact SHA256 including newline `2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3`. All four `R24x8/{CW,CCW}/{fwd,inv}` permutations already in R50, same `Q[j] = P[perm[j]]` **before** substitution. `C[j]=CA[(PA^-1(Q[j]) + sign*k[j]) mod26]`, both signs.

Unlike R50, `k[j]` is defined by **previous ciphertext**, not Gromark:
- For each lag `L=1,2,...,24` and basis `AZ` or `KRYPTOS`, `k[j]=basis_rank(C[j-L])` for `j>=L`, using the **unaltered visible ciphertext**.
- For `j<L`, initial seed letters are **completely free modulo 26**, one per position. Rather than falsely assigning guessed seeds, remove all public-letter constraints on these seed positions. This relaxation is **exactly equivalent to existential seed choice**, because after choosing the two full alphabets each free `k[j]` can be chosen to satisfy its ciphertext/plaintext pair. Do not incorrectly imply that a seed was recovered.
- Both alphabet orientations: 4,749 distinct R44b common-word keyword alphabets + separately reported 12 additional Kryptos-themed distinct alphabets (same fixed R50 inputs), on PA or CA, opposite alphabet an unrestricted bijection. Total **4,761** finite keyword alphas. No enlargement after looking at K4.
- Public 24 K4 plaintext letters are mapped through inverse K3 permutation to positions in Q, then constrained only if those positions `j>=L`. Run the independently audited necessary+exact **two arbitrary alphabets** graph oracle first; for every surviving lag/basis/route/sign, use the exact R50 difference-index + full fixed-keyword injection tests for every candidate (index only skips mathematical impossibilities). No word searches or plaintext guesses.

## Strong evidence filter and interpretability
For each route/lag/basis report the **number of anchor characters at `j>=L`**, and the number of independent graph cycles (computed structurally without key values). Mark configurations with **fewer than 20 known-position anchor letters** as `LOW_COVERAGE`: they can be feasible for vacuous reasons. The primary signal is a keyword-compatible **HIGH_COVERAGE (`>=20`)** setting with nonzero independent graph cycles, outperforming identically screened shuffled-null ciphertexts. A necessary first step, **not** sufficient evidence of solving K4. List *all* settings, including low-coverage. A positive 24-letter match is never independent validation.

## Predeclared controls / nulls
1. **20 synthetic ciphertext-feedback encryption plants** using the already-revealed R44b 97-letter original passages (NOT a new blind holdout), cycling four transposition directions, lags 1..20, AZ/KRY feedback basis, ± operations, keyword PA/free CA (10) and keyword CA/free PA (10). First L seeds selected from deterministic RNG (51000+j) and then each subsequent k computed from the **already encrypted ciphertext** (not from later plaintext). Verify full 97-letter forward ciphertext and inverse plaintext; the *correct* algorithm must pass all 20 graph, indexed and unindexed keyword checks with only post-seed anchors. These controls are algebra only, not unknown-key blind solve.
2. **Two ciphertext unigram-preserving nulls**, same 97 letters of original K4 shuffled with seeds **51100** and **51101**. Apply identical entire four routes × 24 lags × 2 numbering alphabets × 2 signs × 4,761 candidate keyword arrangements.
3. At every K4 route, and both nulls, for first three two-free feasible parameter combinations, assert exact equality of the indexed keyword matches and the independent full unindexed **all-4,761-keyword** scan for both operations and alphabet orientations.
4. Freeze exact source/protocol SHA256 and full output JSON with all pass counts, every setting and literal positions of its **covered known letters**; do not infer statistical significance from two nulls.

## Decision and next steps
- `EXCL` only if **zero** configurations survive (or `NO_HIGH_COVERAGE_FEAS` if all survivors have fewer than 20 known letters or zero graph cycles). Do not overclaim a complete model exclusion when there are low-coverage feasible settings; report them honestly.
- If a high-coverage candidate survives, **separately pre-register a new ciphertext-only blind language-recovery experiment**. It must run without public clue inputs and correctly recover **>=16/20 fresh independently encrypted 97-letter plaintexts with seed/key NOT supplied**, then freeze K4's raw complete plaintext before known-letter check. Old R44b's 20/20 *known-key* success does not count.
- No outside checker, no ciphertext edits, no leaking known K4 letters into a blind solver, no merges to main. K4's World Clock may only be story content.
