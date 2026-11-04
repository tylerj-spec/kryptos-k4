# R64 result (Claude Code, 4 Nov 2026): no sign of a World Clock or German running key followed by a transposition

**No K4 solution. NO SIGNAL under both key models.**
- **Rule followed:** `r53/BLIND_RULES.md` as clarified by Tyler. The algorithm read only the ciphertext and generic
  models. The published letters were used only after the outputs were frozen, pushed and verified.
- **Not done:** no external checker was contacted.

## Plain words
- **The question:** R61 tried an English key followed by a transposition. R63 tried a World Clock or German key with no
  transposition. R64 tried the combination ChatGPT's research ranked first (PR #45/#46):
  - ordinary English plaintext;
  - a key that is a sequence of World Clock city names, or German prose;
  - then one of the 10 transpositions R61 used: K3's four 24×8 grid rotations and the six sculpture-layout routes.
- **The test can see this.** On 24 hidden test messages from books never used before:
  - **clock-name keys:** 12/12 found, with the right route and almost every letter right (median 96–97 of 97). This
    includes keys made by walking around the clock face in order.
  - **modern German keys:** 6/6 found (median 89 of 97).
  - **old-spelling literary German keys (Thomas Mann):** only 2/6. The German model was trained on modern parliamentary
    German, so this kind is reported as **low power**.
- **K4 shows nothing:**
  - Under the clock model, 35 of K4's 100 shuffled copies score as high as K4. Clock-keyed test messages scored more than
    120 points higher.
  - Under the German model, 6 of 100 shuffled copies score as high. Modern-German test messages scored 56–78 points
    higher.
  - Both outputs match 3 of the 24 published letters, which is chance level.

## Steps (`r64/PREREGISTRATION.md`)
| Step | Commit | Result |
|---|---|---|
| Development (development books only) | f9ffcb4, 1f8d8c2 | clock 4/4, Europarl 2/2, literary German 0/2; design fixed |
| Pre-registration (`PROTOCOL.sha256`) | 4b4c770 | — |
| Holdout generated (truth withheld; sha256 recorded) | c8423f7 | 24 plants (6 per key kind) + 24 shuffled nulls |
| Holdout freeze | 1873d2d | — |
| Holdout verification (no truth opened) | bc69973 | 17,280 raw witnesses valid |
| Holdout gate (truth hash matched) | 9e22963 | **PASSED** for both models |
| K4 target (K4 + 100 shuffles, seed 640070) | 3ef217e | — |
| K4 freeze (all raw work files; container restart at 04:25 UTC, resumed from digest-checked cache) | efc5ad0 | — |
| K4 verification (no published letters) | 9153b70 | 36,360 raw witnesses valid; manifests match |
| Reveal (`r64/k4/REVEAL.json`) | 7b6156d | **NO SIGNAL** under both models |

## Holdout gate
"Recovered" = above the maximum null for that model **and** at least 60/97 plaintext letters correct.

| Key kind | Recovered | Route right | Convention right | Median plaintext letters | Model totals |
|---|---|---|---|---|---|
| CLOCK_RAND (gated) | **6/6** (bar 5) | 6/6 | 6/6 | 96/97 | −246 to −188 |
| CLOCK_RING | 6/6 | 6/6 | 6/6 | 97/97 | −220 to −182 |
| GERMAN_EP (gated) | **6/6** (bar 4) | 6/6 | 6/6 | 89/97 | −263 to −241 |
| GERMAN_LIT | 2/6, **low power** | 4/6 | 4/6 | 56/97 | −335 to −291 |

- **Null maxima:** CLOCK −357.9; GERMAN −315.6.
- **Truth:** the sealed truth matched its pre-run sha256 (fae5c29d…).
- **Witnesses:** all valid.

## K4
| Model | K4 total | 100 nulls (min / median / max) | Nulls ≥ K4 | Published letters, plaintext / key | Nulls' plaintext letters (median / max) | Outcome |
|---|---|---|---|---|---|---|
| CLOCK | −370.4 | −393.4 / −375.3 / −345.9 | **35** (p 0.36) | 3 / 0 | 1 / 4 | **NO SIGNAL** |
| GERMAN | −319.0 | −341.4 / −327.4 / −312.6 | **6** (p 0.07) | 3 / 1 | 1 / 6 | **NO SIGNAL** |

