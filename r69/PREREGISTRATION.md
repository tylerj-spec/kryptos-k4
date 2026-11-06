# R69 pre-registration (Claude Code, 6 Nov 2026): which carved rows carry K4's SNAKE_L structure?

Written before the holdout plants are generated and before any R69 run on K4. Follows `r53/BLIND_RULES.md` as
clarified by Tyler: the algorithm reads only the ciphertext and generic models.

**R69 never uses the published K4 letters.** It decrypts nothing that is later compared with them, and no R69 code
holds them. Tyler approved running it on 6 Nov 2026 ("get these started as long as we are making progress to K4").

## Why
- **The anomaly:** K4's only replicated structural anomaly is the SNAKE_L route gap under R64's German-key stage 1:
  - R64 found it;
  - R65 replicated it against 300 fresh shuffles (0/300);
  - R67 found it beyond 192 IC-matched structured ciphers (0/192);
  - R65b showed it is not a German running key.
- **What SNAKE_L changes:** it differs from carved order only in reading K4's carved rows 2 and 4 (31 letters each)
  right-to-left. That alone moves the frozen stage-1 total from −357.3 to −320.9.
- **Historical precedent:** the research in PR #54 and the Deep Research report:
  - alternating-direction rows ("Alternate Horizontal", Hitt 1916) are a documented manual route;
  - Sanborn worked on 14×31 grid sheets;
  - but no source says K4 was written this way.
- **The question:** is the effect tied to specific rows (a copy or writing direction per row), or to the SNAKE_L
  combination as a whole? Does it peak at the sculpture's layout (K4 starting at column 27 of a 31-wide row) or at
  another start column? The report notes the 2007 worksheet "differs slightly" from the sculpture.
- **What a clear answer buys:** it lets the next decryption round run on one reading order instead of 11. If it shows
  nothing, the SNAKE_L lead is retired.

## Readings (frozen: `r69/blind/make_patterns.py` → `r69/data/patterns.txt`, sha256 d6937a16…)
Convention as R61: CT[j] = X[perm[j]], with X the text in reading order.

- **F family (16, primary):** K4's four carved rows, top to bottom.
  - Row 1 is the 4 letters at columns 27–30; rows 2–4 are 31 letters each.
  - Each row is read left-to-right (bit 0) or right-to-left (bit 1), giving `F_b1b2b3b4`.
  - `F_0000` is carved order, `F_0101` is SNAKE_L and `F_1010` is SNAKE_R (asserted against `r61/routes.txt`).
- **B family (62, secondary):** a boustrophedon over 31-wide rows, if K4 had started at column c (0–30).
  - Cell i sits at (r, col) = divmod(c + i, 31).
  - Row r is read right-to-left iff r + q is odd, with q ∈ {0, 1}; the name is `B_cCC_qQ`.
  - `B_c27_q0` is SNAKE_L and `B_c27_q1` is SNAKE_R.

## Instrument (unchanged; nothing tuned for R69)
- **Engine:** R64/R65's stage 1 under the GERMAN key model, via `r69/blind/run.py`, which wraps `r64/blind/run.py`.
  - Solver: R63 two-model beam solver `r63/blind/rk2_solve.cpp` (sha256 d1be0d9c…), binary sha256 f171dbe5… (as
    frozen in R65).
  - Parameters: beam 15000, TOPN 2000, LAMBDA 1, all 6 conventions, POLISH_M 0, WORDS 20000.
  - Models: English LM pinned in `r59/blind/LM_SHA256`; German key model and words pinned in
    `r63/blind/MODELS.sha256`.
- **Statistic per reading:** T = the stage-1 best total over the 6 conventions.
- **Duplicates:** identical permutations are solved once (`F_0101` = `B_c27_q0`, `F_1010` = `B_c27_q1`).

## Target (`r69/sealed/prepare.py`, run after this file is pushed)
- **K4:** the unchanged ciphertext (sha256 2797de14…), all 78 readings (set A).
- **SHUF_000–299:** 300 fresh frequency-preserving shuffles of K4.
  - Seed 690070; none equals K4 or any R64/R65 null.
  - SHUF_000–099 get all 78 readings (set A); SHUF_100–299 get the 16 F readings (set F).
- **R67_CTRL_*:** R67's 192 IC-matched structured-cipher controls, F readings only.
  - Six families (OTP, periodic Vigenère, Quagmire III, plaintext autokey, Quagmire III + route, homophonic + route).
  - File `r69/data/r67_structured.tsv` (sha256 b4430b3f…), extracted from PR #50 head 14c6690 (`BLIND.tsv` sha256
    3f22941e…, `SEALED_TRUTH.json` sha256 ee3af82d…, positives removed).
