# R81a pre-registration (Claude Code, 13 Nov 2026): R79's families on the PALIMPSEST and ABSCISSA alphabets, new position rules, and two checks

Written before the sealed holdout exists and before anything in R81a runs on K4. Code, cuts, seeds, books and decision
rules are fixed by this commit (`r81a/PROTOCOL.sha256`).

**Approval.**
- Tyler, 13 Nov 2026: "I'm fine with trying G5 if you think it'll help, but when we do the check of the plaintext we
  can't have that cheat of the known plaintext."
- Then: "You can do this check that you offered & im fine with us doing it in the future. Its just that if we get a
  possible solution, we will have to have legit proof that could be it before public submission."

**Specification:** `r80/FABLE_IDENTIFIABILITY.md` §2.2: G5 (other alphabets), G4 (new position rules), G6 (one wrong
letter).

## Rules for the published letters (from Tyler's two messages)
1. **Candidates come only from the ciphertext.** The blind run is frozen and pushed before any published letter is
   read.
2. **The published letters are only ever a check.** Nothing is fitted to them: no key letter is completed from them,
   and nothing is re-ranked by them. The R79 validator's completion step is dropped.
3. **The G5X check runs after the freeze, as an exclusion tool.** It checks settings that were never in the blind
   run. A setting that passes it is a lead and nothing more.
4. **Proof before anything leaves the repo.** Before any claim, or any submission (which only Tyler can decide), a
   lead needs:
   - a decode readable over all 97 letters;
   - a key that makes sense (a word or a stated rule);
   - re-encryption to K4 exactly;
   - an independent re-derivation.

## What is tested blind
One tableau stage with the letters in place, as in R79: `IDX[ca][c] = s·IDX[pa][p] + t·(IDX[ka][W[slot]] + S)`.
Keywords have 1–12 letters (any letters).

| Family | What | Conventions | Settings per ciphertext | log10 settings × 26^m |
|---|---|---|---|---|
| H7CT_A (G5) | Keyword + ciphertext feedback, lag 1–48 | pa, ca ∈ {AZ, KRY, PAL, ABS}, ka ∈ {AZ, KRY}, three operations; only the 72 not run in R79 | 41,472 | 20.54 |
| LIB_A (G5) | R79's 982 slot rules (including the walking key); stream none or feedback lag 1–7 | 24 new (stream none) / 72 new (feedback) | 512,448 | 21.65 |
| LIB_G4 (G4) | New rules: ROT (keyword rotated d places each pass), ALT (two keywords letter by letter), both with stream none or feedback 1–7; RESTART (keyword restarts at position 10–87) and SPLIT (keyword A, then keyword B from position 10–87), stream none | All conventions, R79's included | 168,000 | 21.28 |
| PROG_A (G5) | Progressive mask on a second alphabet, before or after a keyword stage | The 24 (pa, ca, sign) combinations with PAL or ABS on the plaintext or ciphertext side | 1,123,200 | 21.97 |

All four families together: log10 settings = 22.21.

**Solver and runner.**
- R79's C solver: pass 1 over every setting, pass 2 with 6 starts on each family's 150 best.
- The runner is `r81a/blind/run.py`, R79's runner with these families.
- For K4 it also freezes the pass-1 blind score of every setting of these four families and of R79's four keyword
  families (`OUT/scores/K4.npz`). So any setting a check flags already has a frozen blind decode, made without the
  published letters.

**Tests** (`r81a/tests/test_r81a.py`, all pass):
- the round trip, for every family;
- the decode path agrees with the explicit cipher;
- the solver reaches the truth's score on planted rows (11 of 12 exactly; the twelfth is an occurrence-count rule
  where a different text scores higher);
- the G4 encryption counters agree with the decode formulas.

## Cuts: letter model ≥ −1.30 and word model ≥ −2.50 per letter (R79's)
Development check (`r81a/dev81.py`, `r81a/results/DEV.json`; spent R79 gate books: *Lord Jim* and *A Room with a View*
for plants, *My Ántonia* and *Ethan Frome* for negatives):

