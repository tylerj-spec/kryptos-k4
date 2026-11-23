# R96 work order (DRAFT for Tyler's approval): conditional recovery on the spent RX2-O panel

Affected ledger IDs: none (planning; a row is added only when R96 runs).
Validation: planning document. The figures quoted are from `r87/`, `r94/RESULT.md`,
`audit/reviews/r95_independent/REVIEW.md` and `audit/RESEARCH_CHARTER.md` §6.3.
Independent review: NONE (draft; the non-builder reviews the registration before execution).

**Status:** draft for Tyler's approval.
- **What happened:** R95 closed GO. The fixed order-5 objective ranks the true text above every below-95/97 one-swap
  neighbor in 47/48 spent cases (charter D-7).
- **What this is:** the next registered stage (charter §6.3): can a fixed optimizer with that objective recover the
  text when one of the two true wirings is supplied?
- **What Tyler must decide:** approve this work order (or amend it), and say who builds it. Nothing has been coded or
  run.

Type: **C, solver development** (synthetic, spent data; no K4).
Builder: Claude Code (proposed) | Breaker and auditor: ChatGPT (proposed; the different model) | Drafted: 23 Nov 2026.

---

## Family and scope (G0)
**Model: RX2-O** (`audit/backlog/multirotor/DESIGN.md`; frozen as in R94/R95). Zero-based positions i, contact indices
in Z/26:

    tau_i = floor((i + r)/n);   s1_i = d1·tau_i;   s2_i = d2·floor((tau_i + h)/26)
    encrypt:  m_i = W1(P_i + s1_i) − s1_i;        C_i = W2(m_i + s2_i) − s2_i
    decrypt:  m_i = V(C_i + s2_i) − s2_i;         P_i = U(m_i + s1_i) − s1_i      (U = W1⁻¹, V = W2⁻¹)

P and C are numbered by each record's input/output alphabet (AZ/KRYPTOS/PALIMPSEST/ABSCISSA).

