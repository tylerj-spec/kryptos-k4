# R72 (Claude Code, 8 Nov 2026; revised after the PR #60 review): reconstruction of Sanborn's documented sheet operations, and the evidence gate for R73

**Documentation and K3 reconstruction only.** No K4 decryption, no K4 search, and no published K4 letters (R53).
Reproduce everything with:
- `python3 -I r72/reconstruct.py`
- `python3 -I r72/novelty.py`
- `python3 -I r72/tests/test_r72.py`

Outputs are in `r72/data/`.

**R73 is on hold** (see the gate below).

## Plain words
- **K3 is reproduced exactly from its two documented worksheets.**
  - Write the plaintext in rows of 42 (the 42 × 8 sheet).
  - Turn the sheet a quarter clockwise.
  - Write the result in rows of 14 (the 14 × 24 sheet).
  - Turn it a quarter clockwise again.
  - That gives all 336 K3 ciphertext letters. Each letter's two sheet positions are in `r72/data/K3_INDEX_MAP.tsv`.
- **Turning a sheet is "take every k-th letter."** With positions numbered from 1 on an n-cell sheet:
  - a quarter turn of a sheet w wide moves position j to w·j mod (n + 1) anticlockwise, and to −w·j clockwise;
  - two turns multiply;
  - so K3 = "multiply by 42 × 14 = 588 ≡ 251 (mod 337)", and decryption multiplies by 192.
  - This was checked for every whole-grid sheet of 336 and of 98 cells.
  - Twelve width pairs give K3's exact ciphertext, so only the worksheets, not the ciphertext, show that Sanborn used
    42 × 8 and 14 × 24.
- **The 14 × 31 sheet is geometrically consistent with an output or transcription layout.**
  - K3's ciphertext, the separator and K4's ciphertext fill it exactly: 336 + 1 + 97 = 434 = 14 × 31.
  - That puts K4 at row 11, column 28 (1-based) onward: 4 + 31 + 31 + 31, explaining the carved row structure without
    any K4 route.
  - `reconstruct.py` builds this grid from the carved ciphertext. It does **not** transcribe the 434 cells of the NOVA
    sheet, which the kryptools catalog says differs slightly from the final sculpture. A cell-by-cell comparison needs a
    high-resolution first-generation image.
  - Sanborn's 2006 NPR account of adjusting line lengths (cited by the reviewer) fits an output layout.
  - Nothing here proves the sheet was unused in K4's encryption.
- **A K4-sized whole sheet is an analogy, not a document.**
  - 97 is prime, so no fully filled rectangle larger than one row holds K4 alone.
  - With one extra cell, 98 = 14 × 7 = 2 × 49. Nothing shows that such a cell existed, where it was, or that the
    carved "?" took part.
  - This idea is not new: Intel Today (2020) and earlier researchers proposed 7 × 14 for K4.
- **The 9 orderings, exactly:**
  - Two same-direction quarter turns of a complete 98-cell sheet (widths 2, 7, 14, 49) give 9 distinct orderings,
    "every k-th cell mod 99", k ∈ {4, 14, 25, 28, 46, 49, 92, 97, 98}.
  - Inverse pairs: (4, 25), (14, 92), (28, 46), (49, 97); 98 is its own inverse.
  - These are not all possible 98-cell readings; they are this one documented operation's orderings.

## Novelty and provenance check (`r72/novelty.py` → `r72/data/NOVELTY.json`)
**Method:**
- Each ordering becomes a 97-letter route by removing the extra cell (first or last).
- A route and its inverse are counted separately. They are different trials in a layered cipher, giving 36 directed
  routes.
