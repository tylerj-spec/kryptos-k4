# R109 pre-registration (Claude Code, 27 Nov 2026): two-free-alphabet plaintext autokey, exact crib check on K4

**Mode: CRIB_ASSISTED / AGGREGATE_ONLY / EXCLUSION_ONLY.** It decodes nothing and completes no key. No witness
alphabet is written.

**Approval:** Tyler, 27 Nov 2026: "Do the 4 proposals then we'll do the audit". This is proposal P1 of
`audit/ROLLING_QUEUE.md`.

**Dependency:** R102's solvers (`r102/s3b102.py` primary, `r102/dfs102.py` second; L191, unaudited, batch B). This
round's own gate (§3) re-verifies them at the shape used here.

**Independent review: NONE** (one model). R109 belongs to audit batch C.

## 1. Model (exact; R102's family S3b)

    B⁻¹(C_i) = s1·A⁻¹(P_i) + s2·F⁻¹(P_{i−L}) + c   (mod 26),   i ≥ L

**Free:**
- **A and B**, any two of 26!;
- **F ∈ {A, B, AZ}**: the feedback letter is ranked in the plaintext alphabet, in the cipher alphabet, or straight;
- **the signs** (s1, s2) ∈ {±1}²;
- **c**, and the primer.

**Lags:** L ∈ {1, …, 96}.

**Plaintext:** the 24 published letters, in place, from the `CLUES` literal of `r73/sealed/reveal_k4.py` (sha256
63121cea…).

**Cells:** 96 × 4 × 3 = **1,152**. A cell has equations only where both P_i and P_{i−L} are published. Cells without
equations are reported as NO_EQUATIONS (no constraint).

## 2. The check
**Primary.** `s3b102.solve` (dmax 7) gives CONSISTENT, INCONSISTENT or UNDECIDED.
- INCONSISTENT means no bijective A and B and no c satisfy the linear congruences mod 26. It is decided by CRT:
  linear algebra mod 2 and mod 13, plus enumeration of the mod-13 solution space with the injectivity
  (two-per-residue) rule.

**EXACT verdict per cell:**
- the primary's verdict;
- a primary UNDECIDED goes to `dfs102.solve` (node cap 100,000), which may decide it;
- anything still undecided is **UNDECIDED**, counted as not excluded.

**Cross-check of every exclusion.** Each EXACT INCONSISTENT cell is also run through `dfs102.solve` (node cap
100,000).
- If the DFS returns CONSISTENT, that is a **disagreement**, which is a stop condition.
- If the DFS returns UNDECIDED, that is recorded.

**DROP verdict** (one published letter wrong, or one ciphertext letter wrong at a published position). It is computed
only for EXACT-INCONSISTENT cells:
- each of the 24 published positions is removed in turn, and the primary alone is re-run;
- **EXCLUDED_DROP** if all 24 variants are INCONSISTENT. An UNDECIDED variant counts as not excluded.
- Removing P_j removes every equation that uses P_j, which covers a ciphertext error at j.

**Chance comparison.** 20 letter-shuffles of K4 (seed 1090400), with the same published letters in place. Each is
scored by the **primary alone**, as the number of INCONSISTENT cells. K4 is also given this primary-only count, so the
two are comparable.

## 3. Sealed synthetic gate (`r109/gate109.py`; reads no K4 file and no published letter or position)
**Seed:** 1090901.

**Masks:** two random non-overlapping windows of 13 and 11 letters.

**Plaintexts:** Carter OCR windows without a published K4 word, with random A, B, F, signs, c and primer.

| Check | What | Pass |
|---|---|---|
| V1 soundness | 150 plants; L drawn from 1–12 and 30–52. The true masked hypothesis is never INCONSISTENT (primary or DFS), and every primary CONSISTENT witness re-encrypts | 0 failures |
| V2 one error | The same 150 plants with one masked letter replaced by a wrong letter: never EXCLUDED_DROP | 0 failures |
| V3 two solvers | 200 random masked hypotheses on random ciphertexts, random cells with equations | 0 disagreements where both decide, and ≥ 50% both decided |

**GO** if V1–V3 all pass. Otherwise **NO-GO**: K4 is not run.

**Gate budget:** 1,800 s / 1,800 s / 2,048 MiB.

## 4. Target (`r109/run_target109.py`; only after the gate's GO and its freeze are pushed)
**Written:**
- the per-cell EXACT verdicts, the DFS cross-check and the DROP verdicts for K4;
- the primary-only INCONSISTENT counts for K4 and for the 20 shuffles.

No witness and no alphabet is written.

**Budget:** 3,600 s / 3,600 s / 2,048 MiB, zero retries.

**Decision** (`r109/evaluate109.py`, from the frozen outputs):
- each K4 cell is **EXCL** (EXCLUDED_DROP), **EXCL_EXACT_ONLY**, **OPEN** (CONSISTENT), **UNDECIDED** or
  **NO_EQUATIONS**;
- the excluded (L, signs, F) cells are listed;
- **LEAD flag:** K4's primary-only INCONSISTENT count is below that of every shuffle, meaning K4 fits unusually well.
  That is a stop condition, to be reported. It is not a plaintext.

## 5. What this cannot exclude
- OPEN, UNDECIDED or NO_EQUATIONS cells.
- Two or more errors.
- A ciphertext not read in place, or any further layer.
- Other autokey forms: ciphertext autokey, or multiple lags.

## 6. Order
1. This file, `QA_MANIFEST.json` and `PROTOCOL.sha256`, pushed alone.
2. Source and `SOURCE.sha256`.
3. The gate, then `holdout/GATE_FROZEN.sha256` and the manifest's GO, pushed.
4. The target, then `k4/FROZEN.sha256`, pushed.
5. The evaluation, then the result note.
