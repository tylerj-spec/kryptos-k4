# R115 pre-registration (Claude Code, 28 Nov 2026): linear-recurrence keystream with two free alphabets, exact crib check X115 (synthetic)

**Type: analysis + synthetic verification. No K4 input of any kind.**

**Approval:**
- Tyler, 27 Nov 2026: "I'm fine with that, continue on along with any logical next steps that you suggest until
  we're ready for an actual substantive review".
- F3 is a fallback task authorized at once (`audit/reviews/BATCH_WORK_ORDER_R102_R107.md` §4). The F3 catalogue
  (`audit/reviews/F3_KEYGEN_CATALOGUE_20261128.md`) ranks this gap first.

**Independent review: NONE** (one model). R115 joins audit batch C.

## 1. Why
**What the ledger covers:**
- L49 excludes affine linear-recurrence keys of order 1–6 under 48 **fixed** conventions;
- L15 covers base-26 lagged Fibonacci with **one** free cipher alphabet;
- L177 covers progressive keys with **one** free alphabet;
- L90 covers **given** key sequences with both alphabets free.

**The gap.** Nothing in the ledger has **both** alphabets free **and** the recurrence's coefficients unknown.

## 2. The model and the check X115 (`r115/x115.py`)
**Model:** y(c_n) = x(p_n) + k_n (mod 26), where:
- x = PA⁻¹ and y = CA⁻¹ are arbitrary bijections;
- k_n = a_1 k_{n−1} + … + a_L k_{n−L} + d (mod 26) holds from the first crib position t0 onward.

**What the model includes:**
- **Beaufort and Variant Beaufort** reduce to this form under free alphabets (L92).
- **Keys generated from position 0** form a subset of this model, so excluding the model also excludes them.
- **The family contains:**
  - progressive keys (a = (1), d ≠ 0);
  - multiplicative congruential keys;
  - Fibonacci-type keys;
  - polynomial keys of degree below L (characteristic polynomial (x − 1)^L);
  - periodic keys of period at most L.

**The check.** For each coefficient vector a, every crib equation is linear in:
- the alphabet values;
- the key state (k_t0, …, k_t0+L−1);
- d.

The system mod 2 depends only on a mod 2, and the system mod 13 only on a mod 13. Each is row-reduced once with
R112's `Sys` class (`r112/x112.py`, unchanged), and the verdicts are combined.

**Verdicts:**
- **EXCL** if a system is inconsistent or forces a collision: two letters of one alphabet equal mod 2 and mod 13, or
  three equal mod 13;
- **EXCL_DROP** if that holds with every single crib equation set aside in turn;
- otherwise **OPEN**, which is not a consistency proof.

**Reference** (`r115/ref115.py`). It shares no code with X115:
- an explicit unknown key at every position from the first to the last crib position;
- the recurrence written out as one equation per position;
- the full vector a, with no mod-2 / mod-13 split of a;
- dense Gauss–Jordan elimination with numpy;
- particular-solution plus null-space signatures, with the same collision rule.

## 3. Registered computations (seed 1150901; masks are random 13 + 11 windows; no K4 positions)
| Step | What | Pass |
|---|---|---|
| **T1 structure** | 300 messages with L 1–6 and random a, seeds, d and alphabets. Each is encrypted forward from position 0 by `run115.py`'s own encryptor. Half use all 97 positions as the mask, half use random masks. Check the round trip, and that every X115 equation, mod 2 and mod 13, vanishes on the true values | **0 failures** |
| **T2 soundness** | 400 masked Carter plants, 100 at each L 1–4. In each L, 25 use structured vectors (below) and 75 random vectors. The true vector is never EXCL. With one crib letter replaced by a wrong letter, never EXCL_DROP | **0 failures** in both |
| **T3 two implementations** | X115 against the reference on 24 messages, half planted and half random ciphertext, with L cycling over 1–3. Covers every vector at L 1–2, 150 random vectors at L 3, and the true vector of each plant. One-drop verdicts on a random 30% of the cells at L 1–2 | **0 disagreements** |
| **T4 chance power** | Random ciphertexts with Carter plaintext at a random mask: 40 messages × every vector at L 1–3, and 20 messages at L 4. Report the share EXCL (including EXCL_DROP) and the share EXCL_DROP | reported |

**Structured vectors:**
- L 1: (1);
- L 2: (1, 1), (0, 1), (2, 25);
- L 3: (0, 0, 1), (3, 23, 1), (1, 1, 1);
- L 4: (0, 0, 0, 1), (4, 20, 4, 25), (1, 1, 1, 1).

These are taken in turn.

**Labels per L** (if T1–T3 pass):
- **ROBUST** if the EXCL_DROP share is ≥ 0.50;
- **TESTABLE** if only the EXCL share is ≥ 0.50;
- **WEAK** otherwise.

A failure of T1–T3 is a stop condition.

**Development** (dev seeds 1151–1155, synthetic only):
- prototype and X115: 40 plants, 0 unsound, 0 wrong-letter EXCL_DROP;
- 3,414 cells against the reference: 0 disagreements;
- EXCL share 1.00, 0.80, 0.18 and 0.20 at L 1–4 on 6 random messages, and EXCL_DROP 1.00, 0.46, 0.03 and 0.01.

A complete feasibility search (enumerating the solution space with injectivity) added nothing at L 1 (0.9962 either
way, on 10 messages). It was too slow at L 2, so it is not used.

**Budget:** `audit/run_bounded_agg.py`, 3,600 s / 3,600 s / 2,048 MiB, zero retries. The expected run time is about
25 minutes.

## 4. What follows
- **The K4 run is not done here.** A K4 run of X115 would be a separate crib-assisted round, proposed as **P8** for
  Tyler's approval. It needs only the published letters to be right, with one error allowed at EXCL_DROP.
- **What to expect from it.** If T4 matches development, the K4 run would:
  - decide every order-1 vector (this includes progressive keys with two free alphabets);
  - test most order-2 vectors;
  - leave orders 3 and above WEAK.
- **Outside X115:** recurrences mod 10 (the chain-addition rows), nonlinear recurrences, and keys that restart or
  are interrupted.
