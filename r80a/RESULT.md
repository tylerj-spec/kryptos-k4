# R80a result: two keyword stages, one key listed and one free — sealed synthetic gate (Claude Code, 14 Nov 2026)

**Outcome: GATE PASSED, all four families.** The solver reliably recovers messages built with two keyword stages on
different tableaux, one keyword from the list and one unknown, in both orders, and it marks none of 100 wrong-family
ciphertexts as confident. **No K4 data was used.** Running these families on K4 (R80) needs its own pre-registration
and Tyler's go.

Pre-registered in `r80a/PREREGISTRATION.md` (commit d31202e, `r80a/PROTOCOL.sha256`) before the holdout existed. The
review of PR #76 asked for this round ("I recommend R80a first, then R81b"), with the following requirements:
- synthetic data only;
- both orders;
- recovery by both key lengths, their gcd and their lcm;
- exact and ≥ 95-letter recovery reported separately;
- nonstandard-spelling controls;
- no hard exclusion of shorter combined periods;
- no K4 run until a sealed gate passes.

Every pair of key lengths was run; none was excluded.

## Steps
| Step | Commit | Result |
|---|---|---|
| Build, unit tests (`r80a/tests/test_r80a.py`) | 4641991 | All pass (round trip 400; decode path 200; fast pass 0 = reference; solver 12/12 exact) |
| Development check on spent books (`r80a/results/DEV.json`) | d31202e | 24/24 exact and confident; STRETCH 7/8; 0/28 negatives confident (best −1.519) |
| Pre-registration (cuts −1.30 / −2.50 kept from R79; bar 18/20 at ≥ 95 letters) | d31202e | — |
| Sealed holdout, 196 ciphertexts (seed 800300; truth sha256 4e3daeae…) | 8f95144 | — |
| Blind run, freeze (`r80a/holdout/run/`) | 207f8d3 | — |
| Verify, before the truth was opened (`r80a/holdout/VERIFY.json`) | aba47fb | 1,762 stored decodes re-encrypt |
| Truth opened (hash matches), gate (`r80a/holdout/GATE.json`) | 0d71fcc | **All four families PASS** |
| Post-reveal diagnostic of the misses (`r80a/holdout/DIAG_MISSES.json`; not part of the gate) | this PR | All 9 misses lost by the pass-0 filter; the solver decodes all 9 exactly from the true setting |

## Model (as pre-registered)
- Stage one: `q = CA1[s1·IDX[PA1][p] + t1·IDX[KA1][k1(i)]]`.
- Stage two: `c = CA2[s2·IDX[PA2][q] + t2·IDX[KA2][k2(i)]]`.
- Operations VIG, BEAU and VARB; alphabets A–Z or KRYPTOS, with CA1 ≠ PA2; 96 conventions per family.

| Family | Listed key | Free key | Settings per ciphertext | log10 settings × 26^m |
|---|---|---|---|---|
| L1 | stage one: one of 28,943 words, phase 0 | stage two, 1–12 letters | 33.3 million | 23.44 |
| L2 | stage two: one of 28,943 words, phase 0 | stage one, 1–12 letters | 33.3 million | 23.44 |
| X1 | stage one: any key of 1–3 letters | stage two, 1–12 letters | 21.1 million | 23.24 |
| X2 | stage two: any key of 1–3 letters | stage one, 1–12 letters | 21.1 million | 23.24 |

## Sealed gate
Positives came from *The Age of Innocence* and *The Moonstone*; negatives from *Kidnapped* (plaintext) and *The
Prisoner of Zenda* (keys). None of the four books had been used in the project before.

| Family | Recovered and confident (bar 18/20) | Exact | ≥ 95 letters | ≥ 85 letters | Plain | 2 letters changed | Nonstandard spelling | STRETCH (11–12) | Best negative in this family (letter model) |
|---|---|---|---|---|---|---|---|---|---|
| L1 | **19/20** | 19 | 19 | 19 | 10/10 | 6/6 | 3/4 | 2/4 | −1.485 |
| L2 | **18/20** | 18 | 18 | 18 | 9/10 | 5/6 | 4/4 | 4/4 | −1.501 |
| X1 | **19/20** | 19 | 19 | 19 | 9/10 | 6/6 | 4/4 | 3/4 | −1.515 |
| X2 | **19/20** | 19 | 19 | 19 | 10/10 | 6/6 | 3/4 | 3/4 | −1.515 |

**Positives: 75/80 recovered and confident, all 75 exact.**
- Every decode was either exact or had at most 15 letters right. Nothing landed between, so there was no shadow decode
  (about half right).
- No wrong decode was confident.
- The weakest recovered decode scores −0.961 on the letter model and −1.453 on the word model.
- 19 of the 75 were decoded under another family's label, mostly X plants decoded by L1 or L2. A key of 1–3 letters
  that is also a listed word, or an equivalent setting, gives the same plaintext. Recovery is judged on the text.

