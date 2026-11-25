# R101: L190, plaintext autokey on any single alphabet, EXCLUDED at lags 1–5

Affected ledger IDs: L190
Validation:
- **Order of commits:**
  - pre-registration 43be642, with `PROTOCOL.sha256`;
  - then source, Amendment 1 and `SOURCE.sha256` at 3a68187;
  - then the gate (seed 1010901) GO, frozen in 22d0a51;
  - then the target, frozen in 77986c7. That freeze was pushed and the remote blobs checked before evaluation.
- **Gate results:**
  - V1 400/400.
  - V2: 0 missed, 49/60 decided. This passes only under Amendment 1's bar of 40, set before the gate from
    development seeds.
  - V3: 28/32 decided by both solvers, 0 disagreements.
  - V4: 16/16 ACA Condi.
  - V5: 0/120 chance-feasible.
- **K4:** all 20 cells INFEASIBLE. The DFS second solver agrees 20/20.
- **Shuffles:** 0/20 with a feasible cell.
- **Resources:** all jobs COMPLETE under `audit/run_bounded_agg.py`, zero retries. Guardrail check PASS.
- **CI:** `.github/workflows/r101-freealpha.yml` re-checks every manifest, recounts all 21 frozen inputs, re-derives
  the shuffles and the decision, and runs the DFS solver on K4.

Independent review: NONE. One model (Claude Code) registered, built and ran R101. ChatGPT is the named
different-model reviewer.

## Summary
This is the exact half of shortlist S3, the plan's next unfinished item. Tyler's instruction, 25 Nov: "Stick with
the plan developed that is in git, we are good to continue with it".

**Cipher:** R99's keyed-tableau plaintext autokey with the alphabet free over all 26! orderings: y_i = s1·x_i +
s2·x_{i−L} + c, all ranks in one alphabet.

**Why the check is exact.** In rank space the recursion is linear. R99's chain links therefore become homogeneous
congruences in the 26 unknown ranks and c, and the question is whether some bijection satisfies them. Two exact
solvers decide it:
- one by CRT, a mod-13 projective enumeration plus GF(2) separation;
- one by depth-first search mod 26.

**Result:** **EXCLUDED** at lags 1–5 for every alphabet, every sign pair and every constant and primer. This covers
ACA Condi with any keyed alphabet.
