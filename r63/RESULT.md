# R63 result (Claude Code, 3 Nov 2026): no sign of a World Clock, German or numeric running key

**No K4 solution. NO SIGNAL in every part.**
- **Rule followed:** following `r53/BLIND_RULES.md` as clarified by Tyler (Amendment 2), the algorithms read only the
  ciphertext and generic models. The published letters were used only after everything was frozen and pushed.
- **Not done:** no external checker was contacted.

## Plain words
- **The question:** R59/R61 tested keys that are English text. R63 tested keys that are **not** English, while the
  plaintext is still ordinary English:
  - **(A) World Clock key:** any sequence of the Berlin World Clock's city names, from the 107-name vocabulary of the
    photo-derived chart. The exact inscription order was never verified, so a model was used instead.
  - **(B) German prose key.**
  - **(C) Number keys:** the digits of π, e, √2 and φ, the K2 coordinates, and three dates.
- **The solver is very good at (A) and (B).** On 20 hidden test messages from unseen books, it detected 20 of 20 and
  identified the tableau in 20 of 20.
  - It read clock-keyed messages perfectly (median 97 of 97 letters).
  - It read German-keyed messages mostly (median 85 of 97).
  - So if K4 were built this way, this test should have caught it.
- **K4 shows nothing:**
  - Under the clock model K4 scores worse than 81 of its 100 shuffled copies. Clock-keyed messages score about
    150 points higher.
  - Under the German model, 27 of 100 shuffled copies score as high as K4.
  - The outputs match 0–3 of the 24 published letters, which is chance level.
- **Number keys:** exactly impossible. None of 92.9 million settings, in place or after 40 K3-style transpositions,
  matches the 24 letters.

## Steps (`r63/PREREGISTRATION.md`; amendments 1 and 2 are dated and precede every (A)/(B) gate and K4 run)
| Step | Commit | Result |
|---|---|---|
| Pre-registration | 95ad2e8 | — |
| Holdout generated (truth withheld; sha256 recorded) | 6c32db5 | 10 CLOCK + 10 GERMAN plants, 20 nulls |
| (C) plants made before the blind run | b7f3a6a | 4 plants |
| (C) freeze / result | e9b0227 / 8f14b00 | **EXCL** (below) |
| Amendment 1 (after the R62 review) / Amendment 2 (owner clarification; withdraws 1) | 7ba3d26 / ac33f6d | — |
| (A)/(B) holdout freeze | e82ec26 | — |
| (A)/(B) holdout gate (truth hash matched) | 711245c | **PASSED** |
| K4 target (K4 + 100 shuffles, seed 630070) | d148a4a | — |
| K4 freeze: results, all raw alternatives, `WORK_FREEZE.sha256` (PR #44 tool) | 2d043af | — |
| Independent verification (PR #44 `verify_frozen.py`; no published letters) | this commit | **PASSED**: 12 manifest entries, 138 work files, 68 cached chunks, 202 + 3,030 re-encryption witnesses |
| Primary reveal (`r63/k4/REVEAL.json`) | this commit | **NO SIGNAL** under both models |
| Exploratory check of all frozen alternatives (`r63/k4/SECONDARY_ALTERNATIVES.json`) | this commit | nothing; below the nulls |

## Holdout gate, (A)/(B)
| Key model | Detected | Convention | Plaintext ≥ 60/97 | Median plaintext letters |
|---|---|---|---|---|
| CLOCK (10 plants) | 10/10 (bar 8) | 10/10 | 10/10 (bar 8) | **97/97** |
| GERMAN (10 plants) | 10/10 (bar 5) | 10/10 | 9/10 (bar 5) | 85/97 |

Null maxima: CLOCK −363.8; GERMAN −323.9. All witnesses were valid.

## K4, (A)/(B)
| Model | K4 total | 100 nulls (min / median / max) | Nulls ≥ K4 | Published letters, plaintext / key | Nulls' plaintext letters (median / max) |
|---|---|---|---|---|---|
| CLOCK | −396.5 | −411.7 / −387.4 / −363.4 | **81** (p 0.81) | 2 / 2 | 1 / 4 |
| GERMAN | −330.4 | −347.5 / −334.4 / −316.4 | **27** (p 0.28) | 0 / 1 | 1 / 5 |

- **Holdout plants for comparison:** CLOCK −229 to −189; GERMAN −286 to −230.
- **Exploratory check (not pre-registered):** the best published-letter match among each model's 9 frozen K4
  alternatives is 3/24 (CLOCK) and 2/24 (GERMAN). The nulls' alternatives reach a median of 3 and 4 and a maximum of
  7 and 8.

**Raw K4 outputs (best per model, unedited).** The key fits its model but the plaintext is gibberish, exactly as on
shuffled letters:
```
CLOCK  KRY_BEAU  plaintext DDOOOYWHYFDIARYISARABACHIPSTAYTDOGLATTLEWARTSATBYPPDADKAMFEMENNTITHENGAMYKEHEEABARWMUSEANEHXXIVFO
                 key       IMOSKAUNIKOSIAASUNCIONKIEWKABULDENVERBELGRADLAPAZDAKARULANBATORWLADIWOSTOKBRUESSELSYDNEYASUNCIONS
GERMAN AZ_VIG    plaintext LHAYMAKESUCHOATHREHOTBYWHENLEFTTOSEAOFDOWNSAMORITZPRIEDDENMEABOUTLEGAGREWLAYLISTGROWINGCHAIRATTAC
                 key       DUKTIONKONSENSVERBUNDENVOMDENINREAKTIONENDASSWIRDBESCHRAENKENENTFERNTGIBTZWISCHENSOHATESAUSDERJAP
```

## (C) Number keys (`r63/numeric/exp/`, strictblind harness)
- **Scope:** every window, forward and reversed, × A–Z/KRYPTOS key numbering × 12 fixed conventions × 41
  route-orders (identity plus 20 K3-style routes × 2 orders).
- **Plants:** 4/4 ranked #1.

| Key | Settings | Best published-letter match | 24/24 |
|---|---|---|---|
| π, e, φ (10,000 digits each) | 19,491,072 each | 9 | 0 |
| √2 (10,000 digits) | 19,491,072 | 10 (chance expectation of ≥ 10: 0.16) | 0 |
| K2 coordinates 38576577844 | 3,747,072 | 6 | 0 |
| 19901103 / 19891109 / 1986 | 3,747,072 each | 7 / 6 / 6 | 0 |

**EXCL (exact):** 0 of 92.9 million fully specified settings match all 24 letters.

## What this rules out, and what it does not
- **Evidence against (STAT):** K4 as an **in-place** running key whose plaintext is English and whose key is a
  sequence of World Clock city names (from this 107-name vocabulary) or German prose. The power is high: the holdout
  detected 20/20.
- **Exact exclusion:** the listed number keys with these fixed alphabets and routes.
- **Not covered:**
  - city names outside the reconstructed vocabulary or spelled differently;
  - a clock reading that includes the UTC offsets or hour numbers;
  - World Clock or German keys combined with a transposition;
  - other key languages;
  - free (unknown) alphabets;
  - masking;
  - a non-English plaintext.

## Acknowledgement
ChatGPT's PR #44, reviewed and not merged, supplied the pre-reveal raw-alternative freeze (`seal_work.py`) and the
independent verifier (`verify_frozen.py`). Both were run here from that branch without changes.