**Negatives: 0/100 confident.**
- The highest letter-model score is −1.485 (one-time pad). Each generator's best is between −1.485 and −1.534:

  | Generator | Best (letter model) |
  |---|---|
  | One-time pad | −1.485 |
  | CTAK | −1.501 |
  | Running key | −1.515 |
  | Homophonic | −1.522 |
  | Periodic | −1.522 |
  | PTAK | −1.525 |
  | Gromark | −1.534 |
  | Shuffles | −1.534 |
  | Two random keys | −1.534 |

- The letter-model cut does the separating. 43 of the 100 negatives clear the word-model cut on its own (best −1.961).
  This is why both cuts are required, as in R79.

### Recovery by key lengths (positives; STRETCH separately)
The gate script's length tables pool positives and STRETCH plants. The tables below split them, computed from
`GATE.json` rows after the gate. The counts are the same data.

| Free-key length | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 (STRETCH) | 12 (STRETCH) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Recovered and confident | 12/12 | 6/6 | 9/9 | 6/6 | 4/4 | 7/7 | 9/9 | 8/10 | 6/7 | 8/10 | 7/9 | 5/7 |

| | Recovered and confident |
|---|---|
| lcm of the two key lengths ≤ 24 | 60/62 |
| lcm 25–48 | 12/13 |
| lcm ≥ 49 (largest 72) | 3/5 |
| STRETCH by lcm: ≤ 24 / 25–48 / ≥ 49 | 6/7, 2/3, 4/6 |
| gcd 1 | 54/57 |
| gcd 2 / 3 / 4 / 5 / 6 / 10 | 12/12, 4/5, 2/2, 0/1, 2/2, 1/1 |
| Listed word length, L families, 3–12 letters | 37/40 |
| Listed key length, X families, 1 / 2 / 3 letters | 17/17, 12/12, 9/11 |

**Free keys of 1–7 letters: 53/53. Free keys of 8–10: 22/27 (81%). STRETCH (11–12, reported only): 12/16, all 12
exact.** The lcm and gcd rows follow the free-key length: every positive miss has a free key of 8–10 letters. The two
lcm ≥ 49 misses are L2 plants with an 8-letter free key.

### Why the nine misses were missed (post-reveal diagnostic)
`r80a/sealed/diag_misses80.py` took each missed plant's true setting, with the truth open. It does not change the
gate.
- **pass0_rank:** the true setting's rank in pass 0 among every setting of its family at its free-key length. The
  runner keeps the best 4,000.
- **Solver from truth:** R79's solver with 6 starts on the true listed key and convention.

| Item | Family | Kind | Listed key | Free key | pass0_rank | Solver from truth | Plaintext quadgram score | Frozen best decode quadgram score |
|---|---|---|---|---|---|---|---|---|
| H_071 | L1 | nonstandard spelling | 5 | 10 | 850,995 | exact | −4.72 | −5.27 |
| H_103 | X2 | nonstandard spelling | 3 | 9 | 23,843 | exact | −4.36 | −5.35 |
| H_112 | X1 | plain | 3 | 10 | 7,849 | exact | −4.24 | −5.26 |
| H_116 | L2 | plain | 9 | 8 | 29,164 | exact | −4.54 | −5.40 |
| H_182 | L2 | 2 letters changed | 7 | 8 | 60,536 | exact | −4.51 | −5.38 |
| H_000 | L1 | STRETCH | 10 | 11 | 1,810,698 | exact | −4.56 | −5.32 |
| H_014 | X2 | STRETCH | 3 | 12 | 11,787 | exact | −4.26 | −5.34 |
| H_076 | X1 | STRETCH | 3 | 11 | 51,351 | exact | −4.41 | −5.50 |
| H_185 | L1 | STRETCH | 11 | 12 | 772,615 | exact | −4.17 | −5.16 |

Every miss was lost by the pass-0 filter: the true setting ranked between 7,849 and 1.8 million, outside the 4,000
kept. Started from the true setting, the solver decodes all nine exactly, and each plaintext scores far above the
frozen wrong decode. So the scoring and the solver are not the limit. The cheap first pass is: with a free key of 8 or
more letters, each slot's best single-letter start is too noisy to rank the true listed key near the top.

## What this means for R80
- **Power:** on K4, a null from these families would be strong for free keys of 1–7 letters, where the gate recovered
  53/53. For 8–10 it would be weaker, at about 81% recovery in the gate, and for 11–12 weaker still (12/16, reported
  only).
- **A possible R80b:** raise K0 for free lengths 8–12 to recover those settings. That changes the runner, so it would
  need its own development check and a new sealed gate before any K4 run. Pass 0 is about 4 µs per setting, so a
  larger K0 costs mainly pass-1 solver time.
- **What R80 would run:** K4 plus 100 shuffles, blind, with these four families exactly as gated (about 2.2 hours on
  4 cores). Then freeze, verify, reveal, and check the frozen work. R80 gets its own pre-registration with these
  numbers and runs only on Tyler's go.

## Not covered by R80a
- Listed keys at other phases (mode L+).
- PALIMPSEST and ABSCISSA alphabets in either stage.
- Listed keys outside the 28,943-word list.
- Free keys of 13 or more letters.
- Both keys free (mode A, outside R80's scope: `r80/FABLE_IDENTIFIABILITY.md` §1.7).
- CA1 = PA2, which collapses to one stage with a summed key (ledger L36).
