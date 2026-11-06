# R70 result (Claude Code, 6 Nov 2026): none of the five named source texts is K4's running key

**No K4 solution. No candidate.** The blind search found nothing above the nulls. The exhaustive post-freeze check
excludes all five pinned texts under the tested models. No external checker was contacted.

## Plain words
- **The test:** could K4 be a running-key cipher whose key is a passage of one of the five books in the Deep Research
  report?
  - the 1912 Berlin Baedeker;
  - the 1908 Egypt Baedeker;
  - Murray's 1907 Egypt handbook;
  - Cook's Egypt handbook (1876 edition);
  - Budge's *Book of the Dead* (1898).
- **What was tried:** every starting point in each book (4.5 million), with the key read straight or along the 10
  sculpture routes, in two alignments and six tableau conventions. That is 570 million settings.
- **The method works:** on 20 hidden test messages built from these books, it recovered every one exactly: right book,
  starting letter, route and convention, all 97 letters. With two letters of the key corrupted (as OCR might), 5/5 were
  still recovered. With a letter dropped, 3/5 were.
- **K4 does not respond:**
  - its best decode scores −450, in the range of 50 shuffled copies of K4 (2 score higher);
  - real test messages scored −128 to −193;
  - that decode is gibberish and matches 1 of the 24 published letters.
- **The exhaustive check after the freeze settles it:**
  - no setting of any book reproduces either published word block exactly on K4 (EASTNORTHEAST, 13 letters, or
    BERLINCLOCK, 11 letters);
  - for the in-place and M1 readings, the key letters of each block are contiguous, so the block test still catches a
    key with one extra or missing OCR letter between the two blocks;
  - K4's best partial match is 8–10 of 24 letters per book, the same as the shuffles (9–11).

## Steps
| Step | Commit | Result |
|---|---|---|
| Pre-registration (`r70/PREREGISTRATION.md`) | aa655bb | — |
| Holdout plants (seed 700001; truth sha256 7a2f892f… withheld) | 2978d25 | 30 plants + 20 nulls |
| Holdout freeze | 9702e0b | 50 × 200 frozen decodes |
| `verify.py` (truth not opened) | ebd4620 | **PASSED**, 10,000 witnesses |
| Gate (truth hash matched) | ebd4620 | **PASSED**: CLEAN 20/20 recovered, setting exact 20/20 |
| Target (K4 + 50 shuffles, seed 700070) | e970f7a | — |
| K4 freeze | 5720b21 | 51 × 200 frozen decodes |
| `verify.py` (no published letters) | 0ff8f9e | **PASSED**, 10,200 witnesses |
| Sealed reveal | edc4c91 | **NO_SIGNAL**, 0 contenders |
| Sealed exhaustive block check | this commit | **EXCL** for all five texts |

## Holdout gate (`r70/holdout/GATE.json`)
| Plants | Recovered | Setting exact | Median letters | Totals |
|---|---|---|---|---|
| CLEAN (20) | **20/20** | 20/20 | 97/97 | −128.0 to −169.9 |
| NOISY_SUB (5; 2 key letters changed) | 5/5 | 5/5 | 95/97 | −165.6 to −192.7 |
| NOISY_DEL (5; 2 changed + 1 deleted) | 3/5 | 2/5 | 65/97 | −242.6 to −461.6 |

- The maximum null score was −455.68.
- Bar: 18/20 CLEAN recovered.

## K4 (`r70/k4/REVEAL.json`, `r70/k4/EXACT.json`)
- **Blind best (rank 0):** EGYPT_1908, offset 1,081,845, COL_LT / M2 / KRY_BEAU, total −450.04 (lm6 −179.12,
  word −270.91).
  - 2/50 nulls score higher, p = 0.059.
  - Nulls' best totals range from −482.8 to −428.0, median −467.8.
- **Raw plaintext** (carved order, unedited):
  ```
  FEMDMYHASJSNIZDQPANVJZWMELESPERICXGOLALOIEXSBOBBUEOMEMDCJOBSALEMFRWERIAKIIABOHQCAIRCPLAINNWIYESTM
  ```
  Key text used (Baedeker 1908): `OTHELEFTWEREACHTHETOMBOFKENAMUNDATINGFROMTHETIMEOFAMENOPHISIIANDDEMANDINGNOTICEONACCOUNTOFTHEMAGN`
- **Published letters:**
  - rank 0 matches 1/24;
  - the best of K4's 200 frozen decodes matches 5/24 (nulls: median 5, maximum 6);
  - **0 contenders** at ≥ 12/24.
- **Exhaustive block check** (every one of 5.7 × 10⁸ settings per ciphertext):

  | Source | K4 max letters (of 24) | K4 full blocks (13/13 or 11/11) | Nulls max letters: median / max | Nulls with a full block | Status |
  |---|---|---|---|---|---|
  | BERLIN_1912 | 9 | 0 | 9 / 11 | 0/50 | **EXCL** |
  | EGYPT_1908 | 10 | 0 | 10 / 11 | 0/50 | **EXCL** |
  | MURRAY_1907 | 10 | 0 | 10 / 11 | 0/50 | **EXCL** |
  | COOK_1876 | 10 | 0 | 9 / 11 | 0/50 | **EXCL** |
  | BUDGE_1898 | 8 | 0 | 9 / 10 | 0/50 | **EXCL** |

## What this means
- **Excluded (exact, within scope):**
  - Scope: a running key read forward from these five pinned OCR texts (these editions, this normalisation), in place
    or along the 10 R61 routes, in either alignment model, under the 6 tableau conventions.
  - For ID and M1 rows, each block's key letters are contiguous. The exclusion therefore tolerates any OCR error outside
    a block's 13 or 11 key letters, including one insertion or deletion between the blocks.
  - For M2 rows, each block's key letters are spread over the 97-letter window by the route. A single OCR slip in the
    wrong place can then break both blocks.
  - The pre-registration's wording ("one insertion or deletion between the blocks still leaves one block exact") holds
    exactly for ID and M1 rows only; this is a clarification, and nothing was re-run.
- **The blind search agrees:**
  - Its power on clean keys from these books is 20/20, and 5/5 with two corrupted letters.
  - K4 looks like its shuffles.
- **Not covered:**
  - other editions, or the report's original 1897 Cook and 1895 Budge (substituted here, see the pre-registration);
  - keys read backwards or skipping letters;
  - mixed alphabets, other transpositions, non-English plaintext, a masking layer;
  - an OCR slip inside a published block's key letters (and, for M2 rows, anywhere among them across the window).
- **Selection was clue-motivated** (Berlin, Egypt) and is disclosed. It does not affect the exclusion.
