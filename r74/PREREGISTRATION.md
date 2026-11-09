# R74 pre-registration (Claude Code, 9 Nov 2026): K1 → K3 → K2 substitution–transposition–substitution

Written before the holdout is generated and before anything runs on K4.

**Approval:** Tyler approved on 9 Nov 2026 ("Send it"), in reply to: "One OK would cover the sealed synthetic test of
120 messages and 300 controls and then, only if that passes, the K4 run."

**Design:** ChatGPT's PR #65, with the changes in `r74/REVIEW.md`.

**The synthetic gate uses no K4 data.**

## Family (fixed; `r74/sandwich.py`)
Each stage runs on the KRYPTOS tableau `KRYPTOSABCDEFGHIJLMNQUVWXZ`:
1. Substitution with keyword Ka (VIG, BEAU or VARB) at phase a.
2. One of 14 directed routes: the 10 frozen `r61/routes.txt` maps and their inverses, duplicates merged.
3. Substitution with keyword Kb (VIG, BEAU or VARB) at phase b.

**Size:**
- The keyword pair is (PALIMPSEST, ABSCISSA) in either order.
- That gives 20,160 raw settings, or **15,680 distinct transforms**, each a fixed invertible map of 97 letters.
- Audit and proofs: `r74/REVIEW.md`, `r74/results/AUDIT.json`.

**Nothing else is in scope:** no other keywords, alphabets, routes or masks.

## Solver and scorers (fixed; `r74/scan.py`, `r74/blind/run.py`)
- **Full scan:** each ciphertext is decrypted under all 15,680 transforms.
- **Ranking:** by the R59 order-6 letter model (log10 per letter, no starting context; sha256 `b1a2a3c7…`, checked).
- **Second, independent scorer:** the R59 word model (`k4kit/data/word_model_orth.tsv`; best segmentation, −7 per
  unknown letter).
- **Stored per ciphertext:** the 5 best distinct decodes.
- **For the K4 target only:** the full 15,680-decode scan (gzip) and the 25-decode review packet are also stored. The
  packet is the best decode of each (route, keyword order) pair, the 25 best of those 28.

## Development record (development books only; never the holdout; nothing run on K4)
- **Pilot** (`r74/pilot.py`, `r74/results/PILOT.json`): 12/12 exact. Positives scored ≥ −0.93 per letter; 33
  controls ≤ −1.80.
- **Cut run** (`r74/dev_cut.py`, seeds 740201/740202, `r74/results/DEV_CUT.json`). It mirrors the holdout:
  - 100 positives from *The Secret Agent* and *The Riddle of the Sands* (50 each), with 10 of each misspelled (2
    random letters changed);
  - 280 R71-generator negatives (*The Thirty-Nine Steps* plaintext, *The Secret Adversary* keys) and 20 shuffles.

| | Recovered | Letter model, worst positive / best negative | Word model, worst positive / best negative |
|---|---|---|---|
| Development | **100/100** (misspelled 20/20) | −1.026 / −1.841 | −1.488 / −3.444 |
| **Cut** (midpoint, rounded down to 0.05) | | **−1.45** | **−2.50** |

## Sealed holdout (`r74/sealed/make_holdout.py`, seed 740300)
**Books:** four GITenberg books never used in this project and not in the R59 letter model's training text. Their
sha256 values are checked by the script.

| Role | Book | GITenberg (file) | sha256 |
|---|---|---|---|
| Positives A | *The Scarlet Pimpernel* (Orczy) | 60 (`60-0.txt`) | 102acac6… |
| Positives B | *King Solomon's Mines* (Haggard) | 2166 (`2166.txt`) | dfdb09f4… |
| Negative plaintext | *The Mysterious Affair at Styles* (Christie) | 863 (`863-0.txt`) | 01822d92… |
| Negative keys | *Around the World in 80 Days* (Verne) | 103 (`103.txt`) | b5bd33ca… |

**Contents:**
- **120 positives:** 60 per book, 10 of each with 2 random letters changed. Each is enciphered under a hidden raw
  setting drawn uniformly from the 20,160.
- **300 negatives:** 40 from each of R71's seven generators, plus 20 shuffles of positive ciphertexts.
- 420 neutral ids in random order.

**Sequence:**
1. Commit the holdout's `blind.tsv` with the truth's sha256 in the commit message.
2. Blind run, then freeze and push.
3. Verify, without the truth: every stored decode re-encrypts by the explicit three-stage encryption.
4. Only then open the truth and apply the gate (`r74/sealed/gate.py`).

**Definitions (frozen):**
- *recovered* = the best decode is the exact enciphered plaintext (misspellings included) **and** its transform is the
  true one;
- *confident* = the best decode scores ≥ −1.45 per letter (letter model) **and** ≥ −2.50 per letter (word model).

**Gate:**
- **PASS** iff ≥ 108/120 positives are recovered **and** confident, **and** 0/300 negatives are confident, **and**
  verification passes.
- Reported: clean and misspelled positives separately, the one-sided 95% lower bound on power, and the 95% upper bound
  on false confidence.

**If it fails, nothing runs on K4.**

## K4 run (only if the gate passes)
**Target** (`r74/sealed/prepare_k4.py`): the unchanged K4 ciphertext (sha256 2797de14…) plus **1,000**
frequency-preserving shuffles (seed 740400).

**Sequence:**
1. Run `r74/blind/run.py` unchanged with `--full K4`, then freeze and push.
2. Verify all stored decodes re-encrypt (`gate.py --verify`, no published letters). That includes all 15,680 K4
   decodes and the packet.
3. Only then run `r74/sealed/reveal_k4.py`. Its published letters come from `r73/sealed/reveal_k4.py`.

**Outcomes:**
- **CONFIDENT** iff K4's best decode clears both cuts **and** its letter-model score is above every null's best.
- **SIGNAL** iff CONFIDENT **and** the decode matches ≥ 10/24 published letters (0-based plaintext positions 21–33 and
  63–73).
- **SCORE_ANOMALY** iff CONFIDENT without the letter match.
- **NO_SIGNAL** otherwise.

**R74X: crib-assisted exclusion check** (after the freeze and verify; reported separately, never part of the blind
outcome; labelled as in R70 Erratum 1).
- **Measure:** the published letters matched by each of K4's 15,680 frozen decodes.
- **Verdict:** **CONSISTENT** iff some transform matches ≥ 20/24 (each one listed raw); otherwise **EXCLUDED**.
- **Calibration:** the same maximum is computed for all 1,000 shuffles. In the synthetic dry run a random target's
  maximum was 7.
- **Strength:** a wrong transform matching ≥ 20/24 by chance has a probability of about 10⁻²³ over the whole family.

**Review packet:** the 25 frozen decodes, each with its letter count added after the freeze. If all are below the
cuts, they are labelled **LOW-CONFIDENCE RAW OUTPUTS, not prospects**.

**Prior expectation** (stated before the run): NO_SIGNAL and R74X EXCLUDED.
