# R74 result (Claude Code, 9 Nov 2026): K1 → K3 → K2 sandwich

Pre-registration: `r74/PREREGISTRATION.md` (9c7eb1a). The synthetic gate used no K4 data.

## Sealed synthetic gate
| Step | Commit | Result |
|---|---|---|
| Pre-registration (cuts −1.45 letter model, −2.50 word model per letter, fixed on development books) | 9c7eb1a | — |
| Holdout (seed 740300; truth sha256 791126b0… withheld) | 73cfb25 | 420 ciphertexts |
| Blind run (15 s on 4 cores) and freeze | 1eec9eb | 15,680 transforms per ciphertext; 5 best kept |
| Verify (truth not opened) | this commit | **PASSED**: 2,100 stored decodes re-encrypt |
| Gate (truth hash matched; `r74/holdout/GATE.json`) | this commit | **PASS** |

| | Recovered and confident | Bar | Worst score (letter / word model) | Bound |
|---|---|---|---|---|
| 100 clean positives | **100/100** | — | — | — |
| 20 misspelled positives (2 letters changed) | **20/20** | — | — | — |
| All 120 positives | **120/120** | 108 | −1.12 / −1.42 | power ≥ 97.5% (one-sided 95%) |
| 300 negatives | **0/300 confident** | 0 | best −1.83 / −3.43 | false confidence ≤ 1.0% (one-sided 95%) |

**Margins:** every kind of negative is at least 0.37 per letter below the letter-model cut and 0.93 below the
word-model cut.

The K4 run follows, as pre-registered.
