# R63 pre-registration (Claude Code, 3 Nov 2026): running keys that are NOT English

Written before any holdout or plant is generated and before any K4 run. Follows `r53/BLIND_RULES.md`:
- no solver sees K4's published letters or their positions;
- outputs are frozen and pushed before a separate reveal.

## Why
- **What came before:** R59 (L149) and R61 (L150) found no sign of a running key whose **key is English text**, in place
  or after K3-style or engraving-route transposition. The working linguistic hypothesis is that K4's plaintext is
  ordinary English. R63 keeps that and changes the **key** to sources motivated by Kryptos:
  - **(A) World Clock key.** Sanborn named the Berlin World Clock (Weltzeituhr, Alexanderplatz) as the clock in
    BERLINCLOCK. The key here is any sequence of its city names, in any order, with repeats allowed.
    - **Vocabulary:** the photo-derived R23/R49 chart (`r49/prior_photo_360_chart.json`, all eras, German forms) plus
      declared variants. That makes 107 names (`r63/data/clock_names.txt`, `r63/corpus/build_keys.py`).
    - **Why a model:** it avoids needing the exact 1988–90 inscription order, which is unverified (L25, L37, L77).
    - **Note on BERLIN:** the vocabulary contains BERLIN because it is on the clock. It is in the **key** model only;
      the plaintext model is the generic English one.
  - **(B) German prose key.** Modern German (NLTK Europarl), motivated by Berlin.
  - **(C) Fixed numeric streams.** The first 10,000 digits of π, e, √2 and φ; the K2 coordinates (38 57 6.5 N,
    77 8 44 W → 38576577844); the dates 19901103, 19891109 and 1986, each repeated.

## (A)/(B) hypotheses and blind solver
- **Model:** in place. c = X[x(p) + x(k)] (VIG), X[x(k) − x(p)] (BEAU) or X[x(p) − x(k)] (VARB), with X = AZ or
  KRYPTOS. p is ordinary English; k comes from the CLOCK or GERMAN model.
- **Solver:** `r63/blind/rk2_solve.cpp`, the R59 solver generalised to two text models. The plaintext stream is scored
  by the R59 English model (`r59/blind/LM_SHA256` plus `word_model_orth.tsv`), and the key stream by the key model.
  - **CLOCK model:** an order-6 letter model trained on a 5,000,008-letter synthetic sequence of the 107 names
    (seed 63000), with the names as dictionary. 0.90 bits/letter.
  - **GERMAN model:** order-6, trained on Europarl German files 1–8 (1,996,309 letters), with its 22,693 words as
    dictionary. 1.81 bits/letter on file 9.
  - **Hashes:** `r63/blind/MODELS.sha256`.
- **Runner:** `r63/blind/run.py`. Each ciphertext is solved under both key models, all 6 conventions, beam 50,000,
  TOPN 2000, LAMBDA 1, POLISH_M 2, POLISH_WORDS 20000. It is resumable, and the solver is deterministic.
- **No tuning after this file is committed.**

## Development record (development sources; K4 never run)
- **Data:** 8 plants (`r63/sealed/make_plants.py`, *Tom Sawyer* plaintext, keys alternating CLOCK / GERMAN from
  Europarl file 9, seed 63001) and 8 shuffled nulls (seed 63002).
- **CLOCK-key plants:**
  - plaintext recovered 93, 96, 97, 97 of 97 (2 exact);
  - totals −216 to −185 under the CLOCK model;
  - null CLOCK totals −404 to −374, so the separation is more than 150.
- **GERMAN-key plants:**
  - plaintext recovered 76, 81, 93, 60;
  - totals −288, −274, −259, −330 under the GERMAN model;
  - null GERMAN totals −340 to −323, so 3 of 4 plants are above every null.
- **Conventions:** identified 8/8 under the plant's own model.
- **Caution:** on nulls, the CLOCK model makes the key look like a valid name sequence while the plaintext is
  gibberish. Only the total score counts.

## Holdout gate for (A)/(B), fixed now
- **Plants:** 20, generated only after this file is pushed:
  `r63/sealed/make_plants.py hold_pt.txt de_hold.txt 20 63100 HOLD OUTDIR`.
  - Plaintext from the R59 holdout books.
  - Keys alternate CLOCK / GERMAN, the GERMAN keys from Europarl file 10, which is unseen.
- **Nulls:** 20 shuffles (`r63/sealed/make_nulls.py BLIND.tsv 63101`).
- **Run:** one blind run, frozen and pushed before `r63/sealed/gate.py` runs.
- **Pass (all of):**
  - **CLOCK:** detected ≥ 8/10 (model total above the maximum null total for that model), and plaintext ≥ 60/97 in
    ≥ 8/10;
  - **GERMAN:** detected ≥ 5/10, and plaintext ≥ 60/97 in ≥ 5/10;
  - **all re-encryption witnesses valid.**
