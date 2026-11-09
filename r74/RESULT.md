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


## K4 run (pre-registered; run because the gate passed)
| Step | Commit | Result |
|---|---|---|
| Target: K4 + 1,000 shuffles (seed 740400) | a115d96 | — |
| Blind run (30 s) and freeze, incl. K4's full 15,680-decode scan and review packet | 7c6c5b8 | — |
| Verify (no published letters; `r74/k4/VERIFY.json`) | 08b1aa0 | **PASSED**: 20,710 decodes re-encrypt |
| Sealed reveal (`r74/k4/REVEAL.json`) | this commit | **NO_SIGNAL** |

**Blind result:**
- **Score:** K4's best decode, over all 15,680 transforms, scores **-1.901** per letter on the
  letter model (cut −1.45) and **-4.13** on the word model (cut −2.50).
  - Real messages in the holdout scored −1.12 or better.
  - K4 scores like its own shuffles: their median best is -1.908, and
    **344 of 1,000** score at or above K4.
- **Best decode:** R24x8/CW/fwd, ABSCISSA then PALIMPSEST. It
  matches 1 of the 24 published letters.
- **Raw decode** (unedited): `YOXAAVSXCWBUQYQUWWGKITHLOIKOUBVOBYEMOMITZJIVTVPELSYITBCGPAWAXCKRCXTEJVJONQSCJDARSSLOMMERCNIXTACCO`

**R74X (crib-assisted, post-freeze; not part of the blind outcome): EXCLUDED.**
- **The check:** each of K4's 15,680 frozen decodes, against the 24 published letters in place.
- **K4's result:** no transform matches more than **6/24**; CONSISTENT would need ≥ 20.
  - Distribution, by letters matched: 0: 6,102, 1: 5,829, 2: 2,691, 3: 831, 4: 185, 5: 36, 6: 6.
- **Chance level:** the shuffles' maximum has median 6 and reaches 9;
  971 of 1,000 shuffles do at least as well as K4.
- **So none of the 15,680 transforms is K4's cipher.** That holds even allowing for several wrong letters, under either
  keyword order, any phases, any of the three operations at either stage, and all 14 routes.

**Review packet:** 25 frozen decodes, one per (route, keyword order) pair, ranked by letter model. All are
**LOW-CONFIDENCE RAW OUTPUTS, not prospects**: every one is below both cuts, and the most published letters any of
them matches is 4/24. The top 5 are below; all 25 are in `r74/k4/REVEAL.json`.

| # | Route | Keywords | Letter model | Word model | Published letters | Raw decode |
|---|---|---|---|---|---|---|
| 1 | R24x8/CW/fwd | ABSCISSA → PALIMPSEST | -1.901 | -4.13 | 1 | `YOXAAVSXCWBUQYQUWWGKITHLOIKOUBVOBYEMOMITZJIVTVPELSYITBCGPAWAXCKRCXTEJVJONQSCJDARSSLOMMERCNIXTACCO` |
| 2 | SNAKE_L | ABSCISSA → PALIMPSEST | -1.922 | -4.34 | 1 | `WWORPICHOCYSZPLRURJWDXLLRAGOIFFBRSMTYJNUBCESCCRYWWWTSKJDMEXTGCENXTOAACHCZEIXOVDDGOWGRFFGNRBKNJPAZ` |
| 3 | COL_RT | ABSCISSA → PALIMPSEST | -1.933 | -4.41 | 4 | `BYZAFNEFCYKTZXHAEDRFHEZUBVJULHGBLOTBERXFTMRCMOLMTQOMHMLPSWDOWSLUGRLTAIREGGTWEXYXXFFRSFUBGUKCVNUVP` |
| 4 | SNAKE_R | ABSCISSA → PALIMPSEST | -1.936 | -4.36 | 1 | `TPMGWVEGZTCUEESARUNIHZNOVEOPICPFAETETXDXBOBAPRVURPMHEBFJEESXAVAFCUATMBIXTOVUXCFGNPCSLTGPKEUZHODWG` |
| 5 | R24x8/CW/fwd | PALIMPSEST → ABSCISSA | -1.945 | -4.16 | 0 | `NYYFDIDHOMMFEVTIVKTHGQUUCPPBJWCHMNJUECCAXRUEAPCIOQDUUKLLDOJEVGCLOTOFEERFENGHVRPSWCUMUZIPOIZSUZNIT` |

## Conclusion
- **K4 is not the K1 → K3 → K2 sandwich as defined:**
  - KRYPTOS-tableau substitution with PALIMPSEST or ABSCISSA;
  - then one of the 14 R61-derived routes;
  - then substitution with the other keyword;
  - any phases, VIG/BEAU/VARB at either stage.
- **The method worked:** 120/120 on a fresh sealed holdout with 0/300 false alarms. A K4 made this way would have
  decoded outright.
- **What stays open:**
  - other routes, which are the real unknown;
  - other keywords or key lengths;
  - unknown periodic keys at both stages (R74b in `r74/REVIEW.md`).
- The ledger row is L164.
