# S2 pre-registration: stronger spelling-aware recovery, fresh hidden test, then K4 (Claude, 26 Oct 2026)

Written after development tuning on ChatGPT's R20 fixtures and **before** any search on the fresh test set or K4.

## Method S2 (frozen)
- `solver_s2.cpp` (sha256 recorded by `fresh_run.py`). Same cipher model and move set as ChatGPT's R7/R20 solver
  (two free alphabets, five-digit Gromark primer, anchors as exact crib-graph constraints).
- Word model: ChatGPT's spelling-aware `word_model_orth.tsv` (R20, sha256 `12392e2d…48676877`), unchanged.
- Objective while annealing: word score W + λ·Q, where Q is the letter-quadgram log10 sum
  (`/home/claude/kryptos/quad_log10.f32`), λ falling linearly from 0.05 to 0. Selection: highest W at λ = 0.
- Budget: **64 restarts × 40,000 proposals** per (ciphertext, primer), then a deterministic polish of every
  restart (all free-letter swaps and group shifts, repeated until no gain).
- Development evidence (R20's 16 fixtures, known primer; development only):
  - R20 as shipped: 3 exact, 5 readable (≤ 5 wrong letters).
  - S2 at 16 restarts: 3–4 exact, 5 readable.
  - S2 at 64 restarts: 6 exact, 10 readable.
  - S2 at 128 restarts: 8 exact, 12 readable.
  - 64 restarts was chosen for run time; quadgram guidance made little difference at 128 restarts.

## Fresh test set (fixed before running)
- **Passages:** 20 newly written everyday passages (`fresh/passages.txt`, sha256 `cc4c6ec1…789c015331`), built
  around the two clues; no templates and no spy themes.
- **Arms:**
  - **0:** no spelling changes.
  - **K:** two changes from rules the spelling dictionary covers, including paired −1/+1 changes. Six passages had
    no two eligible words, so arm K has 14 fixtures.
  - **U:** two same-length changes from held-out rules the dictionary does not cover: O→U and E→A (the K1–K3
    UNDERGRUUND/DESPARATLY pattern), initial W→V, and soft C→S.
- **Fixtures:** 54 in total, each with fresh random alphabets and a random primer. Candidates are the true primer
  plus up to 19 wrong anchor-feasible primers, shuffled. That gives 910 solver lines (`fresh/public_fresh.txt`, sha256
  `a0a2f27b…a83ae8fd12c8b771ff2fa0d77733199fe16cc2`).
- **Blindness:** the answers (`fresh/PRIVATE_fresh.json`, sha256 `f76185e6…bbba53`) are read only by `fresh_run.py eval`.
- **Comparators on the same lines:** ChatGPT's solver as shipped (16 × 40,000), with the V4 dictionary and with the
  orth dictionary.

## Outcomes
- **Primary, per method and arm: blind readable recovery.** The true primer must give the highest score among
  the candidates, and that output must have at most 5 wrong letters.
- **Secondary:**
  - exact recoveries;
  - known-primer readable recovery;
  - discrimination: margin of the true primer over the best wrong primer, and the distribution of best
    wrong-primer scores.

## Gate for K4 (decided now)
- **Adopt S2 for K4** only if its blind readable recovery is **≥ 50% in arm 0 and ≥ 50% in arm K**.
- **If adopted:** run S2 unchanged on K4's 39 anchor-feasible primers.
- **K4 is a candidate** only if its best score **exceeds every best wrong-primer score** in the S2 fresh run.
  Its text must then be shown to Tyler before anyone treats it as more than a score.
- **Otherwise:** report "no Gromark candidate in spelling-aware English", qualified by the measured recovery rate.
  That is not an exclusion of Gromark or of the spelling hypothesis.
- **If the gate fails:** no K4 run.
- **No Paradigm submission in any case** (Tyler's decision).

## Amendment (26 Oct, before any result was evaluated)
- 7 of the 910 candidate lines are wrong primers that pass the per-component check in `gromark.feasible` but have no
  valid joint placement of the anchor components, so no alphabet pair exists for them. Both solvers stop with an
  error on such a line. The S2 run stopped on one.
- `gromark.full_feasible` (complete check; K4 still has exactly 39) removes them. The remaining 903 lines are in
  `fresh/public_fresh_feasible.txt`.
- The 101 lines S2 had fully completed are kept, since each line has its own seed and runs independently. The other
  802 are run as `in_c`/`in_d`. Nothing else changes.
