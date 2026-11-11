# R75 result (Claude Code, 10 Nov 2026): identify K4's method class

Pre-registration: `r75/PREREGISTRATION.md`, with Amendment 1 (a677504). Runbook: `r75/RUNBOOK.md`.

## Part A: sealed synthetic gate (no K4 data)
| Step | Commit | Result |
|---|---|---|
| Holdout (seed 750300; truth sha256 cf55a7bb… withheld) | 2d6cea8 | 160 ciphertexts |
| Blind run (about 12 min on 4 cores) and freeze | a6f65c6 | 6,934,560 fixed methods per ciphertext |
| Verify (truth not opened) | this commit | **PASSED**: 1,751 stored decodes re-encrypt |
| Gate (truth hash matched; `r75/holdout/GATE.json`) | this commit | **PASS** |

| | Recovered and confident | Bar | Worst score (letter / word model) |
|---|---|---|---|
| 60 positives (*The Lost World*, *Three Men in a Boat*) | **58/60** (misspelled 11/12) | 54 | −0.99 / −1.40 |
| 100 negatives | **0/100 confident** | 0 | best −1.76 / −3.03 (cuts −1.45 / −2.50) |

- **By sub-family:** 10/10 for five of the six. Interrupted key with sculpture keywords (F2A) got 8/10.
- **The two misses** are both F2A and both have 95–96 of 97 letters right.
  - **ITALL… read as KSALL…** A different interrupted-key setting matches the true one everywhere except the first
    two letters.
  - **NOWTHE… read as HOWTHE…** The same setting one phase off, which differs only in the first letter.
- So recovery is not the issue. Under an interrupted key, only the opening letters depend on the phase.

## Part B: blind K4 run
| Step | Commit | Result |
|---|---|---|
| Target: K4 + 100 shuffles (seed 750400) | 7b79310 | — |
| Blind run (about 7 min) and freeze, incl. K4's 25-decode review packet | b9e8650 | 6,934,560 fixed methods per ciphertext |
| Verify (no published letters; `r75/k4/VERIFY.json`) | d5ace40 | **PASSED**: 1,131 stored decodes re-encrypt |

## Part C: after the freeze

### C1. Reveal (`r75/k4/REVEAL.json`): **NO_SIGNAL**
- **Score:** K4's best decode scores −1.775 per letter (letter model) and −3.64 (word model), against cuts of −1.45 and
  −2.50. Holdout messages scored −0.99 or better.
- **Shuffles:** 2 of 100 score at or above K4. Their best decodes have median −1.837 and maximum −1.761.
- **Best decode:** interrupted key, keyword EXACT, KRYPTOS tableau, variant Beaufort, stalling after each ciphertext
  S. It matches 4 of the 24 published letters.
- **Raw decode** (unedited):
  `JSADZJVFVMSIIIHUKDILRWIBOXORBYLETTPESBOTHRIIQTDWTJBRXXTHKOTXWWSKEAAYERPWRASLUXSABRALXLENUTESCAMEF`
- **Whole family (crib-assisted):** no method matches more than 9 of 24 published letters; the first 10 shuffles reach
  8–9. 0 methods reach the listing bar of 14.
- **Packet:** all 25 decodes are LOW-CONFIDENCE RAW OUTPUTS; the best matches 4/24.

### C2. Exact checks for every key (crib-assisted; `r75/k4/EXACT.json`, `r75/k4/GRIDX.json`)
| Check | Settings with enough checks | Feasible for K4 | Shuffles: feasible, median / max | Verdict |
|---|---|---|---|---|
| F0X control: one stage, repeating key, periods 1–26, 4 alphabets | 800 | **0** | 0 / 0 | reproduces L03/L04 |
| F1X two stages in place, any keys, periods 1–26 each | 386,048 | 1,868 | 2,354 / 2,846 | **NO_SOLUTION** (best decode −1.68) |
| F2X interrupted key, any key, periods 1–26 | 7,711,232 | **0** | 0 / 22 | **NO_SOLUTION** |
| F3X held key, any key, hold 2–12 | 864,864 | **0** | 0 / 0 | **NO_SOLUTION** |
| F4X grid keys, widths 2–48, every offset, both orientations | 1,624,064 | **0** | 0 / 4 | **NO_SOLUTION** |

- **F1X:** fewer settings are feasible for K4 than for 19 of 20 shuffles. Its decodes keep the published letters (they
  are forced) but are gibberish elsewhere. The best, −1.68, is no better than the shuffles' best (−1.62 to −1.67).
- **F2X, F3X, F4X:** no setting with enough checks is feasible at all. So K4 is not an interrupted key, a held key or a
  row-and-column grid key, for any key letters, on any of the four alphabets.

### C3. Key shape and key class (published letters; diagnosis only)
- **Key shape (`r75/k4/KEYSHAPE.json`): SHAPE_CONFIRMED.**
  - Family-wise p = 0.035 over 48 cells against 200,000 shuffles; the 192-cell secondary family gives 0.127.
  - The strongest cells are under plain A–Z with the sum form, c + p:
    - equal key values at distance 1–2: 7 against 1.6 expected (p 0.0015);
    - equal pairs overall: 22 against 10.6 (p 0.005).
  - Implied key: `9 11 9 14 3 4 6 10 20 10 10 10 11 | 14 2 6 6 1 6 14 10 19 17 20`.
  - **As disclosed in advance**, I noticed this pattern by hand on 9 Nov before the statistics were written. The
    p-value says how unusual the strongest cell is; it is not independent confirmation. The designed false-alarm
    rate is 5%.
- **Key class (`r75/k4/KEYCLASS.json`): DIGITS.**
  - 64% of the 25 nearest synthetic ciphers have decimal-digit keys (Gromark-like). The rest are running keys 16%,
    random 8%, two-layer 8% and periodic 4%.
  - In calibration a running-key cipher is labelled DIGITS 4.8% of the time, and a random key 0.4%.
- **Conflict with the ledger:** a decimal key stream in place, with plain A–Z or KRYPTOS plaintext numbering and *any*
  ciphertext alphabet, is already excluded exactly (L14, pair-difference proof).
- **So the key's structure, if real, does not come from a decimal key in place.** It is either a 3%-level fluctuation,
  partly found by looking, or the mark of a mechanism outside the ten calibrated classes.

## Conclusion
- **Closed, for every key:** the three simple method classes this round targeted, plus grid keys.
  - interrupted keys and held keys (one stage, periods up to 26);
  - two stages in place on different tableaux (no readable decode);
  - grid keys with one key along the rows and one down the columns (widths 2–48).
- **Closed for the listed keywords:** 6.9 million fixed methods, blind (NO_SIGNAL).
- **ChatGPT's PR #67 family** (2,880 settings) is part of F1 and closed with it.
- **What follows, per the pre-registration:** the key class is DIGITS, so the next round is a design round on
  irregular keys under the flagged numbering (plain A–Z, sum form). It must start from the conflict above: decimal keys
  in place are already excluded. Candidates for that round, and the other open hypotheses, are in
  `r76/HYPOTHESES.md`.
- The ledger row is L165.
