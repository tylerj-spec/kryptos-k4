# Current K4 research status — 23 November 2026 update

**No independently verified K4 solution.**

**L182 (R93) is now independently verified.** Claude Code's different-model review is complete: charter §6.1, the
"Now — separate reviewer" item.
- A separately derived and coded checker reproduces every one of R93's 201 per-input counts. All are zero:
  - no setting of the 145,728 fits K4's 24 published letters;
  - none fits with any one letter set aside;
  - the same holds for all 200 shuffles.
- It also reproduces R93's scope accounting.
- Evidence: `r93/audit/independent_review/REVIEW.md` and `audit/reviews/R93_INDEPENDENT_REVIEW.md`.

**Coverage.** With L181, every nonzero step-boundary phase of the position-only single rotor is independently
verified as excluded through period 96. R87's 2,944 zero-phase labels with n 5–96 remain single-model, and are the
next item of the charter's Phase 1 backlog (L176).

**R95's score check is GO by independent replication (L184).** Tyler asked "Can you verify R95". R95's primary
evidence was lost with ChatGPT's workspace: 1 of 48 shards was published, and its verifier never ran. So Claude Code
rebuilt R95's registered model exactly and recomputed the registered endpoint with independent code.
- **Order-5 objective:** 1/48 cases have a below-95/97 one-swap neighbor above truth, against the bar of ≤ 2. The
  order-4 baseline gives 32/48.
- **Agreement:** the one recovered primary shard agrees 650/650.
- **What it permits:** only a separately specified conditional-recovery work order (charter §6.3). No K4 run.
- **R95 is CLOSED.** Tyler: "Yes, that is fine with closing 95" (`audit/reviews/R95_CLOSEOUT.md`). Its
  registration is kept verbatim in `audit/reviews/r95_independent/r95_registration_snapshot/`.
- **R96 conditional recovery PASSES (L185).** Tyler approved it ("I approve"). With one true wiring supplied, R95's
  objective and plain annealing recover ≥ 95/97 letters in 45/48 (true-V) and 47/48 (true-U) cases. Every turnover
  cell is ≥ 5/6.
- There are zero search gaps. The 4 misses are objective counterexamples.
- Outcome: GO_FOR_JOINT_DEVELOPMENT. The next rung (both wirings unknown, structure supplied) needs its own work
  order. No K4 run is authorized (`r96/RESULT.md`).

Everything below is the 22 November status, unchanged.

# Current K4 research status — 22 November 2026 (America/Chicago)

**No independently verified K4 solution. R92–R94 are closed at their recorded scopes;
R95's publication and verification chain is the active 25-meter milestone.**

**Governance:** PR #106 adopted `audit/RESEARCH_CHARTER.md` at `a8f29c0` on
22 November (America/Chicago). The reconciliation in
`audit/reviews/PR106_CHATGPT_RECONCILIATION.md` carries R95 into that plan and
corrects its input boundaries and claim limits. No guardrail, frozen evidence
or ledger row changes in this planning update.

The exact single-rotor record is stronger; the tested structural two-rotor
procedures remain unable to recover the practice texts. R95 tests one fixed
replacement score on spent practice data; it does not yet have a verified
scientific result in the published repository.

| Follow-up | Completed result | Evidence |
| --- | --- | --- |
| Independent R92 review | PASS. L181's finite exact exclusion independently verified, plus the registered 128 zero-phase labels through n=4; all 320 labels fail EXACT and every single-observation omission on 201 frozen inputs | `r92/audit/independent_review/REVIEW.md`, `audit/reviews/R92_INDEPENDENT_REVIEW.md` |
| Wider timing audit R93 | EXACT_SCOPE_EXCL for all 145,728 registered n=5..96 nonzero-phase labels, with any wiring, at all 24 observations or with any one omitted. K4 and all 200 shuffles have zero compatibility. Independent-model review NONE | `r93/RESULT.md`, L182 |
| Structural two-rotor development R94 | COMPLETE_DIAGNOSTIC / SOLVER_NO_POWER: A and B each 0/48 at >=95 letters, including all saved finals. Both one-true-wiring conditions also 0/48. Cipher family OPEN; no K4 run | `r94/RESULT.md`, L183 |

## Active work: finish the existing R95 evidence chain

