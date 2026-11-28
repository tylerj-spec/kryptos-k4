# R117 result (Claude Code, 28 Nov 2026): Slidefair with free alphabets is excluded for K4 in every cell, now with the same-column rule handled exactly; 356 of 768 cells also with one bad pair

**Mode:** crib-assisted, aggregate-only, exclusion-only (P6; Tyler: "I approve all of them"). It decodes nothing.
**Independent review: NONE**; this is audit batch C.

## In plain words
**What R108 left open.** R108 excluded ACA Slidefair with two unknown alphabets for K4, but under one assumption: that
no crib pair falls under Slidefair's special "same column" rule. Real messages hit that rule about once in 26 pairs.

**What R117 did.** It repeated the check with that rule handled exactly. Any number of crib pairs may be same-column,
and each such pair gets its own equations.

**The answer: every one of the 768 cells is still excluded.** That is 16 conventions × every key period from 1 to 47,
plus "any key".
- **356 cells** stay excluded even if one crib pair is wrong.
- **412 cells** need all 22 crib-pair letters to be right.
- **No cell is open.**

**Against R108.** 16 cells that R108 excluded even with one bad pair are now excluded only exactly. The same-column
branches gave them one more way out. None became open.

**No lead.** K4 leaves no cell open. Its 200 shuffles leave a median of 224 open, with a range of 0–588.

## Results (`k4/AGGREGATES.json`, frozen in bb0e108; `k4/EVALUATION.json`; `k4/CROSSCHECK.json`)
| | EXCL_DROP | EXCL (exact only) | OPEN |
|---|---|---|---|
| K4, 768 cells | **356** | **412** | **0** |
| R108 (no same-column pairs) | 372 | 396 | 0 |
| Cells moving from R108 to R117 | 356 stay DROP; **16 go from DROP to exact-only**; 396 stay exact | | |

**K4's DROP cells by key period:**
- 16 of 16 at p 1–5 and p 19;
- 8–12 at p 6–12, 17, 18, 20–22, 24 and 25;
- 4 at p 13–16, 23, 26–47 and any key.

**The 16 cells that moved:** conventions VIG/BEAU_0_0_1 and VIG/BEAU_1_1_1, at p 7, 9, 18 and 21.

**Shuffles** (mean share per cell):
- OPEN: 0.00 at p 1–2, 0.05 at p 5, 0.17 at p 8, 0.40 at p ≥ 30 and any key;
- EXCL_DROP: 1.00 at p 1, 0.69 at p 5, 0.21 at p ≥ 30.

**Checks:**
- **Gate GO** (frozen 2c7e4bf):
  - structure: 0 failures on 7,200 pairs, 1,606 of them same-column;
  - soundness: 0/200, and 0 one-error plants at DROP, with up to 8 same-column crib pairs;
  - X112 against the brute-force reference: 0 disagreements on 1,310 cells.
- **Post-freeze cross-check:** the brute-force reference agrees on **all 768 K4 cells** (0 disagreements).
- **Resources:** COMPLETE under `audit/run_bounded_agg.py`, zero retries:
  - gate: 43 s;
  - target: 933 s wall, 2,747 s CPU over 3 workers.

**Commits:**
- pre-registration 97bc78f;
- source ae50c98;
- gate 2c7e4bf;
- K4 freeze bb0e108.

## What this means
**Excluded (EXACT, within the stated model).** K4 cannot be ACA Slidefair, conditional on the 22 crib-pair letters
being right, where Slidefair means:
- R98's 16 conventions;
- the "letters to the right" same-column rule, applied at any number of crib pairs;
- free plaintext and cipher alphabets;
- a periodic key of any period 1–47, or any key.

R108's assumption of no same-column pair is no longer needed. For 356 cells, the exclusion survives one wrong letter
or pair.

**Masking scope:** valid under reading A only (F1 §2). Slidefair sends plaintext and ciphertext letters through the
same alphabets.

**Not covered:**
- other same-column rules;
- two or more wrong letters;
- other digraphic ciphers;
- transposition layers, which are F2's route rounds;
- masks under reading B.

## Cross-check
The brute-force reference `r112/ref112.py` checked **all 768 K4 cells** after the freeze. It tried every normal or
same-column assignment of every crib pair, with no pruning, and recomputed the drop verdict wherever a cell was
excluded.
- **Disagreements with the frozen X112 verdicts: 0.**
- **Resources:** COMPLETE under its registered budget: 1,747 s wall, 3,065 s CPU over 3 workers, against 7,200 s;
  67 MB.
