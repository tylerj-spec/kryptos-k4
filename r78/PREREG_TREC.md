# R78b pre-registration: T-REC, a key-free test for recency-ordered alphabets (Claude Code, Fable, 11 Nov 2026)

Written before the test is run on K4. It uses the 97-letter ciphertext only. The script (`r78/trec.py`) reads no
published letter. The proof is in `r78/FABLE_MASKING.md` (§3).

## Model
A substitution whose cipher alphabet is a list that is re-ordered after every letter by a recency rule:
- **MTF-C:** the cipher letter just used moves to the front of the list;
- **MTB-C:** it moves to the back.

The plaintext alphabet P is fixed. To encipher p, take its index j in P and write the letter at place j of the
list. The starting list and P may be any two of the 26! orderings.

## Theorem (recency transform)
Let ρ(i) be the number of distinct letters that occur in the ciphertext strictly between position i and the
previous occurrence of the same letter. At every position whose letter has occurred before:
- MTF-C: the plaintext index is ρ(i);
- MTB-C: the plaintext index is 25 − ρ(i).

So the sequence ρ at those positions is a simple (monoalphabetic) substitution of the plaintext, whatever the
starting list. It is computed from the ciphertext alone.

## Test
- **Statistic A:** the index of coincidence of ρ over the positions whose letter has occurred before (71 positions
  for K4).
- **Null:** 10,000 shuffles of K4 (seed 780200).
- **Positives:** 2,000 planted messages. Plaintext: a random 97-letter window of the first 768 letters of
  `k4kit/data/k1k3_plaintext.txt`. P: A–Z, KRYPTOS, or a random ordering. Starting list: random. Rule: MTF-C or
  MTB-C. The theorem must hold exactly in every plant.

## Decision rule (fixed now)
- **SIGNAL:** A(K4) is at or above the 99.9th percentile of the shuffles and at or above the 1st percentile of the
  plants. Then stop and report. No decode is attempted in this round.
- **DISFAVOURED:** A(K4) is below the 1st percentile of the plants. The class (either rule, any starting list, any
  fixed plaintext alphabet, English-like plaintext) is then recorded as STAT, not EXCL.
- Otherwise: no conclusion.

## T-REC2 (the plaintext list is the one re-ordered)
- **Model.** MTF-P / MTB-P: the plaintext letter just enciphered moves to the front (or back) of the plaintext
  list; the cipher alphabet is fixed. The ciphertext is then a fixed relabelling of the plaintext's own recency
  ranks.
- **Statistic B:** the index of coincidence of the ciphertext letters (K4: 0.0361).
- **Positives:** 2,000 plants as above with a random starting list and a random cipher alphabet.
- **Rule:** DISFAVOURED if B(K4) is below the 1st percentile of the plants; otherwise no conclusion.
