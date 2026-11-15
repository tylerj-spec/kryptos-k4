# R83a result: exact checks for four keyword families with no fixed period, F1X drop-one, and shifted clue positions (Claude Code, 14 Nov 2026)

**Outcome: no LEAD.** Of 61 pre-registered verdict rows, 51 are **EXCL** and 10 are **CHANCE**.
- **EXCL:** no setting with ≥ 3 checks fits.
- **CHANCE:** K4 has feasible settings, but only at strengths the shuffles also reach.

Nothing on K4 stands out from the shuffles, so no R83b blind round follows.

**Label: CRIB-ASSISTED, EXCLUSION-ONLY.**
- The published letters entered only the algebraic checks. Nothing was ranked and nothing was sent to any outside checker.
- No file holds a decode or a completed key. The one exception, inside R75's own code, is described under *Run deviation*.

Pre-registered in `r83/PREREGISTRATION.md` (82c3ee8, `r83/PROTOCOL.sha256`); approval: Tyler, "I'd do R83a". Design and synthetic validation: `r83/DESIGN.md`, PR #79.

## Steps
| Step | Commit | Result |
|---|---|---|
| Design, models, exact checks, tests, self-tests, CI | PR #79 (merged) | All pass. Plants 20/20, drop-one 15/15, brute-force equality 92/92 |
| Pre-registration (rules, target K4 + 100 shuffles, seed 830400) | 82c3ee8 | — |
| Run, 381 jobs (`r83/run83a.py`, 4 cores, 20:27–22:06 UTC) | — | 379 jobs done. 2 F1X drop-one jobs (shuffles NULL_010, NULL_011) did not finish: see *Run deviation* |
| Rerun of those 2 jobs (`r83/f1xd_lowmem.py`) | 8b6c58e, a9ea70a | It first reproduced 5 finished parts, K4's included, byte for byte (`r83/k4/run/F1XD_RERUN.log`) |
| Freeze: `r83/k4/run/R83A.json` (sha256 211ab148…), `r83/k4/run/FROZEN.sha256` | 8122101 | Pushed before any verdict was computed |
| Verdicts (`r83/verdict83.py` → `r83/k4/VERDICT.json`) | this commit | 51 EXCL, 10 CHANCE, 0 LEAD |

The LEAD confirmation run on shuffles 6–20 was not needed, because no LEAD arose in any step.

## Exact and drop-one results (K4 and 20 shuffles; LX's drop-one on 5)
Each cell shows three numbers:
1. K4's feasible settings with ≥ 3 checks;
2. the number of shuffles with any such setting;
3. the most any one shuffle has.

For DROP, the count covers settings infeasible as they stand but feasible once one published letter is set aside. Checks are counted with all 24 letters.

| Family | Settings with ≥ 3 checks | EXACT: K4 · shuffles with any · most on a shuffle | Verdict | DROP: K4 · shuffles with any · most | Verdict |
|---|---|---|---|---|---|
| LX | 96,112,640 | 1 · 9/20 · 16 | **CHANCE** | 250 · 5/5 · 250 | **CHANCE** |
| PFX | 39,424 | 0 · 3/20 · 1 | **EXCL** | 17 · 20/20 · 39 | **CHANCE** |
| WPX | 12,800 | 0 · 0/20 · 0 | **EXCL** | 0 · 0/20 · 0 | **EXCL** |
| SLX | 320 | 0 · 0/20 · 0 | **EXCL** | 0 · 0/20 · 0 | **EXCL** |
| SLX-A | 800 | 0 · 0/20 · 0 | **EXCL** | 0 · 0/20 · 0 | **EXCL** |
| SSX | 3,200 | 0 · 0/20 · 0 | **EXCL** | 0 · 0/20 · 0 | **EXCL** |
| F1X (R75) | 386,048 | 1,868 (R75, L165) | — | 4,491 · 20/20 · 5,331 | **CHANCE** |

## Shifted clue positions (one published run moved; letters unchanged)
run1 is the published run at positions 21–33, run2 the one at 63–73 (0-based).

Each cell gives the verdict, K4's feasible settings with ≥ 3 checks, and (in brackets) the shuffles with any. LX ran on 5 shuffles, the others on 20.

