# R96 different-model independent recovery review — 23 Nov 2026

**Reviewer:** ChatGPT (different model from Claude Code builder).
**Scope:** independently recompute recovery counts and decrypt all saved states from published R96 records. This is a review of synthetic development evidence only; no K4 input or known K4 plaintext used.

## Independent procedure

Read `r96/run_v1/RESULTS.jsonl` (96 records, 16 saved starts each) and `r94/inputs/PANEL_TRUTH.json` (48 spent practice messages). Without importing R96 evaluator code, reconstruct each AZ/KRY/PAL/ABS keyed alphabet and invert W1/W2 from the practice truth. For each saved state, use the recorded structural label and supplied true inverse wiring in the condition; substitute the candidate inverse wiring in the other position.

For zero-based character position i, compute tau=floor((i+r)/n), s1=d1*tau mod 26, s2=d2*floor((tau+h)/26) mod 26. Convert ciphertext into the record's output-alphabet indices. Recover intermediate m=(V[(c+s2)%26]-s2)%26, then p=(U[(m+s1)%26]-s1)%26; map p through the input alphabet. Compare the resulting 97-letter text byte-for-byte with the saved start's text. Independently count matches against the spent truth and top-8 recall, with >=95/97 as the recovery bar.

## Results

- 96 condition records; labels agree with their corresponding 48 truth records.
- **1,536/1,536 saved start texts independently reproduced exactly** from the saved inverse wiring and the ciphertext.
- All saved texts are 97 characters; every saved candidate inverse wiring is a 26-element permutation.
- true-V (search U): **45/48** top-1 >=95/97, **43/48** exact, **47/48** recall@8. Per-cell counts in registered order: **6,5,6,6,6,5,6,5**.
- true-U (search V): **47/48** top-1 >=95/97, **44/48** exact, **48/48** recall@8. Per-cell counts: **6,6,6,5,6,6,6,6**.
- Both registered overall and every-cell bars pass. The independently calculated counts agree with `r96/eval_v1/EVAL.json` and `r96/RESULT.md`.

## Limits and disposition

**PASS — independent recovery recount and forward/decryption witness consistency.** This is an independent implementation of the inverse cipher and counting logic, not a re-execution of the stochastic optimizer. The review did **not** independently verify all artifact hashes, Git commit chronology, model digest, resource usage, key-on-used-contact counts or scorer margins. These claims remain sourced to the builder's published record and CI; do not label them independently verified by this review. No fresh holdout was used: the panel is spent. No K4 cipher-family evidence follows.

R96's reported **GO_FOR_JOINT_DEVELOPMENT** is supported by this independent recount. The next stage must be separately preregistered, and no K4 run is authorized by this result.
