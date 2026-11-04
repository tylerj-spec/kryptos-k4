# R66 result (Claude Code, 4 Nov 2026): no sign of homophonic substitution (frequency masking) with a transposition

**No K4 solution.**
- **Part A (blind solver):** **NO SIGNAL**.
- **Part B (exact check):** **EXCL** for all 2,538 explicit routes and for all but 6 of about 88 million columnar
  orders. K4's count of feasible orders is ordinary for its shuffled copies.
- **Not done:** no external checker was contacted.

## Plain words
- **The question:** Scheidt said K4's English was disguised so that its letter statistics don't show. Homophonic
  substitution is the textbook way to do that: common letters get several cipher letters, which flattens the counts. It
  had never been tested on K4.
  - **In place it is impossible:** K4's QQ at positions 26–27 would have to stand for N and O.
  - **So R66 tested it with a transposition**, in either order (they are equivalent here).
- **Part A, the blind search:**
  - **What it does:** a new solver that guesses the letter table from the ciphertext alone, under each of the 10 R61
    routes.
  - **Power:** on 20 hidden test messages it recovered 14 (the bar), and two more were the right text shifted by 13
    letters.
  - **K4:** it scores like its shuffled copies (57 of 100 score as high), and the output is word salad matching 3/24
    published letters.
- **Part B, the exact check (after the freeze):** a homophonic table fits the 24 published letters on a given
  transposition only if no cipher letter would have to stand for two different letters.
  - **None** of the 2,538 explicit routes passes: K3-style rotations, every double rotation with widths 4–28, the
    engraving routes and keyed columnar.
  - **6** of 43,954,712 forward columnar orders (widths 2–11) pass, and **none** of the inverse orders.
  - Shuffled copies of K4 pass just as often or more (median 0, mean 46).

## Steps (`r66/PREREGISTRATION.md`)
| Step | Commit | Result |
|---|---|---|
| Development (solver, cap, search settings) | c9e7fac, 92469d4, 7ac240c | in place 6/6; routed 7/8 recovered |
| Pre-registration (`PROTOCOL.sha256`) | 59d0f63 | — |
| Holdout generated (truth withheld; sha256 recorded) | 9fc5490 | 20 plants + 20 nulls |
| Holdout freeze / verify | 39be0a5 / f23e464 | 3,600 witnesses valid |
| Holdout gate (truth hash matched) + Amendment 1 (before K4) | e3e5610 | **PASSED** 14/20 |
| K4 target (K4 + 100 shuffles, seed 660070) | a704f02 | — |
| K4 freeze / verify | 02db45c / 404cce3 | 9,090 witnesses valid |
| Reveal (Part A) and exact family check (Part B) | this commit | **NO SIGNAL**; **EXCL** (see below) |

## Holdout gate (Part A power)
| Measure | Result |
|---|---|
| Recovered (above the null maximum −192.1 **and** ≥ 60/97 letters) | **14/20** (bar 14) |
| Detected (above the null maximum) | 17/20 |
| Route right | 16/20 |
| Median plaintext letters | 94/97 |
| Recovered plants' totals | −168 to −127 |
| Plants' IC | 0.038–0.049 (K4: 0.036) |

- **The six misses:**
  - **HOLD_07, HOLD_08:** the true plaintext (96/97, 97/97) shifted by 13 letters. They landed on the sister K3
    rotation (CW/inv instead of CCW/inv), whose un-routing is a 13-letter cyclic shift.
  - **HOLD_04:** a false hit on a wrong route.
  - **HOLD_02, HOLD_09, HOLD_13:** below the null maximum (search failures).

## K4, Part A
| | K4 | 100 nulls |
|---|---|---|
| Total | −207.7 (COL_LT) | min −216.4 / median −206.7 / max −194.0; **57 ≥ K4** (p 0.57) |
| Published letters (frozen plaintext) | 3/24 | median 2, max 5 |
| Secondary: best over all frozen alternatives | 7/24 | median 6, max 8; 29 nulls ≥ K4 |
| Secondary (Amendment 1): best over all 97 rotations | 6/24 | median 6, max 10; 81 nulls ≥ K4 |

**Raw K4 output (unedited):**
```
COL_LT  map SHTROORTSHIEWESOHOITENNFAS  plaintext HREISOFTHEHONORINIIINHESEENWORSTISTHESEISHEHOISTHISSIRNOATSIRFREESISRESONOHEITHHOSTESSHOTONITSTOO
```

## K4, Part B (exact; published letters used only here, after the freeze)
| Family | Permutations | K4 feasible | Nulls feasible (median / mean / max) |
|---|---|---|---|
| Explicit routes (`r66/data/feas_routes.txt`) | 2,538 distinct | **0** | 0 / 0 / 0 |
| Columnar widths 2–11, forward | 43,954,712 | **6** (four at w10, two at w11) | 0 / 46.5 / 3,825 |
| Columnar widths 2–11, inverse | 43,954,712 | **0** | 0 / 33.2 / 1,440 |

- **K4's total of 6 is ordinary:** 27 of 100 nulls have at least as many.
- **K4's 6 feasible orders** (`r66/k4/PARTB_K4_FEASIBLE.txt`; key = column read order, fill rows left to right):
  - w10: `2 7 8 1 4 6 3 9 5 0`, `2 7 8 1 5 6 3 9 4 0`, `2 9 8 1 4 6 3 7 5 0`, `2 9 8 1 5 6 3 7 4 0`;
  - w11: `0 8 1 3 6 5 2 10 9 4 7`, `0 8 7 3 6 5 2 10 9 4 1`.
- **These are not candidates.** They were found **by** the published letters. Per the pre-registration, no
  crib-selected solving is done without Tyler's go-ahead.

## What this rules out, and what it does not
- **EXCL (exact):** homophonic substitution, with any table and no cap, combined with:
  - any of the 2,538 explicit routes: identity, the 10 R61 routes, the 20 K3-style r27 routes, every double rotation
    with widths 4–28, the keyed columnar routes;
  - any complete columnar transposition of widths 2–11 except the 6 forward orders listed.
- **STAT (Part A):** no sign of a ≤ 4-homophone table with the 10 R61 routes. Power about 70–80% (14–16/20).
- **Not covered:**
  - other transpositions (irregular columnar, double columnar, widths ≥ 12);
  - homophonic tables that change with position;
  - nulls or padding;
  - non-English or phonetically spelled plaintext;
  - a true one-time pad.
- **Context:** the hidden test plants had IC 0.038–0.049. K4's 0.036 is flatter than any of them. A 26-letter
  homophonic table flattens only partly, so K4's very flat counts are not specifically predicted by this cipher.
