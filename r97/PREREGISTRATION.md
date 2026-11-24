# R97 pre-registration (Claude Code, 24 Nov 2026): joint recovery of both RX2-O wirings, structure supplied

**Type C, solver development.** Synthetic, spent data. **No K4 input at any stage.** Every result is labelled
**spent-panel development**.

**Approval.** Tyler, 24 Nov 2026: **"Your good for the next steps"**. That reply was to the post-R96 work queue
(`audit/reviews/POST_R96_NEXT_STEPS_20261123.md`, PR #113), whose next milestone is R97.
- Disclosed: the approval preceded this written pre-registration.
- The queue asks for owner approval of a separately specified pre-registration, and this file is that
  specification. It is published, with its source, before anything runs.

**Roles:** Builder Claude Code. The different-model reviewer is ChatGPT.

**Scope and throughput:** `r97/G0_FEASIBILITY.md`. Regardless of the outcome, there is no RX2-O fresh gate or K4 run
without a demonstrated structure-pruning method.

## 1. Question
With the structural label supplied and **neither** wiring known, can a fixed joint optimizer using R95's fixed
objective recover the plaintext?

## 2. Model, inputs, objective (as R96)
- **Model:** RX2-O as in R94–R96 (`r96/PREREGISTRATION.md` §2).
- **Cases:** the 48 records of `r94/inputs/PANEL.tsv` (sha256 9b3ed6b4…), in ID order.
- **Solver input:** `r94/inputs/PANEL.tsv` only: id, label and ciphertext. It holds no plaintext and no wiring. The
  solver never opens `PANEL_TRUTH.json`.
- **Objective:** the R95 order-5 model, digest **e9c0848f…**, rebuilt by
  `audit/reviews/r95_independent/build_cr.py`. Score: Σ T_k over the 97 positions, k = min(i + 1, 5).
- **Gauge:** (U, V) and (U(· − g), V(·) + g) decrypt identically for every g. Keys are compared up to this.

## 3. Building block: one conditional anneal
cond(fixed wiring, searched side, start, I, t_start, seed):
- **Start:** the given state, or, when none is given, a uniformly random permutation (Fisher–Yates on the kernel's
  xorshift64 stream from the seed).
- **Proposals:** I swap proposals. A pair x, y is drawn uniformly; x = y is skipped but counted.
- **Acceptance:** Metropolis at T = t_start·(1 − t/I) + 0.001.
- **Polish:** greedy over all 325 swaps, repeated until a pass makes no improvement.
- **Returns:** the polished state and its score.

T0 = 4.0. Seeds are int(sha256("<prefix>|<id>|<restart>|<tag>").hexdigest()[:15], 16).

## 4. Version 1 (runs first): alternating conditional optimization
Per case, **R = 6 restarts** (prefix "970101").
- **Initial V:** a random permutation from random.Random(seed(tag "V0")).shuffle. U is unset.
- **For rounds t = 1..4:**
  - **U-step** (V fixed):
    - a = cond(start none, I_c, T0, tag "U{t}a");
    - b = cond(start = current U at T0/4, or none at T0 when U is unset; tag "U{t}b");
    - U = the higher-scoring; a wins ties.
  - **V-step** (U fixed):
    - a = cond(start = current V, I_c, T0/4, tag "V{t}a");
    - b = cond(start none, I_c, T0, tag "V{t}b");
    - V = the higher-scoring; a wins ties.
  - Score (U, V). Keep the restart's best state over the rounds; the earliest round wins ties.
- **Top-1:** the highest-scoring restart final; the lowest restart wins ties.
- **Retained:** the 6 restart finals (recall is over these).
- **Cost:** 6 × 4 × 4 = 96 anneals per case, 4,608 in all.

**I_c (fixed by rule before any panel run).**
- `selftest97.py` measures s, the proposals per CPU second: the minimum of the two sides on synthetic input.
- I_c = ⌊0.6 × 700 × s / 4,608 / 10,000⌋ × 10,000.
- If I_c < 50,000: INCOMPLETE.

## 5. Version 2 (runs only if version 1 completes and fails a bar): iterated local search over alternation fixed points
Per case, **R = 3 restarts** (prefix "970201"); I_c the same.
- **Initial state:** V from tag "V0". Then 2 rounds exactly as version 1, giving the best state (U\*, V\*, s\*).
- **Then 4 kick cycles k = 1..4:**
  1. Copy the best state.
  2. **Kick:** choose 8 distinct V contacts with random.Random(seed(tag "K{k}")).sample, and shuffle V's values among
     them with the same generator.
  3. Then 2 rounds of single warm anneals:
     - U = cond(start U, I_c, T0/4, tag "K{k}U{t}");
     - V = cond(start V, I_c, T0/4, tag "K{k}V{t}").
  4. If the joint score exceeds s\*, it becomes the best.
- **Top-1 and retention** as version 1, over 3 finals.
- **Cost:** 72 anneals per case, 3,456 in all.

A version passes or fails on its own. Results are never combined across versions.

## 6. Evaluation (`evaluate97.py`; opens the truth only after the version's outputs are frozen and pushed)
Per case, from top-1:
- **letters**, and **recovered** at ≥ 95/97;
- **exact** at 97/97;
- **recall** over the retained finals;
- **key agreement up to gauge:** some g such that V_f(x) = V_t(x) + g on every used ciphertext-side contact, and
  U_f(y + g) = U_t(y) on every used plaintext-side contact;
- **diagnosis:** search gap, objective counterexample or alias, against the true text's score (ε 1e-9).

**Bars (version passes iff both hold):**
- recovered ≥ **44/48**;
- ≥ **5/6** in each of the 8 turnover cells.

**Witness** (`witness97.py`, separately coded, standard library): every retained final re-enciphers to the
ciphertext. Any failure is INCOMPLETE.

## 7. Truth-assisted diagnostics (`diagnose97.py`; after the last evaluated version; reported, never gated)
Prefix "970301", I_c the same. Per case:
- **D1:** from the true (U, V), one round: U = cond(start U_true, T0/4); then V = cond(start V_true, T0/4). Report
  the letters.
- **D2:** for k ∈ {4, 8, 12}:
  - U is the true U with k random swaps, from random.Random(seed(tag "D2k{k}")); V is random.
  - Run 2 rounds of: V = cond(start V, T0/4); U = cond(start U, T0/4).
  - Report the letters, and the share of cases at ≥ 95.
- **Cost:** 14 anneals per case, 672 in all.

## 8. Outcomes
| Result | Outcome |
|---|---|
| A version passes | **GO_FOR_FRESH_GATE_DESIGN**, which the post-R96 queue names. Per G0 that design is **blocked** until structure pruning is shown; the next work order is structure-pruning research |
| Version 1 and version 2 both fail | **SOLVER_NO_POWER** within these methods and budget. Stop the RX2-O solver line |
| A job crashes, exceeds its budget or fails the witness | **INCOMPLETE**. No retry, and version 2 does not run |

Every outcome leaves RX2-O OPEN, makes no K4 claim and excludes nothing.

## 9. Budget (`audit/run_bounded_agg.py`; one worker; zero retries; files in `r97/budgets/`)
| Job | Wall s | CPU s | MiB |
|---|---|---|---|
| Model rebuild | 120 | 90 | 512 |
| Self-tests and speed (fixes I_c) | 120 | 60 | 512 |
| Version 1 | 750 | 700 | 2,048 |
| Version 2 (if run) | 750 | 700 | 2,048 |
| Evaluation, per version | 120 | 60 | 512 |
| Diagnostics | 240 | 120 | 1,024 |

The maximum is 1,790 CPU s, inside the charter's 1,800 / 1,800 / 2,048 development ceiling.

## 10. Publication order (each pushed before the next)
1. This file, `G0_FEASIBILITY.md`, `QA_MANIFEST.json` and `PROTOCOL.sha256`.
2. Source and hashes.
3. Model rebuild and self-test, which fix I_c.
4. Version 1 run, freeze (`run_v1/OUTPUTS.sha256`), push.
5. Evaluation.
6. Version 2 run, freeze and evaluation, if needed.
7. Diagnostics.
8. Result note, ledger row, review note.

Independent review: NONE until ChatGPT's review.
