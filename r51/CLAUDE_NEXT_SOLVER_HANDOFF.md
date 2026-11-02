# K4 research handoff after R50/R51 — stop narrow exact exclusions, pursue novel plaintext recovery

Date: 30 October 2026. All work already pushed. **No recovered K4 plaintext; no external checker submissions; main unchanged.**

## Question reset

The known `BERLINCLOCK` plaintext likely refers to a location or subject; there is **no primary evidence** that its clock faces supply the encryption key. Our prior R23 clock reconstruction is already fully available on `main` (historical 24-zone chart) and source work is not a dependency for a new ciphertext solver. Do not request redundant photos or re-run historical city-list keys.

Artist Sanborn's November 2025 remarks also associate K4/K5 with **delivering a message**, a 1986 Egypt journey and the 1989 Berlin Wall (source: Scientific American, 12 Nov 2025). These are narrative facts, **not candidate plaintext to inject**.

## Completed exact R50 (pre-transposition Gromark)
- [PR #20](https://github.com/tylerj-spec/kryptos-k4/pull/20), [full report](https://github.com/tylerj-spec/kryptos-k4/blob/chatgpt/r50-pretransposition-keyword-feasibility/r50/RESULTS_AND_REPLICATION.md).
- K3-style four 24x8 quarter-turn routes applied **before** substitution (opposite order to R46), all 100,000 decimal 5-digit Gromark primers, ±, keyword PA/free CA or free PA/keyword CA, 4,749 common + 12 additional themed alphas.
- K4 full-free feasible primers by CW/fwd, CW/inv, CCW/fwd, CCW/inv: **52 / 1,569 / 1,479 / 8,805**. Keyword/free matches **0 / 0 / 0 / 0**. 20/20 controls, 2 nulls, complete prefilter, sampled full brute confirmations; **independent C++ full-free arithmetic engine agrees on every route**.
- K4 exact `EXCL` for only this finite model. No decryption.

## Completed exact R51 (a genuinely different keystream, no Gromark)
- [PR #21](https://github.com/tylerj-spec/kryptos-k4/pull/21), [full report](https://github.com/tylerj-spec/kryptos-k4/blob/chatgpt/r51-ciphertext-feedback-k3-feasibility/r51/RESULTS_AND_STRUCTURE.md).
- Same four **T_then_S** K3 double rotations, but `k[j] = AZ_or_KRYPTOS_rank(C[j-L])` for lags **1..24** with first L seeds **completely free**. ±, both keyword orientations, identical finite dictionary 4,761. Zero BERLIN CLOCK or source-word input to key generator.
- Two-free possible lag/basis combos by the same routes: **2 / 8 / 6 / 21**, total 37/192; keyword/free matches **0 / 0 / 0 / 0**. 20/20 independent feedback-encrypt/reverse-positive controls, 2 nulls, sample full-brute matches, independent C++ graph-feasibility check exactly agrees.
- **NEW STRUCTURAL FINDING:** all **37** full-free survivor models close **zero independent public-clue graph cycles**, even when all 24 artist-confirmed letters are outside the free-seed region. The remapped 24 letters are a **forest of constraints** under these particular K3 routes. Full 97-character forward-encryption feasibility with two free alphabets is therefore massively underdetermined and not a candidate discovery. This is more informative than adding zeroes to a broad key catalog.
- Exact `EXCL` only the four route/lags/key maps/keyword class; the full-free model remains far too flexible to infer any new text.

## Recommendation: an actual **positive predictive** research round

**Stop treating more constrained-family exclusions as the primary product.** The two-free unknown alphabet/unknown keystream problem is still the bottleneck; R44b's 20/20 known-key result is valid but insufficient for K4.

Choose and preregister one of the following after independent review:

**A. Solve two-free alphabets on real-text controls when the key is given (first gate).** Replace the failed R43 left-to-right lexical beam (correct plaintext dies by letter 2/10), which Claude already audited. Use **nonsequential word/phrase placement + modular cycle/full-bijection propagation and global language completion**. Evaluate on previously authored D0 plants then a **NEW untouched 20-message holdout**, requiring >=16/20 exact 97-letter matches and correct forward re-encryption. Real keys not leaked. Do NOT introduce EASTNORTHEAST or BERLINCLOCK into this solver; actual K4 ciphertext is *not run* before passing.

**B. Recover unknown keystream jointly with plaintext (next gate).** After A succeeds, vary a **predeclared source-derived or stateful key mechanism**, including its hidden seed/primer. Must fully decode >=16/20 **new, untouched** 97-letter plants with **keys NOT supplied to the decoder**, not just produce 24-crib feasible witnesses. Compare all wrong-key controls and scrambled-text nulls.

If an architecture cannot meet these gates, stop and report a failure, not a 'promising' word score. If it passes, independently re-encrypt a full K4 plaintext from the untouched ciphertext using frozen parameters; commit original full 97 letters **before** consulting the public 24 letters; only then assess the candidate and request external validation if owner authorizes.

**Claude action requested** (owner may forward): independently audit R50/R51 arithmetic and 37 zero-cycle assertion, then take **A** as the next tangible solver contribution; avoid the World Clock as an unproved key and avoid tuning R44b's already-excluded Gromark keys. If A is genuinely impossible without extra language context, identify a mathematically sound alternative with its own pre-registered fresh challenge.

No code needs committing by the user; work and tests are already in the respective GitHub review PRs.
