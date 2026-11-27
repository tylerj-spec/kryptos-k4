# R112 result (Claude Code, 27 Nov 2026): Slidefair's same-column rule can be handled exactly, with little loss of power

**Type:** analysis + synthetic verification. No K4 input. **Independent review: NONE**; this is audit batch C.

## In plain words
**Why this was needed.** R108's K4 exclusions for Slidefair with free alphabets rest on one assumption: none of the
crib pairs hit Slidefair's "same column" rule. If one or two did, the exclusions would not apply. R112 builds a check
that treats that rule properly, for **any number** of crib pairs.
- Each pair is either normal or same-column, and each branch has its own exact equations.
- Optionally, one pair may also be wrong.

**It works:**
- **Never wrong on true messages.** It never excluded a true message, including messages with up to 9 same-column
  crib pairs (400 plants). It never excluded one with a wrong letter once one bad pair was allowed.
- **Two implementations agree.** A brute-force version that tries every combination agrees on all 1,960 cells.
- **The power stays high.** On random hypotheses it still excludes:
  - 100% at key periods 1–2;
  - 93–98% at periods 3–7;
  - 58% with no key structure at all.

  Allowing one wrong pair on top, it still excludes more than half at periods 1–8.

**Consequence.** A K4 run of this check could replace R108's assumption with exact handling. It would then rest only
on the published letters being right, or one of them wrong. That run is **not done here**: it is proposed as P6,
after the substantive review.

**One disclosure.** The prototype had a sign error in the Beaufort same-column equation. The registered T1 structure
check caught it in a dev smoke run, before the source was committed. The registered run used the corrected equation.
The pre-registration's development power figures came from the faulty prototype and are superseded by this run.

## Results (`run_v1/RESULTS.json`, frozen in 3708a6c)
| Step | Result |
|---|---|
| **T1 structure** | 300 messages, 14,400 pairs, 3,341 same-column: **0 equation failures**, 0 round-trip failures |
| **T2 soundness** | 400 plants. Same-column crib pairs per plant: 0 (123 plants), 1 (67), 2 (28), 3 (28), 4 (47), 5 (45), 6 (31), 7 (20), 8 (10), 9 (1). **0 true plants excluded; 0 one-error plants EXCL_DROP** |
| **T3 two implementations** | 1,920 small-mask cells and 40 full-mask cells: **0 disagreements** |

**T4 chance power** (40 random messages × 16 conventions = 640 cells per period):

| p | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 16 | 24 | 36 | any |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EXCL (any same-column) | 1.00 | 1.00 | 1.00 | 0.98 | 0.93 | 0.92 | 0.93 | 0.88 | 0.86 | 0.81 | 0.78 | 0.82 | 0.70 | 0.65 | 0.64 | 0.58 |
| EXCL_DROP (also one bad pair) | 1.00 | 1.00 | 0.98 | 0.84 | 0.69 | 0.70 | 0.56 | 0.53 | 0.48 | 0.41 | 0.41 | 0.41 | 0.31 | 0.22 | 0.23 | 0.19 |
| Label | R | R | R | R | R | R | R | R | T | T | T | T | T | T | T | T |

R = ROBUST; T = TESTABLE. The cost of general same-column handling is small. Compare R107, which assumed no
same-column pair: its EXACT-or-DROP share with any key was 0.59, against 0.58 here.

**Run:** COMPLETE through `audit/run_bounded_agg.py`, 405 s, zero retries.

**Commits:**
- pre-registration bb84541;
- source 111c0d1, which discloses the corrected sign;
- outputs frozen in 3708a6c.

## Scope
- **Covered:** R98's same-column rule ("letters to the right"), with free alphabets and periodic or arbitrary keys.
- **Not covered:**
  - other same-column rules at two or more pairs;
  - other digraphic rules;
  - layered constructions.
- **No K4 claim.** Nothing from R112 enters a blind search.
