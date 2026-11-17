# R84 pre-registration (Claude Code, 16–17 Nov 2026): R80a's two-keyword-stage families on K4, strict blind

**Label: STRICT BLIND.**
- The blind solver runs in an isolated sandbox. It sees only the target TSV (K4 + 100 shuffles), the generic English
  scorers and the family code, with no network and no access to the repository.
- The published letters are read only by `r84/sealed/evaluate84.py`. That runs after the frozen outputs and their
  independent witness check are committed **and pushed**.

**Approval:** Tyler, 16 Nov 2026: "You can merge code & do more in each run. Please try to get a legit solution for
K4". On 17 Nov he approved this re-commit and asked "ensure that the recent findings are properly implemented so we
have good experiment quality".
- The search hold was lifted in PR #88 (`audit/reviews/SEARCH_HOLD_LIFTED.md`).
- R80a made this K4 run conditional on its gate passing and on Tyler's go. Both hold.

## G0. Hypothesis, scope and equivalent old models
**Hypothesis.** K4 is ordinary English, enciphered in place by two keyword stages on different tableaux.
- Stage one: `q_i = CA1[s1·IDX[PA1][p_i] + t1·IDX[KA1][k1[i mod m1]]]`.
- Stage two: `c_i = CA2[s2·IDX[PA2][q_i] + t2·IDX[KA2][k2[i mod m2]]]`.
- One key is **listed**: a word from the 28,943-word list at phase 0 (families L1/L2), or any key of 1–3 letters
  (X1/X2).
- The other key is **free**: 1–12 letters.
- Both orders. 96 conventions: AZ/KRY on each side, VIG/BEAU/VARB, CA1 ≠ PA2.

The model, parameters and code are R80a's, unchanged (`r80a/PREREGISTRATION.md`, `r80a/two80.py`). The inverse is
`two80.decrypt`. An independent encipherer is `r84/sealed/witness84.py` (worked synthetic examples in its tests).

**Equivalent and overlapping old models.**
- CA1 = PA2 collapses to one stage with a summed key, which is L36's territory; it is excluded here, as in R80a.
- **R75's F1X (L165)** is the exact, crib-assisted check of two periodic stages with any keys, periods 1–26, all
  alphabets. It covers 171 of this family's 180 key-length cells. It left K4 at chance level, and the settings it
  could complete read as gibberish. The T2 audit (PR #86) independently confirmed its feasibility setting by setting.
- This run adds two things:
  - a blind, crib-free test of the family;
  - the 9 F1X low-check cells: listed key 11–15 × free key 8–12.

**Prior exposure (R53 rule 5).** The family and every parameter were fixed in R80a (d31202e) before its holdout
existed. No K4 known-letter result was used to choose them. F1X's crib-assisted K4 outcome for this family was known
before this pre-registration. It changes nothing here.

**Cannot rule out:**
- listed keys at other phases;
- PALIMPSEST/ABSCISSA alphabets;
- listed keys outside the word list;
- free keys of 13+ letters;
- both keys free;
- transposition;
- masking or other pre-processing;
- non-English plaintext;
- K4 ciphertext errors beyond what the robustness diagnostic below measures.

A blind NO_SIGNAL is statistical. It excludes no setting exactly.

## G1. Gate and power, by stratum (already passed; not re-run)
`r80a/holdout/GATE.json` (0d71fcc), a sealed holdout of four fresh books. **All four families PASS:**

| Stratum | Recovered and confident |
|---|---|
| L1, L2, X1, X2 | 19, 18, 19, 19 of 20 (every recovery exact) |
| Free key 1–7 | 53/53 |
| Free key 8–10 | 22/27 |
| Free key 11–12 (STRETCH) | 12/16 |
| Nonstandard spelling | 14/16 |
| 2 letters changed | 23/24 |
| Wrong-family negatives confident | 0/100 (best −1.485) |

A K4 null is **informative for free keys ≤ 7**, weaker for 8–10, and weakest for 11–12. The audit's power review
(`audit/historical/POWER_REVIEW.md`, L171) says the same.

## G2. Adversarial checks done before this commit (synthetic only)
- **Reproducibility in isolation.** `r84/sealed/run_isolated.sh` runs the unchanged runner on R80a holdout item H_000.
  It reproduces the archived holdout record **byte for byte**, with only the 12 allowlisted files plus the letter model
  visible.
- **Letter model provenance.** `lm6.v2.bin` was rebuilt from the hash-pinned sources (`r59/corpus/build_corpus.py`,
  `r59/blind/lm_build.cpp`; every book and NLTK zip hash-checked). It equals the pinned sha256 b1a2a3c7…
  (`r59/blind/LM_SHA256`).
- **Independent witness checker.** `r84/sealed/witness84.py` uses the standard library only and imports nothing from
  the solver.
  - It equals R80a's reference cipher on 400 random settings.
  - It passes all 1,762 archived R80a holdout witnesses.
  - It **fails** when one decoded letter, one key letter or one ciphertext letter is changed.
- **Sandbox refusals.** The sandbox builder refuses:
  - an input with extra fields (key, mask or position columns);
  - an input containing a published K4 word;
  - a short row;
  - a reused sandbox.
- **Evaluation refusals.** The evaluation refuses files missing from the freeze and a failed witness check, and
  computes p from the shuffles.
- All of the above are in `r84/tests/test_r84.py`, which passes.
- **Plaintext-driven state:** none. Every key in this family is periodic in the position. The R83a defect (a wrong
  plaintext letter steering later state) cannot arise.
- **Solution counts:** none are computed, so the R75 int64 defect cannot arise.

## G2b. Robustness diagnostic, fixed now, run before the K4 run (reported, NOT gated)
`r84/sealed/ct_error84.py` takes 12 positives that R80a's gate recovered (3 per family, seed 840500; truth already
spent). It changes **one ciphertext letter** at a random position, then runs the same isolated solver.
- **Reported:** recovered = ≥ 95/97 right and confident.
- **Reading:** if ≥ 10/12 are recovered, a single carving error in K4 would not hide a true solution of this family.
  If fewer, the K4 null is weaker against carving errors, and the report says so.
