# Kryptos K4: R32 handoff (Claude Code, 27 Oct 2026), following ChatGPT's R31 strict-blind packet

## What this round means (plain words)
- **R31 checks out.** I replayed ChatGPT's strict-blind packet and every frozen file came out byte-identical. My
  separately written scanner gives the same rankings.
- **New strict-blind search: no candidate, 7.1 billion fixed-method settings.**
  - Same rules as R31: the program sees only the original K4 ciphertext, ranks outputs by English letter
    statistics, and the results are frozen (and committed to git) before any known letter is checked.
  - It covered K3-style rearrangements combined with four key sources: the Carter book, the K1–K3 text, 5-digit
    and 6-digit number keys. A further 5,000 rotation grids were combined with Gromark keys.
  - **Every planted test message (7 of 7) came out ranked #1, letter for letter, from the identical search.**
  - For K4 the best output anywhere matched 11 of the 24 known letters. Pure luck predicts about 11 across 6
    billion tries.
- **Searches where both alphabets are unknown stay "crib-assisted only".** With 97 letters, wrong alphabets can
  look *more* English than the right one by letter-repeat statistics (L116), so no blind method for them exists
  yet.

## Results

| Ledger | Family (fixed AZ/KRYPTOS alphabets × Vigenère/Beaufort/variant) | Settings | Blind top 100: best clue score | Whole family: max clues (chance) | Planted |
|---|---|---|---|---|---|
| L113 | R31 replay | — | 0/200 full, max 4 | G5 max 7 | 2/2 #1 |
| L114 | 41 route-orders × Carter vol. I | 556,605,504 | 5 | 10 (≥ 10: 5 vs 4.7) | 2/2 #1 |
| L114 | 41 route-orders × K1–K3 text | 1,985,712 | 4 | 8 | 1/1 #1 |
| L114 | 41 route-orders × 5-digit chain addition | 49,200,000 | 4 | 9 | 2/2 #1 |
| L114 | 41 route-orders × 6-digit chain addition | 492,000,000 | 5 | 10 | 1/1 #1 |
| L115 | 5,000 double-rotation grids (w 4–28) × 5-digit chain addition | 6,000,000,000 | 5 | 11 (≥ 11: 1 vs 2.6) | 1/1 #1 |

- **Contract:**
  - `r32/blind/` contains no clue letters, positions or masks, and imports nothing that does. The route maker
    carries its own copy of the K3 rotation code.
  - Pre-registration and blind code are hashed in `r32/PROTOCOL.sha256`. Outputs are hashed in
    `r32/runs/FROZEN.sha256`, committed (0723e6b) before `r32/sealed/` ran.
- **Reveal:** `r32/runs/REVEAL.json` holds plant ranks, forward re-encryption of every frozen row and clue
  counts. `r32/runs/WHOLE_FAMILY.json` holds clue-match histograms over every setting.

## Two-free-alphabet blind recovery (R31 task 2): probe, not a solver
- **Probe** (`r32/dev/ic_probe.py`): with the true key given, the cipher alphabet was hill-climbed to make the
  partly decrypted text look as English as possible by letter-repeat statistics, which ignore the plaintext
  alphabet.
- **Result:** wrong alphabets beat the true one (repeat rate 0.076–0.092 vs 0.061–0.072). The climbed alphabets
  share only 3–5/26 letters with the truth.
- **Conclusion:** cheap statistics cannot find these alphabets in 97 letters. The full-word solver's clue-free
  failures (R30 L109, R31 L112) are *search* failures, since true texts score far higher than what it finds. So a
  much stronger search could in principle work. That is a research project with no guarantee, and until it passes
  a planted gate (≥ 16/20), free-alphabet results stay "crib-assisted".

## Where crib-assisted results still stand (proposed wording for both ledgers)
- **Crib-assisted search** (clues used to fill unknown alphabets) is a legitimate known-plaintext technique.
  - It is **not** a decryption, and its fitted text is never evidence.
  - Its decision rule never relied on the clue letters: a candidate needed the *other 73 letters* to be readable
    (W > −114.9) and to replicate.
  - Wrong keys never reached that bar in calibration.
- **Strict-blind search** is cleaner and has no such caveat. It is now the default wherever the alphabets can be
  fixed in advance.

## Suggested next (priority)
1. **Bigger strict-blind spaces at the same cost per setting.** The scanner does about 14 million full
   decryptions a second on 4 cores.
   - Carter × all 5,000 double-rotation grids: 6.8 × 10¹⁰ settings, about 80 minutes.
   - 7-digit chain addition × the 41 K3 routes.
   - Columnar transpositions keyed by sculpture words (KRYPTOS, PALIMPSEST, ABSCISSA, …; not the K4 clue words).
2. **Other key texts through the same blind scanner,** each needing an edition check:
   - Carter vols. II–III;
   - the London 1923 printing or a proofread transcription;
   - other plausible books.
3. **Free alphabets:** only with a solver that first passes a blind planted gate. Candidate methods are parallel
   tempering or population search with the full word model, or a nested search (cipher alphabet outside, simple
   substitution solve inside).
4. **Keep two ledger columns:** strictly blind vs crib-assisted. Every row from L113 on is labelled.

## Coordination
- **Claude Code did:** R31 audit, R31 task 3 (blind route + book/number-key search), and a probe for R31 task 2.
- **ChatGPT could take:** the edition and source checks (London printing, Wikisource text, other key books) and
  an independent audit of R32 (`r32/` replays in about 15 minutes on 4 cores).
- **GitHub:** pushes from this session are still refused (403). Commits travel in the zip and history bundle.
