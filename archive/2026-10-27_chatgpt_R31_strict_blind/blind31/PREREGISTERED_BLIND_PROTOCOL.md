# R31 STRICT BLIND DECRYPTION PREREGISTRATION
Frozen before running R31 K4 scans (the historical user requirement).

## Separation
- Solver processes only ciphertext.txt, quad_log10.f32, carter_az.txt (or an explicitly defined Gromark numeric stream). No known plaintext, crib masks, crib positions, or anchor words are passed to the solver, embedded in its code, or used to select keys, discard settings, change search budgets, or rank candidates.
- Every run creates immutable ranked output and SHA256 before any crib checker runs. A separate checker in sealed31 examines the saved outputs afterward. The checker may not alter ciphertexts, ranked lists, or plaintext.
- No algorithm may score an exact known clue or inject known characters. No retroactive fitting or hand-selection by known words. Source text is the OCR of the original 1923 Carter/Mace book with R30's frozen normalization.

## Original ciphertext
Source ciphertext is the original unmodified 97 letter K4 sequence. No character edits or masking. No external submissions.

## Family A: fixed-alphabet 5-digit decimal Gromark (without fitted alphabets)
- Enumerate every one of 100000 five-digit primers (leading zeros permitted).
- Generate 97-digit chain-addition key, recurrence k_i = (k_{i-5}+k_{i-4}) mod 10.
- Four AZ/KRYPTOS plaintext/ciphertext alphabet pairs and three operation types (Vigenere, Beaufort, variant Beaufort). Total 1,200,000 decryptions.
- Score every one of 97 output letters with fixed quadgram frequencies; retain the 100 highest. No candidate words required; no clues consulted.

## Family B: full Carter 1923 book as key, fixed alphabets
- Normalize OCR with R30's frozen running-header drop.
- For each available 97-letter window in forward and reverse book order, two numbering alphabets (AZ,KRY), four plaintext/ciphertext alphabet pairs (AZ,KRY), three operation types (Vigenere/Beaufort/variant Beaufort); 48 configurations per window.
- Rank on the same fixed quadgram score, retain top 100. All key offsets, no crib prefilter.

## Controls
- Encrypt two independent known 97-letter synthetic English messages under one preselected fixed A-Z Gromark setting and one preselected Carter window A-Z setting; run *identical* blind searches and confirm whether true solution returns in top 100. Fixture plaintext is never included in or read by blind solver.
- If planted key+alphabet known in evaluator, its legitimate encryption/decryption verified outside blind scanner.

## Decision criteria
- First freeze the uninspected K4 rankings and SHA256. Then checker reads known clues for retrospective score of all top 100, correct-anchor count 0..24, and full 97-letter exact forward re-encryption.
- Any candidate with anchor matches <24 is rejected as a K4 solution, but its unedited 97 letters may remain in review-only catalogue.
- An apparent word or phonetic fragment in known-wrong output is not independent evidence.
- A known plaintext on training data is not a blind K4 decryption. Benchmarks diagnose power but do not validate K4.
- If no 24/24 blind output exists, report no K4 solution; do not add clues to 'repair' it.
