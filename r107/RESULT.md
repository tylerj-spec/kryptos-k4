# R107 result (Claude Code, 26 Nov 2026): Slidefair with free alphabets and a periodic key is exactly testable at short periods

**Type:** analysis + synthetic verification. No K4 input, and no published crib positions. **Independent review:
NONE**; this round opens audit batch C.

## In plain words
**The setting.** Slidefair is the ACA two-letter cipher on a sliding chart. R98 ruled it out for K4 whenever both
alphabets are keyword alphabets from R76's tier, whatever the key. With **arbitrary** alphabets it looked untestable.
R107 asks whether a structured key makes it testable: a key that repeats every p pairs, as any keyword key does.

**What the algebra shows.** Each pair is a simple two-way substitution:
- the upper output letter is σ_k of the lower input letter;
- the lower output letter is σ_k⁻¹ of the upper input letter;
- σ_k is built from the two alphabets and the key letter.

Two facts follow:
- **The upper letter never maps to itself.** This holds under every convention, alphabet and key.
- **A known plaintext pair gives two linear equations mod 26** in the alphabets and the key letter. With a periodic
  key, pairs that share a key letter share unknowns. That gives an exact check that needs no search over alphabets.

**What the check does.** X107 declares a hypothesis impossible if either holds:
- some known pair breaks the letter rule; or
- the equations force two different letters to share a position in one alphabet.

It can set one pair aside, to allow for Slidefair's same-column rule or a single error.

**Results:**
- **Never wrong on true plants.** It never excluded a true plaintext beyond what its same-column pairs allow (400
  plants).
- **Two implementations agree:** 0 disagreements on 2,960 cells.
- **On random data, with one pair set aside,** it rules out:
  - 100% of false hypotheses at period 1 and 2;
  - 82–93% at periods 3–4;
  - 79% at period 5;
  - 50–65% at periods 6–11, except period 9 (47%).

  At longer periods the share falls to about 20%, and with no period at all to 18%. Without the one-pair allowance it
  rules out 59% even then.

**Consequence.** Periodic-key Slidefair with free alphabets can be tested on K4 exactly at periods 1–8, 10 and 11.
That K4 run is a separate, crib-assisted, exclusion-only round, and it is **proposed for approval (P4)**, not run
here.

## Verdict (pre-registered): gates pass; **TESTABLE at p 1–8, 10, 11**; WEAK at 9, 12, 16, 24, 36 and any key
| Step | Result |
|---|---|
| **T1 structure** (400 messages, 19,200 pairs, 776 same-column) | 0 round-trip, 0 identity, 0 equation, 0 pair-map, 0 alignment failures |
| **T2 soundness** (400 masked plants) | **0 unsound**. 249 plants had no same-column crib pair: all OPEN. 119 had one: 29 EXCLUDED_EXACT, none EXCLUDED_DROP. 32 had two or more: 3 EXCLUDED_DROP, 6 EXCLUDED_EXACT |
| **T3 two implementations** | 2,960 cells, **0 disagreements** between the null-space test and the rank reference |
| T5 ciphertext-only invariant (exploratory) | T_{2p} of the ciphertext equals that of the aligned plaintext in 23/120 plants. The mean absolute difference is 2.95, from same-column pairs |

**T4 chance power** (60 random messages × 16 conventions = 960 cells per period):

| p | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 16 | 24 | 36 | any |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EXCLUDED_DROP | 1.000 | 0.996 | 0.925 | 0.817 | 0.792 | 0.567 | 0.650 | 0.558 | 0.467 | 0.513 | 0.500 | 0.346 | 0.338 | 0.221 | 0.200 | 0.179 |
| EXACT or DROP | 1.000 | 1.000 | 0.988 | 0.979 | 0.983 | 0.896 | 0.913 | 0.871 | 0.858 | 0.838 | 0.804 | 0.763 | 0.704 | 0.638 | 0.608 | 0.592 |
| Label | T | T | T | T | T | T | T | T | W | T | T | W | W | W | W | W |

T = TESTABLE, W = WEAK. The power is not monotone in p. Which crib pairs share a key letter depends on how p divides
their pair-index differences.

**Run:** COMPLETE through `audit/run_bounded_agg.py`: 254 s wall, 252 s CPU, 19 MB (cap 1,800 / 1,800 / 2,048),
zero retries.

**Commits:**
- pre-registration f76e520, pushed alone;
- source d45aa0e;
- outputs frozen in 7818586.

The CI workflow (ad5909a) was committed during the run. It does not touch anything the run reads.

## Limits
**What the labels are.** They are chance-exclusion powers for one random hypothesis, given two crib windows of 13
and 11 letters. On K4 the real windows and letters apply, and the result for each (convention, p) cell would be
EXCLUDED or OPEN. **OPEN is not a consistency proof.**

**What a K4 exclusion would need to assume:**
- the published plaintext in place;
- at most one same-column or wrong pair among the fully known crib pairs, for DROP;
- or none, for EXACT.

About 4% of pairs are same-column, and in T2 38% of true plants (151/400) had at least one such crib pair. EXACT-only exclusions
are therefore weaker evidence than DROP exclusions.

**Overlap with the ledger:**
- For the 8 conventions with o ≠ r, periodic Slidefair without same-column crib pairs is a special case of L21
  (per-slot bijections in place at m = 2p).
- The other 8 conventions are L21's model after a swap inside each pair, which L21 did not test.
- X107 uses more structure than L21: all slots are tied to two alphabets.

Nothing from R107 enters a blind search.
