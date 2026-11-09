# R73b pre-registration (Claude Code, 9 Nov 2026): R26 retry with letter-model scoring of unknown words

Written before the holdout is generated and before anything is run on K4. **The synthetic gate uses no K4 ciphertext,
published letters or K4 derivative.**

**Approval:** Tyler approved R73b on 9 Nov 2026 ("Do r73 if you think it's worth it before doing 73b"). The option he
approved was proposed after Phase B as: fix the solver's unknown-word handling on development text only, run a new
sealed test on a fresh book under the same pass marks, and "only if it passes would R26 go to K4". The K4 run below is
therefore conditional on the gate passing, and its rules are fixed here, before the holdout exists.

## What changes from R73
- **The family is unchanged:** R26 (`r73/wordkey.py`): y = x + word number (1-based) + position in word + phase b
  (mod 26), on the AZ or KRYPTOS tableau; 52 settings; word divisions removed after encipherment.
- **R26 only.** Family I passed Phase B and has had its K4 run (`r73/K4_PREREGISTRATION.md`: NO_SIGNAL).
- **One solver change** (`r73/wordkey2.py`): an out-of-vocabulary word scores the R59 order-6 letter model's log10
  probability (no starting context) plus a fixed per-word penalty POOV, instead of a flat −7 per letter.
  - In Phase B, R26's misses were names such as WICKHAM read as a dictionary prefix plus garbage (WICK + …), which threw
    the word counter out of step.
  - The R59 word model, the DP over (position, phase of the next word) and all 52 settings are unchanged.
  - The letter model is the R59 model (sha256 `b1a2a3c7…`, `r59/blind/LM_SHA256`), checked by the runner.

## Development record (development books only; never the holdout; nothing run on K4)
**1. POOV sweep** (`r73/dev_r73b.py`, seed 731001; `r73/results/R73B_DEV_SWEEP.json`):
- 40 R26 positives (20 each from *The Thirty-Nine Steps*, GITenberg 558, and *Pride and Prejudice*, 1342, whose
  holdout is spent).
- 56 negatives (8 from each of R71's seven generators).

| POOV | Recovered | Setting exact | Exact plaintext | Fewest letters right | Positives' minimum | Negatives' maximum | Gap |
|---|---|---|---|---|---|---|---|
| −1 | 40/40 | 40/40 | 36 | 93 | −1.008 | −1.442 | 0.43 |
| −2 | 40/40 | 40/40 | 36 | 94 | −1.059 | −1.610 | 0.55 |
| **−3** | 40/40 | 40/40 | 36 | 94 | −1.101 | −1.741 | 0.64 |
| −4 | 40/40 | 40/40 | 35 | 92 | −1.135 | −1.830 | 0.70 |
| −6 | 40/40 | 40/40 | 35 | 91 | −1.182 | −1.986 | 0.80 |

Scores are per letter.

- **Rule for POOV:** the largest gap among the values that keep the most exact plaintexts (36) and the highest fewest
  letters right (94). That gives **POOV = −3**.
- **Caveat:** *Pride and Prejudice* is in the letter model's training text, so its development positives are
  optimistic. The confirmation run below uses only books outside that text.

**2. Confirmation and cut** (`r73/dev_r73b_cut.py`, POOV −3, seeds 731101/731102; `r73/results/R73B_DEV_CUT.json`).
It mirrors the holdout's make-up on development books outside the letter model's training text:
- 100 positives (50 each from *The Secret Agent*, 974, and *The Riddle of the Sands*, 2360).
- 280 generator negatives (40 per generator; *The Thirty-Nine Steps* plaintext, *The Secret Adversary* keys).
- 20 shuffles of positives.

Results:
- **Positives:** 100/100 recovered; setting exact 99/100; exact plaintext 85/100; fewest letters right 92.
  The remaining errors are local, mostly an apostrophe-S or a short name split into fragments.
- **Scores:** positives' minimum −1.031 per letter. Negatives' maximum −1.704 (each kind's maximum lies in −1.70 to
  −1.76).
- **Rule for the cut:** the midpoint of those two values, rounded down to 0.05, gives **CUT = −1.40 per letter**.

## Fixed now
**Solver and runner:**
- Solver: `r73/wordkey2.py` with POOV −3.
- Blind runner: `r73/blind/run_r73b.py`. It reads only the input TSV, the word model and the letter model, and keeps
  the best decode of all 52 settings per ciphertext.
- Hashes: `r73/R73B_PROTOCOL.sha256`.

**Sources:** three GITenberg books that have not been used anywhere in this project and are not in the R59 letter
model's training text (14 novels plus NLTK corpora, `r59/corpus/build_corpus.py`). Only `PT_BOOK` messages are scored
as positives.

| Role | Book | GITenberg (file) | sha256 |
|---|---|---|---|
| `PT_BOOK` (positives) | *The Moonstone* (Collins) | 155 (`155-0.txt`) | c7603d40… |
| `NEG_PT_BOOK` (negatives) | *The Prisoner of Zenda* (Hope) | 95 (`95-0.txt`) | 03a57076… |
| `NEG_KEY_BOOK` (negatives) | *Kidnapped* (Stevenson) | 421 (`421-0.txt`) | f2ea387b… |

The full hashes are checked by `r73/sealed/make_holdout_r73b.py`.

**Holdout** (`r73/sealed/make_holdout_r73b.py`, seed 731200):
- **100 R26 positives:** consecutive whole words totalling exactly 97 letters, each with a hidden setting drawn
  uniformly from the 52.
- **300 negatives:** 40 from each of R71's seven generators (OTP, running key, periodic, homophonic, Gromark,
  ciphertext autokey, plaintext autokey), plus 20 frequency-preserving shuffles of positives.
