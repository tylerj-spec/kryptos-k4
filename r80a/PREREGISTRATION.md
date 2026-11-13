# R80a pre-registration (Claude Code, 13 Nov 2026): two keyword stages, one key listed and one free — synthetic gate only

Written before the sealed holdout exists. **No K4 data is used in R80a**, and no published K4 letter. Code, cuts,
seeds, books and decision rules are fixed by this commit (`r80a/PROTOCOL.sha256`).

**Approval and requirements** (review of PR #76, 13 Nov 2026: "I recommend R80a first, then R81b"):
- synthetic-only testing of two stages with one dictionary keyword and one unknown keyword, in both orders;
- recovery reported by both keyword lengths, their greatest common divisor and their least common multiple;
- exact and at-least-95-letter recovery reported separately, with nonstandard-spelling controls;
- no hard exclusion of shorter combined periods: every pair of lengths is run;
- no K4 execution until a sealed recovery gate shows the algorithm reliably identifies the constructed messages.

**Specification:** `r80/FABLE_IDENTIFIABILITY.md` §1.5–1.7 (Theorem I2: with one key fixed, the other separates slot by
slot).

## Model
Two keyword stages on different tableaux, letters in place:
- stage one `q = CA1[s1·IDX[PA1][p] + t1·IDX[KA1][k1(i)]]`;
- stage two `c = CA2[s2·IDX[PA2][q] + t2·IDX[KA2][k2(i)]]`.

Here `(s, t)` is VIG (1, 1), BEAU (−1, 1) or VARB (1, −1). The alphabets are A–Z or KRYPTOS, with CA1 ≠ PA2. If they
are equal, the stages collapse into one stage with the summed key: that is ledger row L36's summed periodic keys,
excluded exactly where there are 3 or more checks.

| Family | Listed key | Free key | Settings per ciphertext | log10 settings × 26^m |
|---|---|---|---|---|
| L1 | stage one: a word, at phase 0 | stage two, 1–12 letters | 28,943 × 96 × 12 = 33.3 million | 23.44 |
| L2 | stage two: a word, at phase 0 | stage one, 1–12 letters | 33.3 million | 23.44 |
| X1 | stage one: any key of 1–3 letters | stage two, 1–12 letters | 18,278 × 96 × 12 = 21.1 million | 23.24 |
| X2 | stage two: any key of 1–3 letters | stage one, 1–12 letters | 21.1 million | 23.24 |

- **Listed keys:** the 80 Kryptos words (`r75/data/kryptos_words.txt`) and every word of 3–15 letters in the R59 word
  model, without repeats: 28,943 words.
- **Conventions:** 96 per family. PA1, CA1, PA2, CA2 give 8 combinations with CA1 ≠ PA2. The listed stage has 3
  operations and a key numbering of A–Z or KRYPTOS. The free stage has 2 signs; variant Beaufort and the key numbering
  are absorbed by a free key.

## Solver (`r80a/blind/run.py`; pass 0 in `r80a/twostage.c`, then R79's `r79/slotsolve.c`)
- **Pass 0, every setting:** each slot of the free key starts at its best single-letter fit, and the decode is scored
  by quadgrams, with no ascent. The 4,000 best settings of each free length go on.
- **Pass 1:** R79's solver on those settings, 1 start.
- **Pass 2:** the family's 150 best settings again, with 6 starts.
- **Keep:** the family's 60 best distinct decodes, re-derived by the explicit decryptor, then re-scored by the letter
  model as in R79.

**Tests** (`r80a/tests/test_r80a.py`, all pass):
- encryption and decryption round-trip;
- the solver tables decode plants exactly;
- the fast pass 0 equals its reference;
- the solver reaches the truth's score on 12 of 12 plants, all exact.

## Development check (`r80a/dev80.py`, `r80a/results/DEV.json`; spent R81a gate books)
DEV_TABLE

## Cuts: letter model ≥ CUT_LM and word model ≥ CUT_WORD per letter
CUT_TEXT

## Sealed synthetic gate (`r80a/sealed/make_holdout80.py`, seed 800300)
Four GITenberg books never used in this project and not in the letter model's training text:

| Role | Book | GITenberg | sha256 |
|---|---|---|---|
| Positives A | *The Age of Innocence* (Wharton) | 541 | 4e134e83… |
| Positives B | *The Moonstone* (Collins) | 155 | 47fd0032… |
| Negative plaintext | *Kidnapped* (Stevenson) | 421 | 94aa2a92… |
| Negative keys | *The Prisoner of Zenda* (Hope) | 95 | 262d60db… |

**Items.**
- **Positives: 80**, 10 per family per book: 5 plain, 3 with 2 letters changed, and 2 in nonstandard spelling (R79's
  rules).
  - Free key 1–10 letters.
  - L1 and L2: the listed key is a word of 3–12 letters, chosen uniformly by length. X1 and X2: 1–3 letters.
- **STRETCH plants: 16**, free key 11–12 letters, reported only.
- **Negatives: 100.**
  - R79's seven wrong-family generators, 12 each.
  - 8 NEG_TWO_RANDOM: two stages with both keys random strings of 4–12 letters (never a listed word, never 1–3
    letters), so outside every family.
  - 8 shuffles.

**Pass rule** (`r80a/sealed/gate80.py`):
- **Recovered:** at least 95 of 97 letters right. A shadow decode (about half right) is never credited
  (`r80/FABLE_IDENTIFIABILITY.md` §1.6). Exact and ≥ 85 are also reported.
- **A family passes** iff at least 18 of its 20 positives are recovered and confident, AND 0/100 negatives are
  confident, AND every stored decode re-encrypts.
- **Reported:** by free-key length, listed-key length, their gcd and lcm (≤ 24, 25–48, ≥ 49), and spelling kind.

## What follows (fixed now)
| Result | Next |
|---|---|
| A family passes | It is ready for R80: K4 and 100 shuffles, blind, frozen, then the reveal and the check of the frozen work. R80 gets its own pre-registration with these numbers and runs only on Tyler's go |
| A family fails | Report by length where it fails. It is not run on K4 and closes nothing |
| Mode A (both keys free) | Not tested here. "Two unknown non-word keys" stays outside R80's scope (`r80/FABLE_IDENTIFIABILITY.md` §1.7) |

**Not covered by R80a or R80:**
- listed keys at phases other than 0 (mode L+);
- PALIMPSEST and ABSCISSA alphabets in either stage;
- listed keys outside the word list;
- free keys of 13 or more letters;
- both keys free.
