# R109 result (Claude Code, 27 Nov 2026): two-free-alphabet plaintext autokey on K4. 34 cells excluded exactly (6 also with one error); most cells stay open

**Type:** CRIB_ASSISTED / AGGREGATE_ONLY / EXCLUSION_ONLY. **Independent review: NONE**; this is audit batch C.

## In plain words
**The setting.** The cipher family is a plaintext autokey with two secret mixed alphabets: R102's family S3b. The key
letter is numbered in the plaintext alphabet, in the cipher alphabet, or straight (F = A, B or AZ). Lags run from 1 to
96, under all four sign choices. For each such cell, R109 asked whether **any** two alphabets, constant and primer can
reproduce K4's ciphertext at the 24 published letters.

**Only some cells can be checked.** A cell has something to check only where two published letters sit L apart. That
happens at lags 1–12 and 30–52: 420 cells. The other 732 cells place no constraint on K4.

**Results for the 420 checkable cells:**
- **34 are impossible** if the published letters are right. **6 of them** stay impossible with any one published
  letter (or ciphertext letter) wrong:
  - lag 2 with straight feedback (F = AZ), all four sign pairs;
  - lag 9 with F = A and opposite signs.
- **322 are possible.** Some pair of alphabets fits the 24 letters. That proves nothing about K4, since two free
  alphabets leave a great deal of freedom.
- **64 are undecided** within the solvers' limits.
- The two solvers never disagree: the DFS confirmed all 34 exclusions.

**Chance comparison.** K4 is no more consistent with the family than random shuffles of its letters are. The primary
solver alone found 12 impossible cells for K4, against a median of 4 for the 20 shuffles (range 2–46). There is no
lead.

**Consequence.** The two-free-alphabet autokey stays mostly **open** for K4. The exclusions are confined to the short
lags 1–4, 6, 9 and 10 and to 42–43, as listed below.

## Gate (`holdout/GATE.json`, seed 1090901): **GO**
| Check | Result |
|---|---|
| V1 soundness (150 plants; 83 with equations) | 0 true hypotheses INCONSISTENT by either solver; 0 bad witnesses |
| V2 one error (150 plants) | 0 DROP exclusions |
| V3 two solvers (600 cases, Amendment 2) | 142 decided by both, **0 disagreements** |

COMPLETE: 80 s. The gate freeze f177826 was pushed before any K4 input.

**Amendments**, both approved by Tyler on 27 Nov 2026 before the gate:
- **Amendment 1:** primary dmax 7 → 5, for time;
- **Amendment 2:** V3 counts decided cases instead of requiring a 50% share.

Both are conservative.

## Target (`k4/VERDICTS.json`, frozen in 7a7d293; `k4/EVALUATION.json`)
| Verdict | Cells |
|---|---|
| **EXCL** (EXACT and every one-position drop) | **6** |
| **EXCL_EXACT_ONLY** | **28** |
| OPEN (consistent) | 322 |
| UNDECIDED | 64 |
| NO_EQUATIONS (lags 13–29, 53–96) | 732 |

**Excluded cells.** Signs are (s1, s2).

| Level | Cells |
|---|---|
| EXCL (one error allowed) | L2 F = AZ, all four signs; L9 F = A, (+1, −1) and (−1, +1) |
| EXACT only | L1 F = AZ, all four signs; L3 F = A and F = AZ, all four signs each; L4 F = AZ (+1, +1), (+1, −1), (−1, +1), (−1, −1) and F = A (+1, −1), (−1, +1); L6 F = B (+1, −1), (−1, −1); L10 F = A (+1, +1), (−1, −1); L42 F = AZ, all four signs; L43 F = A (+1, −1), (−1, +1) |

**By lag:**
- **Lags 1–4:** every cell is excluded or undecided; none is open.
- **Lags 5–12 and 30–52:** mostly open. The exceptions are the exclusions listed above and the undecided cells
  (lags 5, 6, 8, 32, 33, 36, 37, 42 and 45–50).

**Cross-checks:**
- The DFS cross-check gave INCONSISTENT for all 34 exclusions. There were no disagreements.
- The primary-only INCONSISTENT count was 12 for K4, against 2, 6, 2, 4, 2, 32, 2, 14, 2, 10, 14, 46, 6, 2, 14, 2, 2,
  2, 2 and 6 for the 20 shuffles. LEAD flag: no.

**Run:** COMPLETE through `audit/run_bounded_agg.py`: 130 s wall, 129 s CPU, 151 MB (cap 3,600 / 3,600 / 2,048),
zero retries.

**Commits:**
- pre-registration 5b1b84c;
- Amendment 1 8544bc5, approved in ceb26b0;
- Amendment 2 ceb26b0, approved in af4288f;
- source af4288f;
- gate freeze f177826;
- input list 85633d3;
- target freeze 7a7d293;
- evaluation a208f6d.

## What this excludes, and what it does not
**Excluded exactly** (crib-assisted, the published letters in place): the 34 cells above, for **every** pair of
alphabets, constant and primer. The 6 EXCL cells also allow one wrong published or ciphertext letter.

**Not excluded:**
- the 322 open and 64 undecided cells;
- every lag without crib equations (13–29, 53–96);
- two or more errors;
- other autokey forms;
- any further layer.

**Relation to R111.** R111's blind search covered F = A, B ∈ {AZ, KRY} and L 1–5. For those settings, R109:
- **excludes, for every alphabet pair,** L3 (all four sign pairs) and L4 with opposite signs, at the exact level;
- **leaves the rest undecided or open:** L1, L2 and L4 with equal signs are undecided, and L5 is open or undecided.

R111's NO_SIGNAL stands on its own: it did not use R109.

Nothing from R109 enters any blind search.
