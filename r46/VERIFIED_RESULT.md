# R46 completed result and independent indexed replay (29 October 2026)

**Outcome: EXCL, exactly the finite pre-registered model. No K4 plaintext has been generated.**

- Original protocol SHA256 `efcde4e8c05a91c82bb63c99483447407bf7b1623954ede7ae4e7f7c299c2e0f`.
- Full original Python exact run: [GitHub Actions 40928087044](https://github.com/tylerj-spec/kryptos-k4/actions/runs/40928087044), artifact [12921939261](https://github.com/tylerj-spec/kryptos-k4/actions/runs/40928087044/artifacts/12921939261).
- Independently optimized reimplementation: [GitHub Actions 40931330834](https://github.com/tylerj-spec/kryptos-k4/actions/runs/40931330834), artifact [12922327694](https://github.com/tylerj-spec/kryptos-k4/actions/runs/40931330834/artifacts/12922327694); its source/operational amendment is in [PR #17](https://github.com/tylerj-spec/kryptos-k4/pull/17).
- Uncompressed original raw `R46_EXACT_RESULT.json` **SHA256** `352e4547b527531be5bec3ad0eceb0e49f055d5b06f5dca98e797bc1b0f248be` (805,202 bytes).
- Uncompressed indexed raw `R46A_RESULT.json` **SHA256** `fde17a2eaea03985703b0b270d91a6e01c380a3f5669f5afbe1b7a5052e46692` (808,988 bytes).
- Those two raw JSON hashes differ **because the indexed report includes extra index-diagnostic metadata**; every common scientific field was independently compared and is **exactly equal**, including **every two-free-feasible primer list, every keyword-compatible setting, each substitution-layer ciphertext SHA256, both shuffled-null outputs/seeds, and positive-control truth**. Both GitHub Actions were successful. The raw artifacts are retained by GitHub Actions for 90 days; this permanent note retains their exact SHA256 digests and reproducibility instructions.

## Exact original K4 outcomes

| Pre-registered route (S_then_T) | Both-alphabet-free feasible 5-digit primers | Keyword PA/free CA matches | Free PA/keyword CA matches |
|---|---:|---:|---:|
| R24x8/CW/fwd | 79 | 0 | 0 |
| R24x8/CW/inv | 1,643 | 0 | 0 |
| R24x8/CCW/fwd | 1,486 | 0 | 0 |
| R24x8/CCW/inv | 9,502 | 0 | 0 |

All 100,000 five-digit primers were tested per route, both plus/minus arithmetic signs, all 4,749 independently defined R44b keyword alphabets in both PA/free-CA and CA/free-PA orientations. No crib was fed into a plaintext solver; this is a sealed **postfreeze exact algebraic compatibility** check using the known 24 plaintext letters ONLY for exclusion. A positive result would have been FEAS, not a decryption; the measured result is **zero matches** (EXCL this exact family).

## Controls and null ciphertexts

- All **20/20** independently encrypted and permuted positive controls passed: 10 keyword PA, 10 keyword CA, 10 plus-sign, 10 minus-sign.
- NULL0 (seed 46100) original route order CW/fwd, CW/inv, CCW/fwd, CCW/inv: **8,997, 38, 1,401, 7,659** two-free primer settings; all keyword-match counts zero.
- NULL1 (seed 46101) same order: **226, 30, 68, 9,147** two-free primer settings; all keyword-match counts zero.
- The independently implemented C++ graph/keystream sanity checker separately obtained the four original-K4 two-free counts **79, 1,643, 1,486, 9,502**. Its output was checked before the full-original Python run finished; PR #17 provides another independently indexed exact Python replay, with direct exhaustive checks for three surviving keys per route per ciphertext.

## Boundary of claim

This result excludes **only** the four named 24x8 K3 double-quarter-turn `S_then_T` routes with the listed five-digit decimal Gromark key family, +/- operation and R44b top-5000-word-derived keyword alphabet + arbitrary counterpart alphabet. It does **not** exclude other permutations, key sources, an alphabet outside the tested 4,749, two genuinely free alphabets, or physical tableau mechanisms. No 97-letter K4 plaintext has been recovered; no outside checker has been contacted. Main was not modified.
