# R43 D0 development evidence (before any K4 trial)

Research objective: recover the original full 97-character plaintext of messages encrypted with **two independently random substitution alphabets** when the correct 5-digit Gromark key stream is given. The solver has no access to known K4 clue words or masks. Tests are **development** only; do not treat as a holdout.

## First CI smoke — no letter fallback

- [GitHub Actions run 40806138457](https://github.com/tylerj-spec/kryptos-k4/actions/runs/40806138457), commit `e7e1d1f`.
- Dictionary 834 words; top 64 per length, max word length 14; beam width 64; two independently generated 97-letter controls.
- D0_00: **0 valid full-alphabet witness**, 2,495,328 placements.
- D0_01: **0 valid full-alphabet witness**, 2,252,634 placements.
- Result: 0/2 exact or within three letters, so solver is not usable on K4.

## Second CI smoke — orthographic skip/fallback plus larger beam

- [GitHub Actions run 40806347747](https://github.com/tylerj-spec/kryptos-k4/actions/runs/40806347747), commit `9c0ed0a`.
- Added any-letter fallback at W=-7 to permit a ciphertext to end mid-word or contain an out-of-vocabulary letter, consistent with the existing ORTH model's skip-letter rule.
- Small configuration (beam 64, cap 64/length, max length 14): 0/2, 4,294,290 and 3,556,410 placements respectively; **0 complete consistent graphs** for both.
- Large configuration (beam 384, cap 512/length, max length 18): 0/2, **193,299,580** and **157,060,080** placements respectively; **0 complete consistent graphs** for both.
- Sealed vocabulary coverage for control D0_00 was 23/23 complete words available with the 512-per-length cap, with its final token cut to BRID; for D0_01 20/22 complete words available and the final token cut to F. Thus the first failure cannot be explained solely by missing words.
- No demonstrated plaintext recovery, despite exact consistency checking. Increasing the beam and vocabulary without changing search priority **did not repair** the control failure.

## Third planned comparison (not claimed as successful)

A math-based priority rewards each independent modular cycle that a word placement satisfies. If a random wrong guess produces a new cycle, it must satisfy a relation that would hold by coincidence roughly 1/26 of the time (a heuristic, not a formal calibrated likelihood); the proposed bonus is `log(26) = 3.258096538` per independent cycle. This is **development tuning after observing failure**, clearly not a pre-registered K4 test.

An internal ten-message random-alphabet graph unit test is also added to validate the modular equations and full bijective alphabet reconstruction. Its outcome must be read from CI before any inference.

## Boundary

- No K4 ciphertext was passed to the R43 solver; no K4 plaintext claim.
- Any new solver must pass a distinct untouched set of **20 new planted messages (>=16 exact)** before it is allowed to see the original K4 ciphertext, and must pass independent forward re-encryption.
- There are many consistent *feasible* completions in an unknown-alphabet model; an internally consistent witness without exact plaintext recovery on plants is not evidence of decryption.

This document is a negative development record, not an exclusion of any K4 cipher family.
