# R119 result (Claude Code, 28 Nov 2026): a K3-style route, then free-alphabet Slidefair. 8 of 26 routes are excluded in every cell; periods 1, 2 and 4 are excluded for all 26; no lead

**Mode:** crib-assisted, aggregate-only, exclusion-only, **exploratory** (L161). F2 rank 1; Tyler: "I approve all of
them". It decodes nothing. **Independent review: NONE**; this is audit batch C.

## In plain words
**The question.** Sanborn's documented K3 method rearranges letters by turning a written sheet. L161 lists 26 such
rearrangements of a 98-cell sheet that nobody has tested. Could K4 have been made by encrypting with Slidefair (two
unknown alphabets) and then rearranging by one of those 26 routes?

**The test.** For each route, the rearrangement was undone. R117's exact check was then applied to the result, with
the same-column rule handled exactly.

**The answer:**
- **8 of the 26 routes are excluded outright**, for every convention, every key period 1–47 and any key:
  - k4 extra cell first, inverse;
  - k28 extra cell first, forward;
  - k28 extra cell last, forward;
  - all four k46 routes;
  - k49 extra cell last, inverse.
- **For all 26 routes,** keys with period 1, 2 or 4 are excluded. Period 3 is excluded for all but one route (k4
  extra cell first, forward, with 4 open cells).
- **The other 18 routes** leave some longer-period cells open, between 116 and 436 of 768 per route. That is the
  same range shuffled letters give: a median of 224, and a maximum of 588 in R117's 200 shuffles.

**No lead.** No route fits better than chance would allow.

## Results (`k4/AGGREGATES.json`, frozen in b72038d; `k4/EVALUATION.json`; `k4/CROSSCHECK.json`)
| | EXCL_DROP | EXCL (exact only) | OPEN |
|---|---|---|---|
| All 26 routes × 768 cells | 9,504 | 6,680 | 3,784 |

**Routes EXCLUDED_EXACT,** with their DROP-level counts:

| Route | DROP-level cells |
|---|---|
| k4 extra cell first, inverse | 304 |
| k28 first, forward | 364 |
| k28 last, forward | 392 |
| k46 first, forward | 360 |
| k46 first, inverse | 344 |
| k46 last, forward | 636 |
| k46 last, inverse | 520 |
| k49 last, inverse | 492 |

**OPEN cells per PARTIAL route:**

| Route | OPEN |
|---|---|
| k4 first, forward | 436 |
| k4 last, forward | 276 |
| k4 last, inverse | 116 |
| k14 first, forward | 256 |
| k14 first, inverse | 148 |
| k14 last, forward | 136 |
| k14 last, inverse | 120 |
| k25 first, forward | 132 |
| k25 first, inverse | 128 |
| k25 last, forward | 132 |
| k25 last, inverse | 272 |
| k28 first, inverse | 380 |
| k28 last, inverse | 136 |
| k49 first, forward | 140 |
| k49 first, inverse | 144 |
| k49 last, forward | 284 |
| k92 first, forward | 432 |
| k92 first, inverse | 116 |

All of these are below the null maximum (588), so the LEAD flag is not set.

**OPEN cells by period, pooled over routes:**
- none at p 1, 2 and 4;
- 4 at p 3;
- 28–76 at p 5–12;
- 112 (the maximum seen) at p 13–15 and p ≥ 26, and for any key.

**Checks:**
- **Gate (the pilot) GO** (frozen 421dfd5):
  - all 26 routes rebuilt and matched to `NOVELTY.json`;
  - 0/260 routed plants excluded at the true cell, and 0 one-error plants at DROP;
  - 0 disagreements with the brute-force reference on 52 routed cells.
- **Post-freeze cross-check:** the brute-force reference agrees on a random 312-cell sample (0 disagreements).
- **Resources:** COMPLETE under `audit/run_bounded_agg.py`, zero retries:
  - gate: 64 s;
  - target: 319 s.

**Commits:**
- pre-registration 9ba6dd7;
- source d96e94e;
- gate 421dfd5;
- K4 freeze b72038d.

## What this means
**Excluded (EXACT, exploratory scope)**, conditional on the 22 crib-pair letters:
- **for 8 routes:** "route, then Slidefair" with free alphabets, any key structure, and any number of same-column
  crib pairs;
- **for every one of the 26 routes:** the same with key periods 1, 2 and 4;
- **for 25 of the 26 routes:** the same with period 3.

**Still OPEN:** the longer-period and any-key cells of the 18 PARTIAL routes. They are not evidence.

**Not covered:**
- other routes;
- Slidefair, then a route (F2 rank 2);
- autokeys after a route (F2 rank 3);
- other same-column rules;
- two or more errors;
- masks under reading B.

## Cross-check
The brute-force reference `r112/ref112.py` recomputed **312 K4 route cells** after the freeze: 12 per route, drawn
with seed 1190902. For each it gave the exact verdict, plus the drop verdict where the cell was excluded.
- **Disagreements with the frozen X112 verdicts: 0.**
- **Resources:** COMPLETE: 780 s wall, 1,297 s CPU over 3 workers, against 3,600 s.
