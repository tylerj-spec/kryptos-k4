# R73 Phase B result (Claude Code, 9 Nov 2026): Family I passes its sealed synthetic gate; R26 falls two short

**Synthetic only. Nothing was run on K4, and no published letters were used.** Pre-registration:
`r73/PHASE_B_PREREGISTRATION.md` (4c230f6).

## Steps
| Step | Commit | Result |
|---|---|---|
| Pre-registration | 4c230f6 | — |
| Holdout (seed 730100; truth sha256 7cc22b0e… withheld) | 0ce43ac | 500 ciphertexts |
| Blind run (3.5 min on 4 cores) and freeze | 9dd4310 | all 70 settings per ciphertext kept |
| Verify (truth not opened) | this commit | **PASSED**: 35,000 decodes re-encrypt to their ciphertexts |
| Gate (truth hash matched) | this commit | below |

## Gate (`r73/holdout/GATE.json`)
| | Recovered and confident | Bar | Setting exact | Exact plaintext | Fewest letters right | Worst score per letter | Result |
|---|---|---|---|---|---|---|---|
| Family I | **94/100** | 90 | 100/100 | 63/100 | 82 | −1.37 | **PASS** |
| R26 | **88/100** | 90 | 93/100 | 61/100 | 67 | −1.81 | **FAIL** |
| Negatives | **0/300 confident** | 0 | — | — | — | best −3.12 (cut −2.7) | pass |

## Why R26 failed (diagnosis after the gate; not a re-score)
Of the 12 R26 failures, 7 still had the exact setting, with 80–89 of 97 letters right. There are two causes:
1. **Words missing from the dictionary** (DARCY, WICKHAM, NETHERFIELD, LONGBOURN, COMPOSEDLY, PERUSING, DIGRESSIONS).
   The solver takes a dictionary prefix such as WICK and loses the word counter for a few words.
2. **The wrong phase over the first 2–4 words** (5 cases).

Better handling of unknown words, or a full-text consistency pass, would probably fix both. Under the
pre-registration, though, R26 failed this gate. Any fix needs a new pre-registered round with a fresh holdout; this
holdout is now spent.

## What follows
- **Family I may be proposed for K4.** It passed with exact settings on 100/100 and no false confidence on 300
  negatives.
  - K4's flatness counts against it: only 0.56% of Family I ciphertexts are as flat as K4.
  - The run would be K4 + 100 shuffled nulls through the frozen blind runner, freeze and push, verify, then the sealed
    published-letter check.
  - It costs seconds of compute and needs Tyler's separate approval.
- **R26 is not taken to K4.** It fits K4's flatness much better (22%). If wanted, the next step is R73b: fix the
  unknown-word handling on development data, then a fresh sealed holdout with the same gate.

## K4 run, Family I only (pre-registered in `r73/K4_PREREGISTRATION.md`, 0025cd0; approved by Tyler)
| Step | Commit | Result |
|---|---|---|
| Target: K4 + 100 shuffles (seed 730200) | badf076 | — |
| Blind run (48 s) and freeze | b3f597c | all 70 settings per ciphertext kept |
| Verify (no published letters) | this commit | **PASSED**: 7,070 decodes re-encrypt |
| Sealed reveal | this commit | **NO_SIGNAL** |

- **K4's best Family I decode:** −4.27 per letter (KRYPTOS / KRY / VARB).
  - That is far below the −2.7 confidence cut. Real Family I messages scored −1.37 or better.
  - 67 of 100 shuffled copies of K4 score higher; the best null scores −3.79.
- **Published letters:** the decode matches 2 of 24. The best of all 18 Family I settings matches 4/24 (nulls: median
  3, maximum 5).
- **Contenders:** none, out of K4's 18 decodes.
- **Raw decode** (unedited; mostly unknown-word fragments):
  `O BR R US X OH HVN BA OM I F BC WG LY V QU PYU GR SA OO W TUB JU SA ERR ZX A T JR LVF I AX I NGDVSB VOS MK FT K WH DR ZZSN CE I GR UIW A U ERE AY`

**Conclusion:**
- K4 is not a word-restarted interrupted key with KRYPTOS, PALIMPSEST or ABSCISSA on an AZ or KRYPTOS tableau under
  VIG, BEAU or VARB, with English plaintext.
- The blind solver had 94/100 power on this family and finds nothing. K4 decodes worse than most of its own shuffles.
- This is consistent with the flatness expectation: only 0.56% of Family I ciphertexts are as flat as K4.
