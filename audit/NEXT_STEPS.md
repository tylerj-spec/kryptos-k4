# Next steps after the November 2026 audit — work order for the executing agent

Written 15 November 2026 for an Opus-class agent working in Claude Code. Read this whole file before
doing anything. Do the tasks in order. Each task has a deliverable, a pass condition and a stop condition.

## Where things stand

- **No K4 solution.** Nothing has been sent to any external checker, and nothing may be without Tyler's go.
- The audit (`audit/historical/AUDIT_FINDINGS_AND_DECISIONS.md`) confirmed two defects:
  - **R83a / L172:** the "one published plaintext letter wrong" (DROP) test for PFX and WPX was unsound. It
    removed one equation but kept using the suspect letter to drive later state. The WPX DROP exclusion is
    withdrawn; 260 WPX settings survive a conservative necessary-only check (`r83/audit/ERRATUM.md`).
  - **R75 / L165:** the F1X solution counter multiplies in int64 and can overflow, then enter an unbounded
    enumeration (`r75/audit/ERRATUM.md`). Counts from that path are unverified.
- Independently re-derived and holding: L01–L04 and L167, within their stated scope.
- Everything else in the ledger is **unreplayed**, not wrong. Byte integrity is good: no hash mismatch among
  the 510 primary frozen files that could be identified; 43 of 43 preregistration-before-output checks pass.
- **A search hold is in force** (`audit/SEARCH_HOLD.md`). CI rejects new K4 files in any round.

## Rules for this work order

1. **No new search rounds and no new K4 candidates.** Do not create an `rNN/` directory. Do not delete
   `audit/SEARCH_HOLD.md`.
2. **Additive only.** Never edit or delete a frozen file, preregistration, protocol hash, solver pinned by a
   protocol hash, or an original result. New work goes in `rNN/audit/` or `audit/`. CI enforces this.
3. Every task below is a **post-freeze, crib-assisted audit**. Its code may read the published letters. It
   must never emit a decoded plaintext, complete a key, rank candidates, or feed anything to a blind solver.
4. **Independent code path.** Do not import from the round's original solver in the checker you write. Reading
   the original to understand the model is fine. Importing it in a test, to compare against, is fine.
5. **Counts are Python `int`.** No NumPy product or cumulative product for any count of solutions.
6. **Bounded runs.** Start every job that takes more than a few seconds through `audit/run_bounded.py` with an
   explicit budget. A killed or timed-out job is INCOMPLETE. Report it; do not turn it into a result.
7. **Toy oracle first.** Before a checker touches K4, it must agree with exhaustive brute force on small
   parameters, recover planted truths at the largest parameters, and survive the corruption test that matches
   the claim (a wrong **plaintext** letter for a plaintext-error claim, with the ciphertext re-encrypted from it).
8. **Ledger edits** need a new `audit/reviews/<name>.md` note with `Affected ledger IDs:`, `Validation:` and
   `Independent review:` lines, naming every changed row. State honestly who checked the work. One model
   playing three roles is "NONE".
9. Run untrusted or archived code with `python3 -I`. Follow `k4kit/CLAUDE.md` and `r53/BLIND_RULES.md`.
10. **Stop and report to Tyler** if: a checker disagrees with an archived result in a way that would reopen or
    close a ledger row; any K4 setting survives an exact check that shuffles do not reach; a task would need
    more than its budget; or anything here conflicts with a frozen file.

## Before starting: confirm the baseline is green

```bash
python3 -I audit/tests/test_guardrails.py
python3 -I audit/check_guardrails.py --base origin/main --head HEAD
python3 -I r53/tests/test_contract.py
python3 -I r75/audit/tests/test_f1x_safe.py
python3 -I r83/audit/plaintext_drop.py --synthetic        # needs numpy
python3 -I audit/historical/tests/test_scan.py
python3 -I audit/historical/postfreeze_baselines.py --postfreeze /tmp/baseline.json
python3 -I audit/historical/ciphertext_invariants.py /tmp/invariant.json
```

All eight passed on 15 November 2026. If one fails, fix nothing else until you know why.

## T1 — Exact one-wrong-plaintext-letter check for PFX and WPX (closes L172's open item)

