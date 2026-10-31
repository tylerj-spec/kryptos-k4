# R54 — Identify likely K4 encryption METHOD before attempting K4 keys

**Owner priority, 31 Oct 2026:** Determine the encryption *method/family first*. Only search a K4 key once the cipher model has an independently defensible mechanism and passes hidden-key control recovery. No public K4 plaintext letters or their locations may be supplied to a solver, feature extractor, classifier, key ranker, or candidate generator. Published letters are **only a separate after-freeze validation**, never search input.

**This experiment is ciphertext-only. It knows nothing about K4's confirmed plaintext.** Original 97-letter K4 ciphertext and the independent, already solved K1–K3 plaintext are the *only content inputs*. A no-network, read-only, unprivileged Docker container mounts just those two files and `r54/blind/method_fingerprint.js`. The program cannot read the repo, any sealed code, prior crib-conditioned outputs, or the owner's confirmed plaintext.

## Hypothesis framework

The correct K4 mechanism is **not known**. The first question is whether the ciphertext has the frequency signature of:
1. **A pure transposition** of ordinary English. Letter counts and index of coincidence are conserved exactly. A traditional *single bijective substitution alphabet* also conserves these quantities, though the literal letters change.
2. **A changing/multiple substitution alphabet / Vigenère-like cipher**. Different plaintext occurrences can map to different ciphertext letters; index of coincidence often approaches the uniform random 1/26 baseline.
3. **A layered or homophonic/other frequency-flattening algorithm.** This can also produce near-random letter histograms. No inference about exact routes/keys can be made from a histogram alone.

### Preliminary descriptive statistics observed before R54 code was committed

- **K4 length:** 97 ciphertext letters, all **26 A–Z** represented.
- **K4 IC:** `0.03608247422680412`. For reference, random uniform A–Z has theoretical expectation `1/26 ≈ 0.03846`; standard independent-English marginal model is around `0.0655`.
- **K4 Shannon entropy of observed letter histogram:** about `4.55478` bits/letter. This is a frequency statistic, not a claim of information-theoretic key entropy.
- **1,009 overlapping 97-letter windows of K1–K3's actual known English plaintext:** *none* have IC this low; their minimum was `0.05326460481099656`. They overlap substantially; do not treat as 1,009 independent p-value samples.
- **40,000 frequency-preserving shuffled K4 sequences, all lags 1–48:** observed strongest lag 7, 9/90 equal letters, `z≈3.04`; a peak as high somewhere among 48 lags occurred `≈14.8%` of the time in an exploratory Python implementation. Lag 7 is **not** independently persuasive. R54 uses a new deterministic Node implementation, and its recorded number may differ slightly.

These findings **reduce** the plausibility of pure route transposition or a single fixed substitution on normal English. They **do not exclude** these mechanisms for highly atypical, frequency-balanced original plaintext. They also cannot distinguish running-key, polyalphabetic, homophonic or two-layer methods from each other.

## Method-first calibration—NO K4 keys searched

`r54/blind/method_fingerprint.js` performs all calculations without any K4 plaintext words or positions:

- Count all letter occurrences, IC, distinct letters, entropy and repeated n-grams.
- Compare all contiguous 97-character windows from the independent K1–K3 plaintext; preserve the source SHA256 and count of windows.
- Calculate the probability of this low an IC under 200,000 independent draws from generic English unigram probabilities (an **approximate synthetic baseline**, not a model of Sanborn's full writing).
- Examine every lag 1–48, then re-run 40,000 letter-frequency-preserving permutations of the K4 ciphertext. Report **familywise maximum-lag corrected** probability.
- Sample independent K1–K3 plaintext windows with randomly generated *synthetic* Vigenère shifts of lengths 1, 2, 3, 5, 7, 11, 17, 31 and 97 (6,000 each). Report how frequently each *model class* produces as low an IC as K4. These are model-family calibration keys, **never fitted or applied to the K4 ciphertext**.

The printed JSON is a **descriptive method fingerprint**, not a Bayesian probability a particular cipher was used, nor a claim that a specific cipher has been identified. The synthetic families only check rough distributional compatibility; their priors may not reflect Sanborn's actual composition.

## Strict interpretation and next experiments

A real advance requires identifying a **mechanism with low parameter count and independent justification**, showing it can recover a fresh set of full 97-letter planted messages **when both actual keys and plaintexts are hidden**, then freezing original K4 ciphertext-only 97-letter output before an isolated known-letter comparison. `r53/BLIND_RULES.md` and [PR #23](https://github.com/tylerj-spec/kryptos-k4/pull/23) enforce that order.

**Hashing note:** A modern cryptographic one-way digest is not a reversible encryption scheme; it is extraordinarily implausible that a 97-letter handmade K4 was meant to be decoded by reversing a hash. Method candidates should therefore be reversible transformations or mechanisms with an independently recoverable secret key, unless strong external evidence suggests a hash/preimage construction.

Historical K4 crib-conditioned exclusions (R45–R52 and the example fitted primer 98800) remain historical research records, **not valid blind candidate-generation sources under the owner's current rule**. No K4 clue texts/positions enter R54's code, container or analysis, and no external validator is queried.

Research status: **METHOD DIAGNOSIS**, not a solved K4. Main remains unchanged.
