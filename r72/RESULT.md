# R72 (Claude Code, 8 Nov 2026): reconstruction of Sanborn's documented sheet operations, and the evidence gate for R73

**Documentation and K3 reconstruction only.** No K4 decryption, no K4 search, and no published K4 letters (R53).
Reproduce everything with `python3 -I r72/reconstruct.py` and `python3 -I r72/tests/test_r72.py`. Outputs are in
`r72/data/`.

## Plain words
- **K3 is reproduced exactly from its two documented worksheets.**
  - Write the plaintext in rows of 42 (the 42 × 8 sheet).
  - Turn the sheet a quarter clockwise.
  - Write the result in rows of 14 (the 14 × 24 sheet).
  - Turn it a quarter clockwise again.
  - That gives all 336 K3 ciphertext letters. Every letter's two sheet positions are listed in `r72/data/K3_INDEX_MAP.tsv`.
- **Turning a sheet is just "take every k-th letter."** With positions numbered from 1 and n cells on the sheet:
  - one quarter turn of a sheet w wide moves position j to w·j mod (n + 1) anticlockwise, and to −w·j clockwise;
  - two turns multiply;
  - K3's two turns are therefore "multiply by 42 × 14 = 588 ≡ 251 (mod 337)", and decryption multiplies by 192.
  - This was checked for every whole-grid sheet of 336 and of 98 cells.
  - One consequence: 12 different width pairs give K3's exact ciphertext (7 × 84, 14 × 42, 21 × 28, and so on). The
    ciphertext alone cannot tell you which sheets Sanborn used; only the worksheets can, and they show 42 × 8 and
    14 × 24.
- **The 14 × 31 sheet is a fabrication layout, not an encryption sheet.**
  - It holds K3's ciphertext, the separator and K4's ciphertext: 336 + 1 + 97 = 434 = 14 × 31.
  - That puts K4 at row 11, column 28 (1-based) onward: 4 + 31 + 31 + 31.
  - The carved row structure is fully explained by this sheet, so it is not evidence of a K4 route (agreeing with
    R69 and the archival research).
- **The same documented procedure on a K4-sized sheet:**
  - 97 is prime, so no whole sheet holds K4 alone.
  - With one extra cell (the carved separator, or a blank), the sheet is 98 = 14 × 7 = 2 × 49. 14 rows matches K3's
    14 × 24 sheet.
  - Every double turn of a 98-cell sheet is "take every k-th cell mod 99". Only **9 distinct orderings** exist:
    k ∈ {4, 14, 25, 28, 46, 49, 92, 97, 98}.
  - k = 98 is plain reversal, which was already covered.
  - The other **8 have never been tested on K4**:
    - earlier rounds applied K3-style turns only to the 97 letters on ragged grids (L47, L115, L124, L126, R61–R68);
    - L47's decimations were mod 97, in a pre-R53 crib-assisted search.

## Demonstrated vs speculative (evidence inventory)
| Item | Status | Basis |
|---|---|---|
| K3 plaintext written in rows of 42, turned, rewritten in rows of 14, turned | **Demonstrated** (reproduces K3 exactly) | Worksheet descriptions (kryptools "K3 Step 1/Step 2"), verified here letter for letter |
| 14 × 31 sheet = K3 ct + separator + K4 ct | **Demonstrated** (arithmetic and carved text) | NOVA-era worksheet; `panel_14x31` in `RECONSTRUCTION.json` |
| 14 × 31 is a layout/fabrication sheet, not an encryption sheet | **Strongly supported** | It holds ciphertext only; no operation on it reproduces any plaintext |
| K4 enciphered on its own sheet(s) like K3 | **Analogy only** | Scheidt: "more than one stage"; Sanborn: matrix systems he modified |
| A transparent sleeve or overlay; what "TOP #4" labels | **Not inspected here** | This environment cannot reach the image hosts (PBS, kryptools, thekryptosproject; the environment change was rejected). See the checklist below |
| Masking step | **Undetermined** | Scheidt's statements name it but do not define it |

## Photo checklist (for Tyler or ChatGPT, who can view the frames)
Record for each item: the frame or still, what is visible, and whether it moves with the paper or the sleeve.
1. **"TOP #4":** is it written on the paper sheet or on the transparent sleeve? Which edge is "top"? Is there a "#1–#3"
   anywhere?
2. **Sheet sizes:** count the grid columns and rows of every visible sheet, and write down any sheet that is not
   42 × 8, 14 × 24 or 14 × 31.
3. **Arrows, numbers or marks at row or column ends:** are there arrows showing a reading direction, or numbers
   giving an order of columns?
4. **Folds:** where do the folds cross the grid (row and column)?
5. **Two layers:** do any marks stay fixed while the paper under them moves?
6. **K4 cells:** is any K4-sized sheet visible (97 or 98 cells; 14 × 7, 7 × 14, 2 × 49)? Do not read or record any K4
   plaintext letters if they appear.

## Gate decision for R73
ChatGPT's gate asks for a reversible operation that is independently supported, previously untested, and not fitted
to K4's anomalies.

- **From the photographs: not met,** because they could not be inspected here.
- **From the K3 reconstruction: one narrow candidate qualifies:** K3's own documented double turn, applied to a whole
  98-cell sheet.
  - This gives 8 new orderings, combined with the substitution layer a multi-stage process needs, since K4's flat
    letter counts rule out a pure transposition.
- **Caveats, disclosed:**
  - (a) The extra cell's convention is not documented. It could be the carved "?" as the first cell, or a blank as
    the last cell. Both would be tested; nothing else would.
  - (b) 14 rows is an analogy to K3, not a document.
  - (c) I first noticed 98 = 14 × 7 while looking at K4's width-7 doubled letters (exploratory). The operation itself
    is taken from K3 alone, and R73 would not use the doubled letters or any other K4 anomaly to select or score
    anything. The width-7 pattern stays a secondary diagnostic, not a filter.

## Proposed R73 (not run; needs approval)
- **Orderings:** the 8 untested 98-cell orderings × 2 extra-cell conventions, i.e. 16 transpositions of K4's 97
  letters.
- **Substitution layers:** each transposition is run through the substitution solvers this project has already gated:
  - English running key (R61-type);
  - keyed periodic, Gromark and autokey (R68);
  - homophonic (R66).
- **Gate first:** hidden synthetic plants made with these exact orderings.
- **Then K4:** K4 + shuffled nulls, frozen and verified, before the sealed published-letter check (R53).
- **Cost:** small. 16 orderings instead of R61's 10 routes, on solvers that already exist.
- **Expected outcome:** probably NO SIGNAL, like its predecessors. Its value is that it closes the one K3-documented
  operation never applied to a whole K4 sheet.
