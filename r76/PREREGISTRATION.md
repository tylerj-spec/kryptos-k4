# R76 pre-registration (Claude Code, 11 Nov 2026): H1 new alphabet keyword, H2 scrambled key

Written before the sealed holdout exists and before anything in R76 runs on K4. All code, cuts, seeds, books and
decision rules below are fixed in this commit (`r76/PROTOCOL.sha256`).

**Approval:** Tyler, 11 Nov 2026 ("Sure, send it"), replying to: "I'd spend the credit on me (Opus) running H1 and
H2 next."

**Specification:** `r76/HYPOTHESES.md` (H1, H2 with H2b and H2c, H6), refined as below.

**Order of work:** sealed synthetic gate → blind K4 run → freeze and push → verify → reveal → exact checks. Every use of
the published letters comes after the freeze.

## Refinements to `r76/HYPOTHESES.md`
- **Fact A is narrower than written.** A self-encryption forces a zero key only for the additive form (VIG/VARB) with
  the same alphabet on both sides. For Beaufort with the same alphabet the key there is 2x, not 0. The exact check
  below covers both forms whatever Fact A says.
- **H1 control from the ledger.** L21 excludes arbitrary per-slot alphabets, which includes every H1 setting, at
  periods 1–7, 9, 10, 14, 15, 17, 21, 25, 34, 42, 43, 45 and 50.
  - At those periods H1X must find 0 feasible settings; anything else is a bug.
  - H1's new ground is periods 8, 11–13, 16, 18–20, 22–24, 35–41, 44 and 46–48.
- **A feasible setting matters on its own.** Random ciphertexts give 0 feasible settings in every check (self-test
  below), so K4's feasible settings are listed and compared with 10 shuffles, not only its readable decodes.

