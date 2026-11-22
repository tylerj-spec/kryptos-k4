# R92 — L181: the 192 boundary-phase single-rotor labels: gate GO, K4 blind NO_SIGNAL, exact EXCL; and the RX2-O solver development stop

Affected ledger IDs: L181
Validation:
- **Pre-registration** 14494aa (`r92/PREREGISTRATION.md`, `r92/PROTOCOL.sha256`). It cites ChatGPT's work order
  (`audit/NEXT_STEPS.md`, Priority 2) and the refinement in this PR
  (`audit/reviews/NEXT_STEPS_REFINEMENT_20261122.md`). It discloses two departures:
  - the mode had a single-model review only;
  - the solver development run was over the synthetic-job budget.
- **Development** on spent books (`r92/dev/DEV.md`): 45/48, 0/150; nothing tuned. `python3 -I r92/tests/test_r92.py`
  passes. It includes schedule-equivalence accounting: no clock equals an R87 schedule (n 1–96) up to a constant.
- **Sealed gate** on four fresh genre books, with the truth committed only as a sha256 before the run: GO.
  - 47/48 ok, 44 exact;
  - setting 48/48;
  - masked 11/12;
  - 0/150 negatives confident.
- **Runs** under `audit/run_bounded_agg.py`: COMPLETE, 2 workers, about 2.56 GB aggregate. Witnesses 1,010/1,010 and
  1,005/1,005; determinism 8/8 twice.
- **Freezes** pushed before the truth (92ba8ed) and before any published letter (25026ff).
- **K4:** NO_SIGNAL, p_family 0.254, 0/24.
- **Exact:** EXACT and DROP both EXCLUDED (0 of 192 settings feasible), cross-checked by `rotor92.exact_check`.
- **RX2-O solver development** (`audit/backlog/multirotor/solver/RESULT.md`): stopped after version 3, as the work
  order requires.
  - v1 INCOMPLETE; v2 and v3 0/48 recovered.
  - Each version stayed within its 1,800 s / 1,800 s / 2,048 MiB budget, with every job logged.
  - No K4 and no fresh holdout were used.
- **CI** (`.github/workflows/r92-rxp.yml`) re-derives the witnesses, gate, evaluation, exact check and cross-check byte
  for byte, under the aggregate wrapper.
- Guardrail check PASS.

Independent review: NONE. One model (Claude Code) built and ran R92 and the RX2-O development. No `Promotes:` line.
