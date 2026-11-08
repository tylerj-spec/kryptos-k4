# R71 result (Claude Code, 7 Nov 2026): no tested cipher family explains K4's width-7 / width-21 fingerprints (NO_FAMILY)

**Ciphertext-only. No K4 decryption; the published letters were not used. No candidate.**

## Plain words
- **The fingerprints are real, and rare.** Scanning every width 2–48, as the test must since the widths were found
  by looking:
  - the doubled-letter column concentration (T1) is matched by **0.67%** of K4's shuffles;
  - the repeated vertical pairs (T2) by **0.99%**;
  - **both together by 82 in 1,000,000 (8 × 10⁻⁵)**.
  - The two marginal rates agree with Rondeau's published look-elsewhere figures (about 0.005 and 0.010).
- **No family produces them.** Seven families each encrypted about 100,000 fresh English messages with hidden random
  keys, matched to K4's letter flatness. They reproduce the joint signature only **1–5 times in 10,000**:
  - one-time pad and running key, as baselines;
  - periodic;
  - homophonic + route;
  - Gromark;
  - ciphertext autokey;
  - plaintext autokey.
- **The best candidates fall far short of the bar.** Homophonic (3.1×) and ciphertext autokey (2.6×) against the
  running-key baseline are the highest; the pre-registered bar was 10×. Every candidate's upper bound is below 10×.
- **Where the families fail:**
  - **No family concentrates doubled letters in one column.** Every family's T1 rate (0.57–0.70%) equals the shuffles'.
  - Homophonic + route and ciphertext autokey do raise the repeated-pair rate (7.9% and 4.1% vs about 2% for the
    baselines), but not the joint signature.
- **Pre-registered outcome: NO_FAMILY.** There is no R72 on this signature. The next input should be construction
  evidence (archival), not another family sweep.

## Steps
| Step | Commit | Result |
|---|---|---|
| Pre-registration (`r71/PREREGISTRATION.md`; tests passed) | 382044d | — |
| Run (`r71/run.py`, 6.5 min) | this commit | `r71/results/SUMMARY.json`, `run_log.txt` |

## Results (`r71/results/SUMMARY.json`; IC-matched samples)
**K4:** T1 = 2.945, T2 = 4.236 (D = 6, A₇ = 5, R₂₁ = 11, IC 0.03608).

| Family | Matched n | Acceptance | Joint J | q = J/n [99% CP] | T1 ≥ K4 | T2 ≥ K4 | Fixed (A₇≥5 & R₂₁≥11) | Mean IC |
|---|---|---|---|---|---|---|---|---|
| SHUF (K4 shuffles) | 1,000,000 | — | 82 | 8.2e-5 [6.1e-5, 1.1e-4] | 0.0067 | 0.0099 | 1 | 0.0361 |
| OTP (baseline) | 111,733 | 0.70 | 12 | 1.1e-4 [4.4e-5, 2.2e-4] | 0.0065 | 0.0177 | 0 | 0.0371 |
| RUNKEY (baseline) | 100,819 | 0.56 | 16 | 1.6e-4 [7.5e-5, 2.9e-4] | 0.0067 | 0.0204 | 0 | 0.0374 |
| PERIODIC | 108,941 | 0.45 | 15 | 1.4e-4 [6.3e-5, 2.6e-4] | 0.0066 | 0.0265 | 0 | 0.0375 |
| HOMOPHONIC + route | 101,735 | 0.28 | 50 | 4.9e-4 [3.3e-4, 7.0e-4] | 0.0057 | 0.0790 | 0 | 0.0382 |
| GROMARK | 106,492 | 0.44 | 25 | 2.3e-4 [1.3e-4, 3.9e-4] | 0.0067 | 0.0205 | 0 | 0.0376 |
| CTAK | 107,775 | 0.67 | 44 | 4.1e-4 [2.7e-4, 6.0e-4] | 0.0069 | 0.0413 | 1 | 0.0371 |
| PTAK | 101,861 | 0.57 | 22 | 2.2e-4 [1.2e-4, 3.7e-4] | 0.0070 | 0.0217 | 1 | 0.0374 |

**Decision** (reference baseline: RUNKEY, the highest baseline q):

| Candidate | Ratio vs baseline | Conservative lower bound | Upper bound | Status |
|---|---|---|---|---|
| PERIODIC | 0.87 | 0.22 | 3.44 | NOT_ENRICHED |
| HOMOPHONIC | 3.10 | 1.13 | 9.33 | NOT_ENRICHED |
| GROMARK | 1.48 | 0.45 | 5.13 | NOT_ENRICHED |
| CTAK | 2.57 | 0.91 | 7.93 | NOT_ENRICHED |
| PTAK | 1.36 | 0.40 | 4.87 | NOT_ENRICHED |

**Outcome: NO_FAMILY.**

- **Descriptive, by lag or period:**
  - joint cases are spread thinly. CTAK lag 21 has 4/3,783 (1.1e-3), the same as lag 5 (4/3,541); counts this small
    carry no weight.
  - PERIODIC period 7 has 0 joint cases.
  - Full counts are in `SUMMARY.json`.
- **Unmatched secondary (first 160,000–200,000 attempts):** joint rates are higher for the skewed-IC families (more
  repeats), but no family concentrates doubled letters. Counts are in `SUMMARY.json`.

## What this means
- **Established:**
  - K4's two fingerprints are jointly rare even after scanning all widths (8 × 10⁻⁵ against its own shuffles).
  - None of these families makes them notably more likely:
    - one-time pad, running key, periodic (2–30), homophonic + route, Gromark, ciphertext autokey (1–30), plaintext
      autokey (1–30);
    - each with any plaintext alphabet (AZ, KRYPTOS, random) and, by invariance, any ciphertext alphabet.
- **Caveats:**
  - The two features were themselves chosen from many possible ones by people inspecting K4. That multiplicity is not
    corrected, so 8 × 10⁻⁵ overstates the surprise by an unknown factor.
  - The matched families sit slightly above K4's IC (0.0371–0.0382 vs 0.0361), which inflates their T2 rates. This
    works against NO_FAMILY, and NO_FAMILY was still the outcome.
  - Families outside this set (other layered systems, nulls, physical copying processes) are untested.
- **Next:** per the pre-registration, no R72 on this signature. ChatGPT's archival fallback (worksheet and fabrication
  evidence) is the next input.
