# R85 RX stepping-rotor pilot: NO-GO at the hidden gate (19 Nov 2026)

**No K4 run, no K4 candidate, no cryptographic exclusion.**
- Proposed model: one arbitrary AZ/AZ-wired rotor; n = 1..4; d = ±1, with C++ annealing over hidden 26-element inverse permutation.
- Training: Gensim Lee test news and reduced Wikipedia corpus; 2/3/4-gram model and general word-frequency refinement. Developer data: ten separate movie-review excerpts; 8/10 exact recovered with the improved model.
- First preregistered hidden test: twenty fresh Pang/Lee movie-review 97-letter encrypted excerpts. Search budget 40 restarts × 10,000 swaps per n/d.
- Result: **15/20** recovered to ≥95 of 97 letters with correct n,d; **14/20** exact. Threshold **16/20**: **FAIL**. Independent forward encipherer checked **120/120** stored full-text candidates.
- Local preserved output SHA256: `gate_raw.tsv` = `babcb81e8314ad1bbe2bdf8df88165f4cb8a6ec21d945894d78ad735500af7ea`; gate evaluation SHA256 `edcc943357cabd8c22948eebbdfcb1b9ffccd6277ee10caf2cf785cfef8dcdad`. These are in the downloadable research archive supplied to the owner.
- Under the mandatory stop rule, no K4 ciphertext was used, and no public K4 plaintext was supplied to this solver.
- Next attempt **R86** is a separate preregistered, fresh-heldout experiment. Its only solver change was more random starts/moves, not weakening the gate or fitting K4 clues. See `r86/PREREGISTRATION.md`, `r86/RESULT.md`.

**Status:** SOLVER_NO_POWER on the first gate, not an exclusion. Independent review: NONE. Do not promote or erase this failed test.
