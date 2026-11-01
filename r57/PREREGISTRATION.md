# R57 preregistration: 2×2 Hill digraphic mixing, strict ciphertext-only key search

**Protocol frozen before code, controls, or any K4 R57 decryption.** The classical Hill cipher (Lester Hill, 1929) replaces *pairs* of plaintext letters with a linear 2×2 matrix modulo 26. It is historically much more plausible in 1990 than the later-published Chaocipher, though we have no independent evidence that Hill was used on K4.

## Exact reversible method and odd-length convention

For every plaintext digraph `(x,y)` with A=0..Z=25, calculate:
- `u=(a*x+b*y) mod26`
- `v=(c*x+d*y) mod26`
- `det=(a*d-b*c) mod26` must be invertible modulo 26 (gcd(det,26)=1), allowing exact 2-letter block inversion.

The original K4 ciphertext has **97** letters, an odd length. This research round defines a **nonstandard but exactly reversible truncation convention** instead of making up a 98th observed character: encrypt first 96 plaintext letters as 48 normal digraphs; pair last plaintext letter with a **fixed generic pad X** (23) and output only the first ciphertext component `u96=(a*p96+b*23) mod26`. Require `a` invertible mod26 to allow unique last-letter recovery. This is **not** the usual fully retained ciphertext-padding convention; treating it as a tested hypothesis is explicitly not evidence of K4 provenance.

## Preregistered exhaustive search

Enumerate all matrices with:
- `a` one of 1,3,5,7,9,11,15,17,19,21,23,25 (12);
- `b,c,d` independently 0..25 (26 each);
- `gcd(a*d-b*c,26)=1`.

Total **97,344** matrix keys per input, counted independently before running. No additional affine offset, transposition, right-hand key fit, per-character key, or plaintext mask.

Original 97-letter ciphertext stays unchanged from `r39/ic_gate/k4_ciphertext.txt` (SHA256 `2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3`). Blind solver enumerates exactly 97,344 matrices, computes entire 97-letter inverse and scores via pre-existing generic `k4kit/data/quad_log10.f32`. It freezes **top 12 full 97-letter raw plaintexts**, rank, scores, and complete keys. No published K4 words, locations or positions enter candidate generation or code.

## Hidden plaintext AND key controls before K4

Create 20 new independent English passages, 97 letters each, encrypted with random true matrices uniformly drawn from the *same* 97,344 admissible keys (fixed RNG seed 570057). This is closed-world synthetic calibration, no proof K4 uses Hill. Sealed generator and true keys never mounted in the solver container. Blind binary receives only two TSV columns `id,ciphertext` and generic quadgram scores; runs read-only, no network, unprivileged.

Commit the raw control plaintexts/keys/results hashes to remote Git *before* sealed evaluation sees the true plaintexts and keys. **At least 16/20 exact top-ranked full 97-letter plaintext recoveries and all 240 independent forward witnesses must pass**, else K4 job must not run. Preserve failed controls, too.

## Original K4, only if controls pass

Run original unchanged ciphertext and 12 frequency-preserving shuffled null ciphertexts (RNG 570070), with same frozen code and parameters. Freeze all 13×12 full raw outputs, key parameters, code, model and input SHA256 to a distinct remote Git commit. Another job independently verifies all 156 forward witnesses **without public K4 plaintext**. Only a further isolated verifier, reading the already remote-frozen full raw candidates, compares to the published 24 known K4 letters; no reranking, key selection, fitting, or algorithm tuning from these results. A candidate must be coherent new English, reencrypt to original ciphertext, and match all published letters after freeze; matching alone not sufficient.

Null sample size 12 is descriptive only. Any negative result applies solely to this fixed 97,344-key and odd-length convention, **not** all digraphic or affine Hill variants, padding, routes, or other matrix sizes. No external checker submission. Main branch untouched; PR review before merge.

Prior method explorations R55 and R56 passed controlled 20/20 hidden-key recovery but did not recover K4. No clue-derived keys or their outputs are input to R57. Academic source: University of Rhode Island Hill-cipher article (1929, invertible 2×2 matrix); Emory mathematical exposition.