**Why first:** it is the only place where a published exclusion was withdrawn, and 260 settings are in limbo.

- **Model definitions:** `r83/PREREGISTRATION.md`, `r83/DESIGN.md`, `r83/models83.py` (read only).
- **Write** `r83/audit/exact_drop.py`, standard library only. For each family setting and each of the 24
  published positions `i`, treat the plaintext letter at `i` as an unknown `x` in 0..25 and propagate it
  through **every** later equation it touches:
  - PFX (keyword + plaintext autokey, lag 1–12): the equations at `i` and at `i + lag`.
  - WPX (walking key stepped by the plaintext, ring 2–26): the pointer trajectory after `i`, recomputed for
    each `x`. Letters between published runs are unknown too; handle the pointer across the gap exactly as
    the family definition requires, and write down how.
  A setting survives if some `x` (other than the published letter, and separately including it) makes all
  remaining published letters consistent for some key.
- **Tests** in `r83/audit/tests/test_exact_drop.py`:
  1. Agreement with brute force over all keys on toy sizes (short texts, ring/keyword length ≤ 3).
  2. Planted 97-letter messages with one wrong plaintext letter at the first, last and an interior published
     position, at the largest parameters (m = 26, lag = 12). The true setting must survive.
  3. The two counterexamples in `r83/audit/plaintext_drop.py --synthetic` must survive.
  4. Random ciphertexts: survivor rate reported, to calibrate what "chance" looks like.
- **Run** on K4 and the 20 shuffles in `r83/k4/TARGET.tsv`, bounded. Write `r83/audit/EXACT_DROP.json` with
  per-position counts and settings (structural settings only; no decoded text).
- **Pass condition:** every exact WPX survivor on K4 is among the 260 necessary-only survivors. If not, one of
  the two checkers is wrong: stop and find out which.
- **Then:** report K4's survivor count against the shuffles using R83's LEAD rule unchanged (a K4 setting at
  effective strength ≥ 3 that no shuffle reaches). Update L172 with a review note. Expected outcome is CHANCE
  or EXCL; a LEAD is a stop-and-report event, not a finding.

## T2 — Replay R75's F1X feasibility, setting by setting (closes L165's open item)