- **Pooled nulls:** N = 492.

## Holdout gate (fixed now; run before K4)
- **Plants:** `r69/sealed/make_plants.py hold_pt.txt de_hold.txt 690001 OUT` (seed 690001), 40 plants.
  - Plaintext: held-out English, *The Call of the Wild* + *The Hound of the Baskervilles*, R64's holdout books
    (sha256 17f61fafc…).
  - Key: held-out Europarl German file 10 (sha256 84794e5b…), the sources of R64's and R67's positives.
  - Convention: uniform from AZ/KRY × VIG/BEAU/VARB.
  - Windows: non-overlapping, new seed.
  - 32 F plants (each F reading twice, set F) and 8 B plants (8 distinct start columns c ≠ 27, random parity, set A).
- **Gate:** `attribute.py gate`.
  - An F plant is *rows_ok* when the signs of its main effects E_2, E_3, E_4 all match its true bits.
  - **PASS iff rows_ok ≥ 24/32.**
  - Row 1 (4 letters) and the B plants' argmax recovery are reported but not gated.
- **If the gate fails:** INCONCLUSIVE; no K4 run.

## Statistics and outcomes (`r69/sealed/attribute.py k4`, after the freeze and `verify.py`)
- **Main effects:** for each ciphertext, E_r = mean T(b_r = 1) − mean T(b_r = 0), r = 1–4, over the 16 F totals.
  This is a 2⁴ factorial.
- **Other quantities:**
  - S_max = max of the 16 F totals;
  - I_24 = mean T(b2 = b4) − mean T(b2 ≠ b4), descriptive only.
- **p-values:**
  - p_r = (1 + #nulls with |E_r| ≥ |E_r(K4)|) / 493, two-sided, pooled nulls;
  - also reported separately against the shuffles and against the structured controls;
  - p_S = (1 + #nulls with S_max ≥ K4's) / 493.
- **Significance:** row r is SIGNIFICANT iff p_r ≤ 0.0025 (0.01 / 4).
- **Outcome** (first that applies):

  | Outcome | Condition | What follows |
  |---|---|---|
  | **ARTIFACT** | p_S > 0.01 | Retire the SNAKE_L lead from future designs. |
  | **ALTERNATING** | The significant rows are exactly {2, 4}, both with E > 0 | The next decryption round is restricted to K4's best F reading. |
  | **ROW_SPECIFIC** | Any other non-empty set of significant rows | The next decryption round is restricted to K4's best F reading. |
  | **DIFFUSE** | No row significant | SNAKE_L stays one of the 11 standard paths; no restriction. |

- **Secondary (descriptive, no outcome):** on K4 and SHUF_000–099:
  - B_max = the best of the 62 B readings, and its argmax start column and parity;
  - D = B_max − T(SNAKE_L);
  - p-values of K4's B_max and D against the 100 shuffles;
  - K4's profile over start columns.
- **Post-hoc power report:** after the run, the plants' |E_r| are compared with the 0.0025 null bar.

## Sequence
1. This file plus code, pushed.
2. Plants generated; the truth hash is recorded in the commit message.
3. Holdout run; freeze; `verify.py`; gate.
4. Target generated.
5. K4 + 492 nulls run.
6. Freeze, push, `verify.py`, then `attribute.py k4`.
7. RESULT.md and ledger.

## Development record (development sources only; K4 never run)
- **Sources:** 4 F plants from `make_plants.py dev_pt.txt de_dev.txt 69002`. *Tom Sawyer* (sha256 b27556fd…) and
  Europarl dev file 9 (sha256 3e02ce93…) are R64's development sources.
- **Plants:** F_1000, F_1110, F_0101 and F_1111.
- **Result:** the argmax was correct 4/4, and the signs of E_2–E_4 were correct 4/4 (12/12 rows). Row 1 was correct 3/4.
  Main-effect magnitudes were 9–53.
- **Speed:** stage 1 costs about 8.5 core-seconds per reading. Full run ≈ (1 + 100 + 8) × 76 + (200 + 192 + 32) × 16
  ≈ 15,000 readings ≈ 9 h on 4 cores.

## Not claimed
- R69 cannot identify a cipher, key or plaintext.
- An ALTERNATING or ROW_SPECIFIC outcome says where the structure sits, not what it is.
- The statistic was first noticed after looking at K4 (R64); R65 and R67 replicated it, and R69 asks a new question
  of it.
