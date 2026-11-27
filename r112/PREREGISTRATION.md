# R112 pre-registration (Claude Code, 27 Nov 2026): Slidefair with free alphabets, exact crib check with general same-column handling (synthetic)

**Type: analysis + synthetic verification. No K4 input of any kind.**

**Approval:** Tyler, 27 Nov 2026: "I'm fine with that, continue on along with any logical next steps that you
suggest until we're ready for an actual substantive review". It also answers item 3 of §6 of
`audit/reviews/R108_R111_CHATGPT_QUALITY_REVIEW_20261127.md`.

**Independent review: NONE** (one model). R112 joins audit batch C.

## 1. Why
R108's exclusions assume that no complete crib pair invokes Slidefair's same-column rule. Its DROP cells allow at most
one such pair. With about one pair in 26 same-column, that leaves real messages uncovered. R112 asks for a check that
treats the same-column branch exactly, for **any number** of crib pairs.

## 2. The check X112 (`r112/x112.py`)
**Notation** as in R107: a = PA⁻¹ and b = CA⁻¹; k is the pair's key value (periodic over pairs with period p, or any
key).

**Each complete crib pair takes one of two branches:**

| Branch | Vigenère (or Variant) | Beaufort |
|---|---|---|
| Normal (N) | a(cu) − b(w) + k = 0;  b(cl) − a(u) − k = 0 | a(cu) + b(w) − k = 0;  b(cl) + a(u) − k = 0 |
| Same column (S), R98's "letters to the right" | a(u) − b(w) + k = 0;  a(cu) − a(u) = 1;  b(cl) − b(w) = 1 | a(u) + b(w) − k = 0;  a(cu) − a(u) = 1;  b(cl) − b(w) = −1 |

- **The normal branch's inequality** (the columns differ) is equivalent to cu ≠ u.
- **Neither branch allows cu = u,** so a pair with cu = u is impossible.

**The procedure:**
- A depth-first search assigns N or S to every crib pair.
- It keeps the affine system row-reduced mod 2 and mod 13.
- It prunes a node when the system is inconsistent or forces a collision. A collision is two letters of one alphabet
  equal mod 2 and mod 13, or three equal mod 13. Both conditions are monotone as equations are added, so pruning is
  exact.

**Verdicts:**
- **EXCL** if no assignment survives;
- **EXCL_DROP** (computed with `allow_drop`) if no assignment survives even with one crib pair set aside;
- otherwise **OPEN**, which is not a consistency proof.

**Reference** (`r112/ref112.py`):
- brute force over every assignment, with no pruning;
- each leaf solved by an explicit particular solution plus a null-space basis mod 2 and mod 13;
- the same collision rule applied to the per-letter signatures.

It shares only the per-pair equation table and the crib-pair extraction with X112.

## 3. Registered computations (seed 1120901; masks are random 13 + 11 windows unless stated; no K4 positions)
| Step | What | Pass |
|---|---|---|
| **T1 structure** | Against `r98/slidefair98.py` (all 16 conventions, free alphabets, periodic and any-key keys, half the messages with same-column pairs forced by the key choice), every pair satisfies its branch's equations, and the round trip holds | 300 messages, **0 failures** |
| **T2 soundness** | 400 masked Carter plants: 200 with natural keys (p cycling over 1–12, 16, 24, 36 and any) and 200 any-key plants with about 40% of crib pairs forced same-column. The true hypothesis is never EXCL. With one crib letter replaced by a wrong letter, never EXCL_DROP | **0 failures** in both |
| **T3 two implementations** | X112 against the reference, with and without one drop: 15 random messages with 7 + 5 masks × 16 conventions × p ∈ {1, 2, 4, any}; and 40 cells with full 13 + 11 masks | **0 disagreements** |
| **T4 chance power** | 40 random messages × 16 conventions × p ∈ {1, …, 12, 16, 24, 36, any}: the share EXCL, and the share EXCL_DROP | reported |

**Labels per p** (if T1–T3 pass):
- **ROBUST** if the EXCL_DROP share is ≥ 0.50;
- **TESTABLE** if only the EXCL share is ≥ 0.50;
- **WEAK** otherwise.

A failure of T1–T3 is a stop condition.

**Development** (dev seeds 1121–1122):
- 80 plants (up to 9 forced same-column crib pairs each): 0 unsound;
- 1,536 small-mask cells: 0 disagreements with the reference;
- EXCL share on random data: 1.00 at p 1, 0.94 at p 3, 0.69 at p 6, 0.55 at p 12, and 0.47 with any key.

**Budget:** `audit/run_bounded_agg.py`, 1,800 s / 1,800 s / 2,048 MiB, zero retries.

**What follows.** A K4 run of X112 would replace R108's no-same-column assumption with exact handling. It needs only
the published letters to be right, with one error allowed at EXCL_DROP. It is **not run here**: it is a separate
crib-assisted round, proposed after the substantive review. Other same-column rules at two or more pairs stay outside
X112.
