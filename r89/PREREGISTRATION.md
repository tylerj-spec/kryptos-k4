# R89 pre-registration (Claude Code, 21 Nov 2026): ChatGPT's two R89 arms, built and reviewed independently: F26L (2×13 fractionation + K1/K2 tableau) and RCT (ciphertext-stepped rotor): sealed gate per arm, then K4 strict blind through the passing arms only, then post-freeze exact checks

**Label: STRICT BLIND, gate first, per arm.**
- R87/R88's isolation and freeze protocol applies.
- ChatGPT's design (PR #98, `docs/R89_EXECUTABLE_BOUNDS_V2.md`) is adopted with the changes set out in my independent
  review (`r89/REVIEW_PR98.md`).
- The published letters are read only by `r89/sealed/evaluate89.py` and then `r89/sealed/exact89.py`. Both run after
  the frozen K4 outputs and their independent witness check are committed **and pushed**.

**Approval.**
- Tyler, 21 Nov 2026, relaying ChatGPT's R89 recommendation: "Make the changes for the next experiment".
- The recommendation was to have a separate model review F26L first and then run its fresh gate, with RCT through the
  same process.
- The standing approval is "You can merge code & do more in each run. Please try to get a legit solution for K4".

## G0. Hypotheses, scope and equivalent old models
**Arm F26L** (`r89/f26l.py`).
- **Inner stage, F26:** a keyed alphabet A gives each letter a row (place // 13) and a column (place % 13). In blocks
  of b letters (b 5, 7, 9, 11; the last block has 97 mod b letters), output j takes the row of input (j + u) mod t
  and the column of input (j + v) mod t, with u ≠ v in 1..b−1.
- **Outer stage:** `C_i = KRY[KRY-place(M_i) + sign·KRY-place(U[(i + phase) mod |U|])]`, with U = PALIMPSEST or
  ABSCISSA, sign ±1 and every phase.
- **Scope:** 20 alphabets, 188 (b, u, v) and 36 outer options give **135,360 F26L settings**. A further **3,760 bare
  F26** settings without the outer stage are decoded and reported as a sub-family. Together: 139,120 fixed decryptions,
  **all enumerated**.
- **The 20 alphabets:**
  - **plain and orderings:** AZ, QWERTY, ALT (alternate letters);
  - **K1–K3 keys:** KRYPTOS, PALIMPSEST, ABSCISSA;
  - **K1–K3 plaintext words:** NUANCE, MAGNETIC, PASSAGE, CANDLE, SHADING, IQLUSION, UNDERGRUUND, DESPARATLY,
    LAYERTWO, INVISIBLE;
  - **names:** SANBORN, SCHEIDT, LANGLEY, WEBSTER.

  They fall into 20 distinct F26 equivalence classes (tested). No published K4 word is used.

**Arm RCT** (`r89/rct.py`).
- Offsets start at s_0 = 0. Encryption: `E_out-place(c_i) + s_i = W[E_in-place(p_i) + s_i]`.
- Step: `s_{i+1} = s_i + d·(1 + [(AZ(c_i) + q) mod m = 0])`.
- **Scope:** W any of 26!; contact numberings AZ/KRY/PAL/ABS on each side (16 pairs); 28 schedules (d ±1, m 2–5,
  q 0..m−1). In all, **448 settings**, searched heuristically (R87's kernel and schedule).
- With AZ/AZ this is the design's `c_i = W[(p_i + s_i)] − s_i`.

**Equivalent and overlapping old models.**
- **F26L:** F26 mixes letters within blocks, so it is not in place. None of the in-place exact exclusions (L03 etc.)
  covers it.
- **Square ciphers:** L88's 5×5 squares (Bifid, Playfair) cannot produce 26 letters. 2×13 fractionation has not been
  tested before.
- **RCT:** a restricted case of R77's H8, which was proposed and never run. It is not R87 (regular stepping, L176),
  nor L17 (a one-sided free alphabet with a ciphertext autokey).

**Prior exposure (R53 rule 5).**
- Both arms, their parameter ranges and the gate bars come from ChatGPT's design, written before any R89 code here.
- As that design states, **the outer tableau of F26L was added after seeing that bare F26 cannot reproduce K4's flat
  ciphertext IC.** That is post-hoc mechanism selection on ciphertext-only evidence. It makes a match on IC
  descriptive, not confirmatory.
- No R89 arm has been run on K4 by anyone, and no published letter was used to choose anything.

**Cannot rule out:**
- other fractionation shapes, alphabets or block sizes;
- other outer keys;
- RCT with other trigger rules, other step sizes, or more than one rotor;
- transposition;
- masking;
- non-English plaintext.

A blind NO_SIGNAL is statistical. The exact checks can exclude settings, but only under their stated assumptions.

## G1. Sealed gate (fresh, genre-balanced books; run before anything touches K4)
**Books.** Fresh Project Gutenberg texts (GITenberg mirror). None of these titles appears anywhere in the repository
(`r89/REVIEW_PR98.md` §5). Headers and licences are stripped (`--raw`).

| Role | Book | sha256 of the file |
|---|---|---|
| G1 narrative | Narrative of the Life of Frederick Douglass (#23, `23.txt`) | 948d491964b6ac66df3966476b2a9305b5d7ea56b8ec0b78c3c56815c5d9605f |
| G2 formal historical | Gibbon, Decline and Fall vol. 2 (#732, `732.txt`) | 7e8c1965a8d0053a12e37f2cea3211973d1a225726c9d7660424d83b43323c61 |
| G3 technical | The Radio Amateur's Hand Book, 1922 (#6934, `6934.txt`) | b388b7d76228dc07efe30aca5b9f5be568dbdb3a3eadb6706a4b19303958cd66 |
| Running keys for the RUNKEY negatives | The Federalist Papers (#1404, `1404.txt`) | 64dd04d805964a7c8f946072fcc8ba11d01613c8e6faf908511a28930dcb28e1 |

**Items.** `r89/sealed/make89.py G1,G2,G3 KEY 890500 r89/holdout --raw` gives **255** items, with shuffled ids.
- **Positives:** 48 per arm. Each arm has 4 parameter strata × 3 genres × 4; the first item of every cell is masked
  (C→K, W→V), giving 12 masked per arm.
- **Extras:** 9, reported and never gated.
- **Negatives:** 150 shared. The generators and counts are in `make89.py`:
  - RX, RQ, PERIODIC, RUNKEY, SUBTRANS, PTAK: 15 each;
  - the near-family decoys F26X and RCTX: 15 each;
  - English anagrams: 25;
  - random letters: 5.
- **Every ciphertext goes through both arms with the same effort.**

**Scoring.**
- *Best* is the decode with the highest letter-model score over both arms and all their settings.
- A positive of arm X is **ok** if the best decode is from arm X, is ≥ 95/97 right and is confident.
- *Confident* means letter model ≥ −1.30 and word model ≥ −2.50 per letter.
- **ABSTAIN** = not confident.

**Arm X is GO iff all of the following hold** (ChatGPT's bars):
- ok ≥ **42/48**;
- exact ≥ **36/48**;
- ≥ **9/12** in every parameter stratum;
- ≥ **12/16** in every genre;
- ≥ **8/12** masked;
- the shared negatives are confident in ≤ **1/150**;
- the witness check passes.

The design's F26 shortlist bar is dropped, because F26L is enumerated in full (review §1).

**An arm that fails is retired.** No K4 run goes through it and there is no repair. If both fail: no K4 and no
exclusion (SOLVER_NO_POWER).

**Gate order** (each step a separate commit, pushed):
1. This pre-registration and `PROTOCOL.sha256`.
2. `QA_MANIFEST.json`, `holdout/BLIND.tsv` and `holdout/TRUTH_SHA256` (only the hash).
3. Blind run with both arms, witness, determinism and `GATE_FROZEN.sha256`.
4. Truth file and `holdout/GATE.json`, with each arm's verdict.

## G2. Development and checks done before this commit (synthetic only, spent books)
**Development** (`r89/dev/DEV.md`; full gate size, seed 890300):

| Arm | ok | Exact | Masked | Strata / genres |
|---|---|---|---|---|
| F26L | **48/48** | 48 | 12/12 | all at 12/12 and 16/16 |
| RCT | **45/48** | 44 | 10/12 | lowest stratum 10/12, every genre 15/16 |

- **Negatives:** 0/150 confident. The best is an anagram at −1.337.
- **RCT ciphertext errors:** one propagated completely (7/97). This is the designed propagation, reported.
- **No parameter was tuned** on the development run.

**Checks:**
- **Tests** (`r89/tests/test_r89.py`, all pass):
  - 3,000 round trips per family;
  - the K1/K2 openings;
  - every final-block length;
  - the witness against the references;
  - 20 distinct alphabet classes;
  - the exhaustive solver against the reference;
  - the RCT kernel frame;
  - three-way exact-check agreement;
  - error propagation;
  - witness failures;
  - the holdout maker;
  - the per-arm gate bars;
  - sandbox refusals.
- **Isolation:** 2 development items reproduce **byte for byte** in the sandbox.
- **Letter model:** sha256 b1a2a3c7…
- **Compile race:** none. The kernel is built once, before the workers fork.

## G3. K4 blind run (only for arms that are GO; each step a separate commit, pushed)
1. **Target.** `r89/sealed/prepare_k4.py` (R73's script, seed 890400) writes `r89/k4/TARGET.tsv`: K4 unchanged plus
   **200** frequency-preserving shuffles.
2. **Run.** The same sandbox and runner, with **ARMS = the GO arms only** (4 processes), started through
   `audit/run_bounded.py`.
3. **Freeze.** The witness, determinism (first 8 ids) and kernel checks run first. Then `r89/k4/FROZEN.sha256`.
   Commit and **push**.
4. **Evaluation** (`evaluate89.py`; rules below).
5. **Exact checks** (`exact89.py`, G5), for the GO arms only.

No tuning, re-running, re-ranking or filtering of blind outputs after the evaluation.

## Decision rules (fixed now; R84/R87 rules over the GO arms)
"Best" is the maximum letter-model score over every GO arm and setting, for K4 and every shuffle alike.

| Outcome | Condition |
|---|---|
| **CONFIDENT** | K4's best has letter model ≥ −1.30 and word model ≥ −2.50, **and** is above every one of the 200 shuffles' bests (so p_family = 1/201 ≤ 0.01, the design's anomaly level) |
| **SIGNAL** | CONFIDENT and ≥ 10/24 published letters |
| **SCORE_ANOMALY** | CONFIDENT without that |
| **NO_SIGNAL** | Otherwise |
| **p_family** (reported) | (1 + shuffles with best ≥ K4's) / 201 |
| **Contender** (raw; not a solution) | Any frozen K4 decode (top 5 and each sub-family's best) with ≥ 12/24 |

## G5. Post-freeze exact checks (crib-assisted, exclusion-only; GO arms only)
**F26 / F26L.** Decode the 24 published positions under all 139,120 settings, on K4 and the 200 shuffles.
- **EXACT EXCLUDED** if no setting gives 24/24.
- **DROP EXCLUDED** if none gives ≥ 23/24. This covers one wrong published letter, or one wrong ciphertext letter
  feeding a published position.
- **LEAD** if K4 has such a setting and no shuffle does. Otherwise **CHANCE**.
- The maximum match count is reported for K4 against the shuffles.

**RCT.** For each of the 448 settings, test whether the 24 (input, output) contact pairs form a partial bijection.
- **EXACT EXCLUDED** if K4 has no feasible setting.
- **DROP:** each published letter set aside in turn. This covers one wrong published plaintext letter. A wrong
  ciphertext letter also shifts later offsets and is not covered.
- **LEAD** if K4 has a feasible setting with ≥ 3 checks that no shuffle reaches. Otherwise **CHANCE**.

The exact checks decrypt nothing beyond the published positions and never set a blind scope.

## What follows (fixed now)
| Result | Next |
|---|---|
| **SIGNAL** | Stop; report raw. R87's proof steps. **No external submission without Tyler's go** |
| **SCORE_ANOMALY or a contender** | Report raw; not a solution |
| **NO_SIGNAL with EXACT EXCLUDED** | Ledger: that arm EXCL (exact, crib-assisted) in scope, with blind STAT confirmation |
| **A failed arm** | SOLVER_NO_POWER; retired; no K4 run through it |

**Prior expectation:**
- NO_SIGNAL.
- F26L excluded exactly: a finite family with 139,120 decryptions, against 24 constraints.
- RCT excluded exactly.

## G4. Review
- **The design** (ChatGPT) has now been reviewed by a different model (Claude Code): `r89/REVIEW_PR98.md`.
- **The implementation and this round** were built and run by one model (Claude Code). **Independent review of R89's
  execution: NONE.** No `Promotes:` line.

## Budget (`QA_MANIFEST.json`)
- **Gate:** about 13 min (255 items; development took 749 s on 4 cores).
- **K4 + 200 shuffles:** about 10 min.
- **Limits:** 2 h and 4 GB per run. At most 2,010 kept K4 candidates (201 × (5 + 3)). No retries.

## Disclosures
- **Kernel:** R87's pinned `r87/blind/anneal.c`, compiled with `-march=native`.
- **Scorers:** the word model and letter model are R87's.
- **G3 genre:** the design's "modern news/technical" genre is represented by a 1922 technical manual. This mirror has
  no public-domain modern news.
