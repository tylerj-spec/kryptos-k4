# R53 — Mandatory ciphertext-only, output-first Kryptos research rule

**Owner instruction, 31 October 2026:** The algorithm must NEVER receive any known K4 plaintext letters or their positions. Generate complete outputs from the original ciphertext first; only afterward compare against the known letters. If an output contradicts a confirmed letter, its algorithm/key configuration must be rejected.

This owner instruction **supersedes our previous K4 search protocol**, including earlier postfreeze *crib-assisted* feasibility filtering.

## Unbreakable procedure

1. Define a cipher hypothesis and key source independent of the known K4 plaintext. Develop and measure it on new, independently encrypted plaintexts where **both the original message and true key are concealed from the solver**.
2. The blind process receives only the unchanged 97-letter original K4 ciphertext, reviewed candidate-generation source, general language priors and separately justified cipher/key evidence. **Never supply** public K4 words, locations, a plaintext mask, clue-conditioned scoring, clue-fitting keys, guessed complete plaintexts constructed around public letters, anchor feasibility or feedback from previous K4 known-letter comparisons.
3. **Freeze before reveal**: commit or archive the entire 97-character output(s), associated independently selected algorithm/key, immutable parameters and scores, code hash, ciphertext hash, raw-output SHA256, and complete attempt ledger.
4. Only then may a **separate evaluator** independently forward-encrypt each candidate to check the exact original K4 ciphertext and compare against the published K4 letters at their published offsets. Failure means **reject that key-and-algorithm combination**. Agreement is necessary but **not sufficient** to claim a solution.
5. No tuning, selection, restarting, pruning, re-ranking or filtering of blind candidates based on the K4 validation. If a new method is motivated by past failures, disclose that provenance and test it on fresh independent control data. A fresh run cannot retroactively become never-exposed evidence.
6. Any genuine solve needs coherent, independently recovered novel plaintext; reproducible forward encryption with a genuinely derived key; and the later known-letter check. Reversibility with an arbitrarily *fitted* 97-position key proves nothing.

## Research record correction

Prior R40G and R45–R51 used published K4 letters **during** their finite-family consistency tests. Those historical numerical exclusions may remain in the ledger with an explicit crib-assisted label, but they are **NOT compliant blind K4 searches**. Do not use their clue-conditioned survivors as seed keys or candidate-generation filters.

R52's eight full-text guesses were composed AFTER knowing the published words. Their fitted key shifts, plus the earlier example primer 98800 with two fitted alphabets, are **not** independent decryptions. The fact that a separately constructed 97-letter message can be encrypted back into the original 97-letter ciphertext is no evidence when key/alphabet parameters were fitted using the target message.

R44b did recover 20/20 independent 97-character planted messages with the true key provided; the unsolved challenge is discovering the key and full plaintext without it. R43 failed its actual recovery controls. Do not conflate these facts.

## Enforced demonstration (not a proposed K4 solve)

- The R53 blind solver is a deliberately small **26-shift Caesar smoke example**, which sees only ciphertext and a generic letter-frequency model. It is NOT a claim that K4 uses Caesar. It exists to prove clean input/output separation for later stronger blind algorithms.
- Separate sealed preparation constructs 20 synthetic messages, hides their originals/keys from the blind payload, and checks the authentic K4 ciphertext SHA256.
- CI executes the blind solver in a **no-network, read-only, unprivileged Docker container** mounting ONLY the ciphertext input, reviewed blind source, and an output directory; no repository, public clues, prior candidate files or sealed test truth are mounted.
- Blind output is SHA256-frozen and committed or archived **before** any evaluator job is allowed to access known K4 letters.
- A second job checks the frozen SHA256, independently re-encrypts the output, assesses hidden-key planted examples, and ONLY THEN checks the 24 published K4 letters. Failing a K4 known-letter check is an expected negative result, not a CI failure.
- The source/input contract checks the isolated blind source for forbidden known-plaintext dependencies and rejects hidden key, plaintext, mask and offset fields in blind input.

This applies to **future** K4 attempts; past reports remain archived but are explicitly disqualified as blind decryption claims. No edits to main or external verifier submissions are authorized here.
