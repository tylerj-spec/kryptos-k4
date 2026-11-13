# R79 pre-registration (Claude Code, 12 Nov 2026): H7, the state-rule library with the walking key, a progressive mask, and the rest of H11

Written before the sealed holdout exists and before anything in R79 runs on K4. All code, cuts, seeds, books and
decision rules below are fixed by this commit (`r79/PROTOCOL.sha256`).

**Approval.** Tyler, 12 Nov 2026 ("Swapped to opus, send it"), replying to: "The next step is R79 on the cheaper model,
as ChatGPT wrote it."

**Specification.**
- ChatGPT's R79 instructions, relayed by Tyler after PR #72.
- `r78/FABLE_ANALYSIS.md` Parts 1–4 and 8 (H11 cycle solver, SLOTSOLVE, Theorem K, H7, walking key).
- `r78/FABLE_MASKING.md` §B4 (state-rule library) and §C1 (progressive mask).

**Order of work:** sealed synthetic gate → blind K4 run → freeze and push → verify → reveal → crib-assisted validator.
Every use of the published letters comes after the freeze.

## What is tested
One tableau stage, letters in place: `IDX[ca][c] = s·IDX[pa][p] + t·K (mod 26)`. The key value at position i is a
keyword letter read at a slot, plus an optional known stream: `K = IDX[ka][W[slot(i)]] + S(i)`. Keywords have
1–12 letters and are otherwise unknown (any letters).

