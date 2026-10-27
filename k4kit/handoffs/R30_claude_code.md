# Kryptos K4: R30 handoff (Claude Code, 27 Oct 2026)

## What this round means (plain words)
- **No candidate plaintext.** This round tested five new hypothesis families plus a carving-error check and a
  non-English re-run, about 15,000 new key settings in all. No setting decrypted to readable text.
- **The headline test was the full Carter & Mace 1923 book as a running key** (the book K3 quotes). Every 97-letter
  stretch was tested: 1.13 million stretches × 2 numberings × 2 directions.
  - 585 survived the exact test, about what chance gives.
  - None of the 585 produced English. Planted messages hidden under real Carter keys come back 80% of the time, so
    this is a fairly strong negative for "Carter's book, read straight, as a Vigenère/Quagmire running key with
    English plaintext".
  - *E6 result for German, Dutch and mixed models: see §3.*
- **The K2/K3 punctuation idea (X = full stop, Q = question mark) does not help the search.** The ordinary model
  already reads X-punctuated text about half the time.
- **Every "no candidate" is qualified by recovery power.** Planted messages are recovered 30–80% of the time,
  depending on the family. These are statistical results, not exclusions.

## 1. Rules followed
- **Pre-registration:** `r30/PREREGISTRATION_R30.md`, plus four dated amendments (`r30/AMENDMENT_R30_*.md`). Every
  amendment was written before the outputs it affects were viewed; the sha256s are asserted by the scripts.
- **Fresh hidden fixtures:** 22 punctuated English, 10 German, 10 Dutch.
- **Verification:** every reported row is re-encrypted to K4 independently (`verify_row`) and carries its
  forced-letter mask.
- **No external submissions.**

## 2. Results

| ID | Family | Settings searched | Best W (bar −114.9) | Planted recovery | Outcome |
|---|---|---|---|---|---|
| L106 | Carter & Mace 1923 vol. I running key | 585 (all passes, 64 restarts) | −140.51 | 16/20 under real Carter keys | no candidate |
| L102 | Chain addition, 6- and 7-digit primers | 4,246 (all passes, 16 restarts + top 20 at 64) | −136.40 | 9/20 (16), 12/20 (64) | no candidate |
| L103 | K3-style routes + Gromark, all 1-cycle settings | 6,607 | −142.19 | 9/20 (16), 15/20 (64) | no candidate |
| L105 | One mis-carved clue + Gromark | 3,178 | −140.94 | 4/20 (16), 6/20 (64) | no candidate, low power |
| L104 | X/Q punctuation scoring | 22 fresh fixtures (blind test) | — | 10/22 vs plain 11/22 | rule not useful |
| L108 | German / Dutch / mixed word models on Carter + Gromark | see §3 | see §3 | see §3 | see §3 |

Human-review list (REVIEW ONLY): `r30/SHORTLIST_R30.md` and `r30/shortlist_r30.csv`. They give raw 97 letters,
forced masks and the scorer's word split, labelled as interpretation.

## 3. Non-English re-run (E6, amendment 4)
*Filled in after the run; see L108 and `r30/runs/e6_*.json`.*

## 4. Lessons added this round
1. **Pass-count excesses from book keys are English structure, not signal.** Compare against word-order-shuffled
   copies, not letter shuffles (L106).
2. **Letter-shuffled ciphertexts are a very uneven null for pass counts.** One shuffle gave 80 passes, another
   31,095 (L102).
3. **Planted recovery varies by key set,** 9–16/20 at 64 restarts. Always quote the family's own calibration.
4. **A cheaper separator is not free:** the optimiser spends it on wrong decryptions as readily as on right ones
   (L104).

## 5. What is still open (suggested next)
1. **Carter book variants:**
   - Volumes II (1927) and III (1933);
   - the London (Cassell) printing, if its wording differs;
   - a proofread transcription (Wikisource) to rule out OCR damage in the clue-aligned letters;
   - key numberings beyond AZ/KRYPTOS (e.g. a keyword-mixed numbering).
   `r30/e4_book.py` takes any text file; about 10 minutes per book on 4 cores.
2. **Plaintext autokey with both alphabets free (handoff T3).** Not done. It needs a new solver variant and may be
   poorly identifiable at long lags (L52).
3. **R27 zero-cycle route settings outside K3's own geometry:** about 56,000, around 15 CPU-hours at 16 restarts.
   Low value per setting.
4. **Other source texts** for running keys, each run as a whole-book test with the same harness:
   - Sanborn's other works;
   - Cyrillic Projector texts;
   - Berlin Wall and World Clock literature.
   Getting edition-verified sources suits ChatGPT.

## 6. Coordination (for Tyler and ChatGPT)
- **Claude Code took T1 (Carter), T2 (punctuation), T4 (6/7-digit), a T5 subset (all 1-cycle routes), T6
  (carving errors, Gromark), and a new non-English re-run.**
- **Suggested for ChatGPT:**
  - verify the London 1923 text against the Doran OCR around K3's passage;
  - assemble the Wikisource proofread text, which becomes the test text for a clean re-run;
  - source verification of the Morse plate order and World Clock 1989 inscriptions.
- **Repo:** branch `claude/kryptos-k4-refinement-n8pbh3` (local commits; GitHub push was refused with 403, see
  the chat). The zip `handoffs/R30_handoff.zip` carries everything ChatGPT needs.
