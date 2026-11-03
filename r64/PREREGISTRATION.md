# R64 pre-registration (Claude Code, 3 Nov 2026): World Clock or German running key, THEN a transposition

Written before the holdout plants are generated and before any K4 run. Follows `r53/BLIND_RULES.md` as clarified by
Tyler (R63 Amendment 2): clue-motivated hypotheses are fine; the **algorithm reads only the ciphertext and generic
models**, and the published letters are used only as a check after everything is frozen and pushed.

Built from ChatGPT's research (PR #46, `research/k4_2026-11-03/`, priority A1) and its R64 proposal (PR #45,
`r64/PROPOSED_PROTOCOL.md`). Their requests and how R64 meets them are listed at the end.

## Why
- **R61 (L150):** English running key, then one of 10 transpositions. No signal.
- **R63 (L152):** World Clock or German running key, in place. No signal, with 10/10 power for each.
- **Their combination was never tested.** If Sanborn took a Berlin-clock or German key and then transposed the result
  as in K3, R61 and R63 would both miss it.

## Hypothesis H-NEKT (exactly what is tested)
- **Plaintext:** ordinary English, P.
- **Key:** K from R63's frozen CLOCK model (any sequence of the 107 World Clock city names) or GERMAN model (German
  prose), `r63/blind/MODELS.sha256`.
- **Substitution:** X[i] = S(P[i], K[i]) under one of 6 conventions: AZ or KRYPTOS alphabet × VIG / BEAU / VARB.
- **Transposition:** CT[j] = X[perm[j]] for one of the **10 frozen R61 routes** in `r61/routes.txt` (K3's four 24×8
  rotations; the six 4+31+31+31 engraving-site routes), unchanged.
- **All 10 routes are searched symmetrically.** The R61/R62C COL_LT oddity is not given any extra weight.

## Blind pipeline (frozen: `r64/blind/run.py`)
- **Solver:** the R63 two-model solver `r63/blind/rk2_solve.cpp`, unchanged (binary sha256 f171dbe5…), with the R59
  English model (`r59/blind/LM_SHA256`).
- **For each ciphertext and each key model m (CLOCK, GERMAN) separately:**
  1. undo all 10 routes;
  2. **stage 1:** solve each un-routed text **without polish**: beam B1 = 15,000, TOPN 2000, LAMBDA 1, all 6
     conventions, POLISH_M 0;
  3. **stage 2:** the 2 best routes by stage-1 total (ties: lower route index) are re-solved with the **unchanged R63
     parameters** (beam 50,000, TOPN 2000, LAMBDA 1, all, POLISH_M 2, POLISH_WORDS 20000);
  4. **answer for m:** the best stage-2 total (ties: lower route index), with route, convention and both texts in
     plaintext order.
- **Raw evidence kept:** every solver output of both stages (10 + 2 route rows, each with the best, the 6
  per-convention bests and the top 8) in `work/`, hashed in `WORK.sha256`. Code, models, input and results are hashed
  in `FROZEN.sha256`.
- **Cache:** a finished (ciphertext, model) job is reused after an interruption only if its digest matches the
  ciphertext, model, every model-file hash, the routes hash, the solver-binary hash and the parameters.
- **No tuning after this file is committed.**

DEVELOPMENT_RECORD_PLACEHOLDER

## Holdout gate (fixed now)
- **Fresh sources, never used by R59–R63** (`r64/corpus/build_sources.py`, sha256-pinned GITenberg files):
  - **plaintext:** *The Call of the Wild* + *The Hound of the Baskervilles*. Ordinary English windows; nothing is
    written around K4's published phrases.
  - **German literary key:** Thomas Mann, *Der Tod in Venedig* (1912; pre-1996 spelling).
  - **German Europarl key:** Europarl file 10, R63's unseen holdout file.
  - **Clock keys:** random name sequences (as R63) and walks around the clock ring (`r64/data/clock_ring.txt`).
- **Plants:** 24, generated only after this file is pushed:
  `r64/sealed/make_plants.py hold_pt.txt de_hold.txt de_lit_hold.txt 24 64100 HOLD OUTDIR`.
  - 6 plants of each key kind (CLOCK_RAND, CLOCK_RING, GERMAN_EP, GERMAN_LIT);
  - convention and route uniform at random; truth sealed.
