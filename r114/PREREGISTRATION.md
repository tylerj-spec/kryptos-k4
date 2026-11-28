# R114 pre-registration (Claude Code, 27 Nov 2026): S105 validation on held-out text, balanced cells and full witnesses (P7; synthetic)

**Type: synthetic validation of R105's solver S105. No K4 input of any kind.**

**Approval:** Tyler, 27 Nov 2026: "Continue". The message re-states the quality review, whose table lists this
validation as the next step for the R105 solver. This is P7, the work order in
`audit/reviews/SOLVER_VALIDATION_PLAN_20261127.md`.

**Dependency.** R114 measures S105. It does not rely on R105's GO being correct, so it can run during the batch-B
audit. It changes nothing in S105: `r105/solve105.py` is used unchanged, and its sha256 is in `PROTOCOL.sha256`. Any
solver change it motivates is a new version with its own registration. Nothing is tuned to R111's K4 outputs.

**Independent review: NONE** (one model). R114 joins audit batch C.

## 1. Texts
- **TEST-C:** windows of the **second half** of the Carter OCR, starting at least 2,000 letters after the midpoint.
  R114's own development may use only the first half.
- **TEST-K:** windows of `k4kit/data/k1k3_plaintext.txt` (1,106 letters; out of style; never used to develop S105).
  Windows may overlap.

Both skip windows that contain a published K4 word.

**Limit.** S105's development in R105 drew windows from the whole Carter text, so TEST-C is fresh text but not
provably unseen. TEST-K is unseen by S105's development.

## 2. Arms and endpoints
| Arm | What | Size |
|---|---|---|
| **A1 balanced conditional** | S105 at the plant's own cell. B ∈ {AZ, KRY} × L 1–5 × σ ±1 = 20 cells, signs random within σ, random A, c and primer | **10 per cell = 200 TEST-C plants** |
| **A2 out of style** | As A1, on TEST-K | 40 plants (2 per cell) |
| **A3 quadgram sensitivity** | The first 60 A1 plants and all 40 A2 plants re-solved with a quadgram table built from the Carter **first half only** (counts, add-0.01 smoothing, log10, integer units of 10⁻⁴, as S105). The solver's table is swapped in memory | 100 |
| **A4 full search** | The R111 20-cell search on fresh TEST-C plants: is the true cell on top? | 12 plants (one cell group each, cycling) |
| **A5 decoys** | The same 20-cell search on: 4 uniform random strings; 4 letter-shuffles of A4 plants; and **4 two-free-alphabet autokeys** (B random, not on the list), which are R106's case | 12 |

**Witness for every output.** Emit the primer k_i = B⁻¹(C_i) − s1·A⁻¹(P_i) (mod 26), for i < L. Then forward-encrypt
**all 97** letters with `r100/autokey100.py`. **A failed witness voids that output's recovery** (fail closed).

**Endpoints per arm:**
- exact 97/97, ≥ 95 and ≥ 90, as counts with exact 95% Clopper–Pearson intervals;
- the letters-right distribution;
- the failure class of every miss:
  - lost at stage 1, 2 or 3;
  - annealer gap: the true plaintext scores higher than the output;
  - scorer counterexample: the true plaintext scores lower.

## 3. Registered bars (fixed now)
**VALIDATED** if all five hold:
1. **A1:** ≥ 90 recovery in ≥ 70% of the 200 plants, **and** in ≥ 5/10 in every one of the 20 cells.
2. **A2:** ≥ 90 recovery in ≥ 50% of the 40 plants.
3. **A3:** on the same plants, ≥ 90 recovery with the first-half table is within 15 percentage points of the result
   with the inherited table.
4. **A4:** the true cell is the top cell for ≥ 9 of the 12 plants.
5. **A5:** every A4 plant with ≥ 90 recovery scores above every decoy's top score.

Each failed bar is reported by name. **No bar can be changed after the run.** Exact-recovery rates are reported but
not barred: they are the primary development target, not a pass condition.

**Seeds:** plants 1140901, solver 1140902. **Budget:** two jobs under `audit/run_bounded_agg.py`, each 3,600 s / 3,600 s
/ 2,048 MiB, zero retries:
- Job 1: arms A1–A3, about 2,100 s;
- Job 2: arms A4–A5, about 2,500 s.

An INCOMPLETE job is a stop condition.

## 4. What follows
- **VALIDATED** supports using S105 in its tested scope: B on the list, L 1–5, F = A, English-like text. It does not
  verify R105's original GO, which stays with the batch-B audit.
- **Any failed bar** keeps R111's NO_SIGNAL as solver-limited and blocks broader S105 use until a new solver version is
  validated.
- **The A5 autokey decoys** show how S105 behaves when B is wrong, which bears on R106.
