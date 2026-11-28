# R116 pre-registration (Claude Code, 28 Nov 2026): linear-recurrence keys with two free alphabets, exact crib check on K4 (P8)

**Mode: CRIB_ASSISTED / AGGREGATE_ONLY / EXCLUSION_ONLY.** It decodes nothing and completes no key. Its only output is
one verdict per coefficient vector (at orders 1–2) and verdict counts (at orders 3–4).

**Approval:** Tyler, 28 Nov 2026: "I approve all of them", answering the list of P6, P8, P9 and F2's route rounds.
This is proposal P8 of `audit/ROLLING_QUEUE.md`.

**Dependency:** R115 (L203, unaudited, audit batch C) supplies the check. This round's own gate (§3) re-verifies, with
a fresh seed, everything the check relies on, so the exclusions do not rest on R115's unaudited claims.

**Independent review: NONE** (one model). R116 joins audit batch C.

## 1. Model (exact)
**The cipher:** y(c_n) = x(p_n) + k_n (mod 26), where:
- x = PA⁻¹ and y = CA⁻¹ are **free**: any two of 26!;
- Vigenère, Beaufort and Variant Beaufort all reduce to this form under free alphabets (L92).

**The key:** k_n = a_1 k_{n−1} + … + a_L k_{n−L} + d (mod 26), required from the first crib position onward.
- This is a superset of keys generated from position 0.
- It includes progressive keys, multiplicative congruential keys, Fibonacci-type keys, polynomial keys of degree
  below L, and periodic keys of period at most L.

**Plaintext:** the 24 published letters, in place, in the carved order. They are read from the `CLUES` literal of
`r73/sealed/reveal_k4.py` (sha256 63121cea…).

**Scope.** Every coefficient vector a ∈ Z26^L:
- L = 1 and 2: 702 vectors, each with a verdict;
- L = 3 (17,576 vectors) and L = 4 (456,976 vectors): counts only. R115 labels these orders WEAK, so they cannot
  close the family.

**Masking scope** (F1 §2). X115 sees plaintext letters only through their own free alphabet. The verdicts are
therefore valid:
- under reading A;
- under reading B, for masks that keep the crib letters' equality pattern.

## 2. The check
The check is X115, `r115/x115.py`, unchanged (sha256 in `PROTOCOL.sha256`), with R112's `Sys`. Per vector:

| Verdict | Meaning | When it is a valid exclusion |
|---|---|---|
| **EXCL_DROP** | Excluded with every single crib equation set aside in turn | Covers one wrong published letter or one wrong ciphertext letter |
| **EXCL** (exact only) | Excluded only with all 24 equations kept | Only if all 24 letters are right |
| **OPEN** | Not excluded | It is not a consistency proof |

## 3. Sealed synthetic gate (`r116/gate116.py`; reads no K4 file and no published letter or position)
**Seed:** 1160901.

**Masks:** random 13 + 11 windows, not the K4 positions.

| Check | What | Pass |
|---|---|---|
| V1 structure | 100 messages, L 1–6, forward-encrypted from position 0 by the gate's own encryptor. Check the round trip, and that every X115 equation vanishes mod 2 and mod 13 on the true values | 0 failures |
| V2 soundness | 200 masked Carter plants, L 1–4 (50 each, 12 of them structured as in R115). The true vector is never EXCL. With one crib letter replaced by a wrong letter, never EXCL_DROP | 0 failures |
| V3 two implementations | X115 against `r115/ref115.py` on 12 messages (half planted): every vector at L 1–2, 100 random vectors at L 3, and the true vector of each plant. One-drop verdicts on a random 30% of the cells at L 1–2 | 0 disagreements |

**GO** if V1–V3 all pass. Otherwise **NO-GO**: K4 is not run and nothing is recorded.

**Gate budget:** 1,800 s / 1,800 s / 2,048 MiB.

## 4. Target (`r116/run_target116.py`; only after the gate's GO and its freeze are pushed)
**Inputs:** K4 (sha256 2797de14…) and **200** letter-shuffles of K4 (seed 1160400). Every input uses the same 24
published letters in place.

**Computed, with drops:**
- L 1–3 for every input;
- L 4 for K4 and the first 20 shuffles.

**Written:**
- **for every input:** the number of vectors per verdict at each L;
- **for K4 only:**
  - the per-vector verdicts at L 1–2;
  - the verdicts of the registered structured vectors at L 3–4: (0, 0, 1), (3, 23, 1), (1, 1, 1), (0, 0, 0, 1),
    (4, 20, 4, 25), (1, 1, 1, 1).

**Target budget:** 3,600 s / 3,600 s / 2,048 MiB, zero retries. The estimate is about 25 minutes.

**Decision** (`r116/evaluate116.py`, from the frozen aggregates only):
- **Per L**, K4's counts of EXCL_DROP, exact-only EXCL and OPEN, with the shuffles' distribution of OPEN counts.
- **Family verdict per L:**
  - **EXCLUDED_DROP** if every vector is EXCL_DROP;
  - **EXCLUDED_EXACT** if every vector is excluded but some only exactly;
  - otherwise **PARTIAL**, with the OPEN vectors listed at L 1–2.
- **LEAD flag per L:** set if K4's OPEN count is greater than in every shuffle computed at that L. K4 would then fit
  the family unusually well. That is a stop condition: report it. It is not a plaintext.
- **The named structured keys and their verdicts on K4:**
  - progressive (1);
  - geometric (any a at L 1);
  - Fibonacci (1, 1);
  - period 2 (0, 1);
  - linear progression (2, 25);
  - and the L 3–4 vectors above.

**Post-freeze cross-check** (`r116/crosscheck116.py`). The reference `r115/ref115.py` recomputes, from the frozen
inputs, all 702 K4 verdicts at L 1–2 (with drops) and the structured L 3–4 verdicts. It also checks 300 random L 3
vectors on K4 against a fresh X115 call. Any disagreement is a stop condition.

## 5. What this cannot exclude
- OPEN vectors.
- Orders 3 and above as families.
- Recurrences mod 10 (the chain-addition rows).
- Nonlinear recurrences.
- Keys that restart or are interrupted.
- Errors at two or more crib letters.
- Transposition, insertion or deletion layers.
- Masks that merge two crib letters (F1 §2).

## 6. Order
1. This file, `QA_MANIFEST.json`, `PROTOCOL.sha256` and `budgets/GATE_BUDGET.json`, pushed alone.
2. Source and `SOURCE.sha256`.
3. The gate, then `holdout/GATE_FROZEN.sha256` and the manifest's GO, pushed.
4. The target, then `k4/FROZEN.sha256`, pushed.
5. The evaluation and the cross-check, then the result note.
