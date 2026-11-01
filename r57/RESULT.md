# R57 complete: digraphic Hill 2x2 hidden-key controls pass, K4 fails

**No K4 plaintext or correct cipher identified.** Original known letters never enter blind solver, key-ranking or selection; the separate evaluation occurs only after the entire full-97-letter candidate set was remotely Git-frozen.

## Method
2×2 Hill matrix over Z26 on ordinary 2-letter blocks. Original K4 length 97 is odd. This fixed, *nonstandard* convention appends a generic pad X to last plaintext letter, emits only the first of that final two-letter ciphertext pair, and requires the matrix coefficient a to be invertible to permit exact unique decryption.

Declared and exhaustively searched exactly **97,344** matrices:
`a` coprime to 26, `b,c,d` 0..25, and determinant coprime to 26. No additive translation, no guessed K4 plaintext, no manually fitted key, no clues supplied to generator. Top 12 complete unmodified 97-letter output messages frozen per ciphertext, scored by untouched generic quadgrams.

## Independent synthetic controls (before authentic K4)
- **20/20 exact full 97-letter top-1 message recoveries**, with both original text and actual keys hidden from solver.
- **20/20 true key matrices recovered**.
- **240/240** independent full re-encryption witnesses verified after remote freeze.
- Raw frozen controls SHA256: `5344deee76c4638deda23b5bd176ad625cf96b083734b85d0513e789d22bed62`.
- Closed-world control success is not evidence that K4 uses Hill or the nonstandard odd-length convention.

## Original ciphertext-only K4 run
- Original K4 97-letter ciphertext SHA256 confirmed (no edits), and 12 independent shuffled-ciphertext nulls.
- **13×97,344** matrix search settings tested, with **13×12** full plaintext results remotely frozen **before** known-letter comparison.
- **156/156** independent forward-encryption witnesses passed.
- Raw frozen K4+null candidate output SHA256: `a555bed143a22de4f9deb6d641e014c8fc93999d0883010979377de12629055c`.
- Highest generic English quadgram score on K4: **−646.99887848**. **6 of 12** shuffled nulls score better. Descriptive upper-tail `7/13≈0.53846`, not a formal p-value.
- Top-ranked full 97-letter raw output (no changes):
  `GJGDOCFFGXARDPSLIJTWSXDEDTWTBEUIEGMXOFKENHEGAGHEMWLAEHGFCIGITOXOYBREZLJATROSDFPOLAINEEUODLYEAGUCL`
- **Post remote-freeze only**: top candidate agrees with **0/24** published K4 letters; best of twelve **2/24**; no candidate passes all 24 or reads as English.
- Full evidence: `frozen/CONTROLS_EVALUATION.json`, `frozen/K4_RESULTS.jsonl`, `frozen/INDEPENDENT_FORWARD_AUDIT.json`, `frozen/AFTER_REVEAL_EVALUATION.json`.

## Conclusion
This third, structurally different reversible cipher family is also negative within its registered scope. It does **not exclude** affine Hill (nonzero offset vectors), different block sizes, alternate reversible 97-letter conventions, transposition layers, or entirely different methods. No model/key tuning was performed using known-letter scores. No external checker contacted. Main unchanged. 