- It changes nothing below.

## G3. Blindness, freeze and order (each step a separate commit)
1. **This pre-registration**, `PROTOCOL.sha256` (code, data, sealed scripts and tests) and the sealed scripts.
2. **`QA_MANIFEST.json` and the target.** `r84/sealed/prepare_k4.py`, R73's script with seed 840400, writes
   `r84/k4/TARGET.tsv`: unchanged K4 (sha256 2797de14…) + 100 frequency-preserving shuffles.
3. **Diagnostic (G2b)** in its own sandbox.
4. **Blind run:**
   - `make_sandbox.py` copies the 12 allowlisted files (hash-checked against `PROTOCOL.sha256`), the letter model and
     the target into a fresh sandbox.
   - `run_isolated.sh` runs `r80a/blind/run.py` (4 processes; R80a's parameters: SEED 800001, K0 4,000, starts 1 / 6,
     TOP1 150, KEEP 60) in a new mount and network namespace. There, `/workspace`, `/tmp/claude-0` and `/root` are
     empty and there is no network.
   - The run goes through `audit/run_bounded.py` with the manifest's budget.
5. **Independent witness check** of every stored decode (`witness84.py`, before any published letter is read). Then
   `r84/k4/FROZEN.sha256`, with full repository paths, lists:
   - the target, `RESULTS.jsonl`, the runner's own freeze file, `WITNESS.json` and `SANDBOX.json`;
   - the code;
   - the resource log;
   - the letter-model hash.
   Commit and **push**.
6. **Evaluation** (`evaluate84.py`, rules below). Commit and push.

No tuning, re-running, re-ranking or filtering of blind outputs after the evaluation (R53 rule 5).

## Decision rules (fixed now; R79/R81a rules, family-wise)
"Best" is the maximum letter-model score over **all four families** of the full search, for K4 and for every shuffle
alike. So the comparison with the shuffles is calibrated for the whole scan.

| Outcome | Condition |
|---|---|
| **CONFIDENT** | K4's best has letter model ≥ −1.30 and word model ≥ −2.50 per letter, **and** is above every shuffle's best |
| **SIGNAL** | CONFIDENT and that decode matches ≥ 10/24 published letters |
| **SCORE_ANOMALY** | CONFIDENT without that |
| **NO_SIGNAL** | Otherwise |
| **p_family** (reported) | (1 + shuffles with best ≥ K4's) / 101 |
| **Contender** (listed raw; not a solution) | Any frozen K4 decode (top 5, each family's best) matching ≥ 12/24, reported with the most any shuffle's frozen decode matches |

## What follows (fixed now)
| Result | Next |
|---|---|
| **SIGNAL** | Stop. Report the raw 97 letters unedited, with the key and the witness. Then the proof steps: an independent key re-derivation (re-run the found setting with 64 new-seed starts; the same text within ≤ 5 letters), a check that the key makes sense, and independent re-encryption. **No external submission without Tyler's go** |
| **SCORE_ANOMALY or a contender** | Report raw. Not a solution. The same 64-start stability check; no tuning |
| **NO_SIGNAL** | Ledger row L173: STAT, NO_SIGNAL, informative by the strata above; no exclusion |

**Prior expectation:** NO_SIGNAL (see F1X above).

## G4. Review
Independent review: NONE. One model (Claude Code) is builder, breaker and auditor here. That does not count as
independent review (guardrails G4). A multi-model review can be run on request before or after the evaluation. The
review note will say NONE unless one is run.

## Budget (`QA_MANIFEST.json`)
- 4 h wall clock and 4 GB per process.
- At most 6,060 kept candidates (101 ciphertexts × 60).
- Expected: about 2 h on 4 cores (about 4.5 min per ciphertext per core, measured).

## Disclosures
- **The R59 word model** (`k4kit/data/word_model_orth.tsv`) is a 226k-entry generic English model, the shared scorer
  since R43. It supplies the word score and, through it, R80a's listed keys. It contains EAST, NORTH, NORTHEAST, BERLIN
  and CLOCK as ordinary words (ranks 20,156 and beyond for BERLIN/CLOCK/NORTHEAST). They are kept: removing them
  *because* they are published words would itself condition on the published letters. No position, mask or crib
  feature reaches the solver.
- The Kryptos word list (`r75/data/kryptos_words.txt`) holds K1–K3 words only. None is a published K4 word.
