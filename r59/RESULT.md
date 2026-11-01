# R59 completed: one-time-pad identifiability and empirical masking diagnostics

**Result: R59 successfully calibrated its short-period masking detector, but original K4 showed no statistically significant deviation from uniform. This does NOT establish that K4 used a true one-time pad. No K4 plaintext or key was recovered.**

## Research question and historical motivation

Ed Scheidt said he deliberately obscured the expected frequency statistics of English in K4 and that identifying the underlying technique was the challenge (WIRED, 21 Jan 2005). This does **not** identify how masking was applied, whether there is more than one layer, or whether an actual OTP was involved. A true one-time pad is itself an encryption method, not an alternative to encryption.

Earlier Claude/ChatGPT work in the canonical ledger:
- **L26** general masking and unknown pre-encoding still OPEN.
- **L81–L83** explicit limited null insertion/deletion/salting methods: no convincing output. The original exploratory workflows were not equivalent to the strict R53 ciphertext-only rule.
- **L31, L90, L106, L109–L127** several specific running-key passages, K1–K3 materials, Carter 1923 book text and layered routes: negatives in bounded search conventions, not all possible book keys.
- **L49–L50** recurrent keystreams and physical tableau paths within their assumptions; no K4 solution.
- **R55/R56/R58** small affine feedback, evolving alphabets, tableau/physical-route masks: no K4 solution in tested classes (R58 held under [PR #31](https://github.com/tylerj-spec/kryptos-k4/pull/31)).
- **Claude R52 on PR #12** remains historical/crib-conditioned and does not identify a cipher or suitable seed key for a compliant blind decryption.

## Why the genuine OTP is unidentifiable from original ciphertext alone

For each position in a 26-letter alphabet, `C[i]=(P[i]+K[i]) mod26`.
With an independent, uniform, secret, never-reused `K[i]`, EVERY candidate 97-letter plaintext has **exactly one** compatible 97-letter key, and that key occurs with probability `26^-97`. Consequently, `Pr(C|P)=26^-97` regardless of `P`. No amount of ciphertext-only computation can prefer the correct plaintext when the ideal OTP assumptions hold.

That means deriving `K[i]=(C[i]-P[i]) mod26` from a guessed K4 message and re-encrypting it to match K4 is **not** a decryption, but a reversible tautology. The blind R59 source never calculates a proposed K4 pad and never sees the 24 released letters. Our **simulated pseudo-uniform pads** use a reproducible seeded PRNG for test repeatability and are emphatically **not operationally secure true OTPs**.

## Fixed preregistration and provenance

- [Protocol and pre-control seeded-PRNG clarification](PREREGISTRATION.md) were committed before creating any R59 controls or K4 statistical outputs.
- 90 unknown-source/unknown-key controls, 30 each of:
  1. 97-symbol independently sampled-looking simulated uniform pads.
  2. A uniformly chosen length-3..6 random key repeated across all 97 characters.
  3. A 97-letter **contiguous key from a separate public-domain book**, not repeated or derivable from plaintext.
- Controls from pinned `GITenberg/The-Time-Machine_35` and `GITenberg/The-Adventures-of-Sherlock-Holmes_1661` Git blobs (exact checksums in protocol), with independently selected, non-overlapping 97-letter English passages.
- Neutral, interleaved ciphertext-only IDs; both true plaintext and true key/family hidden from the blind scanner, which ran in a no-network, unprivileged, read-only Docker container without source books, truth files, repository, K4 public clue text or clue positions.
- **Four fixed feature families**: (1) two-sided absolute global index-of-coincidence deviation from uniform (2) maximum pooled periodic-column IC for periods 2–12, (3) maximum standardized lag-repeat equality for lags 1–24, (4) maximum independently shifted English-monogram log likelihood for periods 2–12.
- Calibration: **4,000** simulated iid-uniform ciphertexts for individual upper-tail p-values, an independent **4,000** for the familywise maximum-evidence distribution. `p<=0.01` rejection threshold set in advance. No K4-tuned thresholds.
- Complete original 90+1 encrypted inputs, raw feature values, p-values and hashes remotely Git-frozen **before** the distinct evaluator regenerated any synthetic plaintexts/keys/labels. Original output SHA256: `5f81c4b75e61ceb252ce2353a01b01dbc153d813f5b556fd652f5f4fb58193f2`.
- After freeze: **90/90 independently forward-encrypted full synthetic control witnesses** passed. No K4 plaintext was generated or compared to released letters.

## R59 control results: detector sensitivity and false positives

| Independently generated 97-letter ciphertext type | Marked nonuniform (familywise p≤0.01) | Not flagged | Interpretation |
|---|---:|---:|---|
| Reproducible, simulated uniform pad | **1/30** | 29/30 | False-positive rate in a very small control sample is compatible with chance. NOT an actual secret OTP. |
| Short repeated key / periodic mask (period 3–6) | **28/30** | 2/30 | Good detection power for *this* predetermined short-period mask family. |
| Full-length book-running key | **0/30** | 30/30 | No detection power here. A determinate, structured 97-character key may appear fully uniform under these features. |

Both preregistered controls passed: simulated-pad false positives ≤2/30, periodic-mask detections ≥20/30.

## Authentic original K4: raw blind result

| Predeclared feature | Observed K4 value | Individual upper-tail p (4000-null cohort) |
|---|---:|---:|
| Absolute IC deviation from 1/26 | 0.0023790642 | 0.3901524619 |
| Max pooled column IC, m=2..12 | 0.0449172577 | 0.7553111722 |
| Max lag equality standardized z, lags 1..24 | 3.0357865538 | 0.1149712572 |
| Max shifted English-monogram log likelihood, m=2..12 | 20.2159049648 | 0.9735066233 |

**Predeclared familywise p = 0.3399150212** (≈0.340), far above the 0.01 departure threshold. The strongest single-feature uncorrected tail is the lag-equality maximum (≈0.115), which is itself not significant; after correcting across four feature families, the global result is even weaker. No sign of the tested short-period mask stands out.

This tells us only that K4's 97-letter ciphertext is **statistically compatible with the chosen simulated iid-uniform null** under these tests. It cannot distinguish:
- a cryptographically secure never-reused true one-time pad;
- a deterministic 97-letter running key (our 0/30 result directly demonstrates this weakness);
- a nonlinear or nonperiodic masked tableau, complex fractionation/substitution;
- other unmodeled physical or semantic transformations.

The K4 ciphertext was not modified. The 24 published known letters were neither mounted, read nor otherwise supplied to the scanner. Because R59 produces no candidate plaintext, there is intentionally **no** postfreeze 24-letter candidate comparison.

## Next defensible research direction

**Do not brute-force arbitrary 97-letter pads or invent an "OTP solution" by subtracting an English guess.** If a true OTP is involved, a ciphertext-only solve is mathematically impossible without new key evidence or a broken OTP assumption. Research should prioritize independent evidence about how a K4 keystream could have been manufactured: physical construction notes, 1980s–1990 original source editions, correspondence, or a historically supported text/sequence with exact provenance and length. When such a source is available, preregister a small finite extractive/keyed masking model *before* new ciphertext-only attempts, with hidden-key and unknown-model controls, nulls, remotely frozen 97-letter outputs and postfreeze validation.

If no independent key source can be established, develop out-of-family masking diagnostics or the R58 process classifier further on fresh synthetic controls. Statistical regularity alone is not a substitute for a derived method.

**No external Kryptos checker contacted, no new K4 plaintext/key, and no automatic change to `main`.** This negative/inconclusive result is a meaningful calibration of the feasible attack surface, not a claim the ciphertext is an OTP.