- **Archived output:** `r75/k4/EXACT.json` (`K4.F1X` and 20 shuffles). R83a's F1X drop-one output is in
  `r83/k4/run/R83A.json`; its two problem jobs are shuffles NULL_010 and NULL_011 (`r83/RESULT.md`, "Run
  deviation").
- **Checker:** `r75/audit/f1x_safe.py` (`check_setting`, `enumerated_periods`). It already exists and has an
  exhaustive toy oracle. Write the driver `r75/audit/replay_f1x.py` that walks the same convention and period
  grid as the original (`r75/PREREGISTRATION.md`; `f1x` in `r75/sealed/exact.py`, read only).
- **Compare** feasible/infeasible for every setting on K4 and all 20 shuffles. Then compare solution counts
  wherever the archived count is present. Record every disagreement in `r75/audit/REPLAY_F1X.json`; do not
  resolve disagreements by editing anything old.
- **Must include:** periods 15–18 on both stages, and the period 17 + 17 settings of NULL_010 and NULL_011.
- **Pass condition:** feasibility agrees on every setting. Count disagreements are expected only where the
  true count exceeds 2^63; list them. Any feasibility disagreement is a stop-and-report event.
- **Then:** update L165's audit qualifier with a review note.

## T3 — Does L170 (R81a) share the R83a defect?

L170 also claims exclusion "with any one published plaintext letter wrong" (step G6). `r79/PREREGISTRATION.md`
line 45 says plaintext-driven state was deferred from R79, which suggests R81a's families have no
plaintext-driven state and the claim is sound. **Verify, do not assume:**

1. For each R81a family (H7CT_A, LIB_A, PROG_A, LIB_G4, and R79's H7CT, H7TXT, LIB, PROG), state in one line
   whether any later key or state depends on an earlier **plaintext** letter. Cite the line of
   `r81a/PREREGISTRATION.md` or solver source that shows it.
2. Check how `r81a/sealed/control_validate81.py` builds its "one-off" control: is the ciphertext re-encrypted
   from the altered plaintext, or is only the published letter changed?
3. If every family is plaintext-state-free, write that down in `r81a/audit/DROP_ONE_REVIEW.md` and stop. If
   any is not, write a synthetic counterexample test in the style of `r83/audit/plaintext_drop.py` and report.

Do the same one-paragraph check for any other ledger row that uses the words "one letter wrong", "drop-one"
or "set aside". Search `LEDGER.md` for them.

## T4 — Provenance loose ends (documentation only)

Write `audit/historical/PROVENANCE_NOTES.md` covering:

1. R64, R66, R68: the three development freeze manifests whose preregistration hash matches an **earlier**
   revision than the one present when the manifest was committed. For each: which revision the K4 run
   actually used, shown by commit hashes, and whether the difference between revisions touches parameters,
   cuts or scope.
2. The three R33 delivery manifest entries with no established introduction commit.
3. `k4kit/MANIFEST.sha256` listing itself. Note it as a known defect; do not "fix" the manifest.
4. The 101 unresolved primary hash references: resolve as many as possible by path search and report how
   many then verify. `python3 -I audit/historical/scan.py --out <dir>` writes `INVENTORY.json`.

## T5 — Source map for the 57 weakly sourced ledger rows (documentation only)

51 rows cite only a generic source tag and 6 have unresolved file references. Produce
`audit/historical/SOURCE_MAP.md`: one line per row with the script, result file and parameter bounds if they
can be found in the repository or `archive/`, else "NOT FOUND". Do not change any status.

## T6 — Independent replay of high-impact exclusions, highest risk first

One row per pull request. Same method every time: independent checker, toy brute-force oracle, planted
controls at maximum parameters, bounded run, comparison with the archived numbers, review note.

| Order | Row | Claim | Why it matters |
|---|---|---|---|
| 1 | L172 (rest) | R83a EXACT results for WPX, SLX, SLX-A, SSX, PFX, LX | Same code base as the confirmed defect. Replay a random 5% of settings per family plus all boundary sizes |
| 2 | L169, L170 | R79 / R81a crib-assisted exact exclusions, 2.51M and 1.85M settings | Recent, broad, and R81a reuses R79's C solver |
| 3 | L134, L135, L136 | R40–R42 "any plaintext / any cipher alphabet" exact rule-outs (3.4e8, 1.09e10, 1.71e8 settings) | Widest claims in the ledger. L136's blind gate failed (4/6); keep that separate from the exact check |
| 4 | L117 | R32 whole-family enumeration, 7.10e9 settings | Never independently enumerated (`AUDIT_NOTES.md`). Budget this first; if it does not fit, sample and say so |
| 5 | L164, L166 | R74X and R76 H1X/H2X/H2bX | Exact checks over large route sets |

For settings counts above about 1e9, preregister a sampling plan in the review note before running, and
report the result as "sampled replay", never as a full replay.

After each: use the vocabulary in `audit/FUTURE_TEST_GUARDRAILS.md` (EXACT_SCOPE_EXCL,
POSTFREEZE_CONDITIONAL_EXCL, STAT_NO_SIGNAL, SOLVER_NO_POWER, OPEN). Never promote a NO_SIGNAL to an exclusion.

## T7 — Low-power nulls

List every ledger row whose K4 result is NO_SIGNAL or STAT and whose synthetic gate failed, was not run, or
passed only on part of the parameter range (for example L136; L171's free-key lengths 8–12; L167's T-RK).
For each, state the range in which a null is informative. Output: `audit/historical/POWER_REVIEW.md`. These
are the families a future search may legitimately revisit.

## Not for the agent to decide

- Lifting the search hold, starting R80 or any new round, any external submission: Tyler.
- Multi-model review (the AgentCouncil workflow prepared in R82) has not been run. Until it has, every
  review note written under this work order says so in its `Independent review:` line.

## Reporting

After each task: commit, push, open a draft pull request, and tell Tyler in plain words what was checked, what
agreed, what did not, and what was not done. Update `CURRENT_STATUS.md` when a task changes the picture.
