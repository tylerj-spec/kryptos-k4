# R118 result (Claude Code, 28 Nov 2026): both blind solvers fail on Germanic/Dutch-like respelled English and cope with telegraphese

**Type:** synthetic measurement (P9; Tyler: "I approve all of them"). No K4 input and no K4 claim. **Independent
review: NONE**; this is audit batch C.

## In plain words
**The question.** Two of our K4 "no signal" results rely on solvers that score text by how English it looks:
- R111, the S105 autokey solver;
- R59, the running-key solver.

If Sanborn "masked" the English before enciphering it, would these solvers still find it?

**The test.** The same passages were enciphered three ways:
- plain;
- respelled in a Germanic/Dutch-like style: K for C, V for W, IJ for Y, KS for X, and so on, by 12 fixed rules;
- in telegram style: THE, A, AN and OF dropped, and full stops written as STOP.

**The answer:**
- **Respelling breaks both solvers:**
  - S105 recovered 82.5% of plain messages to at least 90 of 97 letters, but only **10%** of the respelled ones. That
    is a drop of **72.5 points**.
  - R59's solver got at least 60 of 97 letter pairs right on 92% of plain messages, but on only **17%** of the
    respelled ones. That is a drop of **75 points**.
- **Telegram style barely matters:** S105 went from 82.5% to 80%, and R59 from 92% to 92%.

**What this means for K4.** The "no signal" results of R111 and of L149 (R59) **do not cover English respelled in a
Germanic/Dutch-like way**. If K4's plaintext is masked like that, those searches could have missed it. They do cover
telegram-style English.

## Results (`run_v1/RESULTS_S.json` and `RESULTS_R.json`, frozen in 266773b)
**S arm: S105, conditional at the plant's own cell** (40 windows × 3 forms, 2 per R111 cell; witnesses: 0 failures):

| Form | ≥ 90/97 | Exact | Drop from U | Recovered under U but not this form / the reverse | Label |
|---|---|---|---|---|---|
| U, unmasked | **33/40 (82.5%)** | 16 | — | — | — |
| G, Germanic respelling | **4/40 (10%)** | 0 | **72.5 points** | 30 / 1 | **SENSITIVE** |
| T, telegraphese | 32/40 (80%) | 16 | 2.5 points | 2 / 1 | ROBUST |

**R arm: R59's running-key solver, on the plant's own convention** (12 windows × 3 forms; witnesses: 0 failures):

| Form | Pair-correct ≥ 60/97 | Median pair-correct | Exact plaintext | Drop from U | Recovered under U but not this form / the reverse | Label |
|---|---|---|---|---|---|---|
| U | **11/12 (91.7%)** | 83 | 2 | — | — | — |
| G | **2/12 (16.7%)** | 43 | 0 | **75.0 points** | 9 / 0 | **SENSITIVE** |
| T | 11/12 (91.7%) | 80 | 1 | 0 | 1 / 1 | ROBUST |

**Runs:** both COMPLETE under `audit/run_bounded_agg.py`, with zero retries:
- S arm: 851 s, 372 MB;
- R arm: 1,248 s, 1,420 MB, using R59's pinned letter model (sha256 b1a2a3c7…, checked by the script).

**Commits:**
- pre-registration 707b8af;
- source 21e333a;
- frozen outputs 266773b.

## What this means
**Qualifiers added to the ledger** (additive, in L206):
- **R111 (L199)** NO_SIGNAL: does not cover Germanic/Dutch-like respelled plaintext. It does cover telegraphese.
- **R59 (L149)** NO SIGNAL: the same.

**Why the solvers fail.** The respelling removes C, W, Q, X and Y and inflates K, V, Z and J. That defeats English
quadgram and order-6 letter models. This is the scorer problem L69 found for Gromark.

**Development target.** A blind run aimed at masked English needs a scorer trained on the masked orthography, or one
that is robust to it. Any repeat blind K4 run must be separately registered.

**Not measured:**
- other rule sets;
- partial or inconsistent respelling;
- real Dutch or German (L63, L108);
- other solvers.

The G rules are one strong, consistent variant. Lighter masking would probably cost less.
