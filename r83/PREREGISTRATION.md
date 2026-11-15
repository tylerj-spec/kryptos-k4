# R83a pre-registration (Claude Code, 14 Nov 2026): exact checks for four keyword families with no fixed period, F1X drop-one, and shifted clue positions

**Approval:** Tyler, 14 Nov 2026, on PR #79's proposal to run these exclusion-only checks before any blind solver: "I'd do R83a". His earlier rule for such checks: "You can do this check that you offered & im fine with us doing it in the future. Its just that if we get a possible solution, we will have to have legit proof that could be it before public submission".

**Label: CRIB-ASSISTED, EXCLUSION-ONLY.**
- The published letters enter only the algebraic checks.
- Nothing is decrypted, no key is completed and nothing is ranked. A feasible setting is reported as a count and a setting, never as a plaintext.
- Nothing is sent to any outside checker.

**Fixed by this commit** (`r83/PROTOCOL.sha256`): code, target, rules and what follows. Design and synthetic validation: `r83/DESIGN.md`.

## Question
Can a member of each family, with **any** key letters, encipher the published plaintext letters to K4's ciphertext letters at their positions?

Assumptions:
- in place (plaintext letter i is ciphertext letter i);
- K4 carved and transcribed correctly;
- the 24 published letters right.

The drop-one step relaxes the third assumption for one letter. The shift step moves one published run by up to two places.

## Families and settings (`r83/models83.py`, `r83/exact83.py`)
| Check | Family | Settings per ciphertext |
|---|---|---|
| LX | Linked key: one keyword of m = 2–20 letters in two stages on different tableaux. One stage (either) is rotated d = ±1 places per row of w = 2–48 letters; w = 97 is no rotation, a control that F1X covers | 26,624 conventions × 3,610 (rot, m, w, d) cells = 96,112,640 |
| PFX | Keyword (m = 1–26) + plaintext autokey, lag L = 1–12, feedback alphabet β, sign f | 256 × 312 = 79,872 |
| WPX | Walking key stepped by the plaintext, ring m = 2–26, step alphabet α, e ∈ {0, 1}, d = ±1; any start pointer | 12,800 |
| SLX / SLX-A | Per-slot progression `A[r] + j·B[r]` / `(j+1)·A[r]`, m = 1–26 | 832 each |
| SSX | Per-slot progression by the keyword re-enciphering itself on the tableau, m = 1–26 | 3,328 |
| F1XD | R75's F1X (`r75/sealed/exact.py` f1x(), unchanged; two periodic stages, any keys, periods 1–26 each, all four alphabets), with drop-one | 692,224 |

Alphabets on every side are A–Z, KRYPTOS, PALIMPSEST or ABSCISSA; every stage is additive or reverse; free keys.

## Target and steps (`r83/run83a.py`)
**Target:** `r83/k4/TARGET.tsv` (`r83/prepare_k4.py`, seed 830400). It holds the unchanged K4 ciphertext (sha256-checked) and 100 frequency-preserving shuffles; target sha256 dc2cc3b8e7004ba3bb471fd07d9df59aae2b3514c159a78bf2b7d239cc8f627f.

| Step | What | Ciphertexts |
|---|---|---|
| EXACT | every check above except F1XD | K4 + shuffles 1–20 |
| DROP | the same with drop-one: settings infeasible as they stand but feasible once one published letter is set aside | LX: K4 + shuffles 1–5. Others: K4 + 1–20 |
| SHIFT | EXACT with one published run moved by −2, −1, +1 or +2 positions (8 position sets; letters unchanged) | LX: K4 + 1–5. Others: K4 + 1–20 |
| F1XD | F1X with drop-one | K4 + 1–20 |

The published letters and positions come from `r73/sealed/reveal_k4.py` (0-based, 21–33 and 63–73).

## Statistics and verdicts (`r83/verdict83.py`)
- **checks:** independent equations beyond fixing the key (R75's count). For the graph checks LX and F1X this is edges − slots + components.
- **eff:** the effective strength, −log₂₆ of a setting's chance of being feasible on a random ciphertext. It equals checks for the slot checks. For the graph checks it is edges − slots, because every component has 26 tries at its free value.

Per step, family and position set:

| Verdict | Rule |
|---|---|
| **EXCL** | K4 has no feasible setting (DROP / F1XD: no drop-one-feasible setting) with ≥ 3 checks. Every setting with ≥ 3 checks is excluded, under the assumptions above |
| **LEAD** | Some K4 setting with eff e ≥ 3, while no shuffle of the same step on which that family ran has any at eff ≥ e |
| **CHANCE** | Otherwise. K4's feasible settings sit at levels the shuffles also reach. Every other setting with ≥ 3 checks is excluded; these stay open and are listed |

- **Confirming a LEAD from a 5-shuffle step** (LX's DROP and SHIFT): before it counts, that one step is run on shuffles 6–20 of the same target. It stays a LEAD only if none of those 15 shuffles has a setting at eff ≥ e either.
  - The reason: with 5 shuffles a chance LEAD can arise up to about 7% of the time per comparison (λe^(−5λ) ≤ 1/(5e)); with 20, at most about 2%.
- **What a LEAD is:** a reason for a new blind round of that one family and cell. That round gets its own pre-registration, a sealed synthetic gate, then K4 blind, and runs only on Tyler's go. A LEAD is never a solution, and no key is completed from it.
- **Multiple position sets:** SHIFT runs 8 extra position sets. A SHIFT LEAD is reported with that count, and the same confirmation applies.

## What follows (fixed now)
| Outcome | Next |
|---|---|
| EXCL or CHANCE everywhere | One ledger row (L172): the families excluded for every key, by cell, with the drop-one and shift results; the CHANCE settings listed as open. No blind solver is built for these families' decided cells |
| A confirmed LEAD | Reported raw. R83b: a blind round of that family and cell only, pre-registered, gated and run on Tyler's go |
| Weak cells (< 3 checks, or eff < 3: PFX lag ≥ 8; SLX m ≥ 11; LX's few cells at m 18–20) | Stated as not decided. Blind solvers per `r83/DESIGN.md` §4 if Tyler wants them |

## Synthetic validation (before this commit; no K4)
- **Unit tests** (`r83/tests/test_r83.py`), all pass:
  1. round trip;
  2. every check equals exhaustive key search through the explicit encryptor (92 comparisons, clean and with one letter changed);
  3. 20/20 plants;
  4. check table equals the engine;
  5. drop-one recovers 15/15 plants with one published letter corrupted, at that position.
- **Self-tests:**
  - `r83/results/SELFTEST.json`: 20/20 plants. On random ciphertexts, no feasible setting at ≥ 3 checks except 0–3 LX settings at exactly 5 checks (m = 20).
  - `r83/results/F1X_DROP_SELFTEST.json`: 3/3.
- **Dry run** of the runner and verdicts on synthetic letters (a per-slot-progression plant as "K4", 4 shuffles):
  - the plant was a LEAD at its own cell;
  - F1X drop-one and PFX drop-one read CHANCE once eff is used;
  - one chance LEAD (PFX, one shifted set, 1 setting at eff 3 against 4 shuffles at 0) showed why small nulls need confirmation, hence the rule above.

## Cost
About 3 hours on 4 cores. LX drop-one is the largest part, about 70 core-minutes per ciphertext.

## Not covered
- Several stages with transposition.
- A context-dependent pre-mask.
- Ciphertext errors away from the 24 positions (they do not enter these checks).
- Other carving orders.
- Keywords longer than each family's range.
- Lags above 12.
- Rotation steps other than ±1 per row.
