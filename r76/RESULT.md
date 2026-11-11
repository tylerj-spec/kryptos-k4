# R76 result (Claude Code, 11 Nov 2026): H1 new alphabet keyword, H2 scrambled key

Pre-registration: `r76/PREREGISTRATION.md` (1c370ce). Hypotheses: `r76/HYPOTHESES.md`.

## Sealed synthetic gate (no K4 data)
| Step | Commit | Result |
|---|---|---|
| Holdout (seed 760300; truth sha256 573388d9… withheld) | 3a2f194 | 160 ciphertexts |
| Blind run (about 25 min on 4 cores) and freeze | 5d7bca8 | 13,700,640 fixed methods per ciphertext |
| Verify (truth not opened) | this commit | **PASSED**: 1,280 stored decodes re-encrypt |
| Gate (truth hash matched; `r76/holdout/GATE.json`) | this commit | **PASS** |

| | Recovered and confident | Bar | Worst score (letter / word model) |
|---|---|---|---|
| 60 positives (*The Woman in White*, *The Sign of the Four*) | **59/60** (B1 20/20, B2 20/20, B3 19/20; misspelled 12/12) | 54 | −0.97 / −1.17 |
| 100 negatives | **0/100 confident** | 0 | best −1.76 / −3.17 (cuts −1.45 / −2.50) |

**The one miss (B3):** the decode is the true message shifted by one letter (`NDSOBEEFFECTUALLY…ENOUGHIT` for
`ANDSOBEEFFECTUALLY…ENOUGHI`). The sheet route with the extra cell last and the one with it first differ by that shift
for this ordering, so 96 of 97 letters are right, one place out.

## K4
| Step | Commit | Result |
|---|---|---|
| Target: K4 + 100 shuffles (seed 760400) | b1d143b | — |
| Blind run (about 20 min) and freeze, incl. the 25-decode review packet | 24e9a3b | 13,700,640 fixed methods per ciphertext |
| Verify (no published letters; `r76/k4/VERIFY.json`) | a35c808 | **PASSED**: 833 stored decodes re-encrypt |
| Sealed reveal (`r76/k4/REVEAL.json`) | 03adffc | **NO_SIGNAL** |
| Exact checks (`r76/k4/EXACT76.json`) | this commit | **NO_SOLUTION** in all three |

### Blind result: NO_SIGNAL
- **Score:** K4's best decode scores −1.839 per letter (letter model) and −4.18 (word model), against cuts of −1.45 and
  −2.50. Holdout messages scored −0.97 or better.
- **Shuffles:** 62 of 100 score at or above K4. Their best decodes have median −1.833 and maximum −1.757.
- **Best decode:** B1, keyed alphabets SHADING → INVISIBLE, key PASSAGE (KRYPTOS numbering, Beaufort). It matches 2
  of the 24 published letters.
- **Raw decode** (unedited):
  `LDRLKXMLWUJAECLAGWDEOTALIOVUFGVRIFVEJKMISTSISRCMOWLTRARADSFGGDBAEOILTWIXORJAAOCEKUNADWRJVRICHRYSU`
- **Best of each family:** B1 −1.86, B2 −1.89, B3 −1.96 per letter. All are gibberish, with 1–3 published letters.
- **Whole family (crib-assisted):** no method matches more than 8 of 24; the first 10 shuffles reach 8–10.
- **Packet:** all 25 decodes are LOW-CONFIDENCE RAW OUTPUTS.

### Exact checks for every key (crib-assisted, after the freeze)
| Check | What was decided | Feasible for K4 | Shuffles: feasible, median / max | Verdict |
|---|---|---|---|---|
| H1X: one stage, any key, alphabets from 77,229 keyword orderings | Periods 2–24 and 34–48 | 1 alphabet pair at period 37 (counted 7 times with its shifted equivalents) | 0 / 77 (one shuffle: 11 pairs × 7) | **NO_SOLUTION** |
| H2X: key scrambled by any of 64,782 routes, any key, periods 2–24 | 47.2 million settings with ≥ 5 checks | **0** unshifted; 1 with a +1 shift | 0 / 12 | **NO_SOLUTION** |
| H2bX: text routed by the 47 sheet/R61 routes, repeating key ≤ 24 | 71,744 settings with ≥ 3 checks | **0** | 0 / 0 | **NO_SOLUTION** |

**Controls clean:** 0 H1X settings at the periods L21 already excludes, and 0 settings for the identity route in H2X.

**H1X's one feasible setting** is plaintext alphabet PLAITING, ciphertext alphabet ACA-MANDATORIES, additive, period 37.
- All 8 slot-sharing pairs are informative. Across 77,229² alphabet pairs, roughly one such match is expected by
  chance, and 3 of 10 shuffles also have some.
- **Its decode is gibberish.** The completion fills 21 of 37 key letters blind and scores −1.51:
  `ICLIENHASPELLOCALIMSBEASTNORTHEASTRYDESALUEARDUOBORDJALBORFLJOUBERLINCLOCKALETOUTIONGWEBONSLEASWH`.
- **Post-hoc follow-up** (`r76/sealed/h1_followup.py`, `r76/k4/H1_FOLLOWUP.json`; not pre-registered): 60 random
  restarts of the completion.
  - K4's setting reaches −1.37 at best and stays gibberish.
  - The shuffle's 11 chance settings reach −1.19 to −1.34 from the fill-in alone.
  - So K4's one setting is no better than chance.

**A limitation found by the shuffles.**
- One shuffle (NULL_003) came out CONSISTENT in H1X. Its settings are at period 45, where 29 of 45 key letters are
  filled in blind, and the fill-in alone made English-like fragments clear the cuts (`EBLACKOVESISCHANDTOOP…`).
- **What this means:** at periods where more than half the key is unpinned (about 35 and up), H1X's readability test
  has little power. There the K4 result rests on feasibility: exactly one setting, at chance level, with no readable
  decode under any completion tried.
- At periods 8–24, decodes are pinned or nearly so, and the test is strong (synthetic plants: 79–97 of 97 letters
  right).

## Conclusion
- **H1 (K1/K2's method with a different alphabet keyword) is closed for every key** at periods 2–24 and 34–48. That
  covers every plaintext and ciphertext alphabet built from the 28,000+ English words in the R59 word model (three
  constructions each), additive or reverse.
  - This extends L04 (four alphabets) and L21 (arbitrary alphabets, at some periods).
  - Periods 25–33 and 49–52 leave too few same-slot pairs to decide.
- **H2 (key scrambled by a sheet route, message in place) is closed for every key** with periods up to 24, over
  64,782 routes:
  - R72's sheet routes;
  - every K3-style double rotation and single turn up to width 48;
  - every complete columnar of width 2–7 in any column order;
  - the R61 routes.
- **H2b (text routed on R72's sheet routes or the R61 routes, repeating key ≤ 24) and H2c (R74's sandwich on the
  sheet routes) are closed.** That settles R72's on-hold item and R62C's COL_LT lead for these forms.
- **H6:** none of these becomes feasible when a letter is dropped or added between the published strings (shifts
  ±1, ±2), beyond chance-level single settings.
- **What follows, per the pre-registration:** a design round for new ideas (Fable), per Tyler's plan. H3–H5 in
  `r76/HYPOTHESES.md` remain untested.
- The ledger row is L166.
