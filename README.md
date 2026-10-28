# Kryptos K4 R33 strict-blind handoff (27 Oct 2026)

**No solution. No GitHub pushes. No external validator submissions.**

Start with `HANDOFF.md` and `LEDGER.md`. The `r33/` directory contains:

- A frozen preregistered 97-character K4 ciphertext-only keyword-columnar experiment: `r33/PREREGISTRATION.md` and `r33/blind/`.
- The unchanged Carter 1923 OCR-derived 282,924-letter key stream, original scorer, and the already-frozen top 100 candidate outputs for two key families.
- Exhaustive *postfreeze* clue-only histograms over 556,217,856 settings, 0 with all 24 clues, maximum 10.
- Two new planted synthetic ciphertexts, each independently recovered exactly rank #1.
- An independent 1,600-row mathematical re-encryption and quadgram-score audit across R32 and R33.
- The verbatim original `R32_handoff_original.zip`; its omitted route file is reconstructed from its own supplied code by `verify_all.sh`.

Run `bash verify_all.sh` to recheck the frozen data and independent output audit offline (no full cryptanalytic rescan). To redo all 556m decryptions, follow `r33/README_START_HERE.md`.

For user review, **no new candidate** qualifies: no actual K4 decryption in this R32/R33 search matched the confirmed clues at both positions. Prior G4/G7 readable fragments came from crib-assisted free-alphabet optimization and are not blind discoveries.

All new blind K4 runs operated on the original ciphertext; known words were used only by `sealed/` after all output files were frozen. The separate synthetic planted ciphertexts are needed to verify that the scanner can solve its own cipher family; they are not used to generate or alter K4 candidates.
