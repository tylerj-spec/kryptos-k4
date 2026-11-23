# R96 pre-registration (Claude Code, 23 Nov 2026): conditional recovery on the spent RX2-O panel

**Type C, solver development.** Synthetic, spent data, truth-assisted conditions. **No K4 input at any stage.**

**Approval:** Tyler, 23 Nov 2026: "I approve", for the work order `audit/reviews/R96_WORK_ORDER_DRAFT.md`. It is
reproduced as `r96/ROUND_CARD.md`.

**Roles:** Builder Claude Code. The different-model reviewer is ChatGPT, after the result.

This file fixes every parameter before any source is written. It refines the round card only by making it exact.

## 1. Question and stage
With the structural label and **one** true inverse wiring supplied, can a fixed optimizer using R95's fixed
objective recover the plaintext?
- **true-V:** V supplied; search U.
- **true-U:** U supplied; search V.

This is the conditional rung of charter §6.3. It runs after R95's objective GO (L184, charter D-7).

## 2. Model, inputs and objective
**RX2-O as in R94/R95.** Zero-based i:
- tau_i = ⌊(i + r)/n⌋;
- s1_i = d1·tau_i mod 26;
- s2_i = d2·⌊(tau_i + h)/26⌋ mod 26;
- decrypt: m_i = (V[(C_i + s2_i) mod 26] − s2_i) mod 26, then P_i = (U[(m_i + s1_i) mod 26] − s1_i) mod 26.

P and C are indices in the record's input and output alphabets (AZ, KRYPTOS, PALIMPSEST, ABSCISSA; keyword first,
then the rest of A–Z).

**Cases.** The 48 records of `r94/inputs/PANEL.tsv` (sha256 9b3ed6b4…), in ID order, under 2 conditions: **96
conditions**.

**Solver input.** `r96/inputs/CONDITIONS.tsv`, written from `r94/inputs/PANEL_TRUTH.json` (sha256 27aecaf0…) before
any solver code runs. Each row holds the id, condition, label, ciphertext and the supplied inverse wiring, and
**nothing else**. The solver never opens `PANEL_TRUTH.json`.

