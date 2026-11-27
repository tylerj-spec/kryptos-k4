# R108 result (Claude Code, 27 Nov 2026): Slidefair with free alphabets is excluded for K4 under every key structure tested, exactly; 372 of 768 cells survive one bad pair

**Type:** CRIB_ASSISTED / AGGREGATE_ONLY / EXCLUSION_ONLY. **Independent review: NONE**; this is audit batch C.

## In plain words
**The setting.** R98 ruled out Slidefair for K4 when both alphabets are keyword alphabets from R76's tier. R107 found
an exact check for **arbitrary** alphabets. R108 applied that check to K4. It covered all 16 Slidefair conventions,
with a key that repeats every p pairs for each p from 1 to 47, and with **any key at all**.

**What was found:**
- **Every one of the 768 cells is excluded,** on the stated assumption that the 22 published letters in complete
  pairs are right and that none of those 11 pairs hit Slidefair's same-column rule.
- **Allowing one bad pair, 372 cells stay excluded.** A bad pair is a wrong letter, a wrong ciphertext letter, or a
  same-column pair under any rule.
  - This covers every convention at periods 1–5, 7, 19 and 21.
  - With any key, it covers 4 of the 16 conventions.
- **The independent rank-based implementation agrees on all 768.**

**Chance comparison.** On 200 letter-shuffles of K4, a median of 136 cells stayed open. K4 had 0, but so did 48 of
the 200 shuffles. K4 is therefore not anomalous: the exclusion is strong for every such hypothesis, not a sign that
something special happens with K4.

**Consequence.** Slidefair with free alphabets was shortlist item S3, considered untestable. It is now excluded for
K4 in place, at the exact level, under any key. It is excluded at the one-error level for the cells listed below.

## Gate (`holdout/GATE.json`, seed 1080901): **GO**
| Check | Result |
|---|---|
| V1 structure (200 messages, 9,600 pairs) | 0 failures: round trip, identity, equations, pair map |
| V2 soundness (400 masked plants) | **0 unsound** |
| V3 two implementations | 3,472 cells, **0 disagreements** |

COMPLETE: 177 s wall, 176 s CPU. The gate freeze 3b8ac20 was pushed before any K4 input.

## Target (`k4/AGGREGATES.json`, frozen in fff2e8e)
| Input | EXCLUDED_DROP | EXCLUDED_EXACT only | OPEN |
|---|---|---|---|
| **K4** | **372** | **396** | **0** |
| 200 shuffles | median 308 | — | median 136 (min 0, max 548; 48 shuffles at 0) |

**K4 by key structure** (number of the 16 conventions that are DROP / EXACT-only / OPEN):

| Key structure | DROP | EXACT only | OPEN |
|---|---|---|---|
| p = 1–5, 7, 19, 21 | 16 | 0 | 0 |
| p = 6, 9–11, 17, 18, 20, 22, 25 | 12 | 4 | 0 |
| p = 8, 12, 24 | 8 | 8 | 0 |
| p = 13–16, 23, 26–47, and any key | 4 | 12 | 0 |

**With any key, the 4 DROP-excluded conventions** are those whose output order equals their role order on pair
parity 0: VIG and BEAU, (r, o) = (0, 0) or (1, 1).

**Run:** COMPLETE through `audit/run_bounded_agg.py`: 277 s wall, 276 s CPU, 20 MB (cap 1,800 / 1,800 / 2,048),
zero retries.

**Decision** (`k4/EVALUATION.json`):
- Family verdict: **PARTIAL**, because not every cell is DROP-excluded. Every cell is at least EXACT-excluded.
- LEAD flag: **no**.

**Post-freeze cross-check** (`k4/CROSSCHECK.json`): the rank reference agrees with all **768/768** frozen verdicts.

**Commits:**
- pre-registration 0bc11c3;
- source 693f75f;
- gate freeze 3b8ac20;
- target freeze fff2e8e;
- evaluation eaad1a5;
- cross-check 66f2e06.

## What this excludes, and what it does not
**Excluded exactly** (crib-assisted: the published letters in place and in the carved order):
- **Cipher:** Slidefair in all 16 conventions;
- **Alphabets:** any two alphabets;
- **Keys:** periodic over pairs (period 1–47, so every keyword key up to 47 letters), or any key;
- **Assumption:** every letter of the 11 complete crib pairs is right, and no crib pair is same-column.

**Excluded allowing one bad crib pair:** the 372 DROP cells above.

**Not excluded:**
- Two or more same-column or wrong crib pairs. About 38% of true messages have at least one same-column crib pair.
  Those messages are covered only by the DROP cells.
- Other digraphic rules.
- Transposition, insertion or deletion layers.
- The ciphertext not read in place.

Nothing from R108 enters any blind search.

## Errata (additive, 27 Nov 2026; after ChatGPT's partial quality review `audit/reviews/R108_R111_CHATGPT_QUALITY_REVIEW_20261127.md`)
1. **The headline and "Consequence" overstate the scope.** "Excluded … under every key structure tested" and "now
   excluded for K4 in place, at the exact level, under any key" hold only on a condition: the 22 published letters
   in the 11 complete crib pairs are right, and **no crib pair invokes the same-column rule**.
   - The 372 DROP cells remain excluded allowing **at most one** erroneous or same-column pair.
   - Two or more such pairs are outside every R108 guarantee.
   - Same-column handling is an ordinary branch of the cipher, so this is **not an unconditional exclusion of
     ordinary Slidefair** with free alphabets.
   - The title's "372 of 768 cells survive one bad pair" means 372 cells **remain excluded** with one bad pair.
2. **The same-column fraction.** "About 38% of true messages" was R107's panel (151/400). R108's own gate panel had
   **136/400 (34%)** plants with at least one same-column crib pair. 23 of the 109 one-pair plants were labelled
   EXCLUDED_EXACT. That is consistent with the label's stated assumption, and it shows why the assumption must stay
   attached to every summary.
3. **The cross-check is partly independent.** The rank reference re-implements only the forced-collision test. It
   runs inside the same `X.check` pipeline, so pair extraction, equation construction, the identity test and the
   DROP bookkeeping are shared. "Agrees 768/768" is accurate, but it is not an independent re-derivation of the
   whole check.
4. **The counts overlap.** The 768 and 372 are counts of overlapping labelled settings, not independent pieces of
   evidence.
