# R83 design round: what the recent research PRs leave open, and the code for the next experiments (Claude Code, 14 Nov 2026)

**Status: design and synthetic-only code. No K4 run, no published letter read by any new code path.**
- The new exact checks (`r83/exact83.py`) have been run only on synthetic plants and random ciphertexts.
- Their K4 mode refuses to start until `r83/PROTOCOL.sha256` exists, which is written at pre-registration.
- A K4 run needs that pre-registration and Tyler's go.

Reviewed: PR #75 (the R80 design study), #76 (R81a, merged), #78 (R80a, draft) and ChatGPT's #77 (R82, draft).

## 1. Findings in brief
| # | Finding | Consequence |
|---|---|---|
| 1 | **R75's F1X already decides most of what R80 would run on K4.** F1X is the exact check for two stacked periodic stages with *any* keys, periods 1–26 each, on all four alphabets (L165). Of the 180 (listed length 1–15, free length 1–12) cells of R80's families, 171 have ≥ 3 F1X checks; F1X found no readable decode in any of them (§2) | R80's blind K4 run would mainly re-test settings already excluded. Its own new ground is 9 low-check cells and blind confirmation. Recommendation: R80 is optional (§6) |
| 2 | Four keyword families in the review queue have no fixed period ≤ 26, so neither F1X nor any other ledger row covers them: the **linked key** (PR #77 ticket L), **keyword + plaintext autokey** (G2 / B1), the **walking key stepped by the plaintext** (WK-P / B1-WALK) and the **per-slot progressive key** (G3 / B2) | Each has a cheap exact check for any key letters, of the same kind as F1X and G5X (§3) |
| 3 | Those checks are decisive over most of each family's range at K4's published positions: linked key ≥ 5 checks up to keyword length 20 at every row width; walking key ≥ 3 up to ring length 21; per-slot progression ≥ 4 up to keyword length 10 (≥ 3 up to 25 when the keyword re-enciphers itself); plaintext autokey ≥ 3 for lag ≤ 6 with keyword ≤ 12 (§3.2) | The blind solvers that remain to be built are needed only where the checks are weak: long lags, long progressive keywords (§4) |
| 4 | Code written and tested here: reference ciphers for the four families (`r83/models83.py`) and their exact checks with drop-one (`r83/exact83.py`). Each check equals exhaustive key search on small keys, finds 20/20 plants, and runs in minutes per ciphertext (§5) | R83a is ready to pre-register |
| 5 | R80b (a better first pass for R80a's long free keys): measured on R80a's spent misses (§4.3) | Decides whether R80b is worth a new gate |

## 2. F1X and R80: what is already decided
R75's F1X (`r75/sealed/exact.py`, L165) checks every pair of periodic stages in place:
- periods m1, m2 = 1–26;
- PA1, CA1, PA2, CA2 each one of A–Z, KRYPTOS, PALIMPSEST or ABSCISSA;
- each stage additive or reverse;
- free keys, which absorb the key-numbering alphabet and variant Beaufort.

R80a's four families (a listed key of 1–15 letters, a free key of 1–12, A–Z or KRYPTOS on each side, CA1 ≠ PA2) are a subset. Two of F1X's numbers are decided by K4's published positions alone:
- **checks:** the independent equations the published letters impose beyond fixing the key;
- **unpinned:** the key letters that no published position fixes.

| Listed length \ free length | 1–7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|
| 1–10 | ≥ 8 checks | ≥ 8 | ≥ 6 | ≥ 6 | ≥ 4 | ≥ 4 |
| 11 | ≥ 7 | 6 | 5 | 4 | 13 | **2** |
| 12 | ≥ 6 | 8 | 7 | 4 | **2** | 12 |
| 13 | ≥ 5 | 4 | 4 | **2** | **1** | **1** |
| 14 | ≥ 7 | 5 | 5 | 3 | **1** | 5 |
| 15 | ≥ 3 | **2** | 8 | 4 | **0** | **1** |

*(Computed from the 24 published positions only. Full table: §7, item 1.)*

- **171 of the 180 cells have ≥ 3 checks.** At ≥ 3 checks, F1X:
  - left 1,868 K4 settings feasible, fewer than in 19 of its 20 shuffles (median 2,354);
  - completed and scored every feasible setting with at most 2 unpinned letters;
  - found no readable decode (best −1.68; shuffles −1.62 to −1.67).
- Cells with many checks but more than 2 unpinned letters (for example, equal lengths) were still checked for feasibility. A setting there that is infeasible is excluded whether or not it could be decoded.
- **R80's own new ground** is limited to three things:
  - the 9 bold cells, listed words of 11–15 letters against free keys of 8–12;
  - feasible low-check settings that F1X could not complete (more than 2 unpinned letters, or more than 64 solutions);
  - a blind decode, which F1X's crib-assisted check is not.
- **Correction to the R80 design study.** `r80/FABLE_IDENTIFIABILITY.md` §2.2, row G1, says R75 ran 80 words on both stages. It omits F1X, which ran every key. G1's remaining room is therefore much smaller than that study's 0.5–1%. I wrote that study, and the omission is mine.

## 3. Families with no fixed period ≤ 26: exact checks
### 3.1 Definitions (`r83/models83.py`)
One-stage notation as in R75: `IDX[ca][c] = s·IDX[pa][p] + k`, s = ±1. A free key absorbs the key-numbering alphabet and variant Beaufort, so a stage has 32 conventions.

| Family | Rule | Source | Not covered by |
|---|---|---|---|
| **LK** linked key | One keyword x of m letters in two stages on different tableaux. Stage one reads slot i mod m. Stage two reads (i + d·⌊i/w⌋) mod m, so the keyword rotates d places after each row of w letters (or the rotation is on stage one). Stage two numbers the key letters by its own alphabet, `pi = IDX[ka2] ∘ LET[ka1]` | PR #77 `r82/LINKED_KEY_LAYER.md` | F1X: the stage-two key has period m·w, above 26 except for tiny m·w. R81a G4 ROT: one stage only |
| **PF** keyword + plaintext autokey | `k_i = U[i mod m] + f·IDX[β][p_(i−L)]`, primer for i < L | r80 G2; PR #77 B1 | L157 / R68: plaintext autokey *without* a keyword. R79: ciphertext feedback only |
| **WP** walking key, plaintext-stepped | `k_i = U[ptr_i]`, `ptr_(i+1) = ptr_i + d·(IDX[α][p_i] + e) mod m` | r78 §4.2 WK-P; PR #77 B1-WALK | R79 ran the ciphertext-stepped walk (WK-C) only |
| **SL** per-slot progression | `k_i = A[r] + j·B[r]`, r = i mod m, j = i div m. SL-A: A = B | r80 G3; PR #77 B2 | L13: one step for all slots. L49: linear recurrences of order ≤ 6 (SL only for m ≤ 3). F4X grid key: a row term B[j], not j·B[r] |
| **SS** self-enciphering keyword | Pass j+1 key letter of slot r = the pass-j letter enciphered on the tableau by keyword letter W[r] | r80 G3 ("encipher the key with itself") | As SL |

### 3.2 The checks (`r83/exact83.py`)
All are algebraic and never decrypt.

| Check | Method | Settings per ciphertext | Checks at K4's published positions (`r83/results/CHECKS.json`) |
|---|---|---|---|
| **LX** | A graph on the m keyword letters, one edge per published position, linking the slot each stage reads by a bijection. Feasible iff every cycle and self-loop closes. As F1X, but both stages share one set of key letters | 26,624 conventions (4⁴ alphabet combinations, CA1 = PA2 kept because rotation stops it collapsing; s1, s2; the relative sign of the stage-two key; 13 distinct renumberings) × rotated stage 1 or 2 × m 2–20 × w 2–48 with d = ±1, plus w = 97 (no rotation, a control that F1X covers): **96.1 million** | min over widths: 24 − m + 1, i.e. 23 at m = 2 down to **5 at m = 20** |
| **PFX** | Every published position whose letter L earlier is also published pins U[i mod m]; the pins must agree within each slot | 256 (32 × β × f) × L 1–12 × m 1–26 = 79,872 | L = 1: 21 (m = 1) to 10 (m = 12); L = 4: 15 to 4; L = 6: 11 to 1; L ≥ 8: ≤ 7, mostly ≤ 3 |
| **WPX** | Inside each published run the pointer steps are known from the published letters, so the pointer is known up to one offset per run. Feasible iff for some offset between the two runs, equal pointers carry equal key values | 32 × α 4 × e 2 × d 2 × m 2–26 = 12,800 (each over the m offsets) | worst case 24 − m: **≥ 3 up to m = 21** |
| **SLX / SLX-A** | Per slot, some (A, B) (or some A = B) must fit every published position of that slot | 32 × m 1–26, each | SL: 24 − 2·(slots touched): ≥ 4 up to m = 10, 2 at 11, ≤ 1 from 12. SL-A: ≥ 3 up to m = 25 |
| **SSX** | Per slot, some keyword letter must generate every published key value of the slot | 128 (pa, ca, ka, s) × m 1–26 = 3,328 | 24 − slots: ≥ 3 up to m = 25 |

- **Drop-one** (G6, as R81a): each check also reports, per published position, the settings that become feasible once that one letter is set aside.
- **Clue-position robustness** (PR #77 §E: a shifted clue position): every engine takes the published positions as an argument. Shifting one run by ±1 or ±2 is a call with different positions. A pre-registered variant would correct for the 8 extra position sets.
- **Chance level.** Feasibility at few checks is expected by chance in a large family. F1X saw about 2,000 feasible settings at 3–9 checks on any ciphertext. So, as in R75, the K4 counts are read against the same check on 20 shuffles of K4, never alone. The synthetic chance levels are in §5.

### 3.3 Why exact first for these families
These checks can only exclude; a feasible setting is reported as a count and a setting, never as a plaintext (§5). This is the G5X precedent, which Tyler accepted for exclusion-only checks ("You can do this check that you offered & im fine with us doing it in the future"). A blind solver for each family would cost a sealed gate each. The exact checks decide most of each family's range in about an hour for K4 and 20 shuffles. They also show which cells, if any, still need a blind round. **Decision for Tyler: run R83a before building blind solvers for these four families** (§6).

## 4. Blind solvers: where they are still needed, and their design
### 4.1 Where
| Family | Cells the exact checks leave weak (< 3 checks) | Blind solver |
|---|---|---|
| PF | lag L ≥ 8 (most m); L 6–7 with m ≥ 9 | Sequential decoding (below) |
| SL | m ≥ 11 | Pair-slot ascent (below) |
| LK | none up to m = 20 | For discovery only; needed only if LX finds a K4-only feasible cell |
| WP | m ≥ 22 | Sequential decoding |
| SS, SL-A | m = 26 only | — |

### 4.2 Code design (not built yet; built only for cells R83a leaves open)
- **`pairsolve.c`: one kernel for every two-variables-per-letter cipher.**
  - Each letter reads two key variables: `L[i] = T[i][x[a_i]][x[b_i]]`, with T a 97 × 26 × 26 table and x up to 64 variables.
  - Coordinate ascent on quadgrams, as R79's `slotsolve.c`, but each variable updates the letters at both of its kinds of positions.
  - Starts:
    - restart 0 from the pairwise unigram field of PR #77's `r82/pairwise_pilot.py`, by ICM;
    - then random restarts.
  - Then letter-model rescoring as R79, and R79's Theorem K cut.

  | Use | Variables | a_i, b_i | T |
  |---|---|---|---|
  | LK | m | `lk_slots` | two-stage decrypt |
  | SL | 2m (A_r at r, B_r at m + r) | (r, m + r) | decrypt with A + jB |
  | R80 mode A (both keys free) | m1 + m2 | (i mod m1, m1 + i mod m2) | two-stage decrypt; for measurement only, since R80 found 0/48 by ascent |

  Python wrapper `pair83.py` (tables plus explicit decrypt check); tests as `r80a/tests` (fast path equals reference; solver reaches the truth's score).
- **`seqdec.c`: sequential decoding for plaintext-driven keys** (PF, WP).
  - Given the keyword, the decode is deterministic left to right.
  - Exhaust keywords of ≤ 4 letters × conventions × lags.
  - The 28,943-word list at every length.
  - For 5–8 letters, a beam over the first m plaintext letters, which fix the keyword one for one. Score by the letter model on the determined part.
  - Expected to fade above about 8 letters; the gate will say.
- **Gates.** Each solver gets the R80a treatment:
  - development on spent books;
  - a sealed holdout from fresh books: positives by length, with misspelled and nonstandard-spelling kinds;
  - R79's seven wrong-family generators, NEG_TWO_RANDOM, shuffles;
  - cuts fixed before the holdout exists.

  PR #77's own pilots supply the targets to beat: linked key m 9 / w 11 at 9/16 exact; m 12 / w 31 at 0/16.

### 4.3 R80b: a better first pass for long free keys
R80a's 9 misses were all lost by pass 0: the true setting ranked 7,849 to 1.8 million, outside the 4,000 kept. Pass 0 starts each slot at its best single-letter fit and scores the decode by quadgrams, with no ascent.

**Measured here, on the spent misses (`r83/dev/r80b_sweeps.py`):** R80B_RESULT

## 5. Code in this PR
| File | What | Tested by |
|---|---|---|
| `r83/models83.py` | Explicit encryptors and decryptors for LK, PF, WP, SL, SS; random plants | Round trip, 300 settings |
| `r83/exact83.py` | LX, PFX, WPX, SLX, SLX-A, SSX with drop-one; check-count table from the positions alone; self-test; K4 mode guarded by `r83/PROTOCOL.sha256` | `r83/tests/test_r83.py` |
| `r83/tests/test_r83.py` | (1) round trip; (2) every check equals exhaustive search over all keys on small keys, run through the explicit encryptor, on planted ciphertexts and on the same ciphertexts with one published letter changed (92 comparisons); (3) 20/20 plants feasible under their own setting; (4) check table equals the engine | All pass |
| `r83/results/CHECKS.json` | Checks per cell, from the published positions only | — |
| `r83/results/SELFTEST.json` | 20 plants; 4 random ciphertexts through every check at full size | SELFTEST_LINE |
| `r83/dev/r80b_sweeps.py`, `r83/results/R80B_SWEEPS.json` | §4.3 | — |

**Run time per ciphertext:** LX 3,610 graph cells about 3 minutes; the other four checks under 2 seconds together. K4 with drop-one plus 20 shuffles is about 1.5 hours on one core.

**What a feasible K4 setting would and would not mean.** As in R75 and R81a, the check never completes a key from the published letters and never decodes. A K4 setting that is feasible at ≥ 3 checks, and stands out against the shuffles, becomes the subject of a new blind round of that one family: a sealed gate, then K4 blind. It is never a solution in itself. Tyler: "if we get a possible solution, we will have to have legit proof that could be it before public submission".

## 6. Proposed order and decisions for Tyler
| Step | What | Cost | Needs |
|---|---|---|---|
| **R83a** | LX, PFX, WPX, SLX, SLX-A, SSX with drop-one on K4 and 20 shuffles. Then the same with each published run shifted by ±1 and ±2. Also F1X drop-one, the G6 robustness F1X never had, by calling `r75/sealed/exact.py` f1x() with one position removed | about 2 hours | Pre-registration (`r83/PREREGISTRATION.md`, `PROTOCOL.sha256`); **Tyler's go for an exclusion-only check without a blind run first**, as for G5X |
| R83b | Blind solvers (§4.2) for the cells R83a leaves open, or for any family R83a flags; each with a sealed gate | days | R83a's result |
| R80 | R80a's families on K4 + 100 shuffles, blind | 2.2 hours | Tyler's go. Optional given F1X (§2) |
| R80b | A better pass 0, only if §4.3 shows it rescues the long-key misses | a dev check and a new gate | §4.3 |
| R82-F | PR #77's 2 × 13 fractionation | — | Lower priority, agreeing with PR #77's own marginal screen (K4 below all 40 English controls on all four charts). A pre-registered version would need fresh controls and the maximum over charts |

**Not covered by any of this:**
- several stages with transposition (L06–L09, L47/48 and others cover many of those);
- a context-dependent pre-mask (PR #77 ticket M);
- ciphertext transcription errors away from the published positions (they do not affect the exact checks, which read only the 24 published positions);
- a different carving order.

## 7. Supporting tables
1. F1X checks (unpinned letters) for listed length 1–15 × free length 1–12, from the published positions. Produced by the snippet in this round's session; the same numbers follow from `r75/sealed/exact.py` f1x's `checks = ne − len(adj) + len(comps)`.
2. `r83/results/CHECKS.json`: checks per cell for LX (both rotated stages, d = 1, every m and w), PFX (L × m), WPX, SLX, SLX-A, SSX.
