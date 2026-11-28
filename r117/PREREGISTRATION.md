# R117 pre-registration (Claude Code, 28 Nov 2026): Slidefair with free alphabets, exact crib check on K4 with general same-column handling (P6)

**Mode: CRIB_ASSISTED / AGGREGATE_ONLY / EXCLUSION_ONLY.** It decodes nothing and completes no key. Its only output
is one verdict per (convention, key structure) cell.

**Approval:** Tyler, 28 Nov 2026: "I approve all of them", answering the list of P6, P8, P9 and F2's route rounds.
This is proposal P6 of `audit/ROLLING_QUEUE.md`.

**Dependency.**
- R112 (L200, unaudited, audit batch C) supplies the check.
- This round's own gate (§3) re-verifies, with a fresh seed, everything the check relies on, so the exclusions do not
  rest on R112's unaudited claims.
- R108 (L196) is the round this one generalises. R108's verdicts are compared, not reused.

**Independent review: NONE** (one model). R117 joins audit batch C.

## 1. Model (exact)
**The cipher.** ACA Slidefair as in R98 (`r98/slidefair98.py`):
- **16 conventions:** Vigenère/Variant or Beaufort slide × role order × output order × pair parity.
- **Same-column rule:** "letters to the right".

**Alphabets.** PA and CA are **free**: any two of 26!.

**Key.** One value per pair, periodic over the pair index with period **p ∈ {1, …, 47}**, or **any key** (one free
value per pair).

**Same-column handling.** **Every crib pair may be normal or same-column,** with R112's proper equations for each
branch, in any number. This removes R108's assumption that no crib pair is same-column.

**Plaintext.** The 24 published letters, in place, in the carved order. They are read from the `CLUES` literal of
`r73/sealed/reveal_k4.py` (sha256 63121cea…).

**Scope:** 16 conventions × 48 key structures = **768 cells**.

**Masking scope** (F1 §2). Slidefair puts plaintext and ciphertext letters through the same alphabets, so the
verdicts are valid **under reading A only**: the clues must describe the enciphered layer.

## 2. The check
The check is X112, `r112/x112.py`, unchanged (sha256 in `PROTOCOL.sha256`). Per cell:

| Verdict | Meaning | When it is a valid exclusion |
|---|---|---|
| **EXCL_DROP** | Excluded even with any one crib pair set aside | Covers one wrong letter or one wrong ciphertext letter, at one pair |
| **EXCL** (exact only) | Excluded only with every crib pair kept | Only if all 22 letters of the crib pairs are right |
| **OPEN** | Not excluded | It is not a consistency proof |

The drop check runs only on cells that are already EXCL: an exclusion with a drop allowed implies one without it.

## 3. Sealed synthetic gate (`r117/gate117.py`; reads no K4 file and no published letter or position)
**Seed:** 1170901.

**Masks:** random 13 + 11 windows, not the K4 positions.

| Check | What | Pass |
|---|---|---|
| G1 structure | 150 messages against `r98/slidefair98.py`, all 16 conventions, free alphabets. Half have periodic keys (p 1–12); half have any-key keys with crib-region pairs forced same-column with probability 0.4. Check the round trip, and that every pair satisfies its branch's equations | 0 failures |
| G2 soundness | 200 masked Carter plants: 100 with natural periodic keys (p cycling over 1–12, 16, 24, 36, 47 and any), and 100 any-key plants with forced same-column crib pairs. The true cell is never EXCL. With one crib letter replaced by a wrong letter, never EXCL_DROP | 0 failures |
| G3 two implementations | X112 against `r112/ref112.py` (brute force over every branch assignment). 10 random messages with 7 + 5 masks × 16 conventions × p ∈ {1, 2, 4, any}, with and without a drop. Plus 30 cells with full 13 + 11 masks, without a drop | 0 disagreements |

**GO** if G1–G3 all pass. Otherwise **NO-GO**: K4 is not run and nothing is recorded.

**Gate budget:** 1,800 s / 1,800 s / 2,048 MiB.

## 4. Target (`r117/run_target117.py`; only after the gate's GO and its freeze are pushed)
**Inputs:** K4 (sha256 2797de14…) and **200** letter-shuffles of K4 (seed 1170400), all with the same 24 published
letters in place.

**Computation.** All 768 cells per input, processed over 3 worker processes. The results are independent of the
worker count and kept in input order.

**Written:**
- **for every input:** the number of cells per verdict, for each key structure;
- **for K4 only:** the 768 per-cell verdicts.

**Target budget:** 7,200 s / 7,200 s CPU (aggregate) / 2,048 MiB, zero retries. The dev estimate is about 3,300 CPU
seconds.

**Decision** (`r117/evaluate117.py`, from the frozen aggregates only):
- Each K4 cell is reported as **EXCL_DROP**, **EXCL** (exact only) or **OPEN**.
- **The family verdict is:**
  - **EXCLUDED_DROP** if all 768 cells are EXCL_DROP;
  - **EXCLUDED_EXACT** if every cell is excluded;
  - otherwise **PARTIAL**, with the OPEN cells listed.
- **LEAD flag:** set if K4's number of OPEN cells is greater than in every one of the 200 shuffles. That is a stop
  condition: report it. It is not a plaintext.
- **Against R108:** every cell R108 excluded that R117 leaves OPEN, which only same-column branches can explain. The
  count of cells at each level in both rounds.

**Post-freeze cross-check** (`r117/crosscheck117.py`, 3 workers):
- The brute-force reference recomputes every K4 cell's exact verdict, and every K4 cell's DROP verdict among cells
  the reference finds excluded.
- It works from the frozen inputs.
- **Budget:** 7,200 s / 7,200 s CPU / 2,048 MiB.
- **Any disagreement is a stop condition.**

## 5. What this cannot exclude
- OPEN cells.
- Same-column rules other than R98's "letters to the right".
- Errors at two or more crib pairs.
- Structured non-periodic keys, other than the any-key cell.
- Other digraphic rules.
- Transposition, insertion or deletion layers. Routes are F2's rounds.
- Masks under reading B.

## 6. Order
1. This file, `QA_MANIFEST.json`, `PROTOCOL.sha256` and `budgets/`, pushed alone.
2. Source and `SOURCE.sha256`.
3. The gate, then `holdout/GATE_FROZEN.sha256` and the manifest's GO, pushed.
4. The target, then `k4/FROZEN.sha256`, pushed.
5. The evaluation and the cross-check, then the result note.
