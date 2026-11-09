# R73 Phase A pilot (Claude Code, 9 Nov 2026): word-boundary key families from PR #62 — synthetic only

**No K4 input of any kind.** The ciphertext, the published letters and every K4 derivative are untouched. The one
K4-related number used here is its index of coincidence (0.0361), which is already published, and only in a
plausibility check.

Code:
- `r73/wordkey.py`: cipher definitions and a blind word-segmentation solver.
- `r73/pilot.py`: the pilot driver.
- `r73/tests/test_r73.py`: tests.

Raw pilot output: `r73/results/PILOT.json`.

## What was tested
**The two families, exactly as PR #62 defines them.** Plaintext is English words; the word divisions are removed after
encipherment.
- **Family I:** an interrupted key that restarts at every plaintext word.
  - Keyword: KRYPTOS, PALIMPSEST or ABSCISSA.
  - Tableau: AZ or KRYPTOS.
  - Operation: VIG, BEAU or VARB.
  - 18 settings in all.
- **R26:** a 26-letter Ragbaby-like scheme, y = x + word number + position in word + phase (mod 26).
  - Tableau: AZ or KRYPTOS; phase 0–25.
  - 52 settings in all.

**The solver** sees only the ciphertext. For every setting of both families, it chooses the word segmentation that
maximizes the summed word log-probabilities, using R59's word model.
- An unknown word counts as one word, at 7 per letter, so the per-word key phase and word counter stay in step.
- About 1.8 s per ciphertext for all 70 settings.

**Pilot data** (seed 730001):
- 12 messages per family: consecutive whole words of *The Thirty-Nine Steps* totalling exactly 97 letters, each with a
  hidden random setting.
- 30 wrong-family ciphertexts: R71's OTP, running key, periodic, homophonic + route, Gromark, CTAK and PTAK
  generators, built on other books.

## Results (second pilot pass, after one development fix)
| | Family right | Setting right | Exact plaintext | Letters right (worst / median) | Score per letter (worst) |
|---|---|---|---|---|---|
| Family I (12) | **12/12** | **12/12** | 7/12 | 79 / 97 | −1.95 |
| R26 (12) | **12/12** | **12/12** | 9/12 | 83 / 97 | −2.33 |
| 30 wrong-family negatives | — | — | — | — | best −3.06 (median −3.52) |

- **Both families are recoverable blind** from 97 letters with hidden word divisions.
- **The misses are vocabulary gaps:** Scots dialect ("AYE IN GUDE"), names ("BULLIVANT") and rare words in a
  dialect-heavy novel. They are not cipher failures.
- **Positives and negatives separate cleanly:** every positive scored −2.33 per letter or better, and every negative
  −3.06 or worse.
- **The development fix:** the first pass counted every unknown letter as its own word. That desynchronized the key
  phase and the R26 word counter, and gave 7/12 exact for R26. It is now fixed. The pilot messages are therefore
  development data; Phase B must use a fresh source.

## Plausibility against K4's flatness
- The test simulated 20,000 messages per family from other books.
- **Family I:** ciphertext IC has median 0.046; only **0.56%** are as flat as K4 (≤ 0.0361). Restarting the key at every
  word reuses its first 3–4 letters constantly.
- **R26:** median 0.038; **22%** are as flat as K4.
- This does not exclude Family I, but it makes Family I an unlikely explanation for K4, while R26 fits K4's main known
  property.

## Proposed Phase B (synthetic, sealed; needs Tyler's go-ahead)
**Data:**
- **Plaintext:** a fresh, standard-English GITenberg book not used anywhere before, pinned by sha256. Messages are whole
  words totalling 97 letters.
- **Positives:** 100 per family, with hidden settings.
- **Negatives:** 300 wrong-family ciphertexts: 40 each from R71's seven families, plus 20 frequency-preserving
  shuffles of positives.

**Frozen rules:**
- *Recovered* = right family, right setting (or a setting that decodes identically), and ≥ 90/97 letters right.
  *Exact* is reported too.
- *Confident* = best score ≥ −2.7 per letter, fixed now between the pilot's worst positive (−2.33) and best negative
  (−3.06).

**Gate:**
- ≥ 90/100 recovered and confident, in each family;
- **0/300 negatives confident**, a one-sided 95% bound under 1%;
- every recovered decode re-encrypts to its ciphertext.
- If either family fails, that family is not taken to K4.

**Cost:** about 500 ciphertexts × 1.8 s ≈ 15 minutes on one core.

**K4, only after a separate approval:**
- unchanged K4 + 100 shuffled nulls;
- all 70 settings decoded;
- every setting's best decode frozen and pushed;
- forward re-encryption verified;
- then the sealed published-letter check (R53).
- A K4 decode is a candidate only if it is confident and above every null.
