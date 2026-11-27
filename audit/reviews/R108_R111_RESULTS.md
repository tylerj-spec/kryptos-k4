# R108–R111: L196–L199, the four K4 proposals P1–P4 run before the batch-B audit

Affected ledger IDs: L196, L197, L198, L199

Validation:
- **Order of commits.** Each round has its pre-registration pushed alone, then its source, then its sealed synthetic
  gate and the gate freeze, then the K4 run and the K4 freeze, then the evaluation. The commit IDs are in each
  `rNN/RESULT.md`.
- **Resources.** Every K4 job ran through `audit/run_bounded_agg.py` and was COMPLETE within its registered budget,
  with zero retries.
- **Guardrail check:** PASS.
- **CI.** The workflows `r108-slidefair-free.yml`, `r109-s3b-exact.yml`, `r110-lagpair.yml` and
  `r111-blind-s105.yml` check every manifest and re-derive the frozen K4 outputs and decisions.
- **Amendments.** R109 has two pre-gate amendments, each approved by Tyler on 27 Nov 2026 before the gate ran:
  - Amendment 1: the primary solver's dmax goes from 7 to 5;
  - Amendment 2: the two-solver gate check counts decided cases rather than a share.

Independent review: NONE. One model (Claude Code) built and ran all four rounds. They open audit batch C.

## Approval and the dependency deviation
Tyler, 27 Nov 2026: "Do the 4 proposals then we'll do the audit".

**R111 (P3)** relies on R105's solver GO (L194). That GO is not yet independently verified. Under the rolling
procedure §3, R111 would have waited for the audit. It ran first on that explicit instruction, and its conclusion is
marked provisional.

**R108 and R109** reuse R107's check and R102's solvers. Both are unaudited, and each round's own gate re-verifies
the parts it relies on.

## Results
| Round | Proposal | Mode | Result |
|---|---|---|---|
| **R108** (L196) | P4 | crib-assisted, exact | Slidefair with **free** alphabets, all 16 conventions, keys periodic over pairs (p 1–47) or **any key**: **all 768 K4 cells excluded** at the exact level. **372 cells** are also excluded with one bad crib pair. 200 shuffles: median 136 cells open, and 48 shuffles also had 0, so this is not an anomaly. The rank reference agrees 768/768 |
| **R109** (L197) | P1 | crib-assisted, exact | See `r109/RESULT.md` |
| **R110** (L198) | P2 | blind, ciphertext only | Lag 1: **no signal** (p = 0.071). Exploratory lag 21: R_21 = 11 against 3.69 (p = 0.0013; Bonferroni over 24 lags, 0.032) |
| **R111** (L199) | P3 | blind | S105 on K4 at 20 cells (B ∈ {AZ, KRY}, L 1–5, both σ): **NO_SIGNAL**. The best cell scored −459.3, below 9 of the 15 shuffle maxima. The post-freeze clue check gave 1/24 for the top cell |

## Points for the auditor
1. **R108's exact-only cells.** These 396 cells assume that no crib pair is same-column and that the 22 crib-pair
   letters are correct. About 38% of true messages have a same-column crib pair. Only the 372 DROP cells survive one
   such pair.
2. **R110's lag-21 excess** is exploratory. Check it against the ledger's period analyses before any follow-up.
3. **R111's provisional status.** It inherits whatever the batch-B audit finds about S105.
4. **R109's amendments.** They were committed before the source and the gate, and Tyler approved each one at once.
   Check that both are conservative.
