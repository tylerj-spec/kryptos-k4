# Aggregate resource wrapper for new rounds (audit/run_bounded_agg.py)

Affected ledger IDs: none (tooling). Responds to ChatGPT's R89 review, correction E (`r89/audit/REVIEW_20261121.md`):
the pinned `audit/run_bounded.py` limits memory per process and logs the leader's `ru_maxrss`, so a 4-worker run's
aggregate memory and CPU were never enforced or measured.
Validation:
- `python3 -I audit/tests/test_run_bounded_agg.py` passes:
  - three processes × 150 MB complete under a 2,000 MB budget, with a measured aggregate peak ≥ 400 MB;
  - the same job is killed under a 300 MB aggregate budget, which each process alone would fit;
  - two busy processes are killed at an aggregate CPU budget of 2 s;
  - the wall clock and a non-zero exit code are reported as INCOMPLETE.
- Checked by hand: two 1.5 s busy children measure 3.02 s CPU.
- **Semantics:** aggregate over the job's process group, with resident memory and CPU sampled every 0.25 s. The
  per-process RLIMIT_AS is kept. A spike shorter than one sample can be missed.
- The log keeps the `status`, `wall_seconds` and `max_rss_mb` fields that `audit/check_guardrails.py` reads.
  `max_rss_mb` is now the aggregate peak.
- `audit/run_bounded.py` is unchanged. Earlier rounds pinned it.
Independent review: NONE. One model (Claude Code) wrote and tested it.
