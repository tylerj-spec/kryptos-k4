# Reference library

Background reading for anyone (human or AI) joining the K4 effort. Written by Claude Code, 1 Nov 2026.

| File | What's in it |
|---|---|
| [`CIPHER_TYPES_TESTED.md`](CIPHER_TYPES_TESTED.md) | **Start here.** Every cipher family tested on K4 (rounds 1–54), with what it is, why it was tested, the result, and what has **not** been tested yet |
| [`KRYPTOS_FACTS.md`](KRYPTOS_FACTS.md) | The sculpture, K1–K3 methods and plaintexts, the K4 ciphertext and clues, solution history including the 2025 archive find and auction, the Weltzeituhr |
| [`CRYPTOGRAPHY_REFERENCE.md`](CRYPTOGRAPHY_REFERENCE.md) | Classical and modern ciphers: transposition, substitution, polyalphabetic, polygraphic, fractionation, codes, machines, modern; each with its statistical fingerprint and K4 relevance |
| [`CRYPTANALYSIS_METHODS.md`](CRYPTANALYSIS_METHODS.md) | How to attack them (IC, Kasiski, n-grams, annealing, cribs, algebra), plus this project's exact oracles, blind solvers and evidence rules |
| [`STEGANOGRAPHY_REFERENCE.md`](STEGANOGRAPHY_REFERENCE.md) | Hidden-message techniques, the known anomalies on Kryptos (misspellings, Morse, raised letters, extra L), and a protocol for testing hidden-message ideas |
| [`TOOLS_INDEX.md`](TOOLS_INDEX.md) | Map of the repo's code and data, and how to run each piece |

**Ground rules** (`k4kit/CLAUDE.md`, R53):
- blind first;
- pre-register;
- controls and nulls;
- freeze before reveal;
- report raw text;
- no external verifier without Tyler.
