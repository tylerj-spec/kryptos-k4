# R89 result (Claude Code, 21 Nov 2026): ChatGPT's two R89 mechanisms are both excluded for K4

## In plain words
**Neither of the two new ideas fits K4.** ChatGPT designed both:
- **F26L:** the letters are split into two coordinates, mixed within short blocks, then put through a K1/K2-style
  KRYPTOS tableau.
- **RCT:** a rotor with a secret wiring that jumps an extra notch whenever certain ciphertext letters come out.

How each was tested:
- **Design review and build.** I reviewed ChatGPT's design as a different model, fixed it where needed, and wrote all
  the code myself.
- **Practice first.** Both solvers had to prove themselves on 255 sealed practice messages from four new books in three
  genres:
  - F26L broke 47 of 48 of its messages;
  - RCT broke 42 of 48;
  - neither was fooled by any of 150 decoys.
- **K4 without the clues.** Nothing better than in scrambled copies of K4.
- **K4 with the clues.** No setting of either cipher produces the 24 published letters. For F26L every one of its
  139,120 possible settings was tried: the best matches 7 of the 24, which is what scrambled copies of K4 also reach.

## Sealed gate (`r89/holdout/GATE.json`): **both arms GO**
| Measure | F26L | RCT | Bar |
|---|---|---|---|
| Positives ok (right arm, ≥ 95/97, confident) | **47/48** | **42/48** | ≥ 42 |
| Exact (97/97) | 47 | 39 | ≥ 36 |
| By stratum | 12 / 12 / 12 / 11 (b 5 / 7 / 9 / 11) | 11 / 11 / 10 / 10 (m 2 / 3 / 4 / 5) | ≥ 9 each |
| By genre: narrative / formal history / technical | 16 / 16 / 15 | 15 / 13 / 14 | ≥ 12 each |
| Masked (C→K, W→V) | 11/12 | 9/12 | ≥ 8 |
| Arm identified | 47/48 | 48/48 | — |

**Negatives:** **0/150** confident (max letter model −1.352, word −1.809). No family was declared on any negative,
including the near-family decoys F26X and RCTX and 25 English anagrams.

**F26L's one miss (H_116)** is a masked technical text. F26L decoded it exactly, at 97/97 with the true setting, but
that text scores −1.439, below the cut. This is a scorer limit; enumeration cannot miss.

**RCT's misses:**
- three confident partial decodes, at 82, 90 and 94 letters;
- two complete failures, at 6 and 7 letters.

**Extras (reported):**
- **F26L:** 4/4.
- **RCT:** plaintext errors 2/2, but **ciphertext errors 0/2 and the missed update 0/1**. In RCT one wrong ciphertext
  letter derails every later offset. So **under RCT, a single carving error in K4 would very likely hide a true
  solution.**

**Run:**
- isolated sandbox, `audit/run_bounded.py`: COMPLETE, 752 s;
- witness 1,833/1,833;
- determinism 8/8;
- freeze pushed (59a6a91) before the truth was opened.

## K4 strict blind, both arms (`r89/k4/EVALUATION.json`): **NO_SIGNAL**
| Measure | K4 | Shuffles (200) |
|---|---|---|
| Best over both arms, letter model per letter | **−1.439** (cut −1.30), from RCT | median −1.444, max −1.354; **90** at or above K4 (**p_family 0.453**) |
| Word model of that decode | −2.53 (cut −2.50) | 0 shuffles clear both cuts |
| F26L's best over all 139,120 settings | −1.886 | — |
| Published letters matched by the best decode | **1/24** | — |
| Most matched by any frozen decode | 4/24 | max 6; 75 shuffles reach ≥ 4 |
| Contenders (≥ 12/24) | 0 | — |

Raw best decode (RCT, KRY/KRY contacts, d +1, m 4, q 2), unedited:
`YHAUSAVORPRIVINGLMSTSFLUEOCOCEREYINOREXTOPHYISAROUTFINDBERETINTAGENITDRGHAWETHBARREDILEIILARVIXVI`
It is not English.

**Run:**
- COMPLETE, 602 s;
- witness 1,428/1,428;
- determinism 8/8;
- the kernel is identical to a clean compile;
- freeze `r89/k4/FROZEN.sha256` pushed in 60a5b77 before any published letter was read. The remote results blob equals
  the local one.

## Post-freeze exact checks (`r89/k4/EXACT.json`): **both EXCLUDED**
| Check | K4 | Shuffles (200) |
|---|---|---|
| **F26L + bare F26**, all 139,120 settings: most published letters matched | **7/24**: none at 24 (EXACT), none at ≥ 23 (DROP) | max 9; K4's 7 is reached by 88% (p 0.88) |
| **RCT**, 448 settings: feasible, all 24 | **0** | 0/200 |
| RCT, one letter set aside (DROP) | **0** | 0/200 |
| RCT, two set aside (extra, NOT pre-registered) | **0** | not run |

Cross-checked on K4 with the second implementations (`EXACT_CROSSCHECK.json`): full decryption of every F26 setting,
and `rct.exact_check`.

## What this does and does not exclude
**Excluded exactly** (crib-assisted: the published letters right, up to one wrong for DROP, and in order):
- every F26 and F26L setting in scope: the 20 alphabets, blocks 5, 7, 9 and 11, all offsets, and PALIMPSEST/ABSCISSA
  on the KRYPTOS tableau at any sign and phase;
- every RCT setting in scope: 16 contact pairs and 28 trigger schedules, with any wiring.

For F26 the DROP check also covers one wrong ciphertext letter feeding a published position. For RCT it covers only a
wrong published plaintext letter.

**Not excluded:**
- other fractionation shapes, alphabets, block sizes or outer keys;
- RCT with other trigger rules, other step sizes or more than one rotor;
- transposition;
- masking;
- non-English plaintext.

**Caveat (ChatGPT's, agreed).** F26L's outer stage was chosen after seeing K4's flat ciphertext IC. The exclusion is
clean, but the family was always a long shot.

## Review
- **The design** (ChatGPT, PR #98) was independently reviewed by Claude Code: `r89/REVIEW_PR98.md`.
- **The build and execution** were done by one model (Claude Code). **Independent review of R89's execution: NONE.**
  The exclusions are single-model and not promoted.
- A ChatGPT replay of `exact89.py` (2 min) would be the natural independent check.
