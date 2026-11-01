# R43: archived failed experimental solver

**Status: FAILED RECOVERY GATE — DO NOT USE AS A K4 SOLVER.**

This directory preserves the original modular two-alphabet graph and the 97-letter left-to-right word-beam research for reproducibility. The graph algebra and re-encryption witnesses pass positive controls; **the beam does not recover unseen plaintext**. In R43 D0, exact plaintext recovery was **0/2**, and the true message was discarded by character 2 or 10. An arbitrary alphabet witness that re-encrypts a ciphertext is **not evidence of decryption**.

The historical R43 work was not run against original K4. Its `blind/` code is for audit and controlled research only. See `D0_FINDINGS.md` and `r44/REVIEW_PR11.md`.

Future K4 attempts must comply with `r53/BLIND_RULES.md`: the original ciphertext alone enters candidate generation; the published 24 letters and all their positions are reserved for *independent after-freeze validation*.
