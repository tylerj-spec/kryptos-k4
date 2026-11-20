# R88 result (Claude Code, 20 Nov 2026): the stepped progressive Quagmire with one free alphabet is excluded for K4

## In plain words
**This idea is also ruled out.** The cipher tested: one secret scrambled alphabet, one standard (or KRYPTOS-type)
alphabet, and a key that moves one place every few letters.
- **Search without the clues:** the solver first proved on 150 sealed practice messages that it could break this
  cipher. It broke 43 of 48 and found the right setting in every one. It was never fooled by 90 decoys, including
  R87's rotor.
- **K4 itself:** nothing better than what it finds in scrambled copies of K4.
- **Exact check with the clues:** **no setting of this cipher, with any secret alphabet, gives the 24 published
  letters**, even with one or two of them wrong.

## What was tested
- **Family RQ** (`r88/PREREGISTRATION.md`; `r85/DESIGN.md` §5 item 2):
  - a fixed alphabet A (AZ, KRYPTOS, PALIMPSEST or ABSCISSA);
  - a **free** alphabet on the plaintext side (PA) or the cipher side (CA);
  - a key advancing d every n letters.
- **Blind step:** d ±1, n 1–32, 512 settings.
- **Exact step:** step 1–25, n 1–96, 19,200 settings.
- This is R40/R42's one-free-alphabet construction (L134/L136) with a stepped progressive key. It includes the n = 1
  case of L16, which has no code in the repository.

## Sealed gate (four fresh books; `r88/holdout/GATE.json`): **GO**
| Measure | Result | Bar |
|---|---|---|
| Positives recovered (≥ 95/97) and confident | **43/48** (35 exact; setting right **48/48**) | ≥ 40 |
| By stratum S1 (n 1–4) / S2 (5–8) / S3 (9–16) / S4 (17–32) | 11 / 12 / 11 / 9 of 12 | ≥ 9 each |
| Plain / 2 letters changed | 22/24 / 21/24 | reported |
| Wrong-family negatives confident (10 generators, incl. R87's rotor) | **0/90** (max letter model −1.376, word −1.704) | ≤ 1 |
| One ciphertext letter wrong (reported) | 11/12 | — |

- **All 5 misses are confident partial decodes at the right setting:** 94, 93, 94, 77 and 92 of 97 letters. As in
  development, these are scorer limits.
- **Run:**
  - isolated sandbox, `audit/run_bounded.py`: COMPLETE, 611 s, with no compile race (fixed at source);
  - witness 750/750;
  - determinism 8/8;
  - freeze pushed (e0f4339) before the truth was opened.

## K4 strict blind (`r88/k4/EVALUATION.json`): **NO_SIGNAL**
| Measure | K4 | Shuffles (100) |
|---|---|---|
| Best letter model per letter | **−1.437** (cut −1.30) | median −1.444, max −1.393; **42** at or above K4 (**p_family 0.426**) |
| Word model of that decode | −2.45 (cut −2.50) | 0 shuffles clear both cuts |
| Published letters matched by the best decode | **1/24** | — |
| Most matched by any frozen decode (top 5) | 3/24 | max 6; 64 shuffles reach ≥ 3 |
| Contenders (≥ 12/24) | 0 | — |

Raw best decode (cipher alphabet free, AZ fixed, n 25, d +1), unedited:
`ESGNHELEDYHASMEARISSTIANCAAEMNCFLLDUSUALIALLYFOOSTTHEYFOPSRPMGQMUDATTINGDERANDMISGUNOADEVEREWDURK`
It is not English. K4 sits at the shuffles' median.

**Run:**
- COMPLETE, 419 s;
- witness 505/505;
- determinism 8/8;
- the kernel is identical to a clean compile;
- freeze `r88/k4/FROZEN.sha256` pushed in 5329509 before any published letter was read. The remote results blob equals
  the local one.

## Post-freeze exact check (`r88/k4/EXACT.json`): **EXCLUDED**
| Check | K4 feasible settings (of 19,200) | Shuffles with any |
|---|---|---|
| EXACT: all 24 published letters | **0** | 0/100 |
| DROP: any one set aside | **0** | 0/100 |
| Extra, NOT pre-registered: any two set aside | **0** | not run |

Cross-checked on K4 with the second implementation (`EXACT_CROSSCHECK.json`).

**Assumptions of the exclusion.**
- It is crib-assisted: the published letters are taken as right (up to one, or two, wrong), in place and in the
  carved order.
- DROP also covers one wrong ciphertext letter at a published position.

## What this does and does not exclude
**Excluded exactly**, under the assumptions above:
- a free plaintext or cipher alphabet;
- with a fixed AZ/KRYPTOS/PALIMPSEST/ABSCISSA alphabet on the other side;
- a key advancing by any constant step 1–25 every n = 1–96 letters.

**Not excluded:**
- irregular steps;
- a keyword plus a progression;
- two free alphabets (L21's per-slot space);
- R40/R42's ACA and prefix alphabets;
- transposition;
- masking;
- non-English plaintext.

## Review
**Independent review: NONE.** One model (Claude Code). The exclusion is single-model and not promoted. A replay of
`exact88.py` takes under 3 minutes.
