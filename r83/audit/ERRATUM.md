# R83a Erratum — one wrong published plaintext letter (PFX/WPX)

**Date:** 2026-11-15
**Classification:** CONFIRMED TEST-SEMANTICS DEFECT. The original frozen R83a
ciphertext, preregistration, code and results are preserved unchanged.
This additive audit applies to the DROP (one wrong published PLAINTEXT)
claim only; it is a **crib-assisted post-freeze review**, not a blind
K4 plaintext search or a candidate key finder.

## Defect

In the original R83a PFX and WPX checks, setting aside one published
position removes only its local consistency equation. That is not
equivalent to making one published plaintext letter **unknown** when
the plaintext letter also affects later encryption:

- PFX: the letter at i also affects the feedback term at i+lag.
  The necessary equations at both i and i+lag must be relaxed or
  jointly solved with the one unknown letter.
- WPX: the letter at i changes the key-pointer advance, so the
  state trajectory after i must be recomputed or relaxed. Keeping
  the original walk defined by the corrupt letter is unsound.

The old tests changed a **ciphertext** symbol, which is not a valid
positive control for either causal plaintext-error claim.

## Independent synthetic counterexamples (no K4 data)

r83/audit/plaintext_drop.py --synthetic creates two fully reversible
97-letter planted ciphers, changes exactly one known PLAINTEXT letter,
and then checks the original R83 implementation. Both false reject:
- Original PFX drop-one recovers true setting: FALSE.
- Original WPX drop-one recovers true setting: FALSE.
- New PFX necessary-condition test retains truth: TRUE.
- New WPX necessary-condition test retains truth: TRUE.

The fixtures use synthetic position windows 9-20 and 56-67, not
published K4 positions or published plaintext words. Further
synthetic positions confirm that the conservative checker does not
incorrectly exclude the planted truth.

Verification: GitHub Actions run 43734350994
https://github.com/tylerj-spec/kryptos-k4/actions/runs/43734350994

## Corrected post-freeze WPX scope

The new checker removes the suspect plaintext equation AND splits
the known portion of the row at that position. Each unbroken
remaining known segment is checked by an independently recomputed
relative key walk. The phase of each segment is treated as free.

That is intentionally a **conservative necessary-only condition**:
it may accept configurations that are impossible once all global
pointer constraints are enforced, but it does not reject a genuinely
possible configuration because it relied on the allegedly wrong
plaintext letter.

On original K4, the post-freeze necessary-only check finds:

- 260 DISTINCT WPX structural convention settings NOT ruled out
  across the 24 possible dropped published positions.
- At least one not-yet-ruled-out setting on 21 of the 24 possible
  dropped positions (0 survivors on the remaining 3).
- Full JSON with per-position counts and representative settings
  is attached as a GitHub Actions artifact
  r83-plaintext-dependent-drop-audit to run 43734350994.

**Interpretation:** There is NO evidence that any of these 260
settings has a complete 97-letter decryptor witness or would
satisfy the entire K4 message. They are only an **upper bound on
feasible settings** under a single inaccurate plaintext clue.
The former claimed universal "WPX EXCL with any one published letter
wrong" is WITHDRAWN and must not be used to prioritize future work.

## What remains supported

- R83a's original exact, all-24-letters-correct WPX/PFX feasibility
  results are not invalidated by this error.
- The published-position SHIFT tests, assuming each shifted run's
  letters are all correct, are a different mathematical question
  and have not been disproved here.
- Original PFX DROP was already labeled CHANCE, not EXCL;
  however its reported 17 partial survivors is not a complete
  count of configurations allowing one erroneous plaintext symbol.
  Avoid using it as an exhaustive one-error survivor enumeration.
- This does not broaden or eliminate any language-masking,
  transposition, ciphertext-copying-error or earlier untested family.

## Required independent verification before final promotion

1. Implement an independent EXACT state-aware one-error checker for
   both PFX and WPX, with the suspect plaintext variable explicitly
   ranging 0..25 and all pointer updates propagated.
2. Compare that checker to an exhaustive small-key toy brute force
   (and at m=26 under boundary/large-ring planted controls).
3. Verify a random subset of old R83a exact checks with a second
   independent implementation.
4. Only after the exact corrected checker passes may the numerical
   DROP counts be reported as exact and the corresponding ledger
   cells classified as a proper exclusion.
5. Never edit or replace the original r83/PROTOCOL.sha256,
   r83/k4/run/R83A.json or r83/k4/run/FROZEN.sha256.