- **Nulls:** 24 frequency-preserving shuffles of the plants, `r63/sealed/make_nulls.py BLIND.tsv 64101`.
- **Run:** plants and nulls in one blind run, frozen and pushed, then `r64/sealed/verify.py`, then the sealed
  `r64/sealed/gate.py`.
- **Pass (all of):** GATE_BARS_PLACEHOLDER
- **Reported, not gated:** route identified, true route kept after stage 1, convention, and every count per key kind.
  A key kind with fewer than half its plants detected is flagged **low power**. A K4 negative for that kind is then
  reported as **WEAK**, not as evidence against it.
- **If the gate fails:** record **INCONCLUSIVE** and do not run K4.

## K4 test (only if the gate passes)
- **Input:** `r64/sealed/prepare_k4.py` writes the unchanged K4 (sha256 2797de14… including the newline) plus 100
  frequency-preserving shuffles (seed 640070). It reads only the ciphertext file.
- **Order:**
  1. one blind run;
  2. freeze and push;
  3. `r64/sealed/verify.py`, which re-encrypts every saved witness through its route; commit and push;
  4. only then `r64/sealed/reveal_k4.py`, the only R64 code holding the published letters.
- **Positions:** in this model the published positions are **plaintext** positions. They are compared with the frozen
  plaintext-order output.
- **Decision, per key model m:**

  | Outcome | Condition |
  |---|---|
  | **SIGNAL (m)** | K4's model-m total exceeds all 100 nulls' model-m totals **and** K4's frozen plaintext matches ≥ 10/24 published letters |
  | **Score anomaly (m)** | the first condition without the second (STAT; not a candidate) |
  | **NO SIGNAL (m)** | otherwise |

  - The nulls go through the same 10-route, 6-convention search, so the cost of searching many routes is already
    inside the null distribution.
  - Two models are tested, so a chance "above all nulls" under one of them has probability of about 2/101. The letter
    requirement guards against that.
- **Secondary (exploratory, labelled so):** the best published-letter match over **all** frozen raw alternatives of K4,
  with the same number for every null.
- **Any SIGNAL** is reported raw. It is not a solution until the full text reads as coherent new English, the key is
  explained, and the result is independently re-derived. No external checker is used without Tyler's go-ahead.

## What a negative would and would not mean
- **Would argue against (STAT, where power is shown):** K4 = ordinary English, running key from R63's CLOCK model or
  German prose, any of the 6 conventions, then one of these 10 routes.
- **Would not exclude:**
  - transposition first, then substitution;
  - clock hour or UTC-offset keys, or the exact 1989 inscription order (still unverified; see the research dossier);
  - other routes;
  - free alphabets;
  - masking or phonetic spelling of the plaintext;
  - a non-English plaintext;
  - a true one-time pad.

## ChatGPT's R64 requests (PR #45) and where they are met
| Request | R64 |
|---|---|
| R61's 10 routes, unmodified, each checked as a permutation; undo before the unchanged R63 solver | `run.py` `load_routes`, `unroute`; contract test |
| Low-budget stage 1 over all 10 routes, full R63 parameters on the best 2 per model; budget fixed from development, not K4 | B1 = 15,000, chosen above from development plants only |
| CLOCK and GERMAN kept separate; stage-2 score is the model total only | yes |
| Keep every raw witness; reject a stale cache | `work/` + `WORK.sha256`; cache digest |
| Independent post-freeze verifier, separate from the generator and the evaluator | `r64/sealed/verify.py` (pure Python) |
| Fresh English controls with no K4 phrases | *Call of the Wild*, *Hound of the Baskervilles* |
| Out-of-distribution controls: clock ring walk; unseen-genre German | CLOCK_RING; Mann (holdout) and Kafka (development), old spelling |
| Report detection, route kept, convention, letters recovered, witnesses; weak power means INCONCLUSIVE | `gate.py` |
| K4 + ≥ 100 new shuffles; freeze and push before any published letter | seed 640070; order above |
| Decision rule fixed in advance and calibrated on nulls that ran the same search | above |
