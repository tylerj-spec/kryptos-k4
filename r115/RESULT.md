# R115 result (Claude Code, 28 Nov 2026): an exact check for linear-recurrence keys with two free alphabets. Sound; ROBUST at order 1, TESTABLE at order 2, WEAK at orders 3–4

**Type:** analysis + synthetic verification. No K4 input and no K4 claim. **Independent review: NONE**; this is audit
batch C.

## In plain words
**The question.** Can K4's 24 clue letters rule out a key made by a simple number rule? The rule is that each key
value is a fixed combination of the previous one to four values, plus a constant. This covers:
- progressive keys;
- Fibonacci-type keys;
- short repeating keys;
- polynomial keys.

Both cipher alphabets are unknown. The ledger had this family only with fixed alphabets (L49), or with one unknown
alphabet (L15, L177).

**The answer, on synthetic data:**
- **Order 1** (each key value from the previous one): the check rules out **98%** of rule settings on random
  messages, and **89%** even with one clue letter wrong. **ROBUST**.
- **Order 2:** **84%**, or 47% with one letter wrong. **TESTABLE**.
- **Orders 3 and 4:** 48% and 16%. **WEAK**: too many settings stay open to close the family.

**It is correct on every test:**
- the true rule is never ruled out (400 plants);
- a plant with one wrong letter is never ruled out once that letter is set aside;
- a second implementation, written separately, agrees on all 6,828 cells.

Power varies a lot from message to message. At order 2 the per-message share ranges from 0.10 to 1.00, because it
depends on how letters repeat inside the clue windows. K4's own power must therefore be measured on K4, with
shuffles.

## Results (`run_v2/RESULTS.json`, frozen in 55d9589)
| Step | Result | Pass |
|---|---|---|
| T1 structure | 300 messages (L 1–6; 150 with all 97 positions): round trip, and every equation vanishes mod 2 and mod 13 on the true values. 0 failures | PASS |
| T2 soundness | 400 plants (100 per L 1–4, 25 of them structured): the true vector is EXCL **0** times. With one wrong letter, EXCL_DROP **0** times. Without the drop, that wrong letter already gives EXCL in 38, 27, 19 and 3 plants at L 1–4 | PASS |
| T3 two implementations | 6,828 cells (24 messages; every vector at L 1–2, 150 at L 3, the true vector of each plant; drops on 30% at L 1–2). X115 found 3,935 EXCL, 764 EXCL_DROP and 2,129 OPEN, with **0 disagreements** | PASS |

**T4 chance power** (random ciphertext, Carter plaintext at a random 13 + 11 mask):

| L | Messages × vectors | EXCL share (including DROP) | EXCL_DROP share | Per-message EXCL range | Label |
|---|---|---|---|---|---|
| 1 | 40 × 26 | **0.984** | **0.889** | 0.77–1.00; OPEN vectors per message: mean 0.43, none in 35 of 40 | **ROBUST** |
| 2 | 40 × 676 | **0.838** | 0.466 | 0.10–1.00; OPEN vectors per message: mean 110, none in 8 of 40 | **TESTABLE** |
| 3 | 40 × 17,576 | 0.475 | 0.159 | 0.03–1.00 | WEAK |
| 4 | 20 × 456,976 | 0.161 | 0.013 | 0.01–0.92 | WEAK |

**Run history:**
- **Run v1 was INCOMPLETE.** It crashed in the report step after all four computations, so no result was written
  (4a09125).
- **Amendment 1** fixed only the report step and re-ran with the same seed. Tyler approved it: "Approve
  (Recommended)" (5056cb1).
- **Run v2 is COMPLETE** under `audit/run_bounded_agg.py`: 898 s wall, 890 s CPU, 585 MB, zero retries.

**Commits:**
- pre-registration ad3a123;
- source abc0ac0;
- amendment 5056cb1;
- frozen outputs 55d9589.

**Development** used dev seeds 1151–1157 and is disclosed in the pre-registration. On 6 random messages it estimated
order 3 at 0.18; the registered 40-message estimate is 0.48. That difference is part of the message-to-message
spread above.

## What this means
**What the check is.**
- X115 is a sound exact check, in the sense of R112, for "Quagmire IV with a key from an affine linear recurrence
  mod 26". Vigenère, Beaufort and Variant are all included.
- Its exclusions are proofs within that model, conditional on the published letters.
- OPEN is not a consistency proof.

**What a K4 run (P8, needs approval) would be expected to do:**
- **Order 1** (26 vectors; this includes progressive keys with two free alphabets) would most likely be fully
  decided. At most a few vectors would stay open.
- **Order 2:** most of its 676 vectors would be excluded.
- **Orders 3–4** would stay WEAK and could not close the family.

**Masking scope** (F1 §2). The check sees plaintext letters only through their own free alphabet, so it is valid:
- under reading A;
- under reading B, for masks that keep the crib letters' equality pattern.

**Outside X115:**
- recurrences mod 10 (the chain-addition rows);
- nonlinear recurrences (F3 ranks 2–3);
- keys that restart or are interrupted.
