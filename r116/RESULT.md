# R116 result (Claude Code, 28 Nov 2026): two-free-alphabet keys from an order-1 recurrence are excluded for K4, even with one error; 668 of 676 order-2 vectors are excluded

**Mode:** crib-assisted, aggregate-only, exclusion-only (P8; Tyler: "I approve all of them"). It decodes nothing.
**Independent review: NONE**; this is audit batch C.

## In plain words
**The question.** Could K4 be a Quagmire-IV-type cipher, with both alphabets unknown, whose key comes from a simple
number rule? In that rule, each key value is a fixed combination of the previous one or two values, plus a constant.

**The test.** The 24 published letters were checked against every rule of that shape.

**Order 1** (each key value from the one before): **all 26 rules are excluded,** even allowing one wrong published or
carved letter. This covers:
- every progressive key (the key advancing by a fixed step), extending L177, which had only one free alphabet;
- every multiplicative key;
- under Vigenère, Beaufort and Variant alike.

**Order 2** (from the two values before): **668 of 676 rules are excluded**, 470 of them even with one wrong letter.
This includes Fibonacci-type keys, period-2 keys and linear progressions. **8 rules stay open:**
(11, 20), (21, 19), (21, 6), (22, 7), (24, 7), (8, 19), (8, 6), (9, 20). Staying open is not evidence for them. The
check only shows they are not ruled out.

**Orders 3 and 4:** 74% and 14% of rules are excluded. As registered, these orders are too weak to close the family.

**No lead.** K4 leaves *fewer* rules open than most shuffles do. At order 2, 161 of 200 shuffles leave 8 or more
open, with a median of 145. So K4 does not fit this family unusually well.

## Results (`k4/AGGREGATES.json`, frozen in 61b7e78; `k4/EVALUATION.json`; `k4/CROSSCHECK.json`)
| Order | Vectors | K4 EXCL_DROP | K4 EXCL (exact only) | K4 OPEN | Family verdict | Shuffles: OPEN min / median / max; ≥ K4 | LEAD |
|---|---|---|---|---|---|---|---|
| 1 | 26 | **26** | 0 | **0** | **EXCLUDED_DROP** | 0 / 0 / 13; 200 of 200 | no |
| 2 | 676 | 470 | 198 | **8** | PARTIAL (98.8% excluded) | 0 / 145 / 620; 161 of 200 | no |
| 3 | 17,576 | 2,375 | 10,588 | 4,613 | PARTIAL (73.8%) | 1 / 14,927 / 17,459; 172 of 200 | no |
| 4 | 456,976 | 7,449 | 55,157 | 394,370 | PARTIAL (13.7%) | 26,243 / 441,423 / 456,623; 17 of 20 | no |

**Named keys on K4:**

| Key | Vector | Verdict |
|---|---|---|
| progressive | (1) | EXCL_DROP |
| Fibonacci | (1, 1) | EXCL_DROP |
| period 2 | (0, 1) | EXCL_DROP |
| linear progression | (2, 25) | EXCL_DROP |
| period 3 | (0, 0, 1) | EXCL_DROP |
| quadratic | (3, 23, 1) | EXCL (exact) |
| tribonacci | (1, 1, 1) | OPEN |
| period 4 | (0, 0, 0, 1) | EXCL (exact) |
| cubic | (4, 20, 4, 25) | OPEN |
| tetranacci | (1, 1, 1, 1) | OPEN |

**Checks:**
- **Gate GO** (frozen c8bd391):
  - structure: 0/100 failures;
  - soundness: 0/200, and 0 wrong-letter plants at DROP;
  - two implementations: 0 disagreements on 3,214 cells.
- **Cross-check (post-freeze):** the reference `r115/ref115.py` agrees on all 708 frozen K4 cells, and on 300 random
  order-3 vectors, with **0 disagreements**.
- **Resources:** all three jobs are COMPLETE under `audit/run_bounded_agg.py`, with zero retries:
  - gate: 108 s;
  - target: 903 s, 278 MB;
  - cross-check: 106 s.

**Commits:**
- pre-registration 755b0e8;
- source 2e8b53d;
- gate c8bd391;
- K4 freeze 61b7e78.

## What this means
**Excluded (EXACT, within the stated model).** Conditional on the 24 published letters being right, with one error
allowed at DROP:
- the cipher is y(c) = x(p) + k (mod 26), with both alphabets free (Vigenère, Beaufort and Variant included);
- the key is any affine first-order recurrence k_n = a·k_{n−1} + d, from the first crib position onward.
That covers every progressive and multiplicative key.

**At order 2,** all but 8 coefficient vectors are excluded.

**Masking scope:**
- valid under reading A;
- valid under reading B for masks that keep the crib letters' equality pattern (F1 §2).

**Not covered:**
- the 8 OPEN order-2 vectors;
- orders 3 and above as families;
- recurrences mod 10 (the chain-addition rows);
- nonlinear recurrences;
- restarted or interrupted keys;
- two or more wrong letters;
- transposition layers.

**Possible follow-up (needs registration).** A complete feasibility search, enumerating the solution space with
injectivity, could decide the 8 open order-2 vectors exactly. In R115's development the search was too slow on random
messages at order 2. On 8 fixed vectors it is likely feasible.
