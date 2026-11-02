# R59 pre-registration (Claude Code, 2 Nov 2026): is K4's frequency-flattening layer a running key from an unknown English text?

Written before the holdout plants are generated and before any K4 run. Follows `r53/BLIND_RULES.md`:
- the solver never sees K4's published letters or their positions;
- full outputs are frozen and pushed before any comparison;
- a separate program does the comparison.

## Why this hypothesis
- **The working linguistic hypothesis (Tyler, 2 Nov 2026):** K4's plaintext is ordinary readable English (a covertext
  that may carry a second meaning). This replaces the earlier Dutch/German-spelling idea.
- **What the letter frequencies require.** Plain English that is only substituted and rearranged keeps English letter
  statistics. K4 is far flatter than that:
  - its IC is 0.0361;
  - the lowest IC among 1,009 K1–K3 plaintext windows is 0.053 (R54);
  - 0 of 300,000 simulated English-frequency samples are as flat (Tyler's check).

  So some frequency-changing step is needed. Scheidt (WIRED, 2005) said K4 conceals English statistics.
- **A running key is the simplest such step and fits K4.**
  - **Method:** a Vigenère-type tableau whose key is a long English text.
  - **Fit:** in development, 40,000 simulated 97-letter running-key ciphertexts per convention had mean IC 0.0397; 12–13%
    were as flat as K4 or flatter.
  - **Kryptos precedent:** K1/K2 used a keyed tableau, and K3 quoted a book.
- **What is already ruled out:** only specific key texts have been tested. With fixed alphabets, K1–K3 and the full
  Carter & Mace 1923 vol. I were excluded (L109, L111; with two free alphabets, L90/L106).
  - An unknown English key text has only been looked at statistically, with low power (L31, STAT).
  - It has never been searched blind.

## Hypothesis H-RK (exactly what is tested)
- **Placement:** in place, with no transposition and no nulls.
- **Convention:** one of 4, up to symmetry. The alphabet X is AZ or KRY (`KRYPTOSABCDEFGHIJLMNQUVWXZ`), and indices are
  taken in X, as in K1/K2:

  | Convention | Formula |
  |---|---|
  | VIG | c = X[x(p) + x(k)] |
  | BEAU | c = X[x(k) − x(p)] |
  | VARB | c = X[x(p) − x(k)] |

  - VARB is BEAU with p and k swapped.
  - VIG is symmetric in p and k, so the plaintext and the key cannot be told apart by the cipher alone.
- **Texts:** the plaintext p and the key k are both ordinary English, letters only. The key may start anywhere in its
  source text.

## Blind solver (frozen: `r59/blind/rk_solve.cpp`, run only via `r59/blind/run.py`)
1. **Beam search** over positions, beam 100,000. Each hypothesis is a pair (p, k), with k forced by p and c. The score
   is LM(p) + LM(k).
   - **LM:** a generic order-6 letter model with interpolated Kneser–Ney smoothing (`r59/blind/lm_build.cpp`).
   - **Training text:** 23,373,368 letters. 14 public-domain novels, Carter & Mace 1923 vol. I, and NLTK's Brown,
     webtext, inaugural, state_union and gutenberg corpora (four duplicate books skipped).
   - **Reproducibility:** pinned by sha256 in `r59/corpus/build_corpus.py`. Model sha256 in `r59/blind/LM_SHA256`.
   - **States:** states with the same last 5 letters in both texts are merged.
2. **Rescore** the top 2,000 pairs by F = LM(p) + LM(k) + W(p) + W(k). W is the best segmentation into dictionary words
   from `k4kit/data/word_model_orth.tsv`, with −7 per unmatched letter; a word fragment is allowed at each end.
3. **Polish** the best 3 pairs per convention by greedy ascent of F, with three kinds of move:
   - change one letter;
   - (VIG only) swap the two texts from a point to the end;
   - place a dictionary word (top 20,000 words of length 4–12) in either text, with the other text forced.
4. **Choose** the best F over the 4 conventions. The output records both texts, the convention, the scores and the
   alternatives. Every output re-encrypts exactly (checked in the solver, the gate and the reveal).
- **Parameters** (`run.py`): BEAM 100000, TOPN 2000, LAMBDA 1, conventions AZ_VIG/AZ_BEAU/KRY_VIG/KRY_BEAU, POLISH_M 3,
  POLISH_WORDS 20000.
- **No tuning after this file is committed.**

## Corpus roles (non-overlapping; `r59/corpus/build_corpus.py`)
| Role | Source |
|---|---|
| Language model | the training text above |
| Development | plaintext from *Tom Sawyer*; keys from *The Picture of Dorian Gray* |
| **Holdout** (unseen until generation) | plaintext from *The War of the Worlds* and *Treasure Island*; keys from *Heart of Darkness* and *The Time Machine* |

## Development record (development data only; K4 never run)
| Version | Result on 12 development plants (`r59/sealed/make_plants.py`, seed 59001) |
|---|---|
| 5-gram LM, beam 100k, no polish | median 49 letters wrong; convention identified 11/12 |
| Same with beam 500k | identical on 4 plants: search is not the bottleneck |
| 5-gram LM | at its unicity limit: about 2.5 bits/letter held-out, × 2 texts ≈ log2 26 |
| 6-gram LM, larger corpus | 2.37 / 2.31 bits/letter held-out (development texts) |
| + rescoring and polish (this solver) | convention 12/12; median pair-correct 70/97; pair-correct ≥ 60 in 9/12; best 87/97; 0 exact |
| 12 shuffled-plant nulls | best totals −336 to −318; plants −319 to −269; 11/12 plants above every null |

**Lessons:**
- **Readable-looking output is not evidence.** On shuffled letters the solver also produces word salad in both texts.
  Only the score against nulls counts, and agreement with the published letters only after the freeze.
- **VIG lets the two texts cross.** Reading order is lost at crossings, so the recovery measure counts correct letter
  pairs.

## Holdout gate (fixed now)
- **Plants:** 20, generated by `r59/sealed/make_plants.py hold_pt.txt hold_key.txt 20 59100 HOLD OUTDIR` only after
  this file is pushed.
- **Nulls:** one frequency-preserving shuffle of each plant, by `r59/sealed/make_nulls.py BLIND.tsv 59101`.
- **Runs:** both through `run.py`, each frozen and pushed before `r59/sealed/gate.py` runs.
- **Pass (all of):**
  - **detected ≥ 16/20:** the plant's best total exceeds the maximum over all 20 nulls;
  - **convention identified ≥ 16/20;**
  - **pair-correct ≥ 60/97 in ≥ 12/20;**
  - **0 invalid re-encryption witnesses.**
- **If it fails:** record it as negative evidence for the solver, and do **not** run K4.

## K4 test (only if the gate passes)
- **Input:** `r59/sealed/prepare_k4.py`. It reads only `r39/ic_gate/k4_ciphertext.txt` (sha256 `2797de14…0f0a5a3`,
  with newline) and writes K4 plus 100 frequency-preserving shuffles (seed 590070).
- **Run and freeze:** the same `run.py`. Freeze and push before `r59/sealed/reveal_k4.py` runs. The reveal is the only
  R59 code holding the published letters.
- **Decision, fixed now (s = K4's best total; r = number of nulls with a total ≥ s):**

  | Outcome | Condition |
  |---|---|
  | **RUNNING-KEY SIGNAL** | r = 0 (empirical p ≤ 1/101) **and** K4's frozen best output matches the published letters at ≥ 10 of 24 positions in one of its two texts |
  | **Score anomaly, no letter support** | r = 0 but fewer than 10/24. STAT; not a candidate; report and investigate |
  | **NO SIGNAL** | r ≥ 1 |

  - **Expected matches:** a true running key recovered at the holdout's typical accuracy (~70%) would give about 17/24
    matches; chance gives about 1.
  - **NO SIGNAL** is evidence against H-RK as tested, with power equal to the holdout detection rate. It excludes
    nothing outside H-RK: transposition, other tableaux, non-English keys, or masking.
- **A RUNNING-KEY SIGNAL is still not a solution.** It would also need:
  - coherent English in the raw text (reported unedited);
  - exact re-encryption;
  - an attempt to identify the key text;
  - Tyler's decision before anything is sent anywhere.
- No external checker is used.

## Second question: a hidden meaning
`r59/SECOND_MEANING_PROTOCOL.md` is pre-registered with this file. It applies only once some blind round yields
readable plaintext. R59 does not test it.
