# R87 pre-registration (Claude Code, 20 Nov 2026): one stepping rotor with an unknown wiring, 16 contact-alphabet pairs, n 1–32: sealed gate, then K4 strict blind, then a post-freeze exact check

**Label: STRICT BLIND, gate first.**
- The blind solver runs in an isolated sandbox. It sees only an input TSV, the generic English scorers and the family
  code, with no network and no repository.
- Nothing about K4 is run until the sealed gate below says GO.
- The published letters are read only by `r87/sealed/evaluate87.py` and then `r87/sealed/exact87.py`. Both run after
  the frozen K4 outputs and their independent witness check are committed **and pushed**.

**Approval and numbering.**
- Tyler approved the family in the R85 design (PR #93, `r85/DESIGN.md`: "Sure, let's get a cipher family & techniques
  identified").
- On 19 Nov he said "Run both": the R85 sealed gate and the T6 R40–R42 replay.
- On 20 Nov he relayed ChatGPT's R85/R86 results and said "Finish that if you need to". The standing approval is
  "You can merge code & do more in each run. Please try to get a legit solution for K4".
- ChatGPT's draft PR #95 uses `r85/` (its failed pilot) and `r86/` (its AZ/AZ, n 1–4 run). This round is therefore
  **R87**, so the names do not collide. `r85/DESIGN.md` stays the design.

## G0. Hypothesis, scope and equivalent old models
**Hypothesis (family RX, `r85/DESIGN.md` §4).** K4 is ordinary English, enciphered in place by one stepping rotor.
- Contacts are numbered on the input side by alphabet E_in and on the output side by E_out. Each is one of AZ,
  KRYPTOS, PALIMPSEST, ABSCISSA (keyword first, then the rest of A–Z).
- The wiring W is any of the 26! permutations. The starting position is absorbed by W.
- The rotor advances d = ±1 every n letters: s_i = d·⌊i/n⌋, with i counted from 0.
- Encryption: `E_out-place(c_i) + s_i = W[E_in-place(p_i) + s_i]` (mod 26).
- Reference code: `r87/rotor87.py`. Independent encipherer: `r87/sealed/witness87.py`, standard library only.

**Scope.**
| Step | Settings | Each with |
|---|---|---|
| Blind search | 16 alphabet pairs × d ±1 × n 1–32 = **1,024** | a free wiring, searched heuristically |
| Post-freeze exact check | 16 × 2 × n 1–96 = **3,072** | every wiring, decided exactly |

n ≥ 97 is a single alphabet, which L02 excludes.

**Equivalent and overlapping old models.**
- **Progressive keys with fixed alphabets** (L13, L20) are the special case of an affine W.
- **Per-slot arbitrary alphabets** at period 26 (L21, open) contain n = 1 as a structured case, with all 26 slots
  sharing one wiring. L53 says only such extra structure can decide those periods.
- **ChatGPT's R86** (PR #95, draft, not merged) searched 8 of these 1,024 blind settings (AZ/AZ, n 1–4, d ±1). It used
  a different solver and scorer, and its gate was 20 items from one genre. R87 re-covers that subset independently and
  adds 1,016 settings.

**Prior exposure (R53 rule 5).**
- The family and every scope bound above were fixed in `r85/DESIGN.md` (merged 17 Nov) and in this round's solver
  code (NMAX 32), before any rotor result on K4 existed.
- **R86's K4 outcome was seen before this pre-registration:** NO_SIGNAL for AZ/AZ n ≤ 4, best decode at chance, 1–3
  of 24 published letters. It changed no scope bound and no parameter here. The parameters below were chosen on spent
  development books only (§G2).
- No exact crib check of RX has been run on K4 by anyone in this project. The design pilot measured only how often
  random ciphertexts pass (0 of 153,600 setting trials).

**Cannot rule out:**
- two or more rotors;
- stepping triggered by letters, or irregular stepping;
- other contact numberings;
- n 33–96 in the blind step (the exact step covers them);
- transposition before or after the rotor;
- masking or nulls;
- non-English plaintext;
- K4 ciphertext errors beyond what the diagnostic below measures.

A blind NO_SIGNAL is statistical and excludes no setting exactly. The exact step can exclude settings, but only under
its stated assumptions: all published letters right, in place, in the carved order.

## G1. Sealed gate (fresh books; run before anything touches K4)
**Books.** Fresh Project Gutenberg texts, downloaded 19 Nov via the GITenberg mirror. None is in the letter-model
corpus (`r59/corpus/build_corpus.py`), the development books or an earlier holdout. Headers and licences are stripped
(`make87.py --raw`).

| Role | Book | sha256 of the file |
|---|---|---|
| Plaintext | Peter Pan (#16) | b1e7ade0c061259293c7b07fe3f8ba445b4cf3353e6c657c8cdcd0223bbe0eb8 |
| Plaintext | Anne of Green Gables (#45) | 7e99ec4f9f3080e3dd70551df7685709310a8140e3280436d0a4f5789255dd83 |
| Plaintext | Northanger Abbey (#121) | bbd0f21dbcd079832245a4b9990caeada34965059974a99d2990507461b8647f |
| Running keys for the RUNKEY negatives | Black Beauty (#271) | 1cfc3689b80b42a3ee42e189c7d218d3e16d5f0c616ff042472be3ced85b7836 |

Each window is drawn from one of the three plaintext books, chosen uniformly.

**Items.** `r87/sealed/make87.py PT1,PT2,PT3 KEY 870500 12 3 10 r87/holdout --raw` gives **150** items, with shuffled
ids:
- **48 positives:** 12 in each stratum of n (S1 1–4, S2 5–8, S3 9–16, S4 17–32). Each has a random wiring, E_in, E_out
  and d. Half are plain; half have **2 letters changed** before encryption.
- **12 one-ciphertext-letter-wrong positives (CTERR):** 3 per stratum. Reported, not gated.
- **90 wrong-family negatives:** 10 each from
  - periodic Vigenère (key 5–14);
  - Quagmire III on KRYPTOS (key 5–14);
  - running key (Black Beauty);
  - Gromark (KRYPTOS);
  - ciphertext autokey (lag 1–7);
  - two periodic stages on different tableaux;
  - **RX2**, two rotors (odometer): the near-family confounder;
  - a shuffled RX ciphertext;
  - uniform random letters.

**Scoring.**
- *Best* is the decode with the highest letter-model score over all 1,024 settings.
- *Recovered* means it has ≥ 95 of 97 letters equal to the enciphered text.
- *Confident* means letter model ≥ −1.30 **and** word model ≥ −2.50 per letter. These are R59's cuts, unchanged since
  R80a.

**GO iff all of the following hold:**
- (a) positives recovered and confident ≥ **40/48**;
- (b) **≥ 9/12 in every stratum** S1–S4;
- (c) negatives confident ≤ **1/90**;
- (d) the independent witness check passes.

**Reported, not gated:** CTERR recovered and confident, by stratum; exact recoveries; setting recovered; plain vs
2-changed; each generator's best negative score.

On NO-GO: **no K4 run and no exclusion**. The failure is reported as SOLVER_NO_POWER. Any later attempt is a new
round with a new holdout.

**Gate order** (each step a separate commit, pushed):
1. This pre-registration and `PROTOCOL.sha256`.
2. `QA_MANIFEST.json` (stage preregistered), `r87/holdout/BLIND.tsv` and `r87/holdout/TRUTH_SHA256`. The truth file
   stays outside the repository and outside the sandbox. Only its hash is committed.
3. Blind run, witness check and `r87/holdout/GATE_FROZEN.sha256`, which lists the input, results, runner freeze,
   sandbox record, witness and resource log.
4. Then the truth file is committed. `gate87.py` checks it against the committed hash and writes
   `r87/holdout/GATE.json`. The manifest moves to stage gate with the verdict.

## G2. Development and checks done before this commit (synthetic only, spent books)
**Development texts:**
- Tom Sawyer (`r59` dev_pt);
- Dorian Gray (dev_key).

Development decisions are in `r87/dev/DEV.md`.

**Final development figures (same bars, 6 per stratum):**
| | Set 1 (seed 870300) | Set 2 (seed 870301) |
|---|---|---|
| Positives recovered and confident | 22/24 | 22/24 |
| One ciphertext letter wrong | 8/8 | 8/8 |
| Negatives confident | 0/27 | 0/27 |
| Every stratum | ≥ 5/6 | ≥ 5/6 |

- The four misses were confident partial decodes at 88–94 of 97 letters. Long anneals at the true setting show the
  scorer prefers them, so they are scorer limits.
- Recovered positives' lowest letter-model score: −1.075. Negatives' highest: −1.349 letter model, −1.954 word model.

**Checks:**
- **Tests** (`r87/tests/test_r87.py`, all pass):
  - the witness encipherer equals the reference on 400 random settings;
  - the C kernel's score equals the quadgram score of the explicit decrypt;
  - three implementations of the exact check agree on 26,340 setting cases;
  - the witness fails on one changed letter, wiring swap, ciphertext letter, or a wrong "best";
  - sandbox refusals: an extra field, a published word, a short row, a reused box;
  - the holdout maker: counts, re-encryption, one-letter ciphertext errors, determinism;
  - the gate bars, on constructed cases.
- **Isolation reproducibility.** One development item, run through `make_sandbox87.py` and `run_isolated87.sh` with
  the 8 allowlisted files and the letter model, reproduces the open run **byte for byte**.
- **Letter model.** `lm6.v2.bin` was rebuilt from the hash-pinned sources and equals sha256 b1a2a3c7…
  (`r59/blind/LM_SHA256`).
- **Plaintext-driven state:** none. The rotor steps by position only.
- **Solution counts:** none are computed.

## G3. K4 blind run (only after GO; each step a separate commit, pushed)
1. **Target.** `r87/sealed/prepare_k4.py` (R73's script, seed 870400) writes `r87/k4/TARGET.tsv`: K4 unchanged
   (sha256 2797de14…) plus 100 frequency-preserving shuffles.
2. **Run.** The same sandbox and runner as the gate (4 processes), started through `audit/run_bounded.py` with the
   manifest's budget.
3. **Freeze.**
   - `witness87.py` checks every stored decode before any published letter is read.
   - Then `r87/k4/FROZEN.sha256` lists, with full repository paths: the target, `RESULTS.jsonl`, the runner's own
     freeze file, `WITNESS.json`, `SANDBOX.json`, the code, the resource log and the letter-model hash.
   - Commit and **push**.
4. **Evaluation** (`evaluate87.py`, rules below). Commit and push.
5. **Exact check** (`exact87.py`, G5). Commit and push.

No tuning, re-running, re-ranking or filtering of blind outputs after the evaluation (R53 rule 5).

## Decision rules (fixed now; R84's rules)
"Best" is the maximum letter-model score over all 1,024 settings, for K4 and for every shuffle alike.

| Outcome | Condition |
|---|---|
| **CONFIDENT** | K4's best has letter model ≥ −1.30 and word model ≥ −2.50 per letter, **and** is above every shuffle's best |
| **SIGNAL** | CONFIDENT and that decode matches ≥ 10/24 published letters |
| **SCORE_ANOMALY** | CONFIDENT without that |
| **NO_SIGNAL** | Otherwise |
| **p_family** (reported) | (1 + shuffles with best ≥ K4's) / 101 |
| **Contender** (listed raw; not a solution) | Any frozen K4 decode (top 5) matching ≥ 12/24, reported with the most any shuffle's frozen decode matches |

## G5. Post-freeze exact check (crib-assisted, exclusion-only)
`exact87.py` runs on K4 and the same 100 shuffles, after the evaluation.
- For every one of the 3,072 settings it asks whether some wiring maps all 24 published positions correctly (a
  partial bijection). checks = positions − distinct inputs.
- **EXACT** (all 24 letters assumed right):
  - **EXCLUDED** if K4 has no feasible setting;
  - **LEAD** if K4 has a feasible setting with ≥ 3 checks and no shuffle reaches K4's maximum;
  - otherwise **CHANCE**.
- **DROP** (each published letter set aside in turn): the same labels, reported.
- The exact step decrypts nothing. It never changes the blind verdict and is never used to pick settings for a blind
  search.

## What follows (fixed now)
| Result | Next |
|---|---|
| **SIGNAL** | Stop. Report the raw 97 letters unedited, with the setting, the wiring and the witness. Then the proof steps: a 64-start re-run of the found setting with new seeds (the same text within ≤ 5 letters), a check that the key makes sense, and an independent re-encryption. **No external submission without Tyler's go** |
| **SCORE_ANOMALY or a contender** | Report raw. Not a solution. The same 64-start stability check; no tuning |
| **NO_SIGNAL with EXACT EXCLUDED** | Ledger: RX in scope is **EXCL (exact, crib-assisted)** under its assumptions, with blind STAT confirmation. Next family: RQ (progressive Quagmire with one free alphabet, `r85/DESIGN.md` §5) |
| **NO_SIGNAL, EXACT CHANCE or LEAD** | Ledger: STAT NO_SIGNAL. Any LEAD settings are listed, with no evidence beyond the count. A LEAD needs its own pre-registered blind round; it may **not** set the scope of a blind search |

**Prior expectation:** NO_SIGNAL. The exact step will most likely EXCLUDE: the design pilot found 0 of 153,600
random passes.

## G4. Review
**Independent review: NONE.** One model (Claude Code) is builder, breaker and auditor here. It does not count as
independent review (guardrails G4 and rule 10). A ChatGPT or human review can be run before or after the evaluation.
No `Promotes:` line will be written without one.

## Budget (`QA_MANIFEST.json`)
- **Gate:** 150 items at about 22 core-seconds each (development: 59 items in 329 s on 4 cores), about 15 min.
- **K4 + 100 shuffles:** about 10 min.
- **Limits:** 2 h wall clock and 4 GB per process for each run. At most 505 kept K4 candidates (101 × 5). No retries.

## Disclosures
- **Word model.** The R59 word model (`k4kit/data/word_model_orth.tsv`) is generic English. It contains EAST, NORTH,
  NORTHEAST, BERLIN and CLOCK as ordinary words, kept as in R84.
- **Compilation.** The kernel is compiled with `-march=native`. Annealing results are bit-reproducible on this machine;
  on another CPU they may differ in the last bits.
- **R86.** ChatGPT's draft PR #95 (R85 pilot, R86) was cross-checked before this commit from its archived files:
  - its 606 K4-stage and 120 gate decodes re-encrypt under this round's reference code;
  - its gate figures (17/20, 15/20 exact) and p (33/101) reproduce;
  - its round passes the guardrail check.
  That is a check of internal consistency, not a review of its method.