- Each is compared as an exact tuple and placed in one tier:
  - **CONFIRMED_EXECUTED:** identical to a route in a committed run artifact. 5,069 routes across the R32, R34, R35, R41,
    R61, R63, R66 Part B and R69 route files.
  - **LEDGER_DOCUMENTED:** identical to a member of a family the ledger says was run, with no artifact in the repo. These
    are L06 columnars of widths 2–10, L07/L47 decimations mod 97, and L47 same-direction double turns of widths 2–48,
    rebuilt from the ledger because L47's generator is absent.
  - **GENERATED_ONLY:** identical only to a member of a larger generated set never documented as run (single ragged turns
    of every width; mixed-direction double turns beyond R35's 4–28). This is equivalence, not a run.
  - **NEW:** none of the above.

**Results:**

| Ordering | Extra cell first | Extra cell last |
|---|---|---|
| k = 4, 25, 28, 46 | NEW | NEW |
| k = 14 | NEW | GENERATED_ONLY (= single ragged turn, width 14, CCW) |
| k = 49 | NEW | GENERATED_ONLY (= single ragged turn, width 49, CCW) |
| k = 92 | NEW | LEDGER_DOCUMENTED (= columnar width 7, read bottom-up; L06/L47) |
| k = 97 | LEDGER_DOCUMENTED (= decimation 48i+96 mod 97) | LEDGER_DOCUMENTED (= decimation 48i+48 mod 97) |
| k = 98 | LEDGER_DOCUMENTED (reversal) | LEDGER_DOCUMENTED (reversal) |

- **Directed counts:** 0 confirmed executed, 10 ledger-documented, 4 generated-only, 22 new.
- **No documented run:** 13 route classes, i.e. 26 directed routes (NEW + GENERATED_ONLY).
- **Corrections:**
  - My earlier "8 untested orderings" and then "11 genuinely new routes" both overstated what was known.
  - Calling a generated equivalent "tested" was wrong; only an artifact proves a run.
  - None of the 36 matches a committed run artifact.

## Prior work
| Work | What it did | Standing here |
|---|---|---|
| Intel Today (2020), "Analysis of Sanborn K3 worksheet" | Proposed a 7 × 14 (98-cell) K4 layout | Idea only |
| Rondeau, experiment 86, "the question mark as the 98th cell" | 98-cell K3-like rotations with periodic and autokey keys | Checked against the published letters, i.e. **crib-assisted**, not R53-blind evidence |
| This project, L47 | 97-letter K3 double turns, widths 2–48, and mod-97 decimations, with summed periodic keys | Crib-assisted, pre-R53 |
| This project, R32–R69 (committed route artifacts) | 97-letter routes run on K4 | None of the 36 directed 98-cell routes is among them |

## Photo and source evidence (from the reviewer's direct inspection on PR #60; not re-inspected here, because this environment cannot reach the image hosts)
- **"TOP #4"** (NOVA frames 16–17) is bold writing in the translucent, hole-punched margin below a letter grid.
  - It is more consistent with a sleeve or organizational marking than with an instruction to perform a K4 operation.
  - One still frame cannot assign the ink to paper or plastic.
- **Frames 3, 19 and 20:** several sheets, handling and folds are real. None shows two encryption layers being aligned,
  or a K4-only 97- or 98-cell worksheet.
- **The 2014 "K3 Method" page** is secondary researcher inference, not Sanborn's statement. It speculates about the
  sleeve, swapping sheets into it, and a possible "Bottom #4". The photographs do not confirm such a sheet.
- **Kryptools catalog:** #1 42 × 8 and #2 14 × 24 (K3), and output #3 14 × 31. The source says the photographed 14 × 31
  sheet differs slightly from the sculpture.
- **PBS transcript, broadcast 24 July 2007:**
  - Sanborn demonstrates grid transposition for K3.
  - Scheidt says the first challenge for K4 is determining its *masking technique*.
  - The narrator's examples (vowel removal, phonetic spelling) are illustrations, not testimony about Sanborn's method.

**Priority sources to acquire:**
- the full 2007 NOVA *moving* footage around the two sheet-handling sequences;
- higher-resolution first-generation scans of the K3/K4 worksheets, especially the "TOP #4" sleeve and the full
  14 × 31 grid, for a cell-by-cell comparison.
- Do not read any confidential K4 plaintext.

## Gate decision for R73: on hold
- **The photographic gate for a K4 98-cell sheet has not passed.** No such sheet is shown, and the 98-cell model is
  speculation by analogy.
- **R73 is therefore not proposed as a supported experiment.**
- **If Tyler wants it anyway**, it would be an explicitly *exploratory* blind run of the 26 directed routes with no
  documented run:
  - exact orientation, extra-cell insertion and removal, and substitution-before or after-transposition semantics frozen
    first and validated on synthetic plants;
  - separately pre-registered;
  - costed first with a synthetic-only pilot under a hard core-hour cap;
  - gated on hidden-key, hidden-method recovery and null false-positive rates;
  - frozen before a separate post-freeze validator;
  - never using the published letters, crib-assisted survivors or the width-7 observation to generate, rank, prune or
    score anything.
  - A post-freeze crib-assisted check over all settings would be labelled as such, not as a blind exclusion.
- **Disclosure:** I first noticed 98 = 14 × 7 while looking at K4's width-7 doubled letters (exploratory). Those
  letters are not used anywhere in R72.