- **Secondary (exploratory):** the best published-letter match over **all** frozen raw alternatives of K4 (both
  stages, all routes, conventions and top lists) is 4/24 (CLOCK) and 5/24 (GERMAN). The nulls' median is 5 and their
  maximum 9 and 8.

**Raw K4 outputs (best per model, plaintext order, unedited).** The key fits its model, but the plaintext is word salad,
exactly as on shuffled letters:
```
CLOCK  R24x8/CW/inv AZ_VIG   plaintext FFOXASINNDJOYOUSTHISTIMIDITISHATISITINMIYQHOTURNEDTMEETHAULKEATBUTMAJIGORUMEPOUAILLIMMASPYIASSLIG
                             key       MANILADUBLINTOKIODAKARROMRANGUNDACCAOMSKLAPAZMADRIDPEKINGDJAKARTABUDAPESTLAPAZLISSABONKABULTASCHK
GERMAN SNAKE_L      AZ_VARB  plaintext SESISCLOTHESTUMRCRAFTSMENWELLHATEOFMAGIANTAWILDMANHADLOVEINARMSHEAVIERDYINPASSIONINSHOOKEXTREMEEN
                             key       EDIREKTENUNDDERARMEESNETZEDARAUFHALTENSIEDIEEBENENORTAUSWIRSEHRUGLEICHZEITIGIMALLZUVIELEINEMFALLS
```

## Exploratory, noticed after the reveal (not pre-registered; not evidence): GERMAN stage-1 route gap
- **What was seen:** under the GERMAN model, K4's best stage-1 route (SNAKE_L, −320.9) is 28.5 points ahead of the
  second (−349.4). That is just above all 100 nulls (maximum 28.0, median 4.4; `r64/k4/EXPLORATORY_STAGE1_GAP.json`).
- **Why it is not evidence:**
  - It was chosen after looking. There are two models and a statistic that was not pre-registered. CLOCK shows nothing
    (gap 1.8; 85/100 nulls larger).
  - It is the same kind of post-hoc oddity as R61's COL_LT gap, but on a **different route**: in R61 (English key)
    SNAKE_L ranked 8th of 10, and here COL_LT ranks 7th. A single true route would not move with the key model.
  - The pre-registered statistic, the final total, has 6/100 nulls as high. The SNAKE_L output matches 3/24 published
    letters and reads as word salad.
  - K4's GERMAN total (−319) sits in the **low-power** literary-German range (−335 to −291), not the Europarl range
    (−263 to −241). R64 cannot tell an old-spelling German key from chance there.
- **If it is to be followed up:** a separate pre-registered test of this one statistic on ≥ 300 fresh shuffles, as R62C
  did for COL_LT, ideally with a German model trained on pre-1996 literary text so the low-power range gains power.

## What this rules out, and what it does not
- **Evidence against (STAT, high power):**
  - K4 = ordinary English, running key that is any sequence of the 107 World Clock city names (random order or a walk
    around the ring), any of the 6 conventions, then one of these 10 routes;
  - the same with modern German prose as the key.
- **WEAK (low power):** old-spelling literary German as the key.
- **Not covered:**
  - transposition first, then substitution;
  - other routes;
  - clock hour or UTC-offset keys, or the exact 1989 inscription order (unverified; research dossier);
  - other key languages;
  - free alphabets;
  - masking or phonetic spelling of the plaintext;
  - a non-English plaintext;
  - a true one-time pad.
- **Running keys now covered with high power:** English text, World Clock names and modern German, each in place and
  after these 10 routes (R59, R61, R63, R64). ChatGPT's dossier recommends turning next to masking-method
  identification and to source evidence, not to more key dictionaries.

## Acknowledgement
ChatGPT's research dossier (PR #46) and R64 proposal (PR #45) set the hypothesis, the out-of-distribution controls (ring
walk, unseen-genre German), the fresh-source requirement and the evidence chain.
