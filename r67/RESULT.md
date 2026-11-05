# R67 result (ChatGPT design, Claude Code production run, 5 Nov 2026): K4's SNAKE_L route gap is unusual against real structured ciphers too

**No K4 solution, and none was possible: R67 never decrypts K4.** It is a pre-registered *calibration* of one statistic
that was noticed after looking at K4 (R64/R65). No published K4 letters were used anywhere. No external checker was
contacted.

## Plain words
- **The question:** R65 showed that K4's German-model route gap (SNAKE_L, 28.5 points ahead of the next route) beats 300
  shuffled copies of K4. But shuffles destroy all structure, so any real cipher might beat them. R67 asked whether real
  ciphertexts from six structured cipher families also produce gaps that large. The 192 controls were matched to K4's
  flat letter counts.
- **They don't:**
  - **gap:** 0 of 192 reached K4's gap (largest 25.5, median 4.1); none of the six families had a single case;
  - **best-route score:** none had a best-route score as high as K4's SNAKE_L score;
  - **mirror contrast:** only 1 of 192 had SNAKE_L ahead of its mirror route SNAKE_R by as much as K4 (+39.7).
- **The test can detect what it looks for:** 24 planted English-plus-German-key messages were found 21 times with the
  right route and a gap at least K4's. This includes 11 of 12 that used SNAKE_L.
- **But K4 doesn't look like those positives either:**
  - K4's SNAKE_L score (−320.9) is only 1.8 above the best structured control (−322.7);
  - true German-key messages scored −326 to −224 (median −258);
  - R65b already showed, with near-full power, that the key letters forced at the published positions are not German.
- **Net:** K4 read in SNAKE_L order carries some structure that neither shuffles nor these six cipher families
  reproduce. It is not a German running key, and R67 cannot say what it is.

## Steps
| Step | Commit | Result |
|---|---|---|
| Pre-registration (ChatGPT; `r67/PREREGISTRATION.md`, sha256 d1e7208b…) | 28af317, ada01e3 | — |
| Local QA: tests 5/5, protocol hash | — | pass |
| Erratum 1: `solver_source` pin restored to R65's frozen value (the committed pin was a 65-character splice of two hashes) | 1fc55f7 | before any production step |
| Pinned sources built (German = Europarl file 10, byte-identical to R63's held-out file) and 216 controls generated (seed 670001; truth sha256 ee3af82d… withheld) | d051cef | every family filled |
| Isolated sandbox (no Docker daemon here; namespaces: no network, uid 65534, read-only root, only the 13-file stage and `/out`); smoke-tested | 0b26498 | — |
| Blind run in the sandbox, freeze | cff0dd2 | 216 results, 864 raw files |
| `verify_controls.py` (truth not opened) | d3bf4b8 | **PASSED**: 10 pins, both manifests, 32,400 witnesses |
| Truth opened (hash matched); `analyze_controls.py` | 1b2b0fa | below |

## Pre-registered results (`r67/production/REPORT.json`)
**Nuisance controls** (K4's gap 28.4979; K4's best total −320.86; K4's SNAKE_L − SNAKE_R +39.68):

| Family | Accepted / attempted | G ≥ K4 | Rate (1+ge)/33 | Best route SNAKE_L | Gap median / max | Best total ≥ K4 | 2nd-best ≥ K4 | SNAKE_L−SNAKE_R ≥ K4 |
|---|---|---|---|---|---|---|---|---|
| OTP | 32 / 55 | 0 | 0.030 | 2 | 3.5 / 14.6 | 0 | 25 | 0 |
| PERIODIC_VIG | 32 / 97 | 0 | 0.030 | 4 | 5.6 / 22.5 | 0 | 23 | 0 |
| QUAG_III | 32 / 79 | 0 | 0.030 | 4 | 5.8 / 17.3 | 0 | 21 | 0 |
| PLAINTEXT_AUTOKEY | 32 / 47 | 0 | 0.030 | 6 | 4.3 / 13.0 | 0 | 22 | 0 |
| QUAG_III_ROUTE | 32 / 70 | 0 | 0.030 | 2 | 3.5 / 15.3 | 0 | 22 | 0 |
| HOMOPHONIC_ROUTE | 32 / 871 | 0 | 0.030 | 6 | 4.1 / 25.5 | 0 | 25 | 1 |
| **Pooled** | 192 | **0** | **q_pool = 1/193 = 0.005** | 24 | 4.1 / 25.5 | **0** | 138 | 1 |

- **Positive controls** (English plaintext, Europarl-German key, a route):

  | Group | Right route | G ≥ K4 | Both | Median G |
  |---|---|---|---|---|
  | All 24 | 22 | 21 | **21** | 73.5 |
  | SNAKE_L (12) | 12 | 11 | 11 | 81.3 |
  | Other routes (12) | 10 | 10 | 10 | 54.4 |

  - The three misses: two sister K3 rotations (CW ↔ CCW) and one correct SNAKE_L at G 22.2.
- **Pre-registered reading:** q_pool < 0.05 with adequate positive sensitivity, so K4's gap is **unusual within these
  six IC-matched families, conditional on the matching**.
  - This is not a fresh p-value: the statistic was chosen after looking at K4.
  - It identifies no route, cipher, key or plaintext.
- **Selection disclosed:** IC matching kept the flatter tails. Homophonic kept 32 of 871 attempts; the periodic families
  lean to long periods (distributions in `REPORT.json`). No unmatched companion run was made, as pre-registered.

## Exploratory (not pre-registered; frozen witnesses only, no new solves)
- **Method:** each run's best decomposition, split into its two streams and scored by the language models alone (no
  word score).

| | K4 (SNAKE_L) | Structured controls (n=192): median / max / number ≥ K4 | German-key positives (n=24): median / max / number ≥ K4 |
|---|---|---|---|
| Plaintext, English model | −85.0 | −82.4 / −71.4 / 125 | −64.3 / −54.5 / 24 |
| Key, German model | −63.4 | −67.9 / −53.4 / 32 | −53.4 / −43.4 / 23 |

- **Reading:** neither stream is extreme on its own.
  - K4's plaintext side is ordinary; its key side is in the top sixth of the controls.
  - Its edge over the controls comes from the combination (and the word score).
  - Both sides are far below real German-key messages.

## What this means
- **Established (STAT, descriptive):** K4's letter order under the SNAKE_L reading (rows 2 and 4 of the 4+31+31+31
  layout reversed) fits an English-plaintext / German-key decomposition better than shuffles (R65) and better than real
  ciphertexts from these six families (R67).
- **Still rejected with high power (R65b):** a German running key on SNAKE_L with English plaintext.
- **Open:** what the structure is. Candidates worth a separate pre-registered look:
  - other keyed systems not in these six families, e.g. Gromark-type or two-alphabet systems;
  - a physical property of the engraved layout, e.g. row-wise processing in alternating directions.

  These are hypotheses, not findings.
- **Not a K4 candidate:** no decode from R67 is a K4 candidate, and none was produced.
