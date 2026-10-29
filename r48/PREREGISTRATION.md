# R48 preregistration — speculative physical reverse-tableau stream as a full 97-position key

Registered 29 October 2026 before R48 K4 processing. Predecessor: exact R45 five-decimal-digit Gromark model ruled out at frozen commit `1aa8fb3285a959bbfd656e2978024249e9f6a49b`.

## Evidence and uncertainty

Public site [SolveKryptos Field Guide](https://solvekryptos.com/fieldguide) / [Verify](https://solvekryptos.com/verify) prints a purported **physical** letter packet aligned to the copper screen's back: 4-letter tail, two 31-letter tableau rows, one 31-letter alphabet footer. That website **also** supplies a full plaintext reconstruction fitted to the confirmed K4 words, and its so-called helper cards and final gates have been **back-solved** to that reconstruction. **Do not use the reconstruction, gate table, shift table, helper cards, proof claims, or any fitted plaintext in our research.** The packet itself is not independently corroborated by two primary photographs. This entire experiment is conditional on the literal printed packet, not a certified transcription of the sculpture.

Literal packet declared before results, preserving the one footer blank:
- Tail, positions 1–4: `WXZK`.
- Row Y, positions 5–35: `YXZKRYPTOSABCDEFGHIJLMNQUVWXZKR`.
- Row Z, positions 36–66: `ZZKRYPTOSABCDEFGHIJLMNQUVWXZKRY`.
- Footer, positions 67–97: `_ABCDEFGHIJKLMNOPQRSTUVWXYZABCD`.

Lengths must equal `4+31+31+31=97`. The leading footer `_` is **unknown** rather than silently assigned a letter. Enumerate exactly all **26** A–Z alternatives in that one position, with all other 96 fixed exactly as printed. This explicitly tests possible assignments, not claimed physical letters.

## Exact family

- Ciphertext: original 97-letter K4, SHA256 including newline `2797de1451ab97118211735dcef370fc5acd70829f164aa043c47cbf40f0a5a3`; no transposition; no added/null characters.
- Key stream: full literal 97-letter packet above, `_` replaced with every A–Z (26 alternatives), letters converted to integer ranks using either **AZ** or **KRYPTOS** alphabet (2 conventions). Exactly **52 candidate 97-character keys**. All integer arithmetic modulo 26.
- Operations: both `CA_rank(c) = PA_rank(p) + k[i]` and minus-key variant, modulo 26.
- Keyword arrangement: either a plaintext keyword alphabet from **exactly 4,749** R44b dictionary-derived candidates with completely arbitrary bijective ciphertext alphabet, or the exact mirror. No shorthand suggesting this covers all possible alphabets.
- Mathematical precheck: existing independent two-free-alphabet oracle `possible()` at the public 24 K4 positions, followed by necessary-and-sufficient single-fixed-keyword/permutation injectivity tests on *every* pre-screen survivor. Count/report **all** passes; no probability-based score or fitted plaintext.
- Explicit alternate source mechanisms, row-column offsets, helper cards, variable physical gates and full unknown alphabets are OUT OF SCOPE.

## Sealed validation

- Twenty positive controls: independently encrypt the 20 already-revealed R44b plaintexts under cycling through declared 52 nondecimal key candidates, both signs (10 each), keyword PA/free CA (10) or keyword CA/free PA (10). Full re-encryption and 24-anchor constraint checks must pass for every one. These are algebra checks and NOT new holdout evidence.
- Four frequency-preserving shuffled copies of original K4, seeds 48100–48103, receive exactly the same 52 candidate keys, two signs and keyword orientations; count twofree/keyword viability for each null. Do not infer a statistical p-value from four nulls.
- Pin SHA256 of this preregistration, source code, model, ciphertext and raw outputs. Freeze results in GitHub on separate review branch, no mutation to main, no external verifier.

## Interpretation

- Zero settings means `EXCL` solely the **literal, unverified physical packet with 26 blank alternatives**, 2 alphabet rankings, 2 signs, 4,749 keyword choices and two orientations, in place. It does NOT disprove use of the sculpture's back, physical alignments, extra gates, or a different historical transcription.
- Nonzero means `FEAS` **by public 24-letter filtering**, not independently recovered K4 plaintext and not evidence of the site's fitted reconstruction. Any actual solution needs a separately preregistered blind plaintext-recovery run with fresh plants, raw 97 characters frozen before the clue check, plus independent re-encryption.

No result was known at preregistration.
