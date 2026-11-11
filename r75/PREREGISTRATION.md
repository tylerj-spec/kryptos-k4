# R75 pre-registration (Claude Code, 10 Nov 2026): identify K4's method class

Written before the sealed holdout exists and before anything in R75 runs on K4. All code, cuts, seeds, books and
decision rules below are fixed in this commit (`r75/PROTOCOL.sha256`).

**Approval:** Tyler approved the plan on 9 Nov 2026 ("I'm fine with it. If you can, produce the code & as much of the
program details as possible"). That includes the use of the published letters for diagnosis. The runs below still
wait for his go-ahead; see `r75/RUNBOOK.md`.

**Aim:** not another guessed cipher. R75 asks what kind of method K4 uses, with two instruments:
1. **A diagnosis of the key that the published letters imply** (does it have structure, and of which kind?), calibrated
   on synthetic ciphers whose family is hidden.
2. **A close-out of the two simple method classes never tested** (`r75/METHOD_MATRIX.md`, rows 4 and 5), blind first,
   then exactly for every possible key.

**Order of work.** Every use of the published letters comes after the blind K4 run is frozen and pushed.

| Part | What | Uses K4 ciphertext | Uses published letters |
|---|---|---|---|
| A | Sealed synthetic gate for the fixed-method scanner | No | No |
| B | Blind K4 run of the fixed-method families, then freeze | Yes | No |
| C1 | Verify by re-encryption; sealed reveal | Yes | Yes (after the freeze) |
| C2 | Exact checks for all keys (F1X, F2X, F3X; control F0X) | Yes | Yes (crib-assisted, labelled) |
| C3 | Key shape and key class | Yes | Yes (diagnosis; produces no plaintext) |

## Fixed-method families (`r75/families.py`; 6,934,560 methods)
Every member turns a 97-letter ciphertext into exactly one text. A stage is a keyword cipher on a tableau with a
plaintext alphabet, a ciphertext alphabet, a key-numbering alphabet and an operation (VIG, BEAU or VARB).

| Family | Method | Tier A: KRYPTOS / PALIMPSEST / ABSCISSA, every phase; alphabets AZ, KRY, PAL, ABS; key numbering AZ or KRY | Tier B: 80 words from K0–K3 and the sculpture's story (`r75/data/kryptos_words.txt`), phase 0; alphabets AZ, KRY |
|---|---|---|---|
| F1 | Two stages in place on different tableaux | 4,320,000 | 1,843,200 |
| F2 | Interrupted key: after a trigger letter (plaintext or ciphertext) the key restarts, stalls or skips | 374,400 | 299,520 |
| F3 | Held key: each key letter used 2–8 times in a row | 84,000 | 13,440 |

- **F1 contains ChatGPT's PR #67 family** (2,880 settings). The two implementations agree on all 2,880
  (`r75/REVIEW_PR67_PR68.md`).
- **Where the families came from:**
  - F1 from K2's "LAYER TWO" and the gap found in the ledger review.
  - F2 and F3 from the repo's own list of untested ideas (`docs/CIPHER_TYPES_TESTED.md` §17, item 6).
  - **Disclosure:** on 9 Nov, before these files existed, I worked out by hand that the published letters' key
    repeats more than chance under plain A–Z sums. That made F2 and F3 more interesting to me. No setting, keyword or
    cut was chosen from it.

## Blind scanner (`r75/blind/run.py`)
- **Scan:** every method decrypts the ciphertext.
- **Ranking:** the 400 best by a generic quadgram table are re-scored with the R59 order-6 letter model (sha256
  `b1a2a3c7…`, checked) and the R59 word model.
- **Stored:** the 5 best distinct decodes and the best of each sub-family; for K4, a 25-decode review packet (best of
  each sub-family first, then by letter model).
- **Confidence cuts:** letter model ≥ −1.45 and word model ≥ −2.50 per letter (R74's cuts).
  - Development check (`r75/dev.py`, seeds 750201/750202, `r75/results/DEV.json`; books: *The Moonstone*, *The Scarlet
    Pimpernel*; negatives from *The Mysterious Affair at Styles* and *Around the World in 80 Days*, all spent
    holdouts): 36/36 planted messages recovered and confident.
  - Worst positive −0.88 / −1.14; best of 64 negatives −1.80 / −3.02. The cuts stand unchanged.

## Part A: sealed synthetic gate (`r75/sealed/make_holdout.py`, seed 750300)
Four GITenberg books never used in this project and not in the letter model's training text:

| Role | Book | GITenberg (file) | sha256 |
|---|---|---|---|
| Positives A | *The Lost World* (Doyle) | 139 (`139.txt`) | f6b39bd6… |
| Positives B | *Three Men in a Boat* (Jerome) | 308 (`308-0.txt`) | 8947f71d… |
| Negative plaintext | *The Wind in the Willows* (Grahame) | 289 (`289-0.txt`) | f875d0ae… |
| Negative keys | *Kim* (Kipling) | 2226 (`2226.txt`) | 85a20ed2… |

- **60 positives:** 5 per sub-family per book, 6 per book with 2 letters changed; hidden settings.
- **100 negatives:** 12 from each of R71's seven generators, plus 16 shuffles of positives.
- **Sequence:** commit `blind.tsv` with the truth's hash in the commit message → blind run → freeze and push →
  verify (every stored decode re-encrypts) → open the truth → gate.
- **Gate (`r75/sealed/gate.py`): PASS** iff ≥ 54/60 positives are recovered exactly **and** confident, **and** 0/100
  negatives are confident, **and** verification passes.
- **If the gate fails:** Part B and the reveal do not run. C2 and C3 do not depend on the scanner and may still run
  after Tyler agrees.

## Part B: blind K4 run
- **Target** (`r75/sealed/prepare_k4.py`): unchanged K4 (sha256 2797de14…) plus 100 shuffles (seed 750400).
- **Run:** `r75/blind/run.py … --full K4`, then freeze and push before anything in Part C.

## Part C1: reveal (`r75/sealed/reveal_k4.py`)
- **CONFIDENT** iff K4's best decode clears both cuts **and** beats every shuffle's best.
- **SIGNAL** iff CONFIDENT and ≥ 10/24 published letters match; **SCORE_ANOMALY** iff CONFIDENT without that;
  **NO_SIGNAL** otherwise.
- **Whole family (crib-assisted):** every one of the 6,934,560 K4 decodes is compared with the published letters.
  - Any with ≥ 14/24 is listed raw.
  - The chance of one such match in the whole family is about 10⁻⁷.
- **Packet:** if all are below the cuts, they are labelled LOW-CONFIDENCE RAW OUTPUTS.

## Part C2: exact checks for all keys (`r75/sealed/exact.py`; crib-assisted, labelled as in R70 Erratum 1)
**Question:** with any key letters at all, can a member of the family encipher the published letters to K4's letters?

| Check | Scope |
|---|---|
| F0X (control) | One stage, any repeating key, periods 1–26. Must reproduce L03/L04 |
| F1X | Two stages in place, any keys, periods 1–26 each, alphabets AZ/KRY/PAL/ABS on all four sides, each stage additive or reverse: 692,224 settings |
| F2X | Interrupted key, any key, periods 1–26, every trigger letter, both trigger kinds, all three actions |
| F3X | Held key, any key, hold 2–12, periods 1–26, every phase |

- **"Checks"** = independent equations the published letters impose beyond fixing the key. Settings with fewer than
  3 are not counted.
- **Decodes:** where the published letters pin the key, the full 97-letter decode is produced and scored. Up to 3 key
  letters that no published position pins are completed blind (best quadgram score); for a plaintext-triggered
  interrupted key and a two-stage cipher the limits are 1 and 2.
- **Verdict per family:** **CONSISTENT** iff some full decode clears both cuts; otherwise **NO_SOLUTION**. The same
  check runs on 20 shuffles of K4 for comparison.
- **Synthetic validation** (`exact.py --selftest`, `r75/results/EXACT_SELFTEST.json`; keys are random letters, not
  words):
  - 12/12 plants found and decoded exactly by their own family's check (4 each for F1X, F2X, F3X);
  - 0/4 random ciphertexts gave a readable decode in any family.
- **Limit, stated now:** a random ciphertext leaves about 1,900–2,500 F1X settings feasible at 3–9 checks.
  Feasibility alone therefore means little; a readable decode is what counts.

## Part C3: key shape and key class (`r75/sealed/keyshape.py`, `r75/sealed/keyclass.py`)
- **Key shape:** six statistics of the implied key under 8 numbering conventions (48 cells), against 200,000
  shuffles of K4 (seed 750100), with a family-wise correction.
  - **SHAPE_CONFIRMED** iff the corrected p ≤ 0.05; **SUGGESTIVE** iff ≤ 0.20; else **NO_SHAPE**.
  - Self-test (`KEYSHAPE_SELFTEST.json`): planted held keys and period-40 keys were flagged 5/5 each.
  - False alarms (`KEYSHAPE_FALSE_ALARM.json`, 80 random-key ciphers): SHAPE_CONFIRMED in 5%; SUGGESTIVE or stronger
    in 22.5%. That is the designed rate.
- **Key class:** nearest neighbours among synthetic ciphers of ten classes (model `r75/results/KEYCLASS_MODEL.npz`).
  - Calibration with the class hidden (`KEYCLASS_CALIBRATION.json`):

    | True class | Named correctly |
    |---|---|
    | Held | 100% |
    | Autokey (plaintext / ciphertext) | 99.8% / 99.8% |
    | Few values | 89% |
    | Progressive | 83% |
    | Digits | 70% |
    | Periodic 30–52 | 60% |

  - A random key is given a structured label 1.6% of the time.
  - Random keys, running keys and two-layer ciphers cannot be told apart; they are reported together as
    NO_VISIBLE_STRUCTURE.
- **Disclosure:** my hand look on 9 Nov covered the A–Z conventions for T1, T2 and T3. The statistics list was
  written after it. The corrected p-value is therefore a calibration of how unusual K4's strongest cell is, not
  independent confirmation.

## What follows (fixed now)
| Result | Next |
|---|---|
| SIGNAL, or any exact check CONSISTENT | Stop. No tuning. Independent re-derivation and re-encryption; then Tyler decides about an outside check |
| Key class is HELD, FEWVALUES or DIGITS | A design round on irregular keys under the flagged numbering, with its own pre-registration (R76) |
| Key class is an autokey, PROGRESSIVE or PERIODIC | It contradicts L03, L13 or L17: audit those rows under the flagged numbering before anything else |
| NO_VISIBLE_STRUCTURE, and all checks NO_SOLUTION | Rows 2, 4 and 5 of the matrix are closed. What remains (rows 3, 6, 7, 9) cannot be settled from 97 letters and 24 published ones. Say so, and wait for outside information |
| MIXED | Report the raw numbers; no new K4 run without a reviewed proposal |

**Open point:** ChatGPT's note in PR #67 says a diagnosis from the published letters must not steer model choice.
This table assumes it may, per Tyler's approval. If Tyler decides otherwise, rows 2 and 3 of the table are void and
C3 becomes a record only.

**Prior expectation** (stated before the run): NO_SIGNAL; all exact checks NO_SOLUTION; key class MIXED or a weak
FEWVALUES/DIGITS.

## Amendment 1 (10 Nov 2026, before any R75 data was generated: no holdout, no K4 target, no run)
Written after reviewing ChatGPT's latest handoff (PR #40 comment of 10 Nov, summarising its R62 audit, PRs #41–#43).

**1. The open point is settled.**
- That handoff restates Tyler's rule: "clue-*motivated* selection of methods/key-source hypotheses is permitted, but
  known letters/positions must never be inputs to algorithm, candidate generation, scoring, tuning, training,
  filtering or key choice".
- The "What follows" table stands as written. Part C3 may steer which *method class* the next round tests. That
  round's algorithm still never sees the published letters.

**2. R62's findings change nothing in Parts A–C1.**
- Carter & Mace 1923 is in the letter model's training text (R62A). R75's six books are not, so the holdout stays
  independent.
- R62B's power check supports the letter model on modern English. R75 already uses it with the same cuts.

**3. Added: Part C2b, grid keys (`r75/sealed/gridx.py`; hypothesis H4 of `r76/HYPOTHESES.md`).**
- **Why now:** several ciphertext-only features point to a grid layout, and this check is cheap and decisive:
  - K4's joint width-7 / width-21 fingerprints (R71, rare at 8 × 10⁻⁵ against shuffles);
  - R61's COL_LT route gap (R62C: 2 of 300 fresh shuffles reach it; noticed after the fact);
  - the SNAKE_L / row-4 effects (R65, R69).
- **Disclosure:** both published strings also start at a multiple of 21 plus 1. That is noticed from the published
  letters; it motivated the choice of family, not any setting.
- **Definition:** the message in rows of w letters starting at column o (w 2–48, every o). One key repeats along every
  row (one letter per column); a second key changes once per row; each key on its own stage.
  - The 1,024 two-stage configurations of F1X, in both orientations (column key first or row key first).
  - That includes the plain additive form, key = column letter + row letter.
- **Decision:**
  - A setting is checked when it has ≥ 5 independent checks.
  - It is decoded when it has at most 26 key solutions. Unpinned rows or columns are completed blind by coordinate
    ascent on quadgrams.
  - **CONSISTENT** iff some full decode clears both cuts (letter model ≥ −1.45, word model ≥ −2.50); else
    **NO_SOLUTION**.
  - The same check runs on the first 20 shuffles of the K4 target. If any shuffle is also CONSISTENT, a K4 CONSISTENT
    is reported as a calibration failure, not a lead.
- **Synthetic validation** (`gridx.py --selftest`, `r75/results/GRIDX_SELFTEST.json`; random keys):
  - 6/6 grid-key plants (widths 7, 7, 21, 21, 11, 4) gave a readable decode with 72–97 of 97 letters right. The
    misses are rows that no published letter pins.
  - 0/6 random ciphertexts gave a readable decode; their best was −1.60 per letter.
- **Runbook:** step C runs `gridx.py K4 $LM r75/k4/TARGET.tsv r75/k4/GRIDX.json 20` after `exact.py`.
