# R44b holdout B result (evaluated after the freeze at 433572b)

**Gate PASSED: 20/20 exact** (pre-registered bar ≥ 16/20; `r44/PREREGISTRATION_B.md`).

| Measure | Solver + polish (gate) | Solver only |
|---|---|---|
| Exact 97/97 | **20/20** | 16/20 |
| ≤ 3 letters wrong | 20/20 | 19/20 |
| Invalid forward witnesses | 0 | 0 |
| Plaintext alphabet identified | 20/20 | 20/20 |

The polish fixed all 4 solver-only misses (1–4 errors each, on rare ciphertext letters).

## What it shows
Under **H-KW**, 97-letter English can be recovered **exactly and blind**:
- **Plaintext alphabet:** a keyword alphabet, with the keyword among the 5,000 most frequent dictionary words of
  length 5–10.
- **Cipher alphabet:** completely free.
- **Key:** the true Gromark key is given.

Two **uniformly random** alphabets remain unsolved (L138, L139).

## What it does not show
- **Nothing about K4.** The method has never been run on K4.
- **The key is supplied.** For K4 it is unknown, so a K4 round needs a key family, a cost plan and nulls. Cost:
  about 4,749 keywords × 2 operation forms × ~75 ms per key. A key shortlist is needed; for Gromark, R39's
  alphabet-free IC ranking is one. The round must be pre-registered separately, with its blind output frozen before
  the 24 known letters are consulted.
- **Closed world.** The keyword was in the candidate list. A keyword outside it gives a near-miss (the R44
  development case RULED: 11 letters wrong).