**Objective (R95's, fixed).**
- The R59-builder K = 5 model, sha256 **e9c0848f5e256814387968c09006a44804e90a72aeb79034d0b12abfcce31abd**,
  49,426,528 bytes.
- It is rebuilt by `audit/reviews/r95_independent/build_cr.py` from the training file (sha256 871627e5…). A digest
  mismatch is INCOMPLETE.
- **Score:** Σ_{i=0..96} T_k[code(p_{i−k+1..i})], with k = min(i + 1, 5) and T_k the stored float32 log10 tables,
  summed in float64.

## 3. Version 1 (runs first)
For each condition, **R = 16 starts**:
- **Seed:** int(sha256("960101|<id>|<condition>|<start>").hexdigest()[:15], 16).
- **Start:** a uniformly random permutation (Fisher–Yates from the seed's xorshift64 stream) of the searched inverse
  wiring.
- **Anneal:** I proposals.
  - Each proposal draws x, y uniformly from 0..25. If x = y it is skipped, but still counted.
  - Otherwise it swaps entries x and y of the searched wiring.
  - Acceptance is Metropolis at T = T0·(1 − t/I) + 0.001, with **T0 = 4.0**.
- **Polish:** repeatedly try all 325 swaps in order (x < y) and take each improving one, until a full pass makes no
  improvement.
- **Kept:** all 16 polished final states, with score, wiring and decode.
  - **Top-1** is the maximum score; ties go to the lowest start index.
  - **Top-8** are the 8 highest-scoring distinct decodes.

**I (fixed by rule, before any panel run).**
- `selftest96.py` measures s, the proposals per CPU second: the minimum over both modes on synthetic random inputs,
  with no panel data.
- I = ⌊0.6 × 450 × s / (96 × 16) / 10,000⌋ × 10,000.
- If I < 100,000: INCOMPLETE.
- I is written to `r96/selftest/SELFTEST.json` and frozen before the version 1 run.

## 4. Version 2 (runs only if version 1 completes and fails a bar)
The same objective, I, retention and top-1 rule. Seeds use the prefix "960201".
- **Starts 0–7: the exact order-1 assignment.** This maximizes Σ_i T_1[p_i] over the searched permutation, which is
  separable per contact:
  - true-V: cost[b][u] = Σ_{i: b_i = b} T_1[E_in(u − s1_i)], where b_i = (m_i + s1_i) mod 26;
  - true-U: cost[a][v] = Σ_{i: a_i = a} T_1[E_in(U[(v − s2_i + s1_i) mod 26] − s1_i)], where
    a_i = (C_i + s2_i) mod 26.

  It is solved exactly by the Hungarian method. Ties are broken by adding 1e-9·u to each cost, where u is uniform in
  [0, 1) from the start's seed. These starts begin their first phase at T0/4.
- **Starts 8–15:** uniformly random permutations, as in version 1, first phase from T0.
- **Schedule per start:**
  1. Phase 1: I/2 proposals, then polish.
  2. Then 3 rounds of: take the best polished state so far; apply 3 random swaps; anneal I/6 proposals from T0/4;
     polish; keep the state if its score is higher.
- **Moves** in every phase: a swap or a 3-cycle (x → y → z → x on the entries), half each.
- **Polish:** swaps only, as in version 1.

Version 2 passes or fails on its own. Results are never combined across versions.

## 5. Evaluation (`evaluate96.py`; opens the truth only after the version's outputs are frozen and pushed)
**Per condition and case, from top-1:**
- **letters** = positions where the decode equals the true plaintext (out of 97);
- **recovered** = letters ≥ 95;
- **exact** = 97;
- **recall** = any of the top-8 ≥ 95;
- **key on used contacts** = the found searched wiring equals the true one at every contact the message uses: the
  {b_i} for U, the {a_i} for V;
- **diagnosis**, from the true plaintext's score against top-1's (ε 1e-9):
  - *search gap* if the truth scores higher;
  - *objective counterexample* if a wrong text scores higher;
  - *alias* if the text is the same.

**Bars (a version passes iff all hold, for both conditions):**
- recovered ≥ **44/48** per condition;
- recovered ≥ **5/6** in each of the 8 turnover cells, per condition.

**Witness** (`witness96.py`, separately coded, standard library): every saved state's decode, re-enciphered with
(searched, supplied) wirings, equals the ciphertext. Any failure is INCOMPLETE.

## 6. Outcomes
| Result | Outcome |
|---|---|
| A version passes | **GO_FOR_JOINT_DEVELOPMENT**. The joint stage (both wirings unknown, structure supplied) needs its own work order |
| Version 1 fails and version 2 fails | **SOLVER_NO_POWER**. Stop the RX2-O solver line until a materially different method exists |
| Any job crashes, exceeds its budget or fails a witness | **INCOMPLETE** for that version: no retry, no version 2 run on INCOMPLETE |

Every outcome leaves RX2-O OPEN, makes no K4 claim and excludes nothing.

## 7. Budget (`audit/run_bounded_agg.py`; one worker; zero retries; budget files in `r96/budgets/`)
| Job | Wall s | CPU s | MiB |
|---|---|---|---|
| Model rebuild and digest check | 120 | 90 | 512 |
| Self-tests and speed (fixes I) | 120 | 60 | 512 |
| Version 1 | 450 | 450 | 2,048 |
| Version 2 (if run) | 450 | 450 | 2,048 |
| Evaluation, per version | 120 | 60 | 512 |

The total is at most 1,380 s wall and 1,170 s CPU with both evaluations. That is inside the charter's 1,800 / 1,800
/ 2,048 development ceiling.

This refines the round card's total of 1,260 s / 1,110 s, which counted one evaluation. The extra evaluation applies
only if version 2 runs.

## 8. Publication order (each pushed before the next)
1. This pre-registration, the round card, `QA_MANIFEST.json` and `PROTOCOL.sha256`.
2. Source, `CONDITIONS.tsv` and source hashes.
3. Model rebuild and self-test results, which fix I.
4. Version 1 outputs and freeze.
5. Version 1 evaluation.
6. Version 2 run and evaluation, if needed.
7. Result note, ledger row, review note.

Independent review: NONE until ChatGPT's review.
