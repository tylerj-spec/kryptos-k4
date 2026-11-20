# R88 pre-registration (Claude Code, 20 Nov 2026): stepped progressive Quagmire with one free alphabet (RQ): sealed gate, then K4 strict blind, then a post-freeze exact check

**Label: STRICT BLIND, gate first.** R87's protocol and controls, unchanged except where stated.
- The blind solver runs in an isolated sandbox. It sees only an input TSV, the generic English scorers and the family
  code, with no network and no repository.
- Nothing about K4 is run until the sealed gate says GO.
- The published letters are read only by `r88/sealed/evaluate88.py` and then `r88/sealed/exact88.py`. Both run after
  the frozen K4 outputs and their independent witness check are committed **and pushed**.

**Approval.**
- R87's pre-registration and result named RQ as the next family, after RX was excluded.
- On 20 Nov, after that result, Tyler said: "Send it".
- The standing approval is "You can merge code & do more in each run. Please try to get a legit solution for K4".

## G0. Hypothesis, scope and equivalent old models
**Hypothesis (family RQ, `r85/DESIGN.md` §5 item 2).** K4 is ordinary English, enciphered in place with one fixed
alphabet A, one **free** alphabet W, and a key that advances d places every n letters: s_i = d·⌊i/n⌋, with i counted
from 0.
- A is one of AZ, KRYPTOS, PALIMPSEST, ABSCISSA (keyword first, then the rest of A–Z).
- W is any of the 26! permutations.

| Side | Free alphabet | Encryption |
|---|---|---|
| **PA** | the plaintext alphabet | `A-place(c_i) = W[p_i] + s_i` (mod 26) |
| **CA** | the cipher alphabet | `c_i = W[A-place(p_i) + s_i]` (mod 26) |

- Reference code: `r88/rq88.py`. Independent encipherer: `r88/sealed/witness88.py`, standard library only.

**Scope.**
| Step | Settings | Each with |
|---|---|---|
| Blind search | 2 sides × 4 alphabets × d ±1 × n 1–32 = **512** | a free alphabet, searched heuristically |
| Post-freeze exact check | 2 × 4 × step δ 1–25 × n 1–96 = **19,200** | every free alphabet, decided exactly |

- In the exact step, δ 25 is the blind step's d = −1.
- n ≥ 97 is a single alphabet, which L02 excludes.

