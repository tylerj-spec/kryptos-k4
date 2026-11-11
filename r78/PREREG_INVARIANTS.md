# R78 pre-registration: two ciphertext-only, key-free tests (Claude Code, 11 Nov 2026)

Written before either test is run on K4. Both use the 97-letter ciphertext only. No published letter is read by the
script (`r78/invariants.py`). Proofs are in `r78/FABLE_ANALYSIS.md` (Part 1).

## I1. Sum invariant for a self-keyed cipher (r77 H11), for every permutation at once
**Model.** `IDX[ca][c[i]] = s·IDX[A][p[i]] + t·IDX[A][p[π(i)]] (mod 26)`, π any permutation of the 97 positions, A any
alphabet used for both the plaintext and the key (pa = ka), ca any ciphertext alphabet.

**Theorem.** Let `S(ca) = Σ_i IDX[ca][c[i]] mod 26`.
- Beaufort and variant Beaufort (s + t = 0): `S(ca) = 0`.
- Vigenère (s = t = 1): `S(ca)` is even.

The statement does not depend on π or on A.

**Test.** Compute `S(ca)` for ca = AZ, KRY, PAL, ABS (the four alphabets of `r75/core.py`).

**Decision rule (fixed now).**
- `S(ca) ≠ 0`: H11 with pa = ka and that ca is **excluded for Beaufort and variant Beaufort, for every permutation and
  every plaintext alphabet**.
- `S(ca)` odd: the same for Vigenère.
- `S(ca) = 0` or even: no conclusion; that case goes on to the per-route test of Part 1.

**Controls (same script, before K4).**
- 2,000 planted messages (random letters, random permutation, random alphabet A from the four, each ca, each
  operation): the invariant must hold in every one.
- 20,000 random ciphertexts: `S = 0` at a rate near 1/26, `S` even at a rate near 1/2.

## T-RK. Letter-count likelihood for "English ± English" ciphers (first look)
**Model.** Every in-place cipher whose key letters are ordinary English text with no further key: an unknown running
key, a plaintext autokey without keyword, and H11. The ciphertext letter at each position is then
`CA[s·IDX[pa][P] + t·IDX[ka][K]]` with P and K two English letters. For a route without many short cycles the letter
counts are close to multinomial with probabilities `d_v`, the distribution of that sum for convention v.

**Statistic.** `Λ_v = Σ_letters n(letter) · ln(26 · d_v(letter))`, the log-likelihood ratio of K4's letter counts,
"English ± English under v" against "uniform".

**Conventions.** pa, ka, ca each AZ or KRY; VIG, BEAU, VARB: 24.

**English letter frequencies.** The standard table hard-coded in the script (fixed before the run).

**Calibration.** For each v: 20,000 multinomial samples of 97 letters from `d_v` and 20,000 from the uniform
distribution. Report K4's Λ_v as a percentile of both.

**Decision rule (fixed now).**
- This is a first look with independent letters. It gives a STAT statement only, never an exclusion.
- "Disfavoured under v" means K4's Λ_v is below the 2.5th percentile of the `d_v` samples.
- Whatever the outcome, the full version (real 97-letter English windows, real permutations, the repo's corpus) is
  specified in `FABLE_ANALYSIS.md` for the cheaper model to run.

**Not done here.** No decode, no route scan, no use of the published letters.