| | Result |
|---|---|
| Positives | 24/24 confident. 21/24 recovered at R79's 95-letter bar (by family: 5/6, 5/6, 5/6, 6/6); all 24 at 85 letters |
| The three below 95 | 94, 85 and 86 letters right. Each was decoded best by a neighbouring rule giving a near-identical, readable text: a keyword restarting at a position against a plain repeat, and a 2-letter rule expressed two ways. Not a solver failure |
| Plants with 11–12 keyword letters | 8/8 |
| Weakest positive | −1.00 (letter model) / −1.58 (word model) |
| Negatives | 0/26 confident. The best is −1.50 (LIB_G4); best word score −2.12 |

- **The cuts stand.**
- **Change from R79, decided here before the holdout exists:** "recovered" means at least **85** of 97 letters right
  (R79 used 95), because R81a's rules overlap. The gate also reports the 95-letter and exact counts. A K4 decode with
  85 letters right would be plainly readable.

## Sealed synthetic gate (`r81a/sealed/make_holdout81.py`, seed 810300)
Four GITenberg books never used in this project and not in the letter model's training text:

| Role | Book | GITenberg | sha256 |
|---|---|---|---|
| Positives A | *Silas Marner* (Eliot) | 550 | 46b39559… |
| Positives B | *Main Street* (Lewis) | 543 | b68e3483… |
| Negative plaintext | *The Secret Garden* (Burnett) | 113 | 5d5bd30c… |
| Negative keys | *Howards End* (Forster) | 2946 | 4fcd53a8… |

**Items.**
- Positives: 80. That is 10 per family per book: 5 plain, 3 with 2 letters changed, and 2 in nonstandard spelling
  (R79's rules). Keyword length 2–10.
- STRETCH plants: 16, keyword length 11–12, reported only.
- Negatives: 100. These are R79's seven wrong-family generators, 12 each, plus 16 shuffles.

**Pass rule** (`r81a/sealed/gate81.py`):
- **Recovered:** at least 85 of 97 letters right (95-letter and exact counts also reported).
- **A family passes** iff at least 18 of its 20 positives are recovered and confident, AND 0/100 negatives are
  confident, AND every stored decode re-encrypts.
- **Only passing families run on K4.** A family that fails is not run and closes nothing.

## K4
**Target** (`r81a/sealed/prepare_k4.py`): unchanged K4 plus 100 shuffles (seed 810400).

**Blind run:** `--fams <passing> --full K4`, then freeze and push, then verify by re-encryption.

**Reveal** (`r81a/sealed/reveal81.py`; rules as R79):
- **CONFIDENT** iff K4's best decode clears both cuts and beats every shuffle's best.
- **SIGNAL** iff CONFIDENT and at least 10/24 published letters match; **SCORE_ANOMALY** iff CONFIDENT without that;
  **NO_SIGNAL** otherwise.
- Theorem K is reported, not used as a cut.

**Check of the frozen blind work** (`r81a/sealed/validate81.py`; after the reveal; check only):
- every setting of the R81a families and of R79's four keyword families, on K4 and 10 shuffles:
  - exact consistency with the 24 published letters (every setting has at least 12 checks);
  - **drop-one (G6):** consistency once any one letter is set aside;
- for each flagged K4 setting, its frozen blind score and a replay of the same deterministic blind solver call; the
  replayed score must equal the frozen one.

**G5X** (`r81a/sealed/g5x.py`; after the reveal; exclusion check, crib-assisted):
- R79's H7CT, H7TXT and LIB families with one unknown keyword alphabet: plaintext side or ciphertext side, any of
  R76's 77,229 orderings; the other alphabets AZ or KRY.
- Exact consistency by hash join; every setting has at least 12 checks.
- Run on K4 and 10 shuffles.
- Synthetic test: a planted setting with a large-tier alphabet was found, and it was the only setting found.

## What follows (fixed now)
| Result | Next |
|---|---|
| SIGNAL or SCORE_ANOMALY | Stop. Do not tune. Report raw; the proof steps above; Tyler decides |
| A setting consistent with the published letters (exactly, drop-one, or in G5X) on K4 and on no shuffle | Report raw as a lead. Show its frozen or replayed blind decode. Apply the proof steps. Not a solution until they pass |
| Settings consistent on K4 at the shuffles' rate | Chance; recorded |
| A family fails its gate | Report; it closes nothing |
| Everything negative | The passing families are closed in scope: blind STAT, and exact crib-assisted exclusion where every setting has ≥ 12 checks. G5X's scope is excluded exactly. Next: R80a (two stages) |

**Prior expectation:** NO_SIGNAL; no consistent setting anywhere.
