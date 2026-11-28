# R114 result (Claude Code, 28 Nov 2026): S105 holds up on held-out text. 4 of 5 bars pass; bar 3 sits exactly on its boundary (flagged)

**Type:** synthetic validation of R105's solver S105 (P7), with the solver unchanged. No K4 input. **Independent
review: NONE**; this is audit batch C.

## In plain words
**The question.** R105's solver was developed and first tested on one text source. R114 asked whether it still works
in four harder conditions:
- on text it was not tested on;
- spread evenly over every cipher setting R111 used;
- with a language model built without that text;
- inside the full 20-setting search, against decoys.

Every output also had to pass a full 97-letter re-encryption check.

**Results:**
- **Fresh Carter text, 10 messages in each of the 20 settings:**
  - 83.5% recovered to at least 90 of 97 letters (95% interval 78–88%);
  - 66.5% to at least 95 letters;
  - **45% exactly**.

  Every setting recovered at least 5 of its 10.
- **K1–K3 plaintext, a different style never used in development:** 82.5% at ≥ 90 letters, and 30% exact.
- **The full search:** the true setting came out on top in **12 of 12** messages, and all 12 were recovered. Every
  recovery scored −404 or better. The best decoy scored −455.5. That decoy was a two-free-alphabet autokey, which
  matters for R106.
- **Witnesses:** all of them passed.
- **A language model built only from the first half of Carter:** recovery fell from 85 to 70 per 100 on the same
  messages.

**Bar 3.** It allows a drop of at most 15 percentage points, and the drop is exactly 15. The frozen code records it
as a **fail**, because 0.85 − 0.70 is 0.15000000000000002 in floating point. Read on the registered integer counts, it
passes **at the limit**. The frozen result stands as computed; the reviewer decides which reading governs.

Either way, the drop shows the solver depends materially on its language model. That half-size model also had far
less text, so the drop mixes corpus size with any overlap effect.

**Where the misses come from** (33 of 200 on the fresh Carter text):
- the quick-anneal cut (stage 3): 15;
- the scorer preferring a wrong text: 14;
- the earlier cuts: 4.

The quick-anneal cut and the scorer are the two development targets.

## Bars (registered; `run_v1/RESULTS_JOB1.json` and `RESULTS_JOB2.json`, frozen in f54fa56 and 0b26783)
| Bar | Required | Result | Frozen verdict |
|---|---|---|---|
| 1, A1 | ≥ 70% at ≥ 90, and ≥ 5/10 in every cell | **83.5%** (167/200); cell minimum 5 (KRY, L 5, σ + 1) | PASS |
| 2, A2 | ≥ 50% at ≥ 90 | **82.5%** (33/40) | PASS |
| 3, A3 | first-half table within 15 points of the inherited table | 85/100 against 70/100: **exactly 15 points** | **FAIL** as computed (floating-point rounding at the boundary); PASS on the integer reading |
| 4, A4 | true cell on top ≥ 9/12 | **12/12** | PASS |
| 5, A5 | every recovered A4 plant above every decoy | recovered ≥ −404.3; decoys ≤ −455.5 | PASS |

**Endpoints** (exact Clopper–Pearson 95% intervals):

| Arm | n | Exact | ≥ 95 | ≥ 90 | Witness failures | Misses by cause |
|---|---|---|---|---|---|---|
| A1, Carter second half | 200 | 90 (0.38–0.52) | 133 (0.60–0.73) | 167 (0.78–0.88) | 0 | stage 3: 15; scorer: 14; stage 2: 3; stage 1: 1 |
| A2, K1–K3 | 40 | 12 (0.17–0.47) | 19 (0.32–0.64) | 33 (0.67–0.93) | 0 | stage 3: 4; annealer: 3 |
| A3, first-half table | 100 | 38 | 55 | 70 | 0 | stage 3: 17; annealer: 7; scorer: 6 |

**A5 decoys** (best T per kind): random −457.6; shuffles of A4 plants −458.5; two-free-alphabet autokeys −455.5.

**Runs:** both COMPLETE through `audit/run_bounded_agg.py`, with zero retries:
- job 1: 2,213 s, 375 MB;
- job 2: 3,162 s, 368 MB.

Each cap was 3,600 s.

**Commits:**
- pre-registration 62a9747;
- source fee7038;
- frozen outputs f54fa56 and 0b26783.

## What this means
**Supported in the tested scope** (B ∈ {AZ, KRY}, L 1–5, F = A, English-like text):
- S105's ≥ 90 recovery is about 83% and holds on fresh and differently styled text;
- its top-setting selection is reliable (12/12);
- its decoy separation holds, including against autokeys with an unknown cipher alphabet.

**Not shown:**
- **Exact recovery is weak**, at 30–45%, so most outputs need finishing by eye.
- **Dependence on the inherited quadgram model** is material, and its training text is still undocumented.
- **R105's original GO is not verified here.** That remains with the batch-B audit.

**For R111.** Its NO_SIGNAL stays solver-limited. This validation makes a miss less likely in the tested cells, but it
does not exclude them.
