# Protocol for testing a second (hidden) meaning in a recovered K4 plaintext (pre-registered with R59, 2 Nov 2026)

**The working hypothesis (Tyler):** K4's plaintext reads as ordinary English, and its surface text may carry a second
meaning. This raises two separate questions, kept apart here:
1. **How was the letter encryption done, and how is it reversed?** These are R55–R59 and later.
2. **Does the recovered text mean something beyond its surface?** This file covers question 2.

**Question 2 cannot be tested until question 1 produces a blind plaintext candidate.** That candidate must pass its own
round's rules: blind, frozen, re-encrypting exactly, and agreeing with the published letters after the freeze. Nothing
here may be used to search for, choose or score a decryption.

## Source correction (recorded 2 Nov 2026)
- **Scheidt's "cake" codeword example** (WIRED, January 2005) came while discussing an already-deciphered Kryptos
  message. It illustrated **semantic coding** in general. It does **not** say that K4 uses a secret word codebook.
- **His statement specifically about K4** concerned concealing recognisable **English-language statistics**. That is a
  constraint on the letter encryption (question 1), not on meaning.

## What counts as a test of a second meaning
Every test is fixed before it is applied, gets a chance baseline, and is corrected for the number of tests tried.

| # | Test | Fixed rule | Null / baseline |
|---|---|---|---|
| A | **Acrostic / telestich** | First letter, then last letter, of each word, in a single segmentation fixed in advance: the best dictionary segmentation by the R59 word model, recorded before reading. Read forward only | The same rule applied to (i) 1,000 random 97-letter windows of the R59 holdout books, and (ii) the null decryptions of the same round |
| B | **Every n-th letter** | n = 2…12, with each offset, forward | Same nulls, with 11 × offsets tests counted |
| C | **Letters at Kryptos anomaly positions** | Positions of the K1–K3 misspelling letters (IQLUSION, UNDERGRUUND, DESPARATLY) and the K2 "X" separators, mapped by a rule written down *before* reading the candidate | Same nulls |
| D | **Semantic reading** | Read the plaintext against Sanborn's public statements: Egypt 1986, the Berlin Wall 1989, the Weltzeituhr, "delivering a message". Also against code-word ideas (a common word standing for something else) | Labelled **interpretation**. This is not statistical evidence. Each claimed code word must be named in advance in a list, with its meaning sourced from Sanborn/Scheidt material, not invented to fit |

## Reporting rules
- **Raw text:** report the candidate plaintext unedited first. Extraction results come after, each labelled with its
  rule.
- **When a hidden message counts:** only when a pre-declared rule gives a result beating ≥ 99% of nulls **after**
  correction for every rule tried. Otherwise, report it as "no hidden message detected by these rules".
- **Keep the two claims separate:** a semantic reading (D) is never presented as decryption evidence. It may support
  an interpretation once the decryption stands on its own.
- **No external checker** submission without Tyler.
