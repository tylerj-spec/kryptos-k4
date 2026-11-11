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