**Worked example** (R95's): W1 = [1,0,2], W2 = [2,0,1], n = 2, r = 1, h = 1, d1 = d2 = 1, identity contacts.
- The fast shifts are 0, 1, 1 and the slow shifts 0, 0, 0.
- Plaintext [0,1,2] enciphers to [0,0,2], and the inverses recover it.

**Catalogue.** The 48 spent cases of `r94/inputs/PANEL.tsv` / `PANEL_TRUTH.json`: 6 per turnover cell, in ID order,
and the same panel as R94/R95. Each has two conditions:

| Condition | Supplied | Searched | What it reduces to |
|---|---|---|---|
| **true-V** | ciphertext, structural label, the true V | U (26! orderings) | m is known exactly, so this is R87's single stepping rotor with a known output sequence. R87's annealer solved that problem (L176 development and gates) |
| **true-U** | ciphertext, structural label, the true U | V | within each slow-rotor segment, V acts as a fixed substitution on the shifted ciphertext contacts, composed with the known fast rotor. The segments are linked by known shifts |

That gives **96 conditions per version**.

**Equivalence.**
- Unused contacts are not identifiable. A recovered wiring is scored on the text, and on agreement over the contacts
  the message actually uses.
- Same-plaintext aliases (R95 found 15 at the true keys) count as correct text.

**Left OPEN:** both wirings unknown; unknown structure; fresh texts; masking or misspelling; every K4 question.

## Why this stage (charter §6)
- **Q1:** it tests whether R95's objective GO is usable. R94 showed that conditional recovery failed under its order-4
  objective and optimizers: 0/48 in both conditions. The truth outscored the found states in 42/48 (true-U) and
  45/48 (true-V) cases, which is mostly a search gap.
- **Q3:** it is the second rung of the registered capability ladder: objective → conditional → joint → fresh gate.
- **Decision test:**
  - *Pass:* draft the joint stage (both wirings unknown, structure supplied) as its own work order.
  - *Fail:* stop the RX2-O solver line until a materially different method exists. Even one known wiring would not be
    enough with this objective and these optimizers.

  The two outcomes lead to different actions, so the test is satisfied.
- **Budget rule:** RX2-O has had R94 (main) and R95 (objective follow-up). A third step needs new evidence, which is
  R95's GO.

## Methods and power
**Objective (fixed; R95's).**
- The R59-builder K = 5 model, sha256 **e9c0848f…** (49,426,528 bytes).
- It is rebuilt from the pinned training file (sha256 871627e5…) by `audit/reviews/r95_independent/build_cr.py`, and
  must match that digest.
- Score: Σ_i log10 P(p_i | previous min(i, 4) letters), float32 table values summed in float64.
- No other model, cut or tuning.

**Inputs to the solver:**
- per condition: the ciphertext, the label and the one supplied true wiring;
- never the plaintext truth.

The evaluator opens the truth only after all solver outputs are written and hashed: R94's file-read-order convention,
plus a pushed freeze.

**Version 1 (runs first): simulated annealing over the one unknown inverse wiring.**
- **Starts:** R = 16 per condition, each a uniformly random permutation.
- **Seeds:** sha256("960101|case|condition|start"), first 15 hex digits.
- **Moves:** swap two entries.
- **Acceptance:** Metropolis, with linear cooling from T0 = 4.0 to 0.001 over I proposals.
- **Polish:** a greedy pass over all 325 swaps, repeated until none improves.
- **Retention:** every start's polished state. **Top-1** is the highest score; ties go to the lowest start index.
  The **8 best distinct decodes** are kept for recall.
- **I is fixed by a pre-registered rule**, before any panel output:
  - measure kernel speed on a synthetic random input (no panel data);
  - set I so that the forecast is 60% of version 1's CPU cap, rounded down to a multiple of 10,000;
  - if I is below 100,000, the stage is INCOMPLETE, with no other change.

  Expected I ≈ 200,000, about 3.2 M proposals per condition. R87 recovered 97/97 at the true setting with 480,000
  quadgram proposals.

**Version 2 (runs only if version 1 fails a bar; fixed now, not after seeing version 1).**
- The same objective, starts, seeds (prefix "960201"), retention and I rule.
- **Different search:** iterated annealing.
  - Each start runs version 1's schedule over I/2 proposals.
  - Then three rounds of: perturb the best state by 3 random swaps, and re-anneal from T0/4 over I/6.
  - Moves are swaps plus 3-cycles, half each.
  - Half the starts (8 of 16) begin at the exact order-1 assignment. That is the Hungarian solution to the
    unigram-assignment problem, as in R94's version A, with random tie-breaking by seed.
- A version passes only on its own. Cells or conditions are never combined across versions.

**Bars (per version; both conditions must pass):**
- top-1 decode ≥ 95/97 letters equal to the true plaintext in **≥ 44/48** cases per condition;
- **≥ 5/6** in each of the 8 turnover cells per condition.

**Reported, not gated:**
- exact 97/97;
- candidate recall (any of the 8 retained ≥ 95);
- used-contact key agreement;
- a per-case diagnosis: is the true text's score above the top-1 (a search gap), or is a wrong text above the truth
  (an objective counterexample)?
- a forward witness for every saved state.

**Nulls:** none. This is a truth-assisted development stage, not a gate. It has no false-alarm claim.

**Error classes:** none. The texts are exact. Masking and misspelling stay OPEN.

## K4 contact
None. No K4 input, shuffles or sandbox target. The contact index is unchanged.

## Budget (`audit/run_bounded_agg.py`; one worker; zero retries)
| Job | Wall | Aggregate CPU | Memory |
|---|---|---|---|
| Model rebuild and digest check | 120 s | 90 s | 512 MiB |
| Kernel self-tests and speed measurement (synthetic, no panel) | 120 s | 60 s | 512 MiB |
| Version 1: 96 conditions | 450 s | 450 s | 2,048 MiB |
| Version 2 (only if needed): 96 conditions | 450 s | 450 s | 2,048 MiB |
| Evaluation (opens truth after the freeze) | 120 s | 60 s | 512 MiB |
| **Work-order total** | **≤ 1,260 s** | **≤ 1,110 s** | — |

This sits inside the charter's 1,800 s / 1,800 s / 2,048 MiB development ceiling. It resets nothing from R94 or R95,
and nothing unused carries forward. Exhausted or crashed jobs are INCOMPLETE and are not retried.

## Order of work (each step pushed before the next)
1. This work order is approved by Tyler, with his words quoted. Then `r96/ROUND_CARD.md`, `r96/PREREGISTRATION.md`,
   `QA_MANIFEST.json` and `PROTOCOL.sha256`.
2. Source and hashes: kernel, solver, evaluator and a separately coded witness.
3. Model rebuild (digest e9c0848f…), self-tests, and the speed measurement that fixes I.
4. Version 1 run, then outputs frozen and pushed.
5. Evaluation, then the result. If version 1 fails a bar, version 2 follows, then its freeze, then evaluation.
6. Result note, ledger row, review note, and different-model review by the non-builder.

## Approvals and outputs
**Approvals needed:**
- Tyler's approval to register and run, quoted in the pre-registration. So far: "Yes, draft it" (23 Nov 2026), for
  this draft only.
- A choice of builder.

**Expected ledger row:** "R96 conditional recovery (type C, development)". The outcome is one of:
- **GO_FOR_JOINT_DEVELOPMENT** (a version passes both conditions);
- **SOLVER_NO_POWER** (both versions complete and fail);
- **INCOMPLETE**.

No exclusion and no K4 claim either way. RX2-O stays OPEN.

**Different-model review:** whichever model does not build it re-derives the recovery counts from the frozen outputs
and the truth.

## Not established by any outcome
- that a search finds the truth with **both** wirings unknown, which is the joint stage;
- unknown-structure performance or full-search throughput;
- performance on fresh texts, masking or a false-positive rate;
- anything about K4.

A pass is the second of four development rungs. The fresh full-pipeline gate is still required before any K4
contact.
