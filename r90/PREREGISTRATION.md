# R90 pre-registration (Claude Code, 22 Nov 2026): the 15 F26L alphabet classes R89 left open (F26C): sealed gate, then K4 strict blind, then a post-freeze exact check

**Label: STRICT BLIND, gate first.**
- This round follows up ChatGPT's independent review of R89 (`r89/audit/REVIEW_20261121.md`, PR #100). That review
  verified R89's exclusions for R89's own catalog.
- It found that 15 of the 20 alphabet classes in ChatGPT's original design were never tested, and those stay open.
- It asked for the next round to pre-register five things, which this round does:
  - the actual catalog;
  - the final score;
  - the retention rule;
  - the key-equivalence definition;
  - an aggregate resource budget.

  It also uses fresh controls.
- R87–R89's isolation and freeze protocol applies.

**Approval:** Tyler, 22 Nov 2026: "Chat has done some work, take the next steps". The standing approval is "You can
merge code & do more in each run. Please try to get a legit solution for K4".

## G0. Hypothesis, catalog and equivalent old models
**Hypothesis (F26C).** K4 is ordinary English, enciphered by R89's F26 / F26L construction (`r90/f26c.py`; the
equations are identical to `r89/f26l.py`).
- **Inner stage:** the rows and columns of a 2 × 13 layout of alphabet A.
- **Blocks:** b = 5, 7, 9 or 11; the last block has 97 mod b letters.
- **Mixing:** output j takes the row of input (j + u) mod t and the column of input (j + v) mod t, with u ≠ v in
  1..b−1.
- **Outer stage (optional):** `C_i = KRY[KRY-place(M_i) + sign·KRY-place(U[(i + phase) mod |U|])]`, with U =
  PALIMPSEST or ABSCISSA, sign ±1 and every phase.

**Catalog (the actual list).**
- **15 alphabets**, each built as ChatGPT's kit built them: the keyword, then the rest of A–Z.
- **Keywords:** ORCHARD, MYSTERY, TRAVEL, MECHANIC, RIVER, PHILOSOPHY, HORIZON, GARDEN, SECRET, TEMPLE, MARKET, TUNNEL,
  LIBRARY, MIRROR, CIPHER.
- These are exactly the classes ChatGPT's `r89/audit/evidence/ALPHABET_SCOPE.json` lists as not covered.
- They are 15 distinct F26 classes, none among R89's 20 (tested).
- **Settings:** 15 alphabets × 188 (b, u, v) × (36 outer + none) = **104,340** fixed decryptions with no free key.
- **Not searched:** zero offsets, other block sizes and other outer keys.

**Key equivalence** (`f26c.same_key`). Two settings are the same key iff:
- their alphabets are in the same F26 class (same unordered row partition and same column pairs);
- and b, u, v and the outer stage are equal.

A block rotation (u − k, v − k) is a **different** key: it gives a different decode.

**Final score and retention rule.**
- **Stage 1:** every one of the 104,340 settings is scored by quadgrams.
- **Retention:** the **256** best, with ties broken by setting order, are scored by the R59 order-6 letter model.
- **Best:** the letter-model maximum over those 256.

Scoring all settings with the letter model would take about 340 s per ciphertext, so the retention is explicit and
its recall is gated (G1).

