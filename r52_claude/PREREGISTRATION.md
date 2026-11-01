# R52 (Claude Code) pre-registration, 31 Oct 2026: exact screen of all chain-addition key families × keyword alphabets

Written before any R52 result on K4. This is a **sealed, crib-assisted exact feasibility screen** using the 24
published letters. It can exclude a family; it cannot produce or confirm a plaintext. A family that survives would get
a separately pre-registered **blind** R44b run, with no clue letters, plants and a freeze before the reveal.

## Families (all primers of each)
Chain addition k_i = k_{i−b} + k_{i−b+1} (mod B), as in the harness CHAIN/CHAINBASE:
- **B = 10:** b = 4, 5, 6, 7, 8.
- **B = 5–26 except 10:** b = 4 and 5.

## Routes (`r52_claude/routes.txt`, made with `strictblind/blind/routes.py`)
In place, plus the four K3-style 24×8 double rotations (CW/CCW × fwd/inv) in both orders:
- substitute then transpose (S_then_T);
- transpose then substitute (T_then_S).

That is 9 route-orders.

## Alphabets (`r52_claude/alphabets.txt`)
4,761 keyword alphabets:
- the 4,749 R44b ones (top 5,000 ORTH words of length 5–10);
- plus 15 Kryptos-themed words (`r44/audit/kryptos_keywords.tsv`): KRYPTOS, PALIMPSEST, ABSCISSA, BERLIN, SHADOW,
  EGYPT, CARTER, LANGLEY, SANBORN, SCHEIDT, ILLUSION, UNDERGROUND, MAGNETIC, POSITION, WELTZEITUHR.

## Test (`r52_claude/sealed/chain_screen_fast.cpp`)
- **Step 1, two free alphabets:** feasibility of the 24 letters (exact; R43 EdgeGraph with global packing).
- **Step 2, one keyword alphabet:** for each step-1 survivor, a keyword alphabet on the plaintext or cipher side,
  the other free, both signs; exact equality-pattern test.
- **Reference check:** the fast program must agree byte for byte with the slow reference `chain_screen.cpp`. Shown
  on B10/b5, B7/b4 and B13/b4. B10/b5 reproduces the known counts:
  - in place 39 (L22);
  - S_then_T 79 / 1,643 / 1,486 / 9,502 (R46);
  - T_then_S 52 / 1,569 / 1,479 / 8,805 (R50).

## Controls (fixed now)
- **Plants:** messages from the (already public) R44b holdout B, planted in families inside the screen with keyword
  alphabets in both orientations and both orders. Each must be found at its true setting.
- **Nulls:** 2 shuffled-K4 ciphertexts (seeds 52100, 52101) through B10/b5, for descriptive two-free counts.

## Decision
- **0 keyword-feasible K4 settings in a family:** EXCL for that family × these routes × this vocabulary (exact).
- **Any keyword-feasible K4 setting:** listed raw. It is crib-feasible only, not a solution, and the trigger for a
  separate blind R44b pre-registration.
