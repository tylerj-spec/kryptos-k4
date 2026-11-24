# R98 Amendment 1 (Claude Code, 24 Nov 2026): gate details fixed before the gate runs

**Committed with the source, before the gate (seed 980901) has run and before any K4 file or published letter is
read by R98 code.** The pre-registration is unchanged. This note makes it exact where it was loose, and records one
reduction.

## 1. V2 runs 30 inputs, not 60 (the one reduction)
**Kept from the pre-registration:**
- one 120-alphabet sub-tier: A–Z plus 119 alphabets drawn from the large tier;
- every one of the 16 conventions × 120² (PA, CA);
- a brute force that tries every κ per pair with the reference **encryptor** (`slidefair98.enc_pair`).

**Changed:** 30 inputs (15 planted, 15 random) instead of 60.

**Why.**
- A development timing (seed 7, not the gate seed) measured about 3 s CPU per input.
- 60 inputs would take about 180 s. With the other checks, the gate would reach about 205 s of its 240 s CPU cap, and
  an overrun is INCOMPLETE with no retry.
- With 30 inputs, a development smoke run (seed 4242; `dev/DEV_GATE_seed4242.json`) took 105 s.

**Inputs.**
- *Planted:* random conventions; PA and CA from the sub-tier (PA = CA in a quarter of them); 9- and 7-letter windows.
  In a third of them, one published pair is forced into the same column.
- *Random:* short windows (3 + 3, 5 + 3 or 5 + 5 letters), so that chance-feasible counts are non-zero and the
  counting itself is tested.

**Pass condition:**
- the oracle's (EXACT, DROP) equals the checker's **for every convention of every input**;
- at least 10 inputs have EXACT > 0.

## 2. Two counting paths; both are checked
- **Fast path (used by the target):** `checker98.scan_conv` encodes each (PA, CA) row's pair constraints once per
  convention. It derives every drop-one count from those shared codes.
- **Reference path:** `checker98._count`, applied once with all pairs and once per dropped pair, re-encodes the
  constraints each time.

**V2** compares both paths with the oracle.

**V5 adds a requirement:** on its three full-tier synthetic inputs, the two paths' aggregates must be identical. Any
difference is NO-GO.

The throughput forecast uses the fast path, which is the path the target uses. Codes are base-26 integers in int64,
so the checker refuses more than 13 pairs. K4 has 11 per parity.

## 3. V3 and V4 also check the full-tier count
Each plant is checked two ways:
- with the per-setting criterion (`label_feasible`);
- by requiring that the planted convention's full-tier count includes it: EXACT ≥ 1, or DROP ≥ 1 for the
  corrupted-letter plants.

**Corrupted-letter plants:** the corrupted letter is the first letter of a random published pair.

**Same-column plants:** one random *published* pair is forced into the same column.

**V1:** forces 3 random pairs into the same column in every third text.

## 4. The decision's "K4's count", made exact
- **K4's count** is its EXACT count if K4 has any EXACT setting, and otherwise its DROP count.
- A shuffle **reaches** K4 if its count of the same kind is at least K4's.
- **Decisions:**
  - **EXCLUDED** if K4 has 0 EXACT and 0 DROP;
  - **LEAD** if K4 has feasible settings and no shuffle reaches it;
  - **CHANCE** otherwise.

This is implemented in `evaluate98.py`, which reads only the frozen aggregates.

## 5. Fixed values and files
| Item | Value |
|---|---|
| Gate seed | 980901 |
| Gate budget file | `budgets/GATE_BUDGET.json`: 300 s wall, 240 s CPU, 1,024 MiB |
| Target budget | `QA_MANIFEST.json`: 1,800 s, 1,200 s, 1,024 MiB |
| Gate output | `holdout/CHECKER_GATE.json`; log `holdout/VALIDATION_RESOURCE.json`; freeze `holdout/GATE_FROZEN.sha256` |
| Target outputs | `k4/INPUTS.tsv`, `k4/AGGREGATES.json` (counts only); log `TARGET_RESOURCE_LOG.json`; freeze `k4/FROZEN.sha256` |
| Evaluation | `k4/EVALUATION.json`, committed after the freeze |

## 6. Development runs (disclosed; none touched K4 or a published letter)
**Development gate.** `dev/DEV_GATE_seed4242.json` and its log ran the gate code with development seed 4242.
- Every check passed (DEVELOPMENT_ONLY_GO).
- 105 s CPU; aggregate peak 103 MB.

**Synthetic rehearsal of the target.** `dev/smoke_target98.py` built a throwaway tree:
- the "ciphertext" is a Slidefair encryption (BEAU, r 1, o 0, a 0) of random text with two tier alphabets;
- the "clues" are that random text's letters at positions 21–33 and 63–73;
- the source constants were re-pointed at those synthetic files.

It then ran `run_target98.py` and `evaluate98.py` there (`dev/SMOKE_TARGET_EVAL.json`, `dev/SMOKE_TARGET_LOG.json`).
- The stand-in had EXACT 2 and DROP 24, in 2 conventions.
- All 200 shuffles had 0 and 0.
- The decision was LEAD.
- 271 s wall, 269 s CPU, peak 158 MB, under the target's 1,800 / 1,200 s caps.

This shows that the full pipeline finds a planted keyword-alphabet Slidefair on the registered positions, and that it
finishes inside the target budget.

Independent review: NONE (one model).