The pinned branch `chatgpt/r95-fixed-score-challenge-20261122` at
[`8f59313`](https://github.com/tylerj-spec/kryptos-k4/commit/8f59313c7d4fa6327e0cee41a39f092ebbeb23aa)
contains R95's registration, source, verifier and interruption record, but
only one primary neighbor shard. Its complete evidence freeze and scalar
verification are not published. A later session reported recovery with
55/55 output and 22/22 source/input hashes matching and publication accepted;
that report must be reconciled with the remote artifacts before completion
or a scientific verdict is recorded.

R95 compares one fixed rebuilt order-five objective with the lower-order
baseline on the 48 spent R94 cases and all 31,200 legal one-swap neighbors.
Its endpoint is cases with **any** below-95/97 neighbor above truth; at most
2/48 is GO_FOR_CONDITIONAL_DEVELOPMENT, after complete verification. The
historical 25/48 saved-best figure is not this endpoint. A pass only supports
a separately registered conditional-solver proposal; the family remains OPEN.

Finish original evidence publication, the already registered scalar verifier
and the scoped closeout. Check for completed pending operations before any
invocation; preserve the one-primary/one-verifier, zero-retry limits. Missing
original evidence remains INCOMPLETE; no silent primary rerun. The verifier
is a second ChatGPT code path, not independent-model review. This task does
not discharge R93's separate different-model review. Exact remaining steps
and limits are in charter Section 6.2 and the pinned R95 work order.

## What the R92–R94 review establishes

The completed postrun checker verifies 74 artifact hashes, R93's source/gate/
freeze chronology and aggregate arithmetic, and R94's 999 new states, scalar
scores and witnesses, 31,200 true-key neighbors, 1,920 historical final-restart
witnesses, 768 ranked witnesses and 17 historical resource logs. It passed in
3.256 seconds wall/3.204 aggregate CPU with 29.2 MiB sampled aggregate RSS.
This is internal same-model review; it does not promote R93/R94 to
independently reviewed results or independently regenerate R93's full scan.
The signed review is `audit/rotor_followup/REVIEW.md`.

R92's saved gate is 47/48 at >=95/97, with 44/48 exact and 44/48 used-contact key
agreement. Its blind result remains NO_SIGNAL (50/200 shuffles at least as
high; add-one 51/201). Original optimizer/full-model rescoring and raw-book
freshness were not independently certified. The disclosed development overrun
remains a deviation.

R93 completes the recorded phase coverage of the same position-only single
rotor through period 96 when combined with R87/R92: 148,992 labeled settings.
That combined accounting does not independently review the remaining R87
results. The corrected deferred count was 145,728, not 145,920. Other alphabets,
stepping laws, multi-rotor constructions and wider error/alignment models
remain outside these exclusions.

R94 provides evidence against its order-four objective as well as its search:
39/48 true keys have a higher-scoring wrong local neighbor; 25 saved best
counterexamples fall below the >=95 recovery threshold. Even with one true
wiring supplied, the conditional searches have no >=95 recovery. The registered
finite loops reached their stopping conditions; their unused resource ceilings
do not authorize extra attempts.

## Next decisions

The active plan is `audit/RESEARCH_CHARTER.md` Sections 6.1–6.3, carrying
forward `audit/reviews/NEXT_STEPS_AFTER_R94.md` without changing its limits:

1. Finish and verify R95's existing fixed-score evidence chain as the immediate
   25-meter target. Record its actual outcome; do not infer GO from hash checks.
2. In parallel, obtain a different-model R93 exact review before promoting
   L182. Claude or a person must independently re-derive/replay ChatGPT's work.
3. Only after a verified R95 GO, prepare separately specified conditional and
   joint recovery work. Preserve >=44/48 recovery and >=5/6 in each turnover
   cell, then require a fresh full-pipeline GO before K4. These are development
   prerequisites, not evidence that the rotor family is K4's method.
4. Keep the unchanged R82/PTAK procedures and the completed RX2-O/R94 work
   orders parked. Avoid re-enumerating already-covered rotor labels. RX2-D
   remains design-only; RX2-O's failed recovery experiments do not test it.

The earlier R32/R41 replays, R90 independent review, R82/PTAK screens and
multi-rotor design work remain closed at their documented scopes
(`audit/backlog/CLOSEOUT.md`). Frozen work orders and original evidence remain
unchanged; scope/reporting corrections are additive.

The user explicitly approved the source and registered-result publication.
Source, gate and complete result freezes were published in order before their
dependent stages. Automatic publication-review blocks were resolved through
the recorded approval/provenance review; no alternate upload route was used.
The source/gate/result commits are 3e781d5, 2621a5e and 542165b. Current outcomes
supersede the historical pending-approval and unrun snapshots below.

## Historical status snapshots

The following sections are preserved as records of earlier stages. Their
pending/open-task language and earlier work-order priorities are historical.

# Current follow-up status — 21 November 2026 (America/Chicago)

**No independently verified K4 solution.** The R92 independent audit is complete.
The R93 wider timing audit and R94 structural two-rotor work are registered and
source-reviewed, but their formal runs have **not started**.

This is the prepared follow-up branch status. PR #104 remains the merged
baseline at `9e4bd400e64c6aa46ae3afdc9ba0d82a1a927fd1`; the new source/result
bundle and the ledger promotion below await publication approval and merge.

| Requested follow-up | Current outcome | Evidence |
| --- | --- | --- |
| Independent R92 review | PASS for the finite exact exclusion; L181 promotion prepared. All 192 R92 labels plus 128 registered R87 zero-phase labels through n=4 independently replayed on 201 frozen inputs; every exact and single-deletion result is zero | `r92/audit/independent_review/REVIEW.md`, `audit/reviews/R92_INDEPENDENT_REVIEW.md` |
| Wider timing range | R93 registered, source reviewed, NOT RUN. Correct remaining domain: 145,728 labeled settings, n=5..96 and nonzero boundary phases. Exact-checker correctness gate must pass and be published before the aggregate-only target audit | `r93/PREREGISTRATION.md`, `r93/MODE_CLARIFICATION.md`, `r93/EXECUTION_HANDOFF.md` |
| New structural two-rotor work | R94 registered, source reviewed, NOT RUN. Two finite versions on the existing spent 48-case panel, followed by explicitly labeled conditional diagnostics; no K4 authorization or fresh gate | `r94/WORK_ORDER.md`, `r94/audit/STATIC_SOURCE_REVIEW.md`, `r94/EXECUTION_HANDOFF.md` |

## Findings and active limits

R92's recorded recovery is 47/48 at >=95/97 letters, including 44/48 exact
texts and 44/48 used-contact key agreements. Its retained blind pipeline remains
NO_SIGNAL (50/200 shuffles at least as high; add-one 51/201). The independent
audit checked all 2,015 saved candidate witnesses, but did not rerun the original
optimization or full letter-model rescoring. The original development overrun
remains disclosed.

RX2-O with identity second wiring includes the phased single rotor, and distinct
clock schedules need not represent disjoint functions. The old v3 experiment
shows truth above its retained final states in 47/48 cases, not a global score
optimum. These corrections are additive; frozen original evidence is unchanged.

The prior R32/R41 replays, R90 review, R82/PTAK screens and multi-rotor designs
remain closed at the scopes recorded in the previous closeout. R82 and unchanged
PTAK remain parked. The superseded three-version RX2-O work order is complete.
R94 is the separately registered structural development attempt.

Automatic approval review has rejected publication of the new bundle as
potential sensitive egress. Repository/PR metadata and public blob checks
establish the destination and the already-public origin of copied practice
plaintexts/test keys; the rejection nevertheless requires explicit approval of
the exact public payload. No alternate publication route was used. R93/R94
execution remains paused because their registrations require source publication
first. See `audit/reviews/PUBLICATION_PROVENANCE_R92_R94.md` for the concrete
inventory and provenance.

## Historical status snapshots from main

The following sections are preserved as historical records. Their open-task
lists and current-work-order language are superseded by the table above.
The original UTC-dated headings are retained.

# Current K4 research status — 22 November 2026 update

**No independently verified K4 solution.** On 22 November (Claude Code, PR for branch `claude/zen-clarke-s6fwj5`),
both priorities of the work order below were taken to a terminal outcome:

| Work order item | Outcome | Evidence |
| --- | --- | --- |
| Priority 2: the 192 n<=4 boundary-phase single-rotor labels | Full strict-blind round **R92 (L181)**: sealed gate GO (47/48, 0/150); K4 blind NO_SIGNAL (p 0.254, 0/24); post-freeze exact check **EXCLUDED** (EXACT and DROP, 0 of 192 feasible), cross-checked. Single-model; nothing entered RX2 | `r92/RESULT.md` |
| Priority 1: RX2-O blind solver, at most 3 versions | **Stopped after version 3: SOLVER_NO_POWER on development data.** v1 INCOMPLETE (infrastructure), v2 0/48 (quadgram objective overfits), v3 0/48 (order-5 objective ranks the truth first, search never reaches it). No gate, no K4; RX2-O stays OPEN | `audit/backlog/multirotor/solver/RESULT.md` |

The refinement of the work order is `audit/reviews/NEXT_STEPS_REFINEMENT_20261122.md`. Everything below is the
21 November status, unchanged.

# Current K4 research status — 21 November 2026

**No independently verified K4 solution.** The present closeout audits existing exclusions and prepares bounded research; it makes no new K4 candidate claim.

## Current closeout

**All six requested tasks have terminal outcomes.** The complete report is `audit/backlog/CLOSEOUT.md`. R91 is a completed prerequisite power test; its failed arms did not advance to unknown-family classification or K4.

| Task | Current result | Evidence |
| --- | --- | --- |
| R32 historical aggregate replay | Complete full recount: 7,099,791,216 labeled settings; all retained archive statistics agree; zero full known-letter matches | `audit/reviews/R32_INDEPENDENT_RECOUNT.md` |
| R41 historical feasibility replay | Complete algebraic join across all nine saved inputs; all 18 part-counts agree; K4 has zero of 10,912,725,152 feasible settings | `audit/reviews/R41_INDEPENDENT_FEASIBILITY.md` |
| R90 independent review | Exact finite exclusion independently verified and L179 promoted; saved blind statistics remain NO_SIGNAL with no full original LM rerun claimed | `r90/audit/independent_closeout/REVIEW.md` |
| Multi-rotor designs | Complete reversible RX2-O/RX2-D designs, tested exact constraint kernel, phase/equivalence audit and finite execution bounds; cipher families remain OPEN | `audit/backlog/multirotor/DESIGN.md` |
| R82 solver gate | Completed R91 supplied-structure screen: 250/360 exact, 8/18 cells pass; broad bounded attempt SOLVER_NO_POWER. All 18 tested cells lie inside archived R83 LX scope; R91 adds no cipher exclusion | `r91/RESULT.md`, `audit/backlog/R91_RESULT_REVIEW.json`, `audit/reviews/POST_CLOSEOUT_SCOPE_REVIEW.md` |
| PTAK solver gate | Completed R91 lags 13–24 screen: 32/240 exact, 0/12 cells pass; archived bounded attempt SOLVER_NO_POWER, family OPEN | `r91/RESULT.md`, `audit/reviews/R91_POWER_GATE_CLOSEOUT.md` |

R89 and R90 jointly close 35 enumerated F26 alphabet classes, including all 20 original-design classes, within their finite parameter/error bounds. R90's independent exact result does not depend on the language model. Its amended operational retry and sampled summed-RSS semantics remain disclosed.

The multi-rotor review found 192 labeled phase-shifted single-rotor settings outside R87's zero-boundary-phase schedule. They remain OPEN. Equal-motion collapse alone does not certify an old exclusion.

The search hold was lifted on 16 November; current guardrails remain in force. New blind searches still require a fresh power gate, a frozen complete parameter/score/budget specification, and outputs committed and pushed before known-letter evaluation. Same-model subagents count as one review.

## Current next steps after the closeout review

The six-item backlog above was merged in PR #102 at `c16c4ad11c92391377f7347a70d88a5c02710fa5`; it is closed. The active work order is [audit/NEXT_STEPS.md](audit/NEXT_STEPS.md). Its old 15 November checklist is now explicitly historical.

1. **Primary research: RX2-O solver engineering**, at most three versions under fixed development caps. A working blind solver, confidence rule, key-equivalence evaluator and measured whole-search throughput must exist before a fresh formal gate.
2. **Parallel synthetic work: the 192 n<=4 single-rotor boundary-phase labels.** This is scope hygiene, not a K4 lead or a clue-assisted filter for the blind solver.
3. **Park the proposed narrow R82 K4 gate.** Source comparison proves that all 18 R91 linked-key cells, including the successful m=3/4 subgroup, are contained in archived R83 LX. The archive's only EXACT survivor is at m=20. This review does not independently certify or promote R83/L172; it prevents a redundant search from being presented as new coverage.
4. **Park the unchanged long-lag PTAK optimizer.** Reopen only after a materially different implementation demonstrates development recovery and passes a fresh gate.

The prospective rotor screen now has eight turnover-regime cells (160 controls), separating static and moving slow-rotor behavior. The full-method gate must handle nested single-rotor overlap, unidentifiable key labels, and top-ranked recovery separately from candidate recall. These corrections are prospective; no new experiment or K4 computation was performed. See [the review](audit/reviews/POST_CLOSEOUT_SCOPE_REVIEW.md) and [the revised design bounds](audit/backlog/multirotor/DESIGN.md).

## Historical status snapshots

The following text is retained as historical context. Its then-current backlog, dates and thresholds are superseded by the closeout table and current guardrails above.

### Snapshot originally titled: Current K4 research status (15 November 2026)

**No independently verified K4 solution. Nothing was submitted to an external verifier.**

**The K4 search hold was lifted by Tyler on 16 Nov 2026** (`audit/reviews/SEARCH_HOLD_LIFTED.md`). All guardrails stay in force.

**Latest search, R84 (17 Nov 2026):** R80a's two-keyword-stage families on K4, run strict blind in an isolated sandbox. Result: **NO_SIGNAL** (K4's best is no better than 60 of 100 shuffles; 4/24 published letters). See `r84/RESULT.md` and L173.

