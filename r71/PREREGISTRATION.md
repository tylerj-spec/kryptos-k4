# R71 pre-registration (Claude Code, 7 Nov 2026): which cipher families produce K4's width-7 and width-21 fingerprints?

Written before any R71 statistic is computed on K4 or on any synthetic sample. Revises ChatGPT's design in PR #58
(`research/COA_R71_POST_R69_R70_2026-11-07.md`); changes are listed at the end. Tyler approved proceeding with R71
on 7 Nov 2026.

**Ciphertext-only.** R71 decrypts nothing and never uses the published K4 letters. No R71 code contains them
(checked by `r71/tests/test_r71.py`).

## The two fingerprints (published observations, rechecked from the carved ciphertext)
- **Width 7:**
  - K4 has 6 doubled letters (BB, QQ, SS, SS, ZZ, TT). Their 0-based start positions are 18, 25, 32, 42, 46 and 67.
  - 5 of the 6 starts fall in the same column mod 7.
- **Width 21:** written at width 21, K4's 76 vertical letter pairs contain 11 repeats beyond the first occurrence (Bean,
  HistoCrypt 2021).

These were found by people inspecting K4. A single-width p-value is therefore not evidence. R71 scans every width
2–48 for every ciphertext, so the choice of width is paid for. The choice of these two features from all possible
features cannot be corrected, and this is disclosed.

## Statistics (`r71/features.py`)
Every ciphertext, K4 and synthetic alike, gets the same statistics:

- **T1, doubled-letter column concentration at any width:**
  - D = the number of doubled-letter starts.
  - A_w = the largest number of those starts in any one column mod w.
  - P1_w = the exact probability that D start positions drawn uniformly from 0–95 give a column count ≥ A_w. This is
    computed by a product of binomials, with no simulation.
  - T1 = −log10 min over w = 2–48 of P1_w, and 0 when D < 2.
- **T2, repeated vertical pairs at any width:**
  - R_w = the repeats among the ordered pairs (C[i], C[i+w]).
  - Z_w = (R_w − m_w) / s_w, where m_w and s_w come from 100,000 reference shuffles of K4 (seed 710001).
  - T2 = max over w = 2–48 of Z_w.
- **Joint event J:** T1 ≥ T1(K4) **and** T2 ≥ T2(K4). This is the primary event.
- **Fixed-width event (descriptive only):** A_7 ≥ 5 and R_21 ≥ 11.
- **Invariance:** all statistics are unchanged by relabelling ciphertext letters. A keyed or free ciphertext alphabet
  therefore cannot change them, including inside ciphertext-autokey feedback. This is why "two free alphabets" variants
  reduce to their plaintext-alphabet structure here.

## Families (`r71/generators.py`; exact definitions in the file's docstring)
**Plaintext:** fresh English windows at random offsets.
- Sources: Childers, *The Riddle of the Sands* (GITenberg 2360) + Conrad, *The Secret Agent* (974).
- Neither book has been used as plaintext in this project.

**Hidden random keys and conventions:**
- Plaintext alphabet Ap ∈ {AZ, KRYPTOS, random} where it applies.
- Operation ∈ {VIG, BEAU, VARB}.

| Family | Role | Definition |
|---|---|---|
| OTP | negative baseline | uniform independent key |
| RUNKEY | negative baseline | running key from Buchan, *The Thirty-Nine Steps* (GITenberg 558); tableau AZ or KRYPTOS |
| PERIODIC | candidate | period 2–30, uniform shifts |
| HOMOPHONIC | candidate | R66's frequency-proportional homophonic table, then one of the 10 R61 routes |
| GROMARK | candidate | 5-digit primer, d_t = d_{t−5} + d_{t−4} mod 10 (Bean's motivation for width 21) |
| CTAK | candidate | ciphertext autokey, lag 1–30, random primer |
| PTAK | candidate | plaintext autokey, lag 1–30, random primer |

- **SHUF:** 1,000,000 fresh frequency-preserving shuffles of K4 (seed 710002) give the reference null.
- **Lag and period ranges are uniform over 1–30 (2–30 for PERIODIC).** They are deliberately not restricted to 7 or
  21. Rates by lag and period are reported descriptively.
- **Dropped from PR #58:** the "7-phase key-advance" sub-arm. It could not be defined without fitting K4.

## Sampling and matching (`r71/run.py`)
- **Batches:** 20,000 per draw, seed 710010 + family index.
- **Stopping:** each family runs until 100,000 IC-matched ciphertexts or 3,000,000 attempts.
- **Matched (as R67):**
  - |IC − IC(K4)| ≤ 0.004;
  - ≥ 25 distinct letters.
- **Primary analysis:** IC-matched.
- **Secondary:** the first 200,000 attempts, unmatched.
- **Reported per family:**
  - attempts and acceptance rate;
  - J count and q = J / n with Clopper-Pearson bounds;
  - the marginal T1 and T2 tail counts;
  - the fixed-width count;
  - J by lag or period.
- **Compute cap:** about 1 hour on 4 cores. Development smoke tests took about 0.1 ms per ciphertext.

## Decision rule (fixed now; `decide()` in `r71/run.py`)
1. **NOT_DISTINCTIVE** if q_SHUF > 0.01: after the width scan, K4's joint signature is not rare even among its own
   shuffles. Stop R71 and R72 on this signature.
2. **Baselines:** SHUF, OTP and RUNKEY (matched). The baseline with the highest q is the reference.
3. **PROMISING:** a candidate family qualifies if all three hold:
   - ≥ 30 joint cases;
   - q_f / q_baseline ≥ 10;
   - the conservative lower bound min over baselines of (q_f lower bound / q_b upper bound) > 3.
   Bounds are Clopper-Pearson, one-sided at 0.005 each, i.e. family-wise 0.05 over 5 candidates.
4. **NOT_ENRICHED:** a candidate whose ratio upper bound (q_f upper bound / q_baseline lower bound) is < 10.
   Otherwise it is **LOW_POWER**.
5. **Outcome:** PROMISING if any candidate is PROMISING; else LOW_POWER if any is LOW_POWER; else **NO_FAMILY**.

## What follows
- **PROMISING:** R72 may build a blind solver for that family, choosing the variant **not already excluded**. R68's
  crib-assisted exact checks exclude periodic p ≤ 25, Gromark and CTAK L ≤ 71 with AZ/KRYPTOS plaintext alphabets.
  That leaves, for example, a random plaintext alphabet. R72 must pass hidden-plant gates before touching K4, and
  freeze before any published-letter check (R53).
- **NO_FAMILY or NOT_DISTINCTIVE:** no R72 on this signature. Archival construction evidence is the next input.
- **LOW_POWER:** report it. Nothing is enlarged, re-thresholded or re-run on the basis of K4's numbers.

## Changes from PR #58's draft
- **Exact definitions:**
  - T1 is defined exactly (no simulation);
  - T2 is width-normalised against fixed K4 shuffles;
  - the joint event is a single 2-D tail, not a product of p-values.
- **Ciphertext-alphabet invariance** is stated, which collapses free-ciphertext-alphabet variants.
- **The classification power gate (≥ 80% sensitivity / ≤ 1% false positives) is replaced** by an estimability rule
  (≥ 30 joint cases) and Clopper-Pearson bounds on the enrichment ratio. A two-number summary of one 97-letter
  ciphertext cannot classify families at 80/1. The question R71 can answer is the likelihood ratio.
- **Lag and period ranges** are uniform over 1–30, not chosen as {1, 7, 21}.
- **Sample sizes** are larger (1,000,000 shuffles; up to 100,000 matched per family), since the joint tail may be near
  10⁻⁴.
