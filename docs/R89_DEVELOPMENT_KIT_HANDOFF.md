# R89 Synthetic Development Kit (Kryptos K4 research)

**Status: runnable synthetic development ONLY.** This package contains no published K4 plaintext clues, no actual K4 ciphertext in an input file, no K4 candidate results, and no fresh sealed validation gate. It is a research demonstration to support a separate future preregistered experiment and independent review.

## What's inside
- `reference.py`: independent, standard-library 26-letter F26, F26+KRY-tableau and irregular ciphertext-stepped rotor forward/inverse functions. Includes 3,000 random full round-trip checks and verifies opening K1/K2 encryptions.
- `pilot_f26.py`: vectorized full-keysearch F26/F26+tableau synthetic-only unknown-family pilot. Searches all **3,760** F26 settings per shortlisted phase, eight of 36 outer stage settings plus the bare F26 comparator: **33,840 full decodes** per input. It uses the existing R86 generic English 2/3/4-gram score. `--n` and `--neg` change the number of *spent* source controls; no target ciphertext.
- `derive_m1_solver.py`: generates a ciphertext-stepped rotor solver from an archived R86 C++ baseline with explicit checked source replacements. `pilot_m1.py` compiles that source using `g++` and runs a synthetic unknown wiring / step rule pilot.
- `data/r85_truth.json` / `data/r86_truth.json`: **already exposed** historic synthetic control text (never claim fresh holdouts). They are included to reproduce the development pipeline only.
- `model/gram*.bin` and `generic_words.txt`: reused model bytes from the user's November 19 R85/R86 experimental archive, with SHA256 hashes in `model/model_manifest.json`. Their accuracy across genres is not certified here.
- `reports/`: written adversarial method audit and executable bounds v2, including mandated unknown-family gate and negative controls.
- `BOUND_CONTRACT.json`: machine-readable proposed settings. This is not an immutable registered protocol.
- `results/smoke.json`, `results/m1_smoke.json`: completed developer-only smoke evidence. Logs ending abruptly or lacking a JSON report are `INCOMPLETE`, not negative cipher results.

## Environment
Python 3.10+ with NumPy and C++ compiler supporting `-std=c++17`; no networking or external connector required after unpacking. On Windows, install a C++ toolchain or run the M1 C++ pilot in WSL. Tested with Python 3.13 and g++.

## Run the synthetic checks
```bash
python3 reference.py
python3 pilot_f26.py --n 4 --neg 4 --out results/f26_smoke.json
python3 derive_m1_solver.py
g++ -std=c++17 -O3 m1_solver.cpp -o m1_solver
python3 pilot_m1.py --n 3 --starts 16 --iters 6000 --out results/m1_smoke.json
```
For a more demanding **developer-only** probe (not a fresh gate):
```bash
python3 pilot_f26.py --n 16 --neg 16 --out results/f26_development.json
python3 pilot_m1.py --n 8 --starts 80 --iters 16000 --out results/m1_development.json
```
These may require much more wall time; **do not** interpret a timeout as a failure of the cipher family. The complete formal holdout requires different data and a separate isolated runner.

## Current development findings (not a blind K4 claim)
1. F26 basic arithmetic reversible, but preserves per-block coordinate histograms; standalone F26 is not a good fit to K4's flat frequency count. A KRY-tableau stage is a new hypothesis motivated in part by that public ciphertext-only feature. This *post-hoc model selection* cannot be treated as independent supporting evidence.
2. F26+tableau recovered 16/16 previously exposed ordinary English messages exactly with phase and keys hidden in an earlier full development pilot. The rebuilt `pilot_f26.py` successfully completed 4/4 positives and 4 negative *smoke* cases; a longer rerun completed all first 16 positives but was interrupted after part of the negatives. Thus no new 16/16 independent validation claim is made here.
3. M1 previously recovered 7/8 exposed examples exactly at the 80x16,000 settings; the rebuilt reference suite and limited 16x6,000 C++ smoke complete but the larger rerun was interrupted by the container execution timeout. The method-specific development numbers remain historical observations, not gate evidence.
4. The broader transposition-first hypothesis was mathematically equivalent to transposition-after when key stream is unconstrained (independently checked on 2,000 toy random samples), and modular decimation is present in earlier ledger methods. It was rejected from this immediate experiment.

## What must happen BEFORE any K4 attempt
Formal pre-registration in a new `rNN/` directory and separate commits; independent source-code review; new genre-balanced SHA-pinned external text sources; 48 positives **per family** and 150 shared negatives; unknown-method+unknown-key+unknown-plaintext gate with 42/48 near-exact and 36/48 exact plus per-stratum, masked-subset and false-positive bars; independent witnesses, proper bounded sandbox, and all outputs frozen/pushed BEFORE checking published K4 plaintext. If the gate fails or a resource limit interrupts a run, do not run K4. See `reports/R89_EXECUTABLE_BOUNDS_V2.md` and the GitHub draft PR #98. No external answer check authorized.

## Integrity
Run `sha256sum -c SHA256SUMS` after extraction (or PowerShell equivalent). The manifest excludes itself, generated executables, and mutable local `results/` outputs. Recompute frozen experiment hashes only at formal preregistration and do not silently overwrite them.