## Blind fixed-method families (`r76/families.py`; 13,700,640 methods)
| Family | Method | Count |
|---|---|---|
| B1 (H1) | One keyword stage. Plaintext and ciphertext alphabets each one of 81 (A–Z, and every `r75/data/kryptos_words.txt` word with the rest of the alphabet in order). Key = one of those 80 words, phase 0, numbered A–Z or KRYPTOS. VIG/BEAU/VARB | 3,149,280 |
| B2 (H2) | Keyword key scrambled by a route, message in place. Key letter at position j = word[(p[j] + phase) mod length], with p one of 17,524 routes (R72's sheet routes, every K3-style double rotation 2–48, every single turn). KRYPTOS / PALIMPSEST / ABSCISSA at every phase; alphabets A–Z or KRYPTOS; VIG/BEAU/VARB | 10,514,400 |
| B3 (H2c) | R74's K1 → K3 → K2 sandwich with R72's sheet routes in place of R61's | 36,960 |

**Runner:** `r76/blind/run.py`, R75's runner with these families.
- The letter model (sha256 `b1a2a3c7…`) is checked at start.
- Ranking: quadgrams; the 400 best are re-scored by the letter model and the word model.
- Stored: the 5 best distinct decodes and the best of each family; for K4, a 25-decode packet.

**Cuts:** letter model ≥ −1.45 and word model ≥ −2.50 per letter (R74 and R75).
- **Development check** (`r76/dev.py`; *The Moonstone*, *The Scarlet Pimpernel*; negatives from *Styles* and *80
  Days*, all spent holdouts; `r76/results/DEV.json`):
  - 36/36 planted messages recovered and confident (12 per family);
  - worst positive −0.98 / −1.37; best of 64 negatives −1.75 / −3.14.
- The cuts stand.

## Sealed synthetic gate (`r76/sealed/make_holdout.py`, seed 760300)
Four GITenberg books never used in this project and not in the letter model's training text:

| Role | Book | GITenberg (file) | sha256 |
|---|---|---|---|
| Positives A | *The Woman in White* (Collins) | 583 (`583.txt`) | 19007f23… |
| Positives B | *The Sign of the Four* (Doyle) | 2097 (`2097.txt`) | 940b4047… |
| Negative plaintext | *The Invisible Man* (Wells) | 5230 (`5230.txt`) | 567a5212… |
| Negative keys | *The Jungle Book* (Kipling) | 236 (`236-0.txt`) | 2f9486eb… |

- **60 positives:** 10 per family per book, 6 per book with 2 letters changed; hidden settings.
- **100 negatives:** 12 from each of R71's seven generators, plus 16 shuffles of positives.
- **Gate (`r76/sealed/gate.py`): PASS** iff ≥ 54/60 positives are recovered exactly **and** confident, **and** 0/100
  negatives are confident, **and** every stored decode re-encrypts.
- **If it fails,** the blind K4 run does not happen. The exact checks do not depend on the scanner and wait for
  Tyler.

## K4
- **Target** (`r76/sealed/prepare_k4.py`): unchanged K4 (sha256 2797de14…) plus 100 shuffles (seed 760400).
- **Blind run:** `r76/blind/run.py … --full K4`, then freeze and push, then verify by re-encryption.
- **Reveal (`r76/sealed/reveal_k4.py`):**
  - **CONFIDENT** iff K4's best decode clears both cuts and beats every shuffle's best.
  - **SIGNAL** iff CONFIDENT and ≥ 10/24 published letters match; **SCORE_ANOMALY** iff CONFIDENT without that;
    **NO_SIGNAL** otherwise.
  - Whole-family letter count, listing any method with ≥ 14/24.

## Exact checks for every key (`r76/sealed/exact76.py`; crib-assisted, after the freeze, labelled as in R70 Erratum 1)
| Check | Scope |
|---|---|
| H1X | One stage, any key letters, period 2–52, alphabets from the large tier (77,229 orderings: every 4–15-letter word of the R59 word model, three constructions each, plus A–Z), additive or Beaufort sign. Periods with ≥ 8 same-slot pairs use the large tier; 5–7 pairs the small tier (241); fewer are skipped |
| H2X | Key scrambled by a route, any key letters, period 2–24, 64,782 routes (adds every complete columnar of width 2–7 with any column order, and the R61 routes), 32 one-stage conventions; ≥ 5 checks. The identity route is a control |
| H2bX | Text routed (R72 sheet routes + R61 routes, 47), repeating key of period 1–24, both orders, 32 conventions; ≥ 3 checks |
| H6 | For H1X and H2X: the second published string's key index shifted by −2, −1, +1, +2 (a dropped or extra letter). Feasibility only |

- **Decodes:**
  - Pinned key letters are forced.
  - H2X/H2bX: up to 3 unpinned letters completed by exhaustive quadgram search.
  - H1X: unpinned letters completed by coordinate ascent. A decode must also beat 50 forced decodes with random
    alphabets at the same period on the same ciphertext.
- **Verdict per check:** **CONSISTENT** iff some unshifted full decode clears both cuts (and, for H1X, the forced
  nulls); else **NO_SOLUTION**. Feasible counts are reported for K4 beside 10 shuffles.
- **Synthetic validation** (`exact76.py --selftest`, `r76/results/EXACT76_SELFTEST.json`; random keys and alphabets):

  | Check | Plants found | Decoded exactly | Notes |
  |---|---|---|---|
  | H1X | 8/8 | 4 | Periods 8–22: all readable, 79–97 letters right. Periods 38–44: readable, 32–63 letters right, as the completion is partial |
  | H2X | 4/4 feasible | 3 | The fourth had too many unpinned key letters to decode |
  | H2bX | 4/4 | 4 | — |
  | Random ciphertexts | 0 feasible in every check (4 of 4) | — | Both controls clean: 0 H1X settings at L21-excluded periods; 0 identity-route settings |

## What follows (fixed now)
| Result | Next |
|---|---|
| SIGNAL, or any exact check CONSISTENT | Stop. Do not tune. Report raw; independent re-derivation; then Tyler decides about any outside check |
| K4 has feasible settings in H1X/H2X/H2bX, more than every shuffle | Report them raw as a lead for the next design round (Fable) |
| A control fails (L21 periods, or the identity route) | Stop; it is a bug |
| Everything negative | H1 and H2 are closed in the stated scope. The next step is a design round for new ideas (Fable), per Tyler's plan |

**Prior expectation** (stated before the run): NO_SIGNAL; all exact checks NO_SOLUTION; 0 or very few feasible
settings.
