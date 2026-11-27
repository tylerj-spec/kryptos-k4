# R108 pre-registration (Claude Code, 27 Nov 2026): Slidefair with free alphabets and a periodic key, exact crib check on K4

**Mode: CRIB_ASSISTED / AGGREGATE_ONLY / EXCLUSION_ONLY.** It decodes nothing and completes no key. Its only output
is one verdict per (convention, period) cell.

**Approval:** Tyler, 27 Nov 2026: "Do the 4 proposals then we'll do the audit". This is proposal P4 of
`audit/ROLLING_QUEUE.md`.

**Dependency:** R107 (L195, unaudited, audit batch C) supplies the check. This round's own gate (§3) re-verifies
everything the check relies on, so the exclusions do not rest on R107's unaudited claims.

**Independent review: NONE** (one model). R108 belongs to audit batch C.

## 1. Model (exact)
**The cipher.** ACA Slidefair as in R98 (`r98/slidefair98.py`):
- **16 conventions:** Vigenère/Variant or Beaufort slide × role order × output order × pair parity.
- **Same-column rule:** "letters to the right".

**Alphabets.** PA and CA are **free**: any two of 26!.

**Key.** One value per pair, periodic over the pair index with period **p ∈ {1, …, 47}**, or **any key**: one free
value per pair, which is the same as every p ≥ 48 because no parity has more than 48 pairs.

**Plaintext.** The 24 published letters are taken in place and in the carved order. They are read from the `CLUES`
literal of `r73/sealed/reveal_k4.py` (sha256 63121cea…).

**Scope:** 16 conventions × 48 key structures = **768 cells**, each covering every PA, CA and key of that structure.

## 2. The check
The check is X107, `r107/x107.py`, unchanged (sha256 in `PROTOCOL.sha256`). It uses only crib pairs with both
plaintext letters published: 11 per parity. A branch is excluded if either holds:
- some kept pair has its upper output letter equal to its upper input letter (impossible in Slidefair); or
- the homogeneous linear system mod 26 for the kept pairs forces two letters of one alphabet to collide.

**Verdicts per cell:**

| Verdict | Meaning | When it is a valid exclusion |
|---|---|---|
| **EXCLUDED_DROP** | Excluded even with any one crib pair set aside | Covers one wrong letter, one wrong ciphertext letter, or a same-column pair (any rule) at one pair |
| **EXCLUDED_EXACT** | Excluded only with every crib pair kept | Only if all 22 letters of the crib pairs are right and no crib pair is same-column |
| **OPEN** | Not excluded | It is not a consistency proof |

## 3. Sealed synthetic gate (`r108/gate108.py`; reads no K4 file and no published letter or position)
**Seed:** 1080901.

**Masks:** two random non-overlapping windows of 13 and 11 letters (as R102 C5 and R107), not the K4 positions.

| Check | What | Pass |
|---|---|---|
| V1 structure | Against `r98/slidefair98.py`, over 200 messages with free alphabets, all 16 conventions and periodic keys p 1–12: round trip, letter identity, the per-pair equations, and the reciprocal pair map | 0 failures |
| V2 soundness | 400 masked Carter plants with free alphabets; conventions cycling; p cycling over {1, …, 12, 16, 24, 36, 47, any}. No EXCLUDED_* verdict without a same-column crib pair, and no EXCLUDED_DROP with fewer than two | 0 failures |
| V3 two implementations | X107 against `r107/ref107.py` (the rank test). Every V2 cell, plus 4 random messages × 16 conventions × all 48 key structures | 0 disagreements |

**GO** if V1–V3 all pass. Otherwise **NO-GO**: K4 is not run and nothing is recorded.

**Gate budget:** 1,800 s / 1,800 s / 2,048 MiB.

## 4. Target (`r108/run_target108.py`; only after the gate's GO and its freeze are pushed)
**Inputs:** K4 (sha256 2797de14…) and **200** letter-shuffles of K4 (seed 1080400), all with the same 24 published
letters in place.

**Written for every input:** the number of cells per verdict, for each key structure.

**Written for K4 only:** the 768 per-cell verdicts.

**Target budget:** 1,800 s / 1,800 s / 2,048 MiB, zero retries. The estimate is about 500 s.

**Decision** (`r108/evaluate108.py`, from the frozen aggregates):
- Each K4 cell is reported as **EXCL** (EXCLUDED_DROP), **EXCL_EXACT_ONLY** or **OPEN**.
- **LEAD flag:** set if K4's number of OPEN cells is greater than in every one of the 200 shuffles. K4 would then fit
  the family unusually well. That is a stop condition: report it. It is not a plaintext.
- The family-level verdict is EXCLUDED only if all 768 cells are EXCL. Otherwise it is PARTIAL, with the excluded
  cells listed.

**Post-freeze cross-check** (`r108/crosscheck108.py`). The rank reference recomputes all 768 K4 cells from the frozen
inputs. Any disagreement is a stop condition.

## 5. What this cannot exclude
- Slidefair with a non-periodic but structured key, other than the "any key" cell.
- Another same-column rule at two or more crib pairs.
- Errors at two crib pairs.
- Other digraphic rules.
- Transposition, insertion or deletion layers.
- Any OPEN cell.

## 6. Order
1. This file, `QA_MANIFEST.json` and `PROTOCOL.sha256`, pushed alone.
2. Source and `SOURCE.sha256`.
3. The gate, then `holdout/GATE_FROZEN.sha256` and the manifest's GO, pushed.
4. The target, then `k4/FROZEN.sha256`, pushed.
5. The evaluation and the cross-check, then the result note.