| Family | run1 −2 | run1 −1 | run1 +1 | run1 +2 | run2 −2 | run2 −1 | run2 +1 | run2 +2 |
|---|---|---|---|---|---|---|---|---|
| LX | CHANCE 2 (4/5) | EXCL 0 (4/5) | CHANCE 2 (3/5) | EXCL 0 (1/5) | CHANCE 1 (2/5) | CHANCE 1 (1/5) | CHANCE 1 (2/5) | EXCL 0 (3/5) |
| PFX | EXCL 0 (4/20) | EXCL 0 (4/20) | EXCL 0 (2/20) | EXCL 0 (4/20) | EXCL 0 (5/20) | EXCL 0 (7/20) | CHANCE 1 (8/20) | EXCL 0 (6/20) |
| WPX | EXCL 0 (0/20) | EXCL 0 (0/20) | EXCL 0 (0/20) | EXCL 0 (1/20) | EXCL 0 (0/20) | EXCL 0 (0/20) | EXCL 0 (0/20) | EXCL 0 (0/20) |
| SLX | EXCL 0 (0/20) | EXCL 0 (0/20) | EXCL 0 (0/20) | EXCL 0 (0/20) | EXCL 0 (0/20) | EXCL 0 (0/20) | EXCL 0 (0/20) | EXCL 0 (0/20) |
| SLX-A | EXCL 0 (0/20) | EXCL 0 (0/20) | EXCL 0 (0/20) | EXCL 0 (0/20) | EXCL 0 (0/20) | EXCL 0 (0/20) | EXCL 0 (0/20) | EXCL 0 (0/20) |
| SSX | EXCL 0 (0/20) | EXCL 0 (0/20) | EXCL 0 (0/20) | EXCL 0 (0/20) | EXCL 0 (0/20) | EXCL 0 (0/20) | EXCL 0 (0/20) | EXCL 0 (0/20) |

## Why every CHANCE row is chance
The LEAD rule compares each K4 setting's effective strength (eff) with the strongest setting on every shuffle of the same step. The shuffles reach K4's best level in every row:

| Row | K4's feasible settings by eff | K4's best | Shuffles with any at that level |
|---|---|---|---|
| EXACT LX | eff 4: 1 | 4 | 9/20 (one reaches 5) |
| DROP LX | eff 4: 223, 5: 26, 6: 1 | 6 | 5/5 (one reaches 7) |
| DROP PFX | eff 3: 15, 4: 2 (6,266 more with < 3 checks, not counted) | 4 | 5/20 |
| F1XD | eff 3: 135, 4: 1 (and 4,355 with ≥ 3 checks but eff < 3) | 4 | 20/20 (five reach 5) |
| SHIFT LX run1 −2, run1 +1, run2 −2, run2 −1, run2 +1 | eff 4: 2, 2, 1, 1, 1 | 4 | 4/5, 3/5, 2/5, 1/5, 2/5 |
| SHIFT PFX run2 +1 | eff 3: 1 | 3 | 8/20 |

## The open settings
These stay open and are not excluded. They are no evidence for anything: random ciphertexts produce as many.
- **EXACT LX, 1 setting:**
  - conventions KRY / ABS / PAL / ABS, signs +1, −1, −1, key alphabets AZ / KRY;
  - m = 20, rows of w = 4, d = −1, rotated stage 2;
  - 5 checks, eff 4.
- **DROP LX, 250 settings.** The strongest is:
  - PAL / ABS / KRY / PAL, +1 +1 +1, AZ / PAL;
  - m = 18, w = 16, d = −1, rotated stage 1;
  - 7 checks, eff 6, freed by setting aside position 66.
- **DROP PFX, 17 settings.** The two at eff 4 are:
  - PAL→KRY reverse, β ABS, f +1, L 3, m 23, freed by 25 or 71;
  - PAL→KRY additive, β AZ, f −1, L 4, m 15, freed by 27 or 72.
- **SHIFT:**
  - LX, 7 settings in 5 position sets, all m = 20 at eff 4;
  - PFX, 1 setting (run2 +1): PAL→PAL reverse, β ABS, f +1, L 10, m 1, eff 3.
- **F1XD, 4,491 settings.** The strongest is AZ / AZ / ABS / PAL, −1 +1, periods 3 and 23, eff 4, freed by 24 or 70.

Where to find them:
- Every K4 setting, with its full convention, is in `r83/k4/run/R83A.json`. Each list is capped at 300 per family and step, which leaves every list complete except F1XD's.
- The F1XD list holds the 300 strongest: all 136 at eff ≥ 3, and 164 of the 452 at eff 2.
- `r83/k4/VERDICT.json` repeats the first 50 of each list.

## What is excluded, by cell
Assumptions: the cipher works in place, K4 was carved and transcribed correctly, and the 24 published letters are right. Each family's excluded cells below are excluded for every key:

| Family | Excluded exactly and with any one published letter set aside | Also with each run moved ±1, ±2 | Not decided (< 3 checks) |
|---|---|---|---|
| **WPX** walking key stepped by the plaintext | All 12,800 settings: ring m = 2–26, every step alphabet, e, d and convention. On K4 every setting has ≥ 4 checks; DESIGN's 24 − m was a worst case | Yes, all 8 | None |
| **SLX** per-slot progression A + j·B | m = 1–10 (320 settings) | Yes, all 8 | m = 11–26 |
| **SLX-A** progression (j + 1)·A | m = 1–25 (800) | Yes, all 8 | m = 26 |
| **SSX** keyword re-enciphering itself | m = 1–25 (3,200) | Yes, all 8 | m = 26 |
| **PFX** keyword + plaintext autokey | Exactly: the 39,424 settings with ≥ 3 checks: lag 1–2 with m 1–24; lag 3–4 with m 1–15 or 18–23; lag 5–8 with smaller ranges; lag 9 with m 1–3; lag 10 with m 1. Drop-one: CHANCE, 17 open | 7 of 8 position sets EXCL; run2 +1 CHANCE (1 open) | Lag 11–12; for each lag, the other m |
| **LX** linked key, one stage rotated per row | 96,112,639 of the 96,112,640 settings (every setting has ≥ 5 checks). Drop-one: CHANCE, 250 open | 3 sets EXCL (run1 −1, run1 +2, run2 +2); 5 sets CHANCE, 1–2 open each | None |
| **F1X** (R75) | Drop-one: CHANCE, 4,491 open (shuffles 2,914–5,331) | Not run | As R75 |

Under the pre-registered *What follows*, no blind solver is built for the decided cells. The undecided cells can have blind solvers per `r83/DESIGN.md` §4 if Tyler wants them:
- PFX outside the decided cells above (lag 9 beyond m = 3, lag 10 beyond m = 1, lags 11–12, and the gaps at lags 3–8);
- SLX with m ≥ 11;
- SLX-A and SSX with m = 26.

## Run deviation (two F1X drop-one jobs), and what R75's f1x() does inside
**What happened.** The pre-registered run finished 379 of 381 jobs. The F1X drop-one jobs for shuffles NULL_010 and NULL_011 grew until the container's 14.3 GB memory limit killed them, and the worker pool then waited forever.

**Cause.** The cause is in R75's `f1x()` (`r75/sealed/exact.py`, unchanged since R75).
- After its feasibility test, `f1x()` multiplies each component's number of solutions into a 64-bit integer.
- In the equal-period cells (both periods 15–18), almost every key-slot pair is its own component with 26 solutions. The product (26¹⁴ and more) overflows.
- A count that wraps to ≤ 64 (here, negative) sends `f1x()` into its decode branch. That branch enumerates every combination of solutions, which never ends.
- On NULL_010 and NULL_011, 4 feasible settings each hit this, all at periods 17 and 17 with one letter set aside.
- K4 and NULL_000 have none (checked). Nor can the other 18 shuffles, since their jobs finished. A count wraps only when the true count is at least 2⁶³. If it wraps to ≤ 64, `f1x()` starts enumerating all those combinations, which never ends.

**Why the finished results stand.** Feasibility is computed before the decode branch and never uses the count. So the 379 finished parts are exact. R75's own verdicts do not use the count either. A "solutions" figure R75 reports in those cells may be wrong. R75's runs finished, so no wrapped value ≤ 64 occurred there.

**The fix.** `r83/f1xd_lowmem.py` runs the same `run83a.run_job` and `f1x_drop`, both unchanged. In its own process it replaces R75's `grid_of()` with one that returns None, so `f1x()` enters each feasible setting once and never decodes.
- The feasible set cannot change.
- Before the rerun, it reproduced the finished parts of K4, NULL_000, NULL_009, NULL_012 and NULL_019 byte for byte.
- It then ran the two missing jobs in about 70 s each, using 57 MB.
- No file in `r83/PROTOCOL.sha256` changed.

`FROZEN.sha256` lists the script as "deviation". `run83a.py` combined all 381 parts but then failed to write `FROZEN.sha256`, because it was given the target as a relative path. The manifest was written in its format, with resolved paths.

**Disclosure.** In the original run, R75's `f1x()` also computed some decodes in memory (K4's job included). It did this for every feasible setting whose key the published letters fully pin down with ≤ 64 solutions; R75 used this to score decodes.
- `r83/f1x_drop.py` keeps only each setting's identity and throws the decode away.
- No part file holds a decode or a key (checked).
- No scorer read them: the collector has none.
- Nobody saw them.

The pre-registration's "nothing is decrypted, no key is completed" was true of everything reported, but not of `f1x()`'s internal work. `r83/DESIGN.md` had disclosed that F1X decodes where it can complete a key, but R83a should have switched that off from the start. Any later use of `f1x()` for feasibility only should replace `grid_of()` the same way.

## Not covered
As pre-registered:
- several stages with transposition;
- a context-dependent pre-mask;
- ciphertext errors away from the 24 positions;
- other carving orders;
- keywords longer than each family's range;
- lags above 12;
- rotation steps other than ±1 per row.

Also not covered: the undecided cells listed above, and F1X with shifted runs.