- 400 neutral ids in random order.

**Sequence:**
1. Commit the holdout's `blind.tsv` with the truth's sha256 in the commit message; the truth is withheld.
2. Blind run, then freeze and push.
3. Verify, without the truth: `r73/sealed/gate_r73b.py`, using `r73/sealed/gate.py`'s verify unchanged, checks that
   every stored decode re-encrypts to its ciphertext.
4. Only then open the truth and apply the gate.

**Definitions** (frozen):
- *recovered* = ≥ 90 of 97 plaintext letters right;
- *confident* = best score ≥ −1.40 per letter.

**Gate:**
- **PASS** iff ≥ 90/100 positives are recovered **and** confident, **and** 0/300 negatives are confident, **and**
  verification passes.
- Exact plaintext, exact setting and score ranges are reported.

## K4 run (only if the gate passes)
**Target** (`r73/sealed/prepare_k4_r73b.py`): the unchanged K4 ciphertext (sha256 2797de14…) plus 100
frequency-preserving shuffles (seed 731300).

**Sequence:**
1. Run `r73/blind/run_r73b.py` unchanged, then freeze and push.
2. Verify every stored decode re-encrypts (`r73/sealed/gate.py`'s verify, no published letters).
3. Only then run `r73/sealed/reveal_k4_r73b.py`. Its published letters come from `r73/sealed/reveal_k4.py`.

**Statistic:** K4's best R26 decode over the 52 settings, per letter.

**Outcomes:**
- **CONFIDENT** iff K4's best is ≥ −1.40 per letter **and** above every null's best.
- **SIGNAL** iff CONFIDENT **and** the decode matches ≥ 10 of the 24 published letters (0-based plaintext positions
  21–33 and 63–73; R26 enciphers in place).
- **SCORE_ANOMALY** iff CONFIDENT without the letter match.
- **NO_SIGNAL** otherwise.

**Contender screen:** any of K4's 52 decodes matching ≥ 12/24 is listed raw, with the nulls' maximum.

**R26X: crib-assisted exclusion check** (post-freeze, reported separately, never part of the blind outcome; labelled as
in R70 Erratum 1).
- **Question:** for each tableau alphabet, can R26 encipher the 24 published letters to K4's letters at all, for any
  phase, word numbering and word division?
  - Words have 1–18 letters.
  - The plaintext between the two published blocks is unknown.
- **Output:**
  - **EXCLUDED** for an alphabet iff no such path exists.
  - Otherwise every consistent word division inside each block is listed.
  - The same check is reported for the 100 nulls.
- **Validation** (scratch check on synthetic data, no K4):
  - It found the true alphabet and true word divisions in 40/40 planted R26 messages.
  - It found 0 of 2,000 uniform random ciphertexts consistent under either alphabet.
- **Status:** it is an arithmetic consistency check, not a decryption. It does not depend on the language models.

**If the gate fails:** nothing is run on K4, R26X included.

**Prior expectation** (stated before the run): NO_SIGNAL, and R26X EXCLUDED under both alphabets.
