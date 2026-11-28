# R119 pre-registration (Claude Code, 28 Nov 2026): a K3-style route, then Slidefair with free alphabets, exact crib check on K4 (F2 rank 1; R73-class, exploratory)

**Mode: CRIB_ASSISTED / AGGREGATE_ONLY / EXCLUSION_ONLY / EXPLORATORY.** It decodes nothing and completes no key. Its
only output is one verdict per (route, convention, key structure) cell.

**Approval:** Tyler, 28 Nov 2026: "I approve all of them", answering the list of P6, P8, P9 and F2's route rounds. This
is rank 1 of `audit/reviews/F2_LAYERED_CATALOGUE_20261127.md`. L161 requires any run on these routes to be explicitly
exploratory, separately pre-registered and piloted. This file is the registration, and the sealed gate (§3) is the
pilot.

**Dependency.**
- X112 comes from R112 (L200). Its K4 behaviour in place comes from R117. Both are unaudited (batch C).
- The gate re-verifies X112 on routed plants.
- The shuffle null is R117's frozen one (§4).

**Independent review: NONE** (one model). R119 joins audit batch C.

## 1. Model (exact)
**The construction:** ct = π(SF(pt)).
- SF is ACA Slidefair as in R117: R98's 16 conventions; free PA and CA; a periodic key with p 1–47, or any key; every
  crib pair normal or same-column, in any number.
- π is a route with the convention CT[j] = X[π[j]].
- Decryption first undoes the route, X[π[j]] = CT[j], then applies X112 to X with the published letters in place.
  **The crib pairs are unchanged:** the route moves only ciphertext letters.

**Routes.** The **26 directed routes** of L161 with no documented run: the NEW and GENERATED_ONLY rows of
`r72/data/NOVELTY.json`.
- Each is rebuilt by `r72/reconstruct.py` (two same-direction quarter turns of a 98-cell sheet) and `r72/novelty.py`
  (extra cell removed, first or last; forward or inverse).
- Each must match its row's sha256 prefix. Any mismatch is a stop.

**Plaintext:** the 24 published letters, in place, from the `CLUES` literal of `r73/sealed/reveal_k4.py` (sha256
63121cea…).

**Scope:** 26 routes × 16 conventions × 48 key structures = **19,968 cells**.

**Masking scope:** valid under reading A only (F1 §2).

## 2. The check
X112 (`r112/x112.py`), unchanged, on the un-routed ciphertext. The verdicts are as in R117:
- **EXCL_DROP:** excluded even with one crib pair set aside;
- **EXCL:** excluded, but only with every pair kept;
- **OPEN:** not excluded.

## 3. Sealed synthetic gate, which is the pilot (`r119/gate119.py`; reads no K4 file and no published letter or position)
**Seed:** 1190901.

**Masks:** random 13 + 11 windows.

| Check | What | Pass |
|---|---|---|
| G1 routes | All 26 routes are permutations of 0–96 and match `NOVELTY.json`'s sha256 prefixes. Un-routing inverts routing on 100 random strings | 0 failures |
| G2 soundness | 260 masked Carter plants (10 per route), enciphered by `r98/slidefair98.py` (conventions cycling; half periodic with p cycling over 1–12, 16, 24, 36, 47 and any; half any-key with crib pairs forced same-column with probability 0.4), then routed. Un-routed and checked at the true cell, the plant is never EXCL. With one crib letter wrong, never EXCL_DROP | 0 failures |
| G3 two implementations | X112 against the brute-force `r112/ref112.py` on 52 routed plants (2 per route) at random cells with full masks. No drop | 0 disagreements |

**GO** if G1–G3 all pass. Otherwise **NO-GO**: K4 is not run.

**Gate budget:** 1,800 s / 1,800 s / 2,048 MiB.

## 4. Target (`r119/run_target119.py`; only after the gate's GO and its freeze are pushed)
**Input.** K4 (sha256 2797de14…) under each of the 26 routes. For a route, it computes the 768 cell verdicts and
writes them all.

**Null.** A fixed route applied to a uniform letter-shuffle of K4 is again a uniform shuffle. So **R117's 200 frozen
shuffle OPEN counts** (`r117/k4/AGGREGATES.json`, sha256 in `PROTOCOL.sha256`) are the null for every route. No new
shuffles are run.

**Target budget:** 1,800 s / 1,800 s / 2,048 MiB, zero retries. The estimate is about 360 CPU seconds over 3 workers.

**Decision** (`r119/evaluate119.py`):
- **Per route:** K4's EXCL_DROP / EXCL / OPEN counts, and the rank of its OPEN count among R117's shuffles.
- **Per route, the family verdict:** EXCLUDED_DROP, EXCLUDED_EXACT or PARTIAL, as in R117.
- **Overall:** "route then free-alphabet Slidefair" is **EXCLUDED_EXACT** for K4 if every route is EXCLUDED_EXACT or
  better.
- **LEAD flag:** set if any route's OPEN count exceeds R117's shuffle maximum (588). That is a stop condition: report
  it. Its family-wise false-alarm rate is up to about 13% (26 / 201), stated here in advance.

**Post-freeze cross-check** (`r119/crosscheck119.py`, 3 workers). The brute-force reference recomputes 312 K4 cells
drawn at random (seed 1190902; 12 per route): the exact verdict, plus the drop verdict where excluded. Any
disagreement is a stop condition. **Budget:** 3,600 s / 3,600 s / 2,048 MiB.

## 5. What this cannot exclude
- Routes outside the 26.
- Slidefair, then a route (F2 rank 2, which moves the crib pairs).
- Autokeys after a route (F2 rank 3).
- Other same-column rules.
- Two or more errors.
- OPEN cells.

## 6. Order
1. This file, `QA_MANIFEST.json`, `PROTOCOL.sha256` and `budgets/`, pushed alone.
2. Source.
3. The gate, its freeze, and GO.
4. The target and its freeze.
5. The evaluation, the cross-check and the result note.
