# T2: setting-by-setting replay of R75's F1X (L165), 15 Nov 2026

**Label: POST-FREEZE, CRIB-ASSISTED, EXCLUSION-ONLY REPLAY.** Nothing was decoded and no key was completed. No
original file was changed. Work order: `audit/NEXT_STEPS.md`, task T2.

## In plain words
R75's F1X check (two stacked periodic key stages, any key letters) had a known arithmetic bug: its solution counter
could overflow. The question was whether the bug touched the yes/no answers.
- **It did not.** All 692,224 settings were re-checked one by one with a separate checker that uses unlimited-size
  integers, on K4 and 40 shuffles. Feasible or infeasible agrees on every setting, every time.
- **Only the solution counts were wrong**, and only where the true count is astronomically large (above 2^63, about
  9 × 10^18). On K4 that is 30 settings.
- **R83a's account of its two stalled jobs is confirmed exactly.** On shuffles NULL_010 and NULL_011, 4 settings each
  (periods 17 and 17, one published letter set aside) have counts above 2^63. Each of them would have sent R75's code
  into its never-ending decode loop. K4 has none.

## What was compared (`replay_f1x.py`, `t2_overflow_17.py`; checker `f1x_safe.check_setting`, Python int)
| Comparison | Ciphertexts | Result |
|---|---|---|
| Setting-by-setting feasibility against the original `f1x()` re-run with its decode branch off (R75's `grid_of` replaced by None in-process, as `r83/f1xd_lowmem.py`), every setting with ≥ 3 checks | R75 target: K4 + 20 shuffles; R83 target: 20 shuffles (41) | **0 disagreements** |
| Tested and feasible tallies by checks, all checks levels (all 692,224 settings) | 41 | Equal to the original re-run on all 41 |
| `r75/k4/EXACT.json`: K4 tallies by checks; the 300 listed K4 settings with their solution counts; each shuffle's feasible total at ≥ 3 checks | R75 target | All equal (K4 1,868; listed counts all agree) |
| `r83/k4/run/R83A.json` F1XD: tested and feasible tallies; the 300 listed settings | K4 + R83's 20 shuffles | All equal; every listed setting feasible in the replay |
| Solution counts against the original's int64 counts | 41 | 5,670 disagreements, **every one a true count ≥ 2^63**: periods 25+25 (4,460), 24+24 (1,206), 16+24 and 24+16 (2 each). On K4: 30 |
| Periods 15–18 on both stages, all letters | 41 | 16,384 settings each; no feasible count reaches 2^63 (largest has 18 digits) |
| Periods 15–18 with one published letter set aside (R83a F1XD semantics): count ≥ 2^63 and decode branch reached (≤ 2 unpinned key letters, wrapped count ≤ 64) | NULL_010, NULL_011, K4 (R83 target) | NULL_010: 4, all at 17+17 (PAL/PAL/KRY/ABS, signs ∓±). NULL_011: 4, all at 17+17 (PAL/ABS/KRY/KRY, ±±). **K4: 0.** Matches `r83/f1xd_lowmem.py`'s account |

The settings at 24–25 that overflow have more than 2 unpinned key letters. So R75's original run never took its decode
branch for them, which is why R75's own K4 job finished.

## Pass condition: PASS
Feasibility agrees on every setting. Count disagreements occur only where the true count is above 2^63. All are listed
in `REPLAY_F1X.json` (`count_disagreements`, with true and int64 values).

## Consequence for L165
- F1X feasibility, its tallies, and the "1,868 feasible vs shuffle median 2,354" comparison are confirmed by an
  independent checker.
- The overflow affects only reported solution counts above 2^63. None of the 300 listed settings has one.
- The archived K4 "no readable decode" depended on decodes R75 built in memory; those were not replayed here (by rule).

## Resources (all `audit/run_bounded.py`, budget `T2_BUDGET.json`, COMPLETE)
| Job | Wall time | Memory |
|---|---|---|
| R75 target | 915 s | 32 MB |
| R83 target | 766 s | 32 MB |
| Drop block | 32 s | 19 MB |
| Overflow block | 334 s | 16 MB |

The comparison step re-ran the original `f1x()` without decodes.

**Not done:** a full drop-one replay of F1XD (24 × the cost); only the 15–18 block was replayed.

**Independent review: NONE.** One model did this work.
