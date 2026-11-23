# R93 independent-model exact review plan (Claude Code reviewing ChatGPT's R93)

Reviewer: Claude Code, a different model from R93's builder (ChatGPT).
Baseline: `e359ee59` (main after PR #107).
Mode: **POST-FREEZE, CRIB-ASSISTED, AGGREGATE-ONLY EXCLUSION REVIEW**.

**Why now.** This is the "Now — separate reviewer" item of `audit/RESEARCH_CHARTER.md` §6.1 and Priority 1 of
`audit/reviews/NEXT_STEPS_AFTER_R94.md`: L182 needs a different-model re-derivation before promotion. Tyler: "Can you
run the next steps based on the new plan" (23 Nov 2026). R95, the other "now" item, is assigned to ChatGPT and is not
touched here.

**Order.** Every step is a separate commit, pushed and checked on the remote before the next:
1. this plan and its budgets;
2. the review source and its hashes (`SOURCE.sha256`);
3. the synthetic correctness and throughput gate (no K4 data), with its result;
4. the single target replay;
5. the signed review and, only if every check passes, a narrow promotion of L182.

No frozen R93 file is changed. Nothing produced here enters RX2, R95 or any blind search.

## 1. The finite claim under review (L182)
- **Model:** a single rotor with any wiring W of 26 contacts.
- **Contacts:** input and output alphabets independently AZ, KRYPTOS, PALIMPSEST or ABSCISSA (keyword first, then the
  rest of A–Z): 16 pairs.
- **Schedule:** s_i = d·⌊(i + r)/n⌋ with i from 0, **n 5–96, r 1..n−1, d ±1**.
- **Encryption:** c_i = E_out[(W[(E_in.index(p_i) + s_i) mod 26] − s_i) mod 26].
- **Count:** 16 × 2 × Σ(n − 1) = **145,728 labels**.
- **Inputs:** the frozen 201 inputs `r93/k4/INPUTS.tsv` (K4 + 200 shuffles) and the 24 published observations.
- **Claim:** every input has zero labels compatible with all 24 observations (EXACT), and zero compatible with any one
  observation omitted (DROP).

## 2. Independent derivation and code path
I write the review from the pre-registration's model text and my own proof. I do **not** read `checker93.cpp`,
`reference93.py`, `validate93.py` or `runner93.py` before my source is published. The review imports no R87, R92 or
R93 code.

**Proof.** A setting fixes, at each observed position, x_i = (E_in.index(p_i) + s_i) mod 26 and
y_i = (E_out.index(c_i) + s_i) mod 26, and demands W[x_i] = y_i.
- Some permutation W does this iff the relation {(x_i, y_i)} is a partial bijection: equal x imply equal y, and equal
  y imply equal x. Any partial bijection extends to a permutation by pairing the unused inputs with the unused outputs
  in any order.
- s_i depends only on i. So one wrong published plaintext letter, or one ciphertext substitution at an observed
  position, changes exactly one pair. A substitution elsewhere changes none.
- So DROP-infeasibility (no single omission yields a partial bijection) excludes each single-error model.

**Different formulation.** R93 uses a pairwise conflict graph and intersects edge endpoints to evaluate all omissions
at once. This review instead:
- builds forward and backward contact tables directly for the full observation set;
- **re-checks each of the 24 omissions from scratch** (brute force, 25 partial-bijection checks per label and input);
- computes the offsets by **counting step events** (s steps by d at each position k ≥ 1 with (k + r) mod n = 0), not
  by the floor formula. The two are compared in the gate.

The checker is C (`check93r.c`), driven by Python (`review93.py`). Toy and plant oracles are separate Python code.

## 3. Synthetic gate (before the target is read; `SYNTHETIC_BUDGET.json`: 180 s wall, 120 s CPU, 512 MiB)
| Check | Pass condition |
|---|---|
| T1 Toy complete-key oracle | For moduli q = 2, 3, 4, 5, exhaustively enumerate every list of contact pairs in Z_q × Z_q: q 2 lengths 1–6, q 3 lengths 1–4, q 4 lengths 1–3, q 5 lengths 1–3 (33,483 lists). The C checker's EXACT flag and all omission flags must equal brute force over all q! permutations, with zero disagreements |
| T2 Schedules | Step-counting offsets equal d·⌊(i + r)/n⌋ for all 9,108 clocks × 97 positions. Recount: 145,728 labels; distinct 97-position clock sequences mod 26; overlap with R87 zero-phase clocks (n 1–96) and R92's clocks. These must equal R93's published accounting (4,690; 75,040; 94; 1,504; 36,096; 73,536; R92 overlap 0), or the difference is reported |
| T3 Plants at every label | One 97-symbol plant per label, **all 145,728** (seed 931101): random wiring, plaintext and 24-position observation mask (always containing positions 0 and 96 and one step boundary), enciphered by a separate Python forward cipher. The true label must be EXACT-feasible, with a 97/97 round trip |
| T4 Error plants (every 16th label, 9,108) | (a) one observed plaintext letter changed and re-enciphered: that omission feasible. (b) a ciphertext substitution at an observed position: that omission feasible. (c) a ciphertext substitution off the mask: EXACT feasible |
| T5 Second implementation | A pure-Python dictionary checker equals the C checker on 4 random ciphertexts × 3,000 random labels, every flag |
| T6 Sensitivity and throughput | Full 145,728-label C scans of 3 random synthetic inputs (seed 931102) plus 1 input planted at a random label. The planted input must report that label EXACT- and DROP-feasible (so the scan can report positives). Forecast for the 201-input target, from twice the measured per-input wall and CPU × 201 + 10 s, must be < 80% of the target caps (1,440 s wall, 960 s CPU) |

**Outcomes.**
- Any mismatch is NO-GO: no target run, and it is reported.
- Infrastructure or budget failure is INCOMPLETE.
- Neither is retried silently. A repair is an additive amendment with a new gate.

## 4. Target replay (once, after the gate's GO is pushed; `BUDGET.json`: 1,800 s wall, 1,200 s CPU, 512 MiB; zero retries)
**Provenance checks first:**
- `r93/k4/INPUTS.tsv` sha256 fbc28710…;
- its K4 row equals `r39/ic_gate/k4_ciphertext.txt` (sha256 2797de14…, stripped);
- the 24 observations are parsed as a literal (`ast`, no import) from `r73/sealed/reveal_k4.py` (sha256 63121cea…):
  24 unique in-range positions;
- the 200 shuffles are distinct, frequency-preserving and ≠ K4, and are regenerated byte for byte by the registered
  procedure (`random.Random(930400)`, list shuffle, reject the original and duplicates, cap 10,000).

**Then** the full scan of 201 × 145,728 = 29,291,328 setting/input calls, each with 25 partial-bijection checks
(732,283,200 omission decisions plus 29,291,328 EXACT decisions).

**Per input, only:** EXACT-feasible labels, labels with some feasible omission, and label/omission pairs, compared with
`r93/k4/AGGREGATES.json`.

**No output** of any plaintext, wiring, feasible-label list, ranking or score.

## 5. Decision
| Finding | Action |
|---|---|
| Gate GO, provenance checks pass, every per-input count equals R93's (all zero) | Promote **L182's finite exact exclusion only** to INDEPENDENTLY VERIFIED, with a signed review and `Promotes: L182` |
| Any disagreement | Preserve everything, write an additive erratum, no promotion; the affected claim is OPEN |
| INCOMPLETE | No promotion; report what is missing |

**Not reviewed:**
- R93's blind status (it has none);
- R87's remaining labels;
- other alphabets, step sizes, n ≥ 97, multiple rotors, irregular clocks, transposition, insertion or deletion, or
  simultaneous errors.

Same-model subtasks are one review.
