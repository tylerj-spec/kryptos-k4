# R44 pre-registration (Claude Code, 29 Oct 2026): fresh holdout for the keyword-plaintext-alphabet solver

Written before the holdout ciphertexts are generated or the solver sees them. Development data used so far, planted only
and never K4:
- R43's D0 messages (D0_00, D0_01, D0_10, D0_11, D0_15);
- the L109/D1 plants.

## Question
**Hypothesis H-KW:**
- the plaintext alphabet is a **keyword alphabet**: a keyword's letters with repeats dropped, then the unused letters
  in A–Z order, the way the KRYPTOS, PALIMPSEST and ABSCISSA alphabets are built;
- the cipher alphabet is **completely free**;
- the true 97-digit Gromark key is supplied.

Under H-KW, can 97-letter English plaintext be recovered **exactly** with no plaintext, crib or mask input?

## Solver (frozen: `r44/blind/kwpa_solve.cpp`, defaults KCAND = 5000, RESTARTS = 8, TOP2 = 50, RESTARTS2 = 64)
- **Candidates:** every distinct keyword alphabet from the 5,000 most frequent exact words of length 5–10 in
  `k4kit/data/word_model_orth.tsv` (4,749 alphabets).
- **Inner solve:** for each candidate, anneal the cipher alphabet by quadgram score (8 restarts × 30,000 swaps).
- **Second stage:** re-solve the 50 best candidates with 64 restarts.
- **Answer:** the best-scoring plaintext, both alphabets, and an exact re-encryption check.
- **No tuning after this file is committed.**

## Development record (planted only)
- **Prototype:** a Python enumeration with the inner solve. 3/3 exact: keywords EXECUTED, RULED, RELATE, on R43
  D0_10, D0_11 and D0_15 text.
- **Blind solver smoke tests:**
  - **EXECUTED:** exact (−402.0; runner-up −439.5).
  - **RELATE:** exact (−366.8; runner-up −406.4).
  - **RULED:** 11 letters wrong. RULED ranks 5,008th and lies just outside the 5,000-word candidate list, where 247
    words tie on score. The solver returned the nearest keyword alphabet, so the miss is a closed-world violation,
    not a search failure.
- **Change made in development:** the stage-2 re-solve of the top 50 was added after the first smoke test, before
  registration.

## Holdout (`r44/sealed/make_holdout.py`)
- **Passages:** 20 new passages written for R44, not used in development.
- **Keyword:** drawn uniformly from the solver's 5,000 candidate words. This is a **closed-world** test: the true
  keyword is in the dictionary.
- **Cipher alphabet:** uniformly random.
- **Key:** uniformly random 5-digit Gromark primer.
- **Seeds:** 44200–44219.
- **Order:** the generator runs only after this file and the solver are committed.

## Gate (fixed now)
- **Pass:** at least **16/20** messages recovered **exactly** (97/97 letters), with **0** invalid forward-encryption
  witnesses. Scoring is done after the solver output is frozen and committed, with R43's independent
  `r43/sealed/evaluate.py`.
- **What a pass means:** H-KW is blind-solvable when the key is known. It is **not** a K4 result and authorises no K4
  run by itself. A K4 use needs its own pre-registration with a key search, a cost plan and nulls.
- **Not covered:** two uniformly random alphabets (R43's D0 bar) are outside H-KW; no method here solves them (L138,
  R44 notes).
