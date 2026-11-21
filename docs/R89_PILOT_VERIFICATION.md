# R89 development-kit independent verification and limitations (21 Nov 2026)

**Category: synthetic DEVELOPMENT only — no K4 input, no published K4 plaintext, no sealed holdout, and no external checker.** Builder/reviewer GPT-6, not independent-model review.

## Runnable development package

The user has a separate ChatGPT attachment named `R89_Kryptos_Method_Audit_Dev_Kit_2026-11-21.zip` (SHA256 `8588e64e7055a02df2aa7c9ce80a55ab6aae88c60a5364a0992e5a41a42b8e36`). This binary attachment is NOT committed to GitHub; it must be supplied separately to the next agent if needed. `docs/R89_DEVELOPMENT_KIT_HANDOFF.md` gives the offline commands and a description of its files. Do not infer that running this ZIP constitutes a passing formal gate.

The code uses the previous R85/R86 experiment's public-to-our-project, **already exposed** synthetic data and language-model bytes. The model source hashes are `gram2.bin` 8953dbf68c9102d3..., `gram3.bin` 388abdfa9ceb774d..., `gram4.bin` 570e79713ea9ef21...; their complete SHA256 values are in the ZIP's `SHA256SUMS`.

## Completed new smoke checks

| Check | Result | Meaning |
|---|---|---|
| Python reference encrypt/decrypt three models | **3,000 random round trips/model** (random lengths 1–98) | Inverse/reference functions agree on tested keys; not unknown-key recovery |
| Known K1 and K2 tableau beginning | **both exact** | The *outer* KRYPTOS-style tableau is a historical cipher; F26 inner stage remains invented |
| F26L model/keys hidden (archive source) | **4/4** exact, complete | Single-genre *spent* developer sample, no sealed confidence |
| Four negative rotor examples in F26L smoke | **0/4** above exploratory score −1500 | This is development threshold only; classifier normally forces a family unless abstention is implemented |
| RCT model/keys hidden (16 × 6000 budget) | **3/3** correct m,q,d; **2/3 exact**; remaining 51/97 | Same single-genre *spent* source, not a passed gate |
| Longer fractionation developer rerun | **INCOMPLETE** at 21/32 inputs (16 positives, five negatives processed) | No full false-positive estimate; do not promote |
| Higher-budget rotor developer rerun | **INCOMPLETE** before final output | No new 80 × 16,000 result in this kit |

All completed smoke programs were launched in the current container; standalone scripts are in the ZIP. The previously reported, earlier-session 16/16 F26L and 7/8 RCT at higher budgets remain **historical, spent development observations**, not fresh independently reproduced holdout evidence.

## Source-file integrity
- `reference.py` SHA256 `b263e44f8e34e66112965ad29f44bd255a1a3c5624469809fc292e3a393c36f7`
- `pilot_f26.py` SHA256 `bd0c6abacd0d4f540d8d0386eec718599471ef2ee57f0007cc2ff6923965cdde`
- `derive_m1_solver.py` SHA256 `302d16b5c77501483f0845f010700c4feda61060ea827059b8af438d3ec29038`
- `pilot_m1.py` SHA256 `15b2200343f746e3117e5b86e0db3585864341d62792da4b8ac9028534a2f6ea`
- `m1_solver.cpp` SHA256 `78d8200f738a05c20a55670dba077799e2861741614316a5859ade932e867c4d`
- `results/smoke.json` SHA256 `0898c5df0b6fa6e8d05d0a55c294921516f6becaed89b35915303e53c0bbb748`
- `results/m1_smoke.json` SHA256 `c6f88701bfe85dbc07fcb0ca95ac8fde795ed9a6e0835fcd4bc0bacfefe29df3`

The ZIP's full-file `SHA256SUMS` was checked with `sha256sum -c`, and ZIP integrity with `unzip -t`, both passed.

## Reviewer issues that block a real K4 run

1. A **separate reviewer** must verify uniqueness/equivalence against R77 H8 / R79 state rules and existing transposition screens. Doing this by repeated personas of one model is NOT independent review.
2. Optimized F26L implementation must be rewritten for throughput while preserving exact independent witnesses. Walltime extrapolation from a 4+4 sample is unsafe.
3. Define a **genuine abstention classifier** and score calibration that compares the maximum across *both* arms to the matching maximum among all wrong-family controls and nulls. One arm's raw ngram score is not automatically a calibrated posterior against the other.
4. Pin fresh genre-balanced corpus hashes and create **48 positives per family** (max 96) and **150 shared negatives**, all hidden; maintain the fixed 4×3 parameter×genre grid (four in each cell), of which 12 of the 48 per arm are orthographic masks. Add mutation controls outside that gate denominator.
5. Freeze gate inputs, outputs and full seed/source/resource logs through the repository's bounded/isolated workflow. Only positive family-specific GO (42/48 near-exact, 36/48 exact, per-stratum and genre minima, <=1/150 false confident) permits conditional original K4+200 shuffles. No K4 attempt until all mandatory checks pass.

## Scientific caveat

The synthetic frequency improvement from adding a second tableau was noticed because the original K4 ciphertext's **publicly known index of coincidence** was flatter than standalone F26 outputs. This is post-hoc model development on K4 **ciphertext-only** evidence, allowable for hypothesis creation but not independent evidence that the new invented cipher is correct. Even a later chance-level K4 score must not be interpreted as a broad exclusion of any named classical family. An anomalous score after exploratory family selection requires especially skeptical interpretation.
