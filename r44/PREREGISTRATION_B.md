# R44b pre-registration (Claude Code, 29 Oct 2026): word-score polish, tested on a second fresh holdout

Written before the second holdout exists. Same hypothesis as R44 (H-KW: keyword plaintext alphabet, free cipher
alphabet, true Gromark key given).

## Change from R44 (developed on the now-seen R44 holdout)
- **Pipeline:** `r44/blind/kwpa_solve.cpp`, unchanged and with the same parameters, is followed by
  **`r44/blind/polish.cpp` with LAMBDA = 1**.
- **What the polish does:** re-optimises the cipher alphabet by greedy pairwise swaps under quadgrams + word score.
  The plaintext alphabet is kept.
- **Development result:** on the first R44 holdout, now development data, 14/20 → **20/20 exact** at λ = 1 (λ = 0.5:
  18/20; λ = 2: 20/20).
- **The first holdout no longer counts for any gate.**

## Holdout B (`r44/sealed/make_holdout_b.py`)
- **Passages:** 20 new passages, none used before.
- **Keyword:** drawn uniformly from the solver's 5,000 candidate words (closed world).
- **Alphabets and key:** uniformly random cipher alphabet; uniformly random 5-digit Gromark primer.
- **Seeds:** 44300–44319.
- **Order:** generated only after this file is committed.

## Gate (fixed now)
- **Pass:** **at least 16/20 exact** 97/97 after the polish, with **0 invalid** forward witnesses.
- **Scoring:** `r43/sealed/evaluate.py`, only after the solver and polish outputs are frozen and committed.
- **Also reported:** the pre-polish solver result.
- **A pass shows only** that H-KW is blind-solvable with the key known. It does not authorise a K4 run; that needs
  its own pre-registration with a key search, a cost plan and nulls.