**Audit fixes merged 17 Nov:**
- #89: a broken workflow's YAML.
- #90: T1's WPX one-error strength labels were stale.
- The corrected statistic, recalibrated on K4 + 20 shuffles, gives K4 max s 2 (no setting at s ≥ 3) and p 0.38. No lead. See `r83/audit/WPX_STRENGTH.md`.

## November 2026 audit

- Two confirmed defects, both corrected by additive errata; original frozen files are unchanged:
  - **L172 (R83a):** the WPX "one published plaintext letter wrong" exclusion is withdrawn; PFX's drop-one count is not exhaustive (`r83/audit/ERRATUM.md`).
  - **L165 (R75):** F1X solution counts can overflow int64; those counts are unverified (`r75/audit/ERRATUM.md`).
- Independently re-derived and holding within their scope: L01–L04, L167.
- All other ledger exclusions are **unreplayed**, not disproved. No hash mismatch in any identifiable primary frozen file.
- Findings: `audit/historical/AUDIT_FINDINGS_AND_DECISIONS.md`. Rules for all future tests: `audit/FUTURE_TEST_GUARDRAILS.md`.
- **Work order progress (15 Nov, PR #86):**
  - **T1 done:** with one wrong published letter, WPX and PFX are both CHANCE. WPX has 2 survivors (inside the conservative 260); PFX has 22.
  - **T2 done:** F1X feasibility is confirmed setting by setting; only counts ≥ 2^63 were wrong.
  - **T3 done:** R81a's drop-one is sound. L35's Hill claim is flagged.
  - **T4, T5, T7 done:** documentation.
  - **T6 item 1 done (16 Nov):** R83a's EXACT results reproduced independently. LX was replayed in full on K4. There were 0 disagreements. Items 2–5 are not started.
  - The conditions for lifting the search hold now rest on review of T1/T2 and Tyler's decision.
- **What to do next:** `audit/NEXT_STEPS.md`.

The sections below preserve the status as of 31 October 2026. Their priorities and thresholds are historical, not current work instructions. Rounds R55–R83 are recorded in `LEDGER.md`.

---

## Status as of 31 October 2026

**No independently verified K4 solution. Nothing was submitted to an external verifier.**

## Merged work

- R49 (PR #19): previously reconstructed Berlin World Clock 24-face chart preserved with provenance/uncertainty; **not** authenticated as a K4 key.
- R53 (PR #23): hard ciphertext-only / freeze-before-reveal K4 input firewall; the Caesar solver is **only a pipeline smoke test**.
- R54 (PR #24): isolated ciphertext-only cipher-family fingerprints. IC is **0.0360824742** for the original 97-character ciphertext and all 26 letters occur. The best lag-7 signal has corrected p ≈ 0.149; period-column p ≈ 0.958. No cipher, key, or plaintext is identified.

## Preserved earlier work in this branch

- R43: **failed** word-beam solver, retained as an algebraic audit and negative result. Never use for K4 plaintext recovery.
- R44b: **20/20 exact** controlled blind recovery of 97-letter English messages *given the true key*, with independent forward-re-encryption witnesses. This is a valid **known-key** alphabet solver, **not** an unknown-key method.

## Not suitable as independent K4 evidence

- Claude's later R52/R52b branch: used confirmed K4 letters/positions to **choose a key/route** before a separated final solver ran. Therefore its selection pipeline is **crib-conditioned**, even though the final run omitted those letters; its 1/24 K4 output match and four known-key plants do **not** exclude a broad cipher family.
- Other historical finite-family postfreeze clue screens (R40G, R45–R51) may remain archival mathematical exclusions within their exact scopes but cannot seed a new ciphertext-only key search.

## Mandatory next steps

1. Specify reversible cipher/masking mechanisms and independently sourced key hypotheses **without K4 known letters**.
2. Demonstrate fully blind 97-letter recovery on at least 16/20 **fresh hidden-plaintext, hidden-key** encrypted controls for the exact method and key-search procedure; include proper null/false-positive calibration and independently verify every forward-encryption witness.
3. Run the original 97-letter ciphertext only in isolation; freeze full outputs and algorithm/key metadata; independently evaluate K4 published words and positions only **after** the freeze.
4. Do not tune on failed known-letter results. Document prior exposure of hypotheses and rerun on genuinely new control families before considering another K4 attempt.

Canonical owner rule: `r53/BLIND_RULES.md`.