**Equivalent and overlapping old models.**
- **R89 (L178, independently verified):** the same construction over 20 other alphabet classes.
- **R82 (PR #77):** proposed 2×13 fractionation generally.
- **In-place exclusions (L03 etc.)** do not cover F26.

**Prior exposure (R53 rule 5).**
- The construction, the outer stage and these 15 keywords are ChatGPT's, fixed before R89.
- As R89 disclosed, the outer stage was chosen after seeing K4's flat IC.
- **R89's K4 results were known before this pre-registration.** They concern only other alphabets, and they changed
  nothing here.
- No published letter was used to choose anything.

**Cannot rule out:** other alphabets, block sizes, offsets or outer keys; other fractionation shapes; insertion or
deletion errors; transposition; masking; non-English plaintext.

## G1. Sealed gate (fresh, genre-balanced books; before anything touches K4)
**Books.** Fresh Project Gutenberg texts (GITenberg mirror), none named anywhere in the repository. Headers are
stripped (`--raw`).

| Role | Book | sha256 |
|---|---|---|
| G1 narrative | Dana, Two Years Before the Mast (#2055, `2055.txt`) | 6bf280ed9ed3667b84e12a225939635ab4d4c1f75bce9e2ae26e456dd9233833 |
| G2 formal historical | Thucydides, The History of the Peloponnesian War (#7142, `7142.txt`) | 8133508f58434f1235fa15025e99758a3f378c182ce90b38fbc680321947a199 |
| G3 technical | Faraday, Experimental Researches in Electricity vol. 1 (#14986, `14986.txt`) | 05f778fe9113897ff016812cb8fb9cbf64ede3c8ede3bb195b3170f7939f1967 |
| Running keys for the RUNKEY negatives | Smith, The Wealth of Nations (#3300, `3300-8.txt`) | a4c14c88e2ecbc107907712a42502b3815d3f6d93b3ff0dcf0eb2fc7a59e304a |

**Items.** `r90/sealed/make90.py G1,G2,G3 KEY 900500 r90/holdout --raw` gives **202** items.
- **48 F26C positives:** 4 block strata × 3 genres × 4, with 12 masked (C→K, W→V).
- **4 extras:** reported only.
- **150 negatives** from 11 generators, as listed in `make90.py`:
  - R89's six classical generators;
  - three near-family decoys: F26 with an unlisted alphabet, **R89's excluded catalog**, and R89's RCT;
  - 25 anagrams;
  - 8 random.

**Scoring.**
- A positive is **ok** if the best decode is from F26C, has the **right key** under the equivalence above, is
  ≥ 95/97 right, and is confident.
- *Confident* means letter model ≥ −1.30 and word model ≥ −2.50.
- A positive is **retained** if its true setting is among the 256 kept by stage 1.

**GO iff all of the following hold:**
- ok ≥ **42/48**;
- exact ≥ **36/48**;
- ≥ **9/12** per stratum;
- ≥ **12/16** per genre;
- ≥ **8/12** masked;
- **retained ≥ 46/48**;
- negatives confident ≤ **1/150**;
- the witness check passes.

These are ChatGPT's design bars, with its key requirement and its shortlist bar restored. On NO-GO: no K4 run and no
exclusion.

**Gate order:** pre-registration → QA manifest + `holdout/BLIND.tsv` + `holdout/TRUTH_SHA256` → blind run, witness,
determinism, `GATE_FROZEN.sha256` (pushed) → truth + `holdout/GATE.json`.

## G2. Development and checks done before this commit (spent books)
- **Development** (`r90/dev/DEV.md`; full gate size, seed 900300):
  - 48/48 ok with the right key, 48 exact, masked 12/12;
  - the true setting was **stage-1 rank 1 every time**;
  - 0/150 negatives confident (best −1.709);
  - nothing tuned.
- **Tests** (`r90/tests/test_r90.py`, all pass):
  - round trips and every final-block length;
  - the witness against the reference;
  - catalog distinctness against R89;
  - same-key semantics;
  - the exhaustive solver against the reference;
  - exact hit counts;
  - the one-ciphertext-error bound (≤ 2 letters);
  - witness failures;
  - the holdout maker;
  - the gate bars;
  - sandbox refusals.
- **Isolation:** 3 development items reproduce **byte for byte** in the sandbox.

## G3. K4 blind run (only after GO; each step a separate commit, pushed)
1. **Target.** `r90/sealed/prepare_k4.py` (R73's script, seed 900400) writes `r90/k4/TARGET.tsv`: K4 unchanged plus
   **200** frequency-preserving shuffles.
2. **Run.** The same sandbox and runner, started through **`audit/run_bounded_agg.py`** (aggregate budget below).
3. **Freeze.** Witness, determinism (first 8 ids), then `r90/k4/FROZEN.sha256`. Commit and **push**.
4. **Evaluation** (`evaluate90.py`).
5. **Exact check** (`exact90.py`).

## Decision rules (fixed now; R84/R87 rules)
"Best" is the letter-model maximum over the 256 retained settings, for K4 and every shuffle alike.

| Outcome | Condition |
|---|---|
| **CONFIDENT** | K4's best clears −1.30 / −2.50 **and** is above every one of the 200 shuffles' bests (p_family = 1/201) |
| **SIGNAL** | CONFIDENT and ≥ 10/24 published letters |
| **SCORE_ANOMALY** | CONFIDENT without that |
| **NO_SIGNAL** | Otherwise |
| **p_family** (reported) | (1 + shuffles with best ≥ K4's) / 201 |
| **Contender** (raw) | Any frozen K4 decode (top 5 and each sub-family's best) with ≥ 12/24 |

## G5. Post-freeze exact check (crib-assisted, exclusion-only)
`exact90.py` decodes the 24 published positions under **all 104,340 settings**, on K4 and the 200 shuffles.

| Screen | Feasible if | Covers |
|---|---|---|
| **EXACT** | 24/24 | all published letters right |
| **DROP-PT** | ≥ 23/24 | one wrong published plaintext letter |
| **DROP-CT** | ≥ 22/24 | the **necessary** screen for one wrong ciphertext letter, which can change two decoded letters (ChatGPT's correction C) |

- **EXCLUDED** if K4 has no setting at ≥ 22. That excludes the family under all three error models: none, one wrong
  plaintext letter, one wrong ciphertext substitution.
- **LEAD** if K4 has such a setting and no shuffle does. Otherwise **CHANCE**.
- K4's maximum is reported against the shuffles.

## What follows (fixed now)
| Result | Next |
|---|---|
| **SIGNAL** | Stop; report raw. R87's proof steps. **No external submission without Tyler's go** |
| **SCORE_ANOMALY or a contender** | Report raw; not a solution |
| **NO_SIGNAL with EXCLUDED** | Ledger: the F26C catalog EXCL (exact, crib-assisted), with blind STAT. Together with L178 this closes all 20 alphabet classes of ChatGPT's original F26L design, plus R89's 15 others, in the stated scope |
| **NO-GO** | SOLVER_NO_POWER; no K4 run |

**Prior expectation:** NO_SIGNAL and EXCLUDED.

## G4. Review
**Independent review: NONE** for this round, one model (Claude Code). ChatGPT's R89 review set its requirements.

## Budget (`QA_MANIFEST.json`; enforced by `audit/run_bounded_agg.py`)
- **Limits:** 2 h wall per run, **4 GB aggregate** resident memory over all workers, **28,800 s aggregate CPU**.
- **Candidates:** at most 1,407 kept K4 candidates (201 × 7: the top 5 plus the 2 sub-family bests). The retained-
  settings lists are 256 tags per ciphertext.
- **No retries.**
- **Expected:** under 30 s per run (development: 202 items in 12 s on 4 cores).