- **If it fails:** record it, and do not run K4.

## K4 test for (A)/(B), only if the gate passes
- **Input:** `r63/sealed/prepare_k4.py` writes the unchanged K4 plus 100 shuffles (seed 630070).
- **Run, freeze, reveal:** the same runner; freeze and push; then `r63/sealed/reveal_k4.py`. The reveal is the only
  code holding the published letters.
- **Decision, per key model m:**

  | Outcome | Condition |
  |---|---|
  | **SIGNAL (m)** | K4's model-m total exceeds all 100 nulls' model-m totals **and** K4's frozen plaintext matches ≥ 10/24 published letters |
  | **Score anomaly (m)** | the first condition without the second (STAT; not a candidate) |
  | **NO SIGNAL (m)** | otherwise |

  - Two models are tested, so a chance r = 0 under one of them has probability of about 2/101. The letter
    requirement guards against that.

## (C) Fixed numeric streams: strict-blind harness (`strictblind/`)
- **Experiment directory:** `r63/numeric/exp/`.
  - **Key files:** the eight `key_*.txt` from `r63/numeric/make_keys.py`, with digit d written as letter chr(65+d).
  - **Routes:** `strictblind/blind/routes.py r27` (identity plus 20 K3-style routes × 2 orders = 41 route-orders).
  - **Scope:** every key file × every window, forward and reversed, × A–Z/KRYPTOS key numbering × 12 fixed conventions.
- **Plants:** 4, made **before** the blind run: `strictblind/sealed/make_plants.py` with keys PI, E, SQRT2, PHI,
  templates 0–3, seeds 63201–63204.
- **Order:** blind experiment, then freeze committed and pushed, then `reveal.py` and `whole_family.py`.
- **Decision:**
  - **EXCL** for each exact family (key file × routes × conventions) if no setting matches all 24 published letters
    and the 4 plants rank #1.
  - **Any 24/24 setting** is listed raw and checked for English.
- **Overlap:** periodic keys such as repeated coordinates and dates were already excluded in place (L03, L04) and with
  these routes (L47). They are re-run here only for completeness.

## Amendment 1 (3 Nov 2026; after the R62 review comment on PR #40, BEFORE the (A)/(B) holdout gate and BEFORE any (A)/(B) K4 run)
- **Reclassification, prompted by the R62 review.** `r53/BLIND_RULES.md` requires key sources that are independent of
  the known K4 plaintext. That excludes choosing keys or methods **because of** the published clues, not only feeding
  the letters to a program.
  - **(A) CLOCK** was chosen because Sanborn tied the published BERLINCLOCK clue to the Weltzeituhr.
  - **(B) GERMAN** was partly motivated by "Berlin".
  - Both are therefore **EXPLORATORY / SOURCE-DERIVED**, not R53-compliant blind key selection.
- **What stays the same for (A)/(B):**
  - the holdout gate still runs, as a **solver-capability benchmark**; it uses no K4 data;
  - **no K4 run** for (A)/(B) will be described as candidate generation;
  - whether to run K4 under (A)/(B) at all, as a clearly labelled exploratory check, is **Tyler's decision**;
  - if run, the published letters can only reject outputs, never select variants;
  - results will not be pooled with compliant blind tests.
- **(C) numeric keys, already frozen and revealed (all EXCL, so no selection could occur):**
  - π, e, √2, φ, the K2 coordinates (a K2 fact) and 19901103 (the dedication date) are independent of the K4 clues;
  - **19891109** (Berlin Wall) and **1986** (Egypt trip) come from Sanborn's 2025 statements about K4, so they are
    labelled **SOURCE-DERIVED** in the result.
- Nothing else changes. `PROTOCOL.sha256` was re-hashed for this amendment.

## Amendment 2 (3 Nov 2026; owner clarification, still BEFORE the (A)/(B) gate and any (A)/(B) K4 run)
- **Owner clarification of R53.** Tyler, who set the rule, clarified it: *"Clue motivated ideas are fine. The issue I
  had was that the known text was part of the algorithm instead of being a check. I only want the cypher text used for
  the algorithm & then if we can produce solutions that depict the known characters in the right spots then we are on
  to something."*
- **What this means for R63:**
  - Amendment 1's reclassification is **withdrawn**.
  - (A) CLOCK, (B) GERMAN and all of (C) are ordinary R53-compliant blind tests. The algorithm reads only the ciphertext
    and generic models; the published letters are used only as the after-freeze check.
  - The K4 rule for (A)/(B) applies **as originally pre-registered**.
- Nothing else changes. `PROTOCOL.sha256` was re-hashed.
