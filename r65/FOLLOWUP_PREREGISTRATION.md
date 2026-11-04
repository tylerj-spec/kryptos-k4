# R65b pre-registration (Claude Code, 4 Nov 2026): do the implied key letters read as language on the anomalous routes?

Written after R65's ciphertext-only result (REPLICATED: K4's GERMAN stage-1 route gap on SNAKE_L beat 300/300 fresh
nulls) and **before** this check is computed.
- **What R65b does:** a **check** of a fixed hypothesis against the published letters, as Tyler's rule allows ("then if
  we can produce solutions that depict the known characters in the right spots").
- **What it does not do:** nothing here generates or selects a candidate.

## Hypotheses checked (fixed now)
- **H1:** K4 = ordinary English plaintext, running key in **German**, letterwise convention c, then route **SNAKE_L**.
  This is the R64/R65 anomaly.
- **H2:** the same with an **English** key and route **COL_LT**. This is R61's anomaly, retested in R62C (ChatGPT; 2/300).

## Statistic (fixed now)
- **Implied key.** For a route R, X = un-route(K4, R). At each published plaintext position i (0-based 21–33 and 63–73)
  the key letter is forced by X[i], P[i] and the convention c, for each of the 6 conventions (AZ/KRY × VIG/BEAU/VARB,
  as in `r63/blind/rk2_solve.cpp`). This gives two fragments: 13 and 11 consecutive key letters.
- **T(R, L)** = the maximum over the 6 conventions of the summed letter-model log10 probability of the two fragments.
  - Each fragment is scored from an empty context by the order-6 model of language L.
  - L = German: `lm6_de.bin` (sha256 5451a6ce…). L = English: the R59 model (sha256 b1a2a3c7…).
- **Null:** the same statistic for **10,000 uniformly random permutations** of K4's 97 positions (seed 650071), under
  the same language.
- **p = (1 + #{null ≥ T}) / 10,001.**

## Decision (fixed now)
- **p ≤ 0.01:** the implied key letters on that route read like language L. This is a strong, specific lead. It is
  reported raw with the fragments; the next step is a full solve under a better-matched key model, pre-registered
  separately.
- **p > 0.01:** the implied key is not language-like. The route anomaly is **not** explained by a running key in
  language L on that route, under any of the 6 conventions.
- **Raw output:** all 6 conventions' fragments for H1 and H2 are listed, whatever the result.
- **Code:** `r65/sealed/implied_key_check.py`. It is the only R65 code holding the published letters, and it runs only
  after this file is pushed.
