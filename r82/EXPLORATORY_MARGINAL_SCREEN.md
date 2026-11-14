# R82 separate exploratory ciphertext-only marginal screen (NOT preregistered)

**Status:** one post-design descriptive screening calculation, not a K4 method-discovery
run, not a frozen experiment, not a ledger exclusion. It used the
**original 97-character ciphertext only** plus 80 *previously revealed*
R81a synthetic English plaintext controls. It did **not** use any published
K4 plaintext words, positions, or proposed plaintext. No keys or candidate
plaintext were constructed or fitted from these results. Do not use
this exploratory statistic to tune a subsequent K4 candidate generator.

## Prior mathematical prediction

The reversible R82 pure 2x13 fractionation model, with one alphabet A
used before and after coordinate recombination and any independent
within-block row/column *position* permutations, preserves both:
(1) the total count of each of the 2 row-coordinate values and
(2) the total histogram of the 13 column-coordinate values.
This remains true for any number of **whole-letter transpositions**
before or after that one fractionation stage, because transpositions
preserve the complete multiset of letters.

An ordinary-English plaintext should therefore leave ordinary-
English-like *coordinate marginals* in ciphertext, for each correctly
specified fixed alphabet A. Any final substitution, any second
fractionation on a different alphabet, an unknown chart, or systematic
preprocessing is outside this pure-model necessary condition.

## Exploratory screen setup

- K4 source: immutable original ciphertext entry in
  r81a/k4/TARGET.tsv, used only as 97 observed ciphertext letters.
- English source: 80 positively labeled, already revealed 97-letter
  English passages in r81a/holdout/sealed_truth.json, not any
  public-known K4 plaintext. The passages contain some misspellings.
- Named alphabet charts: AZ, and keyed KRYPTOS, PALIMPSEST,
  ABSCISSA (deduplicate keyword and then append unused A-Z).
- Random split was deterministic but not preregistered:
  Fisher-Yates on source-order positive entries, seed 821371,
  LCG step seed=(1664525*seed+1013904223) mod 2^32,
  swap i with seed mod (i+1), from i=79 down to 1.
  First 40 -> training; last 40 -> independently scored English.
- For each alphabet, estimate the two row-coordinate probabilities
  and thirteen column-coordinate probabilities from training with
  pseudo-count 0.5 each, normalized SEPARATELY per coordinate axis.
- For each string t, compute the simple *pseudo*-log-likelihood:
  S_A(t)=sum over letters i of
  log[p_row(r_A(t_i))] + log[p_col(c_A(t_i))].
  Do NOT interpret S_A as a calibrated joint probability; row and
  column variables are not assumed independent in real English.
- Compare the observed ciphertext score to the range of scores
  of 40 held-out English controls under the identical fixed chart.
  There was NO K4 key, route, word, or alphabet selection.

## Observed numbers

| Fixed chart | K4 pseudo-LL | Lowest of 40 English heldout | English median | English controls <= K4 |
|---|---:|---:|---:|---:|
| AZ | -342.489 | -310.799 | -298.980 | 0/40 |
| KRY | -338.965 | -306.425 | -297.546 | 0/40 |
| PAL | -335.641 | -304.806 | -297.434 | 0/40 |
| ABS | -340.997 | -313.035 | -292.394 | 0/40 |

**Interpretation:** With these four *fixed* charts, pure 2x13
fractionation (including additional whole-letter transposition)
preserves marginals that make the observed K4 ciphertext
markedly unlike the sample of ordinary English controls.
Thus this narrow pure-fractionation construction is a
lower-priority candidate than R80a or plaintext-driven key
schedules. It is **statistical only**, not impossible or
algebraically excluded.

**Do not generalize:** An arbitrary unknown alphabet can dramatically
change coordinate counts; another substitution stage destroys this
particular invariant; preprocessed or nonstandard-English covertext
can shift the baseline. The training sample is only 40 passages from
two books, the 40 observations are correlated, and model selection
was not frozen before the original K4 score was inspected. These
numbers are *NOT* a preregistered p-value and must NOT count as
a new exclusion row in LEDGER.md.

**Controls warning:** Shuffling the original K4 ciphertext is
not an appropriate null for this particular statistic; its
global row and column marginal counts are identical after every
letter permutation. For a future properly preregistered marginal
test, use fresh natural-text populations, changed-orthography
populations, independent wrong-family cipher populations, and
independent random ciphertexts. Control for the maximum over any
alphabet family actually searched.

## Priority impact

Focus next on R80a one-stage-known/two-tabulae, especially the
single-shared-key rotated-second-stage variant specified in
r82/LINKED_KEY_LAYER.md; and R81b plaintext-driven state. Do NOT
tune 2x13 routes on K4 to recover English-looking snippets on
the basis of this post hoc negative screen.
