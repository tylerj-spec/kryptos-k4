# R35 M0: K1-K3 plaintext running key x opposite-direction double rotations

Registered before scan. This is a limited, exploratory fixed-alphabet family, distinct from the larger Carter M1 experiment.

- Original K4 ciphertext: use `r34/k4_ciphertext.txt` unmodified (97 letters).
- Key source: `k4kit/data/k1k3_plaintext.txt`, normalized to ASCII A–Z, all 97-character windows, forward and reversed, numbered AZ and KRYPTOS.
- Routes: `rot-mixed 4 28`, 5,000 route-orders (25^2 width pairs, 2 direction assignments, 2 inversion choices, 2 orders).
- Cipher conventions: 12 fixed combinations of AZ/KRYPTOS plain/cipher alphabets and VIG/BEAU/VARB.
- Plant controls: reference_messages.json r20_templates indices 0, 1 (reused earlier, but never exposed to scanner), independently encrypted by sealed encryptor; fixed seeds 35001 and 35002.
- Runs: K4 first plus 2 plants. English quadgram scoring; freeze per-run top-100 results before revealing known words or planted truth.
- Decision: plants must both return rank #1. Candidate must have all 24 published letters *and* read as meaningful language, passing independent re-encryption. Whole-family matching alone is not a verified solution.
- Zero full24 with successful controls excludes **only this exact** key/route/cipher-convention family.
- GitHub workflow creates and pushes a separate immutable-by-procedure `chatgpt/r35-m0-frozen` branch containing output, hashes, and scanned source snapshot, **without running sealed reveal**. Follow-up reveal is only performed after branch commit exists. Actions does not automatically merge any result.
- We do not use the known words for M0 search or experiment selection; publication of results is mandatory even when null.
