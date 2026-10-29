# R40G research findings — 28 October 2026

## 1. Mathematical degeneracy in the R39 IC ranking (proved)

Five-digit Gromark recurrence is linear over the ring `Z/10Z`. Multiplication by any of the four invertible residues `1,3,7,9` relabels every key-digit group bijectively, so the **key-conditioned IC score is identical** for all keys in that orbit, on *every* ciphertext. Burnside gives exactly 25,024 orbits under those transformations, down from 100,000 primer labels. In the R39 top four, `27641, 61823, 49287, 83469` are one such orbit, not four independent discoveries.

## 2. Independent larger null test (ciphertext only; no K4 known words)

Preregistered in `r40g/PREREGISTRATION.md`, then built and run using a separately written C++ implementation, using 1,000 seed-40001 letter-frequency-preserving shuffles of the original K4 ciphertext.

- Verified original maximum IC: `0.075107296137339061` (representative `27641`), agreeing with R39.
- **716 / 1,000** shuffled ciphertexts attained maximum IC >= K4; four tied K4 exactly.
- Exceedance estimate with plus-one correction: **717/1001 = 0.71628371628371623**.
- Null median maximum **0.0770925110**; 5th percentile **0.0714285714**; 95th percentile **0.0871459695**.

This is strong evidence **against using maximum IC to distinguish K4 from its letter-shuffled controls**. It does not mathematically exclude Gromark, nor identify any key or plaintext.

Independent local output SHA256: `aca8343ebed0b5ab896816a0976abfb3147dc8bdf0487df245a3b194c7e304c2`. A GitHub Actions reproduction is configured; treat that separate execution as unconfirmed until its logs and/or committed output are checked.

## 3. Postfreeze intersection with exact two-free-alphabet 24-letter constraints

Predeclared in `r40/POSTFREEZE_ORACLE_PREREGISTRATION.md`, and then scored using all 100,000 R39-defined blind IC settings with the independent known-clue constraint oracle.

- Exactly **39 / 100,000** five-digit primers fit the published clue graph under the direct, identity-route, two-free-alphabet Gromark model (same as prior independent toolkit finding).
- **0** feasible keys in the **top 100** IC, **0** in the **top 1,000**, and **1** in the **top 5,000**.
- Best feasible key: `98800`, blind IC rank **1,436** of 100,000, score `0.05622489959839357`.
- Next best feasible keys: `10319` (rank 6,874), `70173` (rank 6,929), `20707` (rank 9,247).
- Crib constraints and blind scores are both derived from the SAME ciphertext: no naive independence p-value or candidate claim is justified. Even a complete fit to these 24 letters would be only crib-feasibility, **not full plaintext recovery**.

The known words were **never** used to generate R39 rankings or R40's independent null maxima. The intersection is a separately labeled **postfreeze** reveal.

## 4. Development-only repeated-pattern optimizer — clear negative result

On 20 already-revealed R39 planted examples with each true 5-digit key supplied, intermediate symbol sequences under the actual cipher alphabets have on average **8.45 duplicate trigram pairs**; 1,000 random wrong cipher-alphabet permutations per example average roughly **0.35**. However, a naive annealer optimizing unigram/digram/trigram/tetragram repetition overfits: on five development controls, the best **incorrect** alphabet permutation achieved scores far exceeding the actual alphabet's score, recovering at most **4/26** cipher-alphabet positions up to overall rotation. This is **not** a valid solver. The diagnostic used secret letters only for evaluation after optimizing and did **not** run on K4.

Implication: the next candidate method needs a proper English language likelihood and independent planted exact-text recovery, not pure IC or repeated patterns.

No verified K4 solution, no external verifier contact.

**Independent replay:** Claude's integration review in the merged repository ledger (L137) separately reproduced 716/1,000 and the 39-primer intersection. This is still not a plaintext candidate.