**Equivalent and overlapping old models.**
- **R40 (L134, PA free) and R42 (L136, CA free)** are the same one-free-alphabet construction with chain-addition and
  running keys. They were replayed exactly in T6 (#96). RQ replaces those keys with a stepped progressive key.
- **L16** lists "free-alphabet keystreams … affine progressive" as EXCL, which overlaps n = 1. Its code is not in the
  repository (`audit/historical/SOURCE_MAP.md`: NOT FOUND), so R88 also gives that case its first reproducible check.
- **L13 and L49** cover progressive keys with fixed alphabets only.
- **R87 (L176)** covers the rotor, where the shift acts on both sides of a free wiring. In RQ the shift acts on one
  side only. A single rotor is included as a negative generator here.

**Prior exposure (R53 rule 5).**
- The family was named in `r85/DESIGN.md` (17 Nov) and in R87's "What follows" (20 Nov), before any RQ result on K4
  existed.
- The scope bounds and solver parameters are R87's, which were fixed on spent books. R87's K4 outcome (NO_SIGNAL; RX
  exact EXCL) was known. It changed nothing here except that RX became a negative generator.
- No RQ check has been run on K4 by anyone in this project.

**Cannot rule out:**
- keys other than a stepped progression: irregular steps, or a periodic keyword plus a progression;
- two free alphabets;
- other fixed numberings, such as R40/R42's seven alphabets, which include the ACA and prefix forms;
- n 33–96 in the blind step (the exact step covers them);
- transposition;
- masking;
- non-English plaintext.

A blind NO_SIGNAL is statistical. The exact step can exclude settings, but only under its stated assumptions.

## G1. Sealed gate (fresh books; run before anything touches K4)
**Books.** Fresh Project Gutenberg texts, downloaded 20 Nov from the GITenberg mirror. None of these titles appears
anywhere in the repository: not in the letter-model corpus, the development books, or any earlier holdout, R87's
included. Headers and licences are stripped (`--raw`).

| Role | Book | sha256 of the file |
|---|---|---|
| Plaintext | The Prince and the Pauper (#1837, `1837-0.txt`) | cc8b70736946e043166e8f6e00704c42fe3c1fc404f6eebc14f5e1a3f6237799 |
| Plaintext | Rebecca of Sunnybrook Farm (#498, `498.txt`) | 4a8b5eee9b36995c06792b81dac44b22f635f909c6222423cd2d86775ad4795c |
| Plaintext | The Railway Children (#1874, `1874-0.txt`) | 4847f211c6416621f7e74afe24d3e7e7d7182a8821fb989abf85d92b86b88b5e |
| Running keys for the RUNKEY negatives | White Fang (#910, `910.txt`) | cb8f3e4cfb99e34ad9741ebae21e177bf5fe5edc1c1342dcc5dea2bcdf53f3cb |

**Items.** `r88/sealed/make88.py PT1,PT2,PT3 KEY 880500 12 3 9 r88/holdout --raw` gives **150** items, with
shuffled ids:
- **48 positives:** 12 per stratum of n (S1 1–4, S2 5–8, S3 9–16, S4 17–32). Each has a random side, alphabet, d and
  W. Half are plain; half have 2 letters changed before encryption.
- **12 one-ciphertext-letter-wrong positives (CTERR):** reported, not gated.
- **90 wrong-family negatives:** 9 each from 10 generators:
  - R87's 9 generators, with SHUFRX replaced by SHUFRQ;
  - plus **RX, R87's single rotor, as the near-family decoy**.

**Scoring** (as in R87):
- *Best* is the decode with the highest letter-model score over all 512 settings.
- *Recovered* means ≥ 95/97 letters equal to the enciphered text.
- *Confident* means letter model ≥ −1.30 and word model ≥ −2.50 per letter.

**GO iff all of the following hold:**
- (a) positives recovered and confident ≥ **40/48**;
- (b) **≥ 9/12 in every stratum**;
- (c) negatives confident ≤ **1/90**;
- (d) the witness check passes.

On NO-GO: **no K4 run and no exclusion** (SOLVER_NO_POWER).

**Gate order** (each step a separate commit, pushed; as R87):
1. This pre-registration and `PROTOCOL.sha256`.
2. `QA_MANIFEST.json`, `holdout/BLIND.tsv` and `holdout/TRUTH_SHA256`. Only the truth file's hash is committed.
3. Blind run, witness, determinism and `holdout/GATE_FROZEN.sha256`.
4. Truth file and `holdout/GATE.json`.

## G2. Development and checks done before this commit (synthetic only, spent books)
**Development texts:** Tom Sawyer (dev_pt) and Dorian Gray (dev_key); seeds 880300 and 880301; 6 positives per
stratum, 2 CTERR per stratum, 3 per generator. **R87's solver parameters are used unchanged.** No parameter was tuned
for R88. Results: `r88/dev/DEV.md`.

**Final development figures** (same bars, 6 per stratum):

| | Set 1 (seed 880300) | Set 2 (seed 880301) |
|---|---|---|
| Positives recovered and confident | 21/24 (16 exact) | 22/24 (19 exact) |
| Every stratum | ≥ 5/6 | ≥ 5/6 |
| One ciphertext letter wrong | 7/8 | 7/8 |
| Negatives confident | 0/30 | 0/30 |

- Negatives' highest score: −1.392 letter model, −2.046 word model.
- Recovered positives' lowest letter-model score: −0.961.
- The three hard misses are scorer limits (). At the true setting, which ranked 1st or 2nd in pass 1,
  the quadgram scorer prefers a wrong text to the truth. Expect more partial (93–94/97) recoveries than in R87.

**Checks:**
- **Tests** (`r88/tests/test_r88.py`, all pass):
  - the witness encipherer equals the reference on 400 random settings, both sides;
  - the R87 kernel in R88's frames scores the explicit decrypt exactly, both sides;
  - three implementations of the exact check agree on 31,137 setting cases, δ 1–25 included;
  - the witness fails on one changed letter, alphabet swap, ciphertext letter, side, or a wrong "best";
  - sandbox refusals;
  - the holdout maker, with all 10 generators;
  - the gate bars.
- **R87 Amendment 1 fixed at the source.** The kernel is now built once, before the workers fork, under a per-process
  temporary name. The determinism check (`determinism88.py`: first 8 ids re-run outside the sandbox, byte for byte)
  and the kernel-hash check are kept for both runs.
- **Isolation reproducibility:** one development item, rerun in the sandbox, must reproduce the open run byte for
  byte. Result: the R88 runner, sandbox and launcher with 2 processes reproduce the open run of development item H_000 **byte for byte**. There was no compile race.

## G3. K4 blind run (only after GO; each step a separate commit, pushed)
1. **Target.** `r88/sealed/prepare_k4.py` (R73's script, seed 880400) writes `r88/k4/TARGET.tsv`: K4 unchanged plus
   100 frequency-preserving shuffles.
2. **Run.** The same sandbox and runner (4 processes), started through `audit/run_bounded.py`.
3. **Freeze.**
   - The witness, determinism and kernel checks run first.
   - `r88/k4/FROZEN.sha256` lists, with full paths, every output, the code, the logs and the gate.
   - Commit and **push**.
4. **Evaluation** (`evaluate88.py`; R84/R87 rules below). Commit and push.
5. **Exact check** (`exact88.py`, G5). Commit and push.

No tuning, re-running, re-ranking or filtering of blind outputs after the evaluation.

## Decision rules (fixed now; R87's)
"Best" is the maximum letter-model score over all 512 settings, for K4 and every shuffle alike.

| Outcome | Condition |
|---|---|
| **CONFIDENT** | K4's best has letter model ≥ −1.30 and word model ≥ −2.50, **and** is above every shuffle's best |
| **SIGNAL** | CONFIDENT and that decode matches ≥ 10/24 published letters |
| **SCORE_ANOMALY** | CONFIDENT without that |
| **NO_SIGNAL** | Otherwise |
| **p_family** (reported) | (1 + shuffles with best ≥ K4's) / 101 |
| **Contender** (listed raw; not a solution) | Any frozen K4 decode (top 5) with ≥ 12/24 |

## G5. Post-freeze exact check (crib-assisted, exclusion-only)
`exact88.py` runs on K4 and the 100 shuffles after the evaluation, over 19,200 settings.
- For each setting it asks whether some free alphabet maps all 24 published positions (a partial bijection). checks =
  positions − distinct left-hand values.
- **EXACT** (all 24 letters assumed right):
  - **EXCLUDED** if K4 has no feasible setting;
  - **LEAD** if K4 has a feasible setting with ≥ 3 checks that no shuffle reaches;
  - otherwise **CHANCE**.
- **DROP** (each letter set aside in turn): reported with the same labels.
- The exact step decrypts nothing and never sets the scope of a blind search.

## What follows (fixed now)
| Result | Next |
|---|---|
| **SIGNAL** | Stop; report raw. Proof steps as in R87. **No external submission without Tyler's go** |
| **SCORE_ANOMALY or a contender** | Report raw; not a solution; a 64-start stability check |
| **NO_SIGNAL with EXACT EXCLUDED** | Ledger: RQ in scope EXCL (exact, crib-assisted) with blind STAT confirmation |
| **NO_SIGNAL, EXACT CHANCE or LEAD** | Ledger: STAT NO_SIGNAL. LEAD settings are listed and need their own pre-registered blind round |

**Prior expectation:**
- NO_SIGNAL, with the exact step EXCLUDED.
- The free alphabet makes each setting looser than RX's, so random passes are likelier. The design pilot's
  0-in-153,600 rate was measured for RX, not RQ. The 100 shuffles calibrate this.

## G4. Review
**Independent review: NONE.** One model (Claude Code). No `Promotes:` line without a named independent reviewer.

## Budget (`QA_MANIFEST.json`)
- About 14 core-seconds per item, half of R87's 1,024 settings.
- Gate and K4: each under 15 min on 4 cores.
- Limits: 2 h and 4 GB per process per run. At most 505 kept K4 candidates. No retries.

## Disclosures
- The word model and letter model are R87's, unchanged.
- The kernel is R87's pinned `r87/blind/anneal.c`, compiled with `-march=native`.
