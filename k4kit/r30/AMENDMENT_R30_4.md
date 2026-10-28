# R30 amendment 4 (Claude Code, 27 Oct 2026): E6, non-English word models (Tyler: "the plaintext might not be in English")

Written before any E6 model was built, calibrated or run on K4.

**Why.**
- The exact key test is language-independent, but the readability search used an English word model (ORTH, with
  Dutch-like spelling variants).
- Earlier other-language tests (L63, L64) used small trigram models and other families. They never covered the
  Carter book.

**Models** (same solver, `solver_s2kp`; same TSV format: `WORD exact edit`).
- **Source:** Python package `wordfreq` 3.1.1 from PyPI, the top 100,000 words of each language.
- **DE (German):**
  - Each word is lower-cased; ä→ae, ö→oe, ü→ue, ß→ss; remaining diacritics stripped (NFKD); upper-cased.
  - Non-A–Z characters are removed; empty words and words over 24 letters are dropped.
  - Score = log10 of the word's frequency, summed over words that collide after transliteration. Edit score
    −1e100 (no spelling variants).
- **NL (Dutch):** the same procedure.
- **Clue words:** DE and NL both get EAST, NORTH, NORTHEAST, BERLIN and CLOCK at their ORTH scores (the clues are
  English in any reading of K4).
- **MIX:** the union of ORTH, DE and NL, keeping the maximum exact score per word and ORTH's edit scores. It covers
  English mixed with German or Dutch words and spellings.

**Calibration C6** (fresh fixtures `fixtures_lang.json`, sha256
`6bd171630e7ee03d94542272b1d8e431a5e2f5eb0692e298109e7aa686173acf`).
- Each message is encrypted in place with 5-digit Gromark, random primer and alphabets, seed 30006.
- Lines per message: the true primer plus up to 9 wrong feasible primers (seed 30006). 64 restarts.
- Model assignment:
  - DE: the 10 German messages.
  - NL: the 10 Dutch messages.
  - MIX: the 10 German, 10 Dutch, and the first 10 R21 English passages.
- **Blind readable:** the best line is the true primer, with ≤ 5 wrong letters.
- **Gate:** DE ≥ 5/10, NL ≥ 5/10, MIX ≥ 15/30. A model that fails its gate gets exploratory K4 runs only.
- **Bar per model:** the best W over all wrong-primer lines in its own calibration.

**K4 runs (E6), each model, 64 restarts:**
- all 585 Carter book passes (E4);
- all 39 feasible 5-digit Gromark primers.

**Candidate rule:**
- W above the model's bar;
- **and** a 64-restart replication with new seeds within 5 letters.

The 5 best per model and target go to the review shortlist with forced masks, labelled REVIEW ONLY.
