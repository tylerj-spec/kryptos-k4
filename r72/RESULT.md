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
- **The 14 × 31 sheet looks like an output or transcription layout.**
  - K3's ciphertext, the separator and K4's ciphertext fill it exactly: 336 + 1 + 97 = 434 = 14 × 31.
  - That puts K4 at row 11, column 28 (1-based) onward: 4 + 31 + 31 + 31.
  - That explains the carved row structure without any K4 route.
  - The reviewer adds Sanborn's 2006 NPR account of adjusting line lengths for the panel's look.
  - It does **not** prove the sheet was never used in K4's encryption. The earlier wording "not an encryption sheet"
    was stronger than the evidence.
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

## Novelty check (`r72/novelty.py` → `r72/data/NOVELTY.json`)
**Method:**
- Each ordering becomes a 97-letter route by removing the extra cell (first or last), in both directions.
- Each route is compared as an exact tuple with 26,701 routes this project has already run on K4:
  - ragged single turns of every width;
  - K3-style double turns, widths 2–48, same and mixed direction (L47, L115, L124, R35);
  - all mod-97 decimations (L07, L47);
  - complete columnars, widths 2–10 (L06);
  - the R61 routes and the R69 readings.
- L47's original generator is not in the repository, so its catalog is rebuilt from its ledger description.

**Results:**

| Ordering | Extra cell first | Extra cell last |
|---|---|---|
| k = 4, 25, 28, 46 | new | new |
| k = 14 | new | = single quarter turn, width 14, CCW (tested) |
| k = 92 | new | = single quarter turn, width 7, CW (tested) |
| k = 49 | new | = single quarter turn, width 49, CCW (tested) |
| k = 97 | = decimation 48i+96 mod 97 (tested) | = single quarter turn, width 2, CW (tested) |
| k = 98 | = reversal (tested) | = reversal (tested) |

**Eleven genuinely new 97-letter routes**, counting a route and its inverse once:
- k = 4, 25, 28 and 46 with the cell first or last (8 routes);
- k = 14, 49 and 92 with the cell first (3 routes).

My earlier count of "8 untested orderings" overcounted. This table replaces it.

## Prior work
| Work | What it did | Standing here |
|---|---|---|
| Intel Today (2020), "Analysis of Sanborn K3 worksheet" | Proposed a 7 × 14 (98-cell) K4 layout | Idea only |
| Rondeau, experiment 86, "the question mark as the 98th cell" | 98-cell K3-like rotations with periodic and autokey keys | Checked against the published letters, i.e. **crib-assisted**, not R53-blind evidence |
| This project, L47 | 97-letter K3 double turns, widths 2–48, and mod-97 decimations, with summed periodic keys | Crib-assisted, pre-R53 |
| This project, R61–R69 | 97-letter routes with blind solvers | None of the 11 new routes is among them |

## Photo evidence (from the reviewer's inspection of the NOVA stills on thekryptosproject.com; not re-inspected here, because this environment cannot reach the image hosts)
- **"TOP #4"** is plainly visible in the margin below the letter grid, next to a translucent or punched edge.
  - A still frame does not establish whether the ink is on the paper or on the sleeve.
  - It does not show that a fourth cipher-operation sheet existed.
  - A 2014 interpretation calls the layer uncertain.
- **Several sheets:** folds and a flexible sheet (still 19) and another gridded sheet in the background (still 3) show
  several physical sheets being handled. They do not show a two-layer encryption mechanism.
- **K3 step 2 and the 14 × 31 layout:** the step-2 still and the 14 × 31 reconstruction agree with the known K3
  process and panel alignment. The red fold lines on the reconstruction are later researcher annotations.
- **No K4 sheet:** no photographed standalone 97- or 98-cell K4 encryption sheet was found.
- **Still open from the checklist:** sheet sizes other than 42 × 8, 14 × 24 and 14 × 31; reading-direction arrows; the
  fold-to-grid coordinates.

## Gate decision for R73: on hold
- **The photographic gate for a K4 98-cell sheet has not passed.** No such sheet is shown, and the 98-cell model is
  speculation by analogy.
- **R73 is therefore not proposed as a supported experiment.**
- **If Tyler wants it anyway**, it would be an explicitly *exploratory* blind run of the 11 new routes only:
  - separately pre-registered;
  - costed first with a synthetic-only pilot under a hard core-hour cap;
  - gated on hidden-key, hidden-method recovery and null false-positive rates;
  - frozen before a separate post-freeze validator;
  - never using the published letters, crib-assisted survivors or the width-7 observation to generate, rank, prune or
    score anything.
  - A post-freeze crib-assisted check over all settings would be labelled as such, not as a blind exclusion.
- **Disclosure:** I first noticed 98 = 14 × 7 while looking at K4's width-7 doubled letters (exploratory). Those
  letters are not used anywhere in R72.
