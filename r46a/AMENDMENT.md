# R46A operational amendment — indexed exact keyword feasibility

29 October 2026, **after** the original R46 preregistration was pinned and an original exhaustive Python GitHub Actions job was started, **before** receiving any completed R46 keyword-family match counts. The original job is still running at this registration. This amendment changes **only** the implementation and CPU cost; the key generation, four routes, two signs, two alphabet orientations, 4,749 keyword alphabets, 20 positive controls, two nulls and decision rule are IDENTICAL to `r46/PREREGISTRATION.md`.

## Motivation and already-observed facts

An independent C++ implementation of the two-free-alphabet prescreen was run after R46 preregistration, and found on *original K4*:
- `R24x8/CCW/fwd`: 1,486 primers;
- `R24x8/CCW/inv`: 9,502 primers;
- `R24x8/CW/fwd`: 79 primers;
- `R24x8/CW/inv`: 1,643 primers.
These **already-observed prescreen counts are disclosed here**, so they are not claimed to have been preregistered or blind. They do NOT include any keyword feasibility results.

The slow Python implementation scans all 4,749 keyword alphas for *every* feasible primer and each of two arithmetic signs and both orientations. This becomes costly where 9,502 primers survive.

## Exact indexed optimization

For a given (unrotated) substitution-layer ciphertext:
- **Keyword-PA orientation:** if two positions of confirmed public plaintext produce the **same ciphertext character**, their derived CA position must be equal. Therefore for positions i,j with `C_i=C_j`, a candidate keyword PA must satisfy `PA^-1(p_i)-PA^-1(p_j) = sign*(k_j-k_i) mod 26`.
- **Keyword-CA orientation:** if two positions of confirmed public plaintext contain the **same plaintext character**, their derived PA rank must be equal. Thus for positions i,j with `p_i=p_j`, a candidate keyword CA must satisfy `CA^-1(C_i)-CA^-1(C_j) = sign*(k_i-k_j) mod 26`.
- Pre-index all 4,749 keyword alphabets by the vectors of those simple exact pair-difference invariants, using at most the first six repeated pairs per orientation. A correct candidate **must** satisfy all selected pair equations, so skipping others cannot create false negatives.
- After index lookup for a key/sign, execute the original R45 **complete** `fixed_pa()` or `fixed_ca()` necessary-and-sufficient test on *every returned keyword*. The pre-existing `possible()` two-free oracle is unchanged.
- For the first three two-free surviving primers on EACH route and each of the K4/2 null ciphertexts, compare every indexed keyword match with an independent **full unindexed 4,749-alphabet brute-force scan** at BOTH signs/orientations and assert the exact match lists agree.

Run all original R46 K4/2 null settings; no shortcut, candidate threshold or crib change. The output will preserve R46's schema/route counts and be separately frozen under `r46a/`, with the amendment, indexed source and full raw results SHA256-pinned. The original R46 process is not modified. If the original process finishes, compare numerical route counts/viable settings; any disagreement invalidates this run.

This is explicitly a **sealed postfreeze, known-letter finite-family feasibility study** and cannot generate unknown K4 plaintext or stand as a cipher solution.