| Family | Slot | Stream S | Conventions | Settings per ciphertext | log10 settings × 26^m |
|---|---|---|---|---|---|
| H7CT (H7) | i mod m | ciphertext feedback `IDX[ka][c[i−L]]`, L 1–48 (0 before L) | pa, ca, ka ∈ {AZ, KRY} × VIG/BEAU/VARB (24) | 13,824 | 20.06 |
| H7TXT (H7) | i mod m | K1–K3 plaintext (769 letters, first copy of K3) or K1–K3 ciphertext (CIA transcription, 768), every offset, both directions (2,690 streams) | 24 | 774,720 | 21.81 |
| LIB (walking key and state rules) | 982 rules, below | none (8 conventions) or ciphertext feedback lag 1–7 (24) | 8 or 24 | 170,816 | 21.18 |
| PROG (progressive mask) | i mod m | none; a shift a·i + b on a second alphabet A1 ∈ {AZ, KRY, PAL, ABS}, before the stage (A1 ≠ pa) or after it (A1 ≠ ca) | pa, ca ∈ {AZ, KRY} × VIG/BEAU | 374,400 | 21.49 |
| H11 (rest) | — | the key at i is the plaintext letter at route position p[i]; 73,537 routes (R76's 64,782 plus every affine map not already there) | the 16 conventions L167 leaves open | 1,176,592 | 6.07 |

**LIB rules** (`r79/families.py: mapdefs`), all with m ≤ 12:
- **Walking key (WK-C)**, 176 rules: the place in the keyword moves by ±(number of the cipher letter just written,
  + 0 or 1), numbered in any of the four alphabets.
- **Reverse at a trigger (REV)**, 319: the direction flips at a trigger cipher letter (one letter, or the letters of
  KRYPTOS, PALIMPSEST or ABSCISSA).
- **Omit (OMIT)**, 22: pass j skips element j, or starts at element j.
- **Numeric interruption (IKN)**, 75: segment lengths from the alphabetical ranking of a sculpture word.
- **Occurrence count (CNT)**, 11: the slot is the count of the previous cipher letter.
- **Letter class (CLS)**, 44: the class of the previous cipher letter (eight classes), alone or combined with i mod m₁.
- **Controls**, all already excluded: repeating (REP, 12), held (HELD, 33), restart at a trigger (TRIG, 286).

**H11 conventions** (left open by L167):
- the same alphabet for plaintext and key (AZ or KRY), Vigenère, ciphertext alphabet KRY or ABS: 4;
- plaintext and key alphabets different (AZ/KRY or KRY/AZ), ciphertext alphabet AZ or KRY, three operations: 12.

**Deferred** (not in R79): the plaintext-driven walking key (WK-P) and plaintext feedback, which need sequential
search; unknown keyword alphabets; two keyword stages with unknown keywords (LAYERSOLVE).

## Solver and runner
**Solver.**
- `r79/slotsolve.c`: SLOTSOLVE for the keyword families and the H11 cycle solver (r78 Theorem 1).
- Objective: coordinate ascent on quadgrams.
- Pass 1: every setting, one start (each slot's best single-letter fit).
- Pass 2: each family's 150 best settings again, with 6 starts.

**Runner** (`r79/blind/run.py`): keeps each family's 60 best distinct decodes; keyword decodes are re-derived by the
explicit decryptor; everything is re-scored by the letter model (sha256 `b1a2a3c7…` checked at start) and the word
model.

**Stored per ciphertext:** the 5 best decodes, the best of each family, and H11's count of settings passing the
cycle conditions (ciphertext only). For K4, also a 25-decode review packet.

**Tests** (`r79/tests/test_r79.py`, all pass):
- explicit encryption and decryption round trip;
- the vectorised decode path agrees with the explicit cipher;
- the solver recovers planted rows;
- H11 cycles close at the truth, and the solver's output re-encrypts;
- the sum invariant holds;
- every slot rule uses only earlier ciphertext.

## Confidence cuts: letter model ≥ −1.30 and word model ≥ −2.50 per letter
**Development check** (`r79/dev.py`, `r79/results/DEV.json`; spent R76 books: *The Woman in White* and *The Sign of
the Four* for plants, *The Invisible Man* and *The Jungle Book* for negatives):

| | Result |
|---|---|
| Positives | 30/30 recovered and confident: 6 per family; 10 plain, 10 with 2 letters changed, 10 in nonstandard spelling |
| Plants with 11–12 keyword letters | 8/8 |
| Weakest recovered positive | −1.09 (letter model) / −1.36 (word model) |
| Negatives | 0/26 confident at the old cut. The best is −1.53 (PROG), then −1.53 (H7TXT); best word score −2.20 |

**Change from R74–R76.** The old letter-model cut, −1.45, sits only 0.08 above the best negative. R76's negatives
reached about −1.8; these families' free keywords let random text score higher.
- The letter-model cut is therefore −1.30, about midway between the weakest positive (−1.09) and the best negative.
- The word cut stays at −2.50.
- This is decided here, before the holdout exists.

**Theorem K** (r78 §2.1, corrected in Part 8), reported, not used as a cut:
- For all five families, log10 settings = 22.05.
- At 10⁻⁶ expected false alarms the cut is −1.126 against a uniform null and −0.916 against shuffles of K4's letters.
- The bound assumes families fixed in advance; K4's history of selection is not covered. Shuffles and wrong-family
  plants remain the operative controls.

## Sealed synthetic gate (`r79/sealed/make_holdout.py`, seed 790300)
Four GITenberg books never used in this project and not in the letter model's training text:

| Role | Book | GITenberg | sha256 |
|---|---|---|---|
| Positives A | *Lord Jim* (Conrad) | 5658 (`5658.txt`) | 10a716c3… |
| Positives B | *A Room with a View* (Forster) | 2641 (`2641.txt`) | d9a82687… |
| Negative plaintext | *My Ántonia* (Cather) | 242 (`242.txt`) | 84bac88c… |
| Negative keys | *Ethan Frome* (Wharton) | 4517 (`4517.txt`) | d992ab24… |

**Positives: 100.**
- 10 per family per book, with random settings. Keyword length 2–10.
- Each 10 is 5 plain, 3 with 2 letters changed, and 2 in nonstandard, Germanic-looking spelling: PH→F, CK→K, C→K
  before A/O/U, W→V, initial Y→J, initial TH→D, final ED→T, each with probability 0.35 per eligible word.
- Plus 16 STRETCH plants, keyword length 11–12, reported only.

**Negatives: 100.**
- 12 from each of seven wrong-family generators: OTP, RUNKEY, HOMOPHONIC and GROMARK from R71; PERIODIC, CTAK and
  PTAK with a random plaintext alphabet only, because their A–Z and KRYPTOS forms are R79 members.
- 16 shuffles of positives.

**Gate** (`r79/sealed/gate.py`):
- **Recovered:** the best decode agrees with the plant in at least 95 of 97 letters. Exact recovery is reported
  too.
- **A family passes** iff at least 18 of its 20 positives are recovered and confident, AND 0/100 negatives are
  confident, AND every stored decode re-encrypts.
- **K4 is run with the passing families only.** A family that fails is not run on K4 and closes nothing.

## K4
**Target** (`r79/sealed/prepare_k4.py`): unchanged K4 (sha256 2797de14…) plus 100 shuffles (seed 790400).

**Blind run:** `r79/blind/run.py … --fams <passing> --full K4`, then freeze and push, then verify by re-encryption.

**Reveal** (`r79/sealed/reveal_k4.py`):
- **CONFIDENT** iff K4's best decode clears both cuts and beats every shuffle's best.
- **SIGNAL** iff CONFIDENT and at least 10/24 published letters match.
- **SCORE_ANOMALY** iff CONFIDENT without that.
- **NO_SIGNAL** otherwise.
- The Theorem K cut is reported beside the outcome.

**Crib-assisted validator** (`r79/sealed/validate79.py`), after the reveal, labelled as in R70 Erratum 1:
- **Keyword families:** every setting is checked for agreement with the published letters; feasible settings are
  counted by number of checks, for K4 and 10 shuffles. Up to 50 feasible settings per family with 5 or more checks
  are completed and scored.
- **H11:** the exact checks where a published position's key position is also published.
- Its completions are never blind discoveries.

## What follows (fixed now)
| Result | Next |
|---|---|
| SIGNAL or SCORE_ANOMALY | Stop. Do not tune. Report raw; independent re-derivation; then Tyler decides about any outside check |
| A validator setting with ≥ 5 checks completes to a decode that clears both cuts, on K4 but on none of the 10 shuffles | Report raw as a crib-assisted lead; not a blind discovery; design round |
| A family fails its gate | Report which and why; it closes nothing; fix only in a new pre-registered round |
| Everything negative | The passing families are closed in the stated scope (STAT, blind). The validator's counts are recorded. The next step is LAYERSOLVE (`r78/FABLE_MASKING.md` §B7) |

**Prior expectation** (stated before the run): NO_SIGNAL; the validator's feasible counts for K4 at chance level.
