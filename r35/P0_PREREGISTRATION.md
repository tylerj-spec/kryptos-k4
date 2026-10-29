# R35 P0: K1-K3 running-key text, opposite-direction double rotations

**Pre-registered BEFORE scanning K4.** No prior K4 output from this hypothesis.
Historical basis: K1–K3 plaintext is part of the same installation; K3 uses consecutive geometric rotations. Opposite-direction two-stage rotations were not in R32/R34's same-direction route sweeps. This is a speculative but bounded hypothesis, not a claim about the sculptor's key.

## Exact family

- Input: original public K4 ciphertext, 97 characters, byte-for-byte SHA256 `2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3`.
- Route: `strictblind/blind/routes.py rot-mixed 4 28`, 5,000 route-orders (625 width pairs x 2 opposite direction assignments x forward/inverse x 2 operation orders).
- Key: `k4kit/data/k1k3_plaintext.txt`, every contiguous 97-letter window, forward and reverse, with A–Z or KRYPTOS letter numbering. This text is the actual K1–K3 decrypted text, not K4 clues.
- Alphabet/cipher convention: 12 fixed choices (plaintext alphabet A–Z / KRYPTOS, ciphertext alphabet A–Z / KRYPTOS, Vigenère / Beaufort / variant Beaufort).
- Plaintext ranking: unmodified project quadgram model, top 100 per entire family.
- Cipher transforms: original `S_then_T` and `T_then_S` semantics. No plaintext hints, masks, or disclosed clue letters in any blind scan input.

## Controls / negative controls

- Two planted English messages from `r35/controls.json` indices 0 and 1, first 97 normalized letters, neither contains any of the published K4 clue phrases. Generated before scanning under a random family setting with seeds 35001 and 35002. Exact plaintext retained in `sealed/truth.json`, never passed to blind code.
- One null ciphertext: a permutation of the original 97-letter K4 ciphertext, preserving the letter histogram, generated once with Python's `random.Random(35003)`. It must be scanned identically; compare best blind scores as a descriptive diagnostic, not a statistical significance claim from one null.
- All four ciphertexts use the same scanner/route/key/score combination.

## Freeze and reveal

- Run `strictblind/blind/experiment.py`, then commit all relevant inputs and frozen artifacts to GitHub **before** invoking `sealed/reveal.py` or `sealed/whole_family.py`.
- Every frozen top-100 row must independently re-encrypt to its input ciphertext. Plants must rank 1 for an unqualified negative inference.
- Whole-family count must include every key, route, and 12 convention settings. Separately count exact 24/24 known-letter matches after the freeze; do not use the known letters to select or optimize any blind candidate.
- Full 24/24 is a *candidate*, not a solution unless independently reconstructed, readable and corroborated. Zero 24/24 with successful controls is **EXCL only within this exact fixed-alphabet hypothesis**.
- Report even negative outcomes; do not tune parameters or reinterpret null controls after reveal. Never call the external verifier.

The public K4 plaintext and method remain unverified within this project.
