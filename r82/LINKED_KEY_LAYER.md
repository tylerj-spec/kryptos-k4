# R82 addendum: one shared keyword across noncommuting layers

**Design study only (no K4 ciphertext, known clues, or key-fitting).**

## Motivation from the existing ledger

R75/L165 scanned **fixed** pairs of sculpture words / 80 named words through two different tableaux, and the F1X post-freeze check showed no plaintext. R80/Fable proved that independently random keys in both stages make 97-letter blind recovery difficult (0/48 plants by naïve coordinate ascent), but with one stage fixed the other can be solved per slot. R79/L169 and R81a/L170 eliminated many **single-stage** ciphertext-driven key schedules; R81a G4 includes rotating a keyword after each pass. **None of these results automatically excludes the composite one-unknown-key family below.** Before building it, inspect implementation-level overlap with R75 F1, R80a and R81a G4; this is a research gap assessment, not an unqualified novelty claim.

## A manually executable construction with ONE key

Take a keyword K of length m > 1; use two fixed stage-tableaux with *different intermediate alphabets* (CA1 != PA2), so the stages do not generally reduce to one additive Vigenere cipher.

Stage 1:
  u_i = LET[CA1][(s1 * IDX[PA1][p_i] + IDX[KA][K[i mod m]]) mod 26]

Stage 2: rotate the same keyword one position after each hand-written row of width w:
  r2(i) = (i + floor(i / w)) mod m
  c_i = LET[CA2][(s2 * IDX[PA2][u_i] + IDX[KA][K[r2(i)]]) mod 26]

For decryption, subtract the row-rotated key at stage 2, then the unrotated key at stage 1. This is deterministic, reversible and can be executed on paper from one keyword, two alphabet charts and a row-width instruction. All labels, signs, keyword alphabets and widths must be fixed in a preregistered finite catalog.

**Potentially important structural property:** The ordered *pair of key positions* repeats after m*w symbols, not m symbols, for generic independent key symbols. To prove the period, a global period T must be a multiple q*w of the row width (otherwise floor((i+T)/w)-floor(i/w) varies with i). Invariance of both key indices demands m divides q*w and q*(w+1). Subtracting shows m divides q. Hence the smallest generic full period is T=m*w. For example, m=9 and w=11 give period 99 > K4's 97 characters, despite using only a 9-letter key. The actual output's period can be shorter if keyword letters coincide or the intermediate alphabet has an accidental symmetry.

If w=m, stage-2's slot schedule resembles R81a's single-stage ROT rule, but the TWO-stage different-tableau composition is not equivalent to that single-stage experiment. This is a useful way to avoid searching for a completely unconstrained nonrepeating key while explaining weak short-period traces.

## Why this could be more tractable than R80's two arbitrary keys

One word K controls both layers. Its raw uncertainty is m*log2(26) bits, versus roughly (m1+m2)*log2(26) for unrelated random keys. Since each unknown letter influences both stages, ordinary R79 separability does not apply automatically. But a finite **dictionary-mode** search can enumerate K directly, with explicit width and convention choices, and score the entire 97-letter candidate; alternatively use a joint factor-graph/beam scorer over K positions. Synthetic 97-letter recovery will decide if this is actually feasible.

Suggested first gate (NO real K4):
- Fixed alphabets AZ/KRY/PAL/ABS, ordered CA1 != PA2; signs +/−, with equivalences deduplicated.
- Width choices specified independent of clues or K4 score. Compare w=m, a short row-width set, and a few independently justified worksheet widths. State both the number of distinct full transforms and the raw labeled count.
- Keyword K selected from an existing pinned 1990-plausible word list; fresh **holdout words not in that list** distinguish a dictionary limitation from a cipher-model failure.
- Fresh normal-English and systematic orthography-masked 97-character passages; positive controls by (m,w), plus wrong-family and equal-budget random controls; exact re-encryption.
- Score the **max over all words, alphabets, widths, signs, and routes** against the identical search over each shuffled control. Freeze a family-wide decision threshold BEFORE any K4 trial.
- On every positive, separate method detection, exact 97-letter plaintext recovery, and correct keyword recovery (some keys may be equivalent on finite data). A single English-looking output is never proof.
- The negative result would only exclude *list-word* (or other proved-covered) keys and conventions; do not generalize to arbitrary unknown words or unlisted rows.

**Decision:** try this as a low-cost R80a subfamily on synthetic controls, adjacent to the one-word-known/second-word-free model. Only promote it to K4 after the same strict freeze-and-holdout gate. No K4 test or published-letter check occurs here.
