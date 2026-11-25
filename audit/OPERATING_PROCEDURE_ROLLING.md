# Rolling experiment and audit procedure (adopted 25 Nov 2026)

**Adoption.** ChatGPT proposed this procedure on 25 Nov 2026. Tyler endorsed it the same day ("This seems like a
better approach for you to do more work"). It refines the work cadence of `audit/RESEARCH_CHARTER.md`, and does not
replace the charter, `r53/BLIND_RULES.md` or `audit/FUTURE_TEST_GUARDRAILS.md`.

## 1. What every experiment still does (never deferred)
- **Mathematical derivation and pre-registration**, committed and pushed before any source.
- **Positive and negative controls**: planted plaintext recoveries or plants, and shuffles or random inputs.
- **Blind integrity.**
  - Published K4 plaintext letters never generate, select, optimize or rank blind candidates.
  - Crib-assisted exact exclusions stay separate from blind recovery.
- **An independent checker or reference implementation**, run in the gate and, for K4, after the freeze.
- **Artifact freezes.** Gate and target freezes are pushed before evaluation, all jobs run through
  `audit/run_bounded_agg.py`, and a CI workflow recounts.

## 2. What runs on a cadence
| Activity | When |
|---|---|
| Different-model (ChatGPT) independent audit | Every 4–6 experiments, as a batch |
| Comprehensive ledger reconciliation | Every 10 experiments |
| Research-strategy reassessment | After each audit batch |

Claude Code may continue with approved, **independent** experiments while ChatGPT audits the previous batch.

## 3. The dependency rule
An experiment that relies on an **unverified** result from an earlier experiment waits until that result has been
independently reviewed. Examples of such results are an exclusion, a solver GO or an identifiability verdict. Each
work order lists its dependencies, and the rolling queue (`audit/ROLLING_QUEUE.md`) marks which are verified.

## 4. Mandatory stop conditions (interrupt the batch and ask for review at once)
1. A planted positive control is missed, or independent implementations disagree.
2. A pre-registered threshold needs changing. An amendment committed before its gate still counts and is reported
   at once.
3. A possible K4 plaintext emerges.
4. Published plaintext information may have contaminated a blind experiment.
5. A new experiment would depend on an unverified exclusion or solver result.
6. An experiment exceeds its registered budget.
7. Evidence suggests that earlier ledger entries are wrong.

Otherwise, Claude Code continues through the approved queue without asking again.

## 5. Approvals
- **A batch work order** (for example `audit/reviews/BATCH_WORK_ORDER_R102_R107.md`) is approved once. The
  experiments inside its scope then do not need separate approval.
- **Conditional items** in a batch run only when their registered entry conditions hold, and they are announced
  before they start.
- **No submission** to Paradigm or any outside checker without Tyler's explicit go.
- **The objective** is to identify the construction and recover K4, not to maximize the number of experiments.
