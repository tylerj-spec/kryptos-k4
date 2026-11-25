# R101 result (Claude Code, 25 Nov 2026): plaintext autokey on ANY single alphabet is EXCLUDED at lags 1–5

## In plain words
**A plaintext autokey on any single alphabet is ruled out for K4 at lags 1–5.**
- **The cipher:** R99 tested K1/K2's tableau with a self-keying key for 77,229 keyword alphabets. This round lets
  the alphabet be **anything**: all 26! ≈ 4 × 10²⁶ orderings.
- **The family:** each letter is keyed by the plaintext letter L places earlier, all ranks are read in that one
  alphabet, and there are four sign variants, any constant and any starting key.
- **ACA Condi** is the case L = 1 with any keyed alphabet.

**Result.** No alphabet and no setting fits K4's 24 published letters at any lag from 1 to 5.

**Why one alphabet is enough to decide this.** In rank space the self-keying recursion is linear. Every chain
between two published letters therefore becomes a linear congruence in the 26 unknown ranks. The question is whether
any genuine alphabet (a bijection) satisfies them all, and two separately written exact solvers answer it.

**Shuffles:** all 20 shuffled copies of K4 are also infeasible wherever decided.

## Gate (`holdout/CHECKER_GATE.json`, seed 1010901): **GO**
| Check | Result |
|---|---|
| V1 reference round trip, random alphabets | 400/400 |
| V2 plants (uniformly random alphabets, lags 1–5) | **0 missed**; 49/60 decided (amended bar 40; the registered bar of 50 would have failed on undecided cells; see `AMENDMENT_1.md`) |
| V3 two exact solvers | 28/32 cells decided by both, **0 disagreements** |
| V4 ACA Condi (separately coded), random alphabets | 16/16 found |
| V5 chance and throughput | 0/120 random cells feasible; forecast 401 s CPU (limit 960) |

**Run:** COMPLETE, 90 s wall, 89 s CPU, peak 388 MB (cap 900 / 600 / 1,024). Gate freeze 22d0a51 was pushed before
any K4 input was read.

## Target (`k4/AGGREGATES.json`, frozen in 77986c7): **EXCLUDED**
| Lag | Links | Mod-13 solution dimension (4 signs) | K4 status (4 signs) |
|---|---|---|---|
| 1 | 23 | 4, 5, 5, 4 | INFEASIBLE ×4 |
| 2 | 22 | 5, 4, 4, 5 | INFEASIBLE ×4 |
| 3 | 21 | 5, 5, 5, 6 | INFEASIBLE ×4 |
| 4 | 20 | 6, 6, 6, 6 | INFEASIBLE ×4 |
| 5 | 19 | 7, 7, 7, 7 | INFEASIBLE ×4 |

- **Shuffles:** 0 of 20 have a feasible cell; 4 of their 400 cells were UNDECIDED (dimension > 7).
- **Decision** (`k4/EVALUATION.json`): **EXCLUDED**. All 20 K4 cells are infeasible, and none is undecided.
- **Run:** COMPLETE, 114 s wall, 113 s CPU, peak 401 MB (cap 1,800 / 1,200 / 1,024), zero retries. The freeze was
  pushed, and the remote blobs were checked before evaluation.

## Post-freeze cross-check (`k4/CROSSCHECK.json`)
`crosscheck101.py` re-decides K4's 20 cells from the frozen inputs with the second solver. That solver is a
depth-first search over ranks mod 26 with forward checking; it uses no field decomposition and no enumeration.
- It **decides all 20 and agrees on all 20**: INFEASIBLE.
- 9 s CPU.

## What this excludes, and what it does not
**Excluded exactly** (crib-assisted: the published letters in place and in the carved order):
- **Cipher:** y_i = s1·x_i + s2·x_{i−L} + c, with plaintext, ciphertext and feedback ranks in one alphabet.
- **Alphabets:** **any** of the 26! orderings.
- **Other parameters:** any c, any primer, all four sign pairs, lags 1–5.

This includes:
- ACA Condi with any keyed alphabet;
- R99's keyword cases (L188) at these lags;
- the one-alphabet plaintext-feedback case of L26 ("unknown-alphabet feedback autokey"), at these lags.

**Not excluded:**
- lags 6–96, where chance fits begin and the solution space grows;
- one wrong letter (no DROP screen);
- separate plaintext, cipher and feedback alphabets, which is the two-free-alphabet half of S3;
- a keyword combined with the autokey;
- ciphertext autokey;
- a transposition layer;
- insertion or deletion.

Nothing from R101 enters any blind search.

## Review
**Independent review: NONE.** One model (Claude Code) registered, built and ran R101. ChatGPT is the named reviewer.
The natural independent checks are:
- re-deriving the rank-space congruences (`PREREGISTRATION.md` §2);
- deciding K4's 20 cells with any third exact method (for example an SMT solver given enough time).
