# R92 review complete; R93 and R94 ready for publication and execution

Affected ledger IDs: L181
Validation: Completed independent R92 exact/saved-evidence audit; source and
mathematical review of the separately registered R93/R94 work; public repository
and copied-input provenance checks. No new R93/R94 formal result is asserted.
Independent review: PARTIAL. ChatGPT independently reviewed Claude's R92 as
documented in the separate signed promotion note. R93/R94 are new ChatGPT work;
their same-model internal reviews do not constitute independent-model review.

Date: 21 November 2026, America/Chicago. Original UTC-dated archive files retain
their original dates.

## Current disposition

| Requested task | Completed work | Remaining step |
| --- | --- | --- |
| Independent R92 review | Exact proof/replay PASS; saved witnesses, gate/evaluation arithmetic and hashes checked; additive scope corrections and L181 promotion prepared | Publish and merge the reviewed package |
| Wider timing range | R93 registration published; exact checker, independent synthetic oracle, QA, finite scope, resource bounds and execution handoff prepared and source-reviewed | Approved source publication; formal correctness gate; published gate; one target audit; published freeze; interpretation |
| Structural two-rotor work | R94 registration published; old v1-v3 audit, two finite structural versions, diagnostics, caps and source review complete | Approved source publication; one cumulative development invocation; result review |

**There is no new K4 solution, R93 result or R94 recovery result.** Neither new
round's formal invocation has started. Main remains the merged PR #104 baseline
`9e4bd400e64c6aa46ae3afdc9ba0d82a1a927fd1`. The current remote follow-up branch
head is the preregistration/checker stage
`567f418961cc18847207008468679115074f4c93`; the reviewed source bundle and new
ledger/status edits are local prepared work.

## R92: evidence supports narrow promotion

An independently derived conflict-graph checker covers every one of R92's 192
labels on K4 and all 200 frozen shuffles. It finds zero feasible wirings under
all 24 observations and under each of the 24 possible one-observation omissions.
The additionally registered 128 R87 zero-phase labels for n=1..4 give the same
result. Together these certify all 320 phase/contact/direction labels through
period four, within the stated alphabets, position-only stepping and error model.
The remaining R87 zero-phase periods were not independently replayed here.

The correctness evidence includes 289,412 exhaustive toy comparisons, 320
full-size plants, both 31,040-case substitution panels and 1,280 identity-second-
rotor embeddings. All 2,015 saved candidate re-encryptions, 52 positive/extra
truth witnesses and 101 hash-manifest entries pass the independent audit.

Saved gate counts are **47/48 confident at >=95/97 letters, 44/48 exact,
44/48 used-contact wiring agreements and 0/150 confident negatives**. The saved
K4 result remains NO_SIGNAL: 50/200 nulls score at least as high, with add-one
value 51/201. This validates recorded arithmetic and witnesses; it does not
rerun the unavailable original full letter model, original optimization or
historical operating-system isolation. Raw-book freshness was not independently
certified. The original disclosed development budget overrun remains a deviation.

The sole audit job completed in 1.754 seconds wall, 1.628 aggregate CPU seconds
and 34.8 MiB sampled aggregate RSS, within 300/180 seconds and 1,024 MiB, with
zero retries. The detailed signed result is
`r92/audit/independent_review/REVIEW.md`; the promotion note is
`audit/reviews/R92_INDEPENDENT_REVIEW.md`.

## Corrections to the earlier interpretation

- RX2-O with identity second wiring contains the phased single rotor, even
  when the second rotor's schedule moves.
- Different clock schedules do not establish disjoint cipher functions.
- The deferred nonzero phases for n=5..96 number **145,728**, not 145,920; the
  latter includes R92's 192 already-tested labels.
- R92's blind maximum is the maximum retained by a pruned search pipeline,
  rather than an exhaustive letter-model optimum over all settings/wirings.
- The exact wiring contradiction does not require the unknown text to be
  English. Its one-observation tolerance does not cover insertions, deletions,
  lost stepping updates or two errors at different observed positions.
- Old RX2-O v1 is INCOMPLETE, not zero recovery. v2/v3's zero recovery refers
  to saved final states. Truth beating v3's saved states in 47/48 cases does
  not establish a global score optimum; one wrong saved state outscores truth.

The old rotor resource review accounts for all 17 committed logs, including
failed jobs. Their per-version sums fit the stated version allowances, but do
not prove absence of unlogged work or a historical shared cumulative enforcer.
The independent saved-output replay is implemented in R94 and has not run.

## R93: finite exact-checker experiment

The domain is n=5..96, phase 1..n-1, both directions and 16 contact pairs, with
arbitrary wiring. All 145,728 labels are retained even where finite schedules
overlap. They produce 4,690 distinct 97-position clocks; 94 also occur in R87.
These are parameter/schedule counts, not independent statistical trials or
proofs of disjoint cipher functions.

The formal gate is explicitly **EXACT_CHECKER_CORRECTNESS**, not blind recovery.
It requires 141,793 exhaustive small-alphabet cases against a complete-key
oracle, 8,832 full-size parameter plants, error/bulk-boundary checks and a
three-input throughput forecast. The development smoke result is labeled
DEVELOPMENT_ONLY and supplies no formal gate pass.

| Stage | Wall limit | Aggregate CPU limit | Memory limit | Attempts |
| --- | ---: | ---: | ---: | --- |
| Exact-checker correctness gate | 180 s | 120 s | 512 MiB | One, no automatic retry |
| K4 plus 200 fixed-seed shuffles, after published GO | 1,800 s | 1,200 s | 512 MiB | One, zero retries |

The target accounts for 29,291,328 setting/input calls and 732,283,200 logical
exact/deletion decisions. Counts use Python integers. Only 201 aggregate
records and provenance are emitted; decoded plaintexts, wiring completions
and surviving-setting outputs are capped at zero. Any positive compatibility
count remains COMPATIBLE/OPEN. No score, candidate or setting enters RX2.
The formal gate must be published before target execution, and the complete
target freeze must be published before interpretation. Any failed or incomplete
stage blocks the next stage. Independent-model review remains NONE.

The complete command/order handoff is `r93/EXECUTION_HANDOFF.md`.

## R94: structural two-rotor development

With inverse wirings U and V, the normalized decryption has the form
`P_i=U[V[C_i+s2_i]-(s2_i-s1_i)]-s1_i`, with contact arithmetic modulo 26.
Given either wiring, the other can be optimized exactly by a 26-by-26 linear
assignment for the additive unigram objective. This is a finite conditional
move; alternating such moves is not a global solution.

- **A:** eight starts on each of the existing 48 supplied-structure practice
  cases; at most 16 alternating whole-wiring unigram sweeps.
- **B:** the same final A starts; at most 24 order-four sweeps using assignment
  proposals, legal permutation cycles and a fixed swap fallback. Assignment is
  exact only for the surrogate; acceptance uses the actual order-four score.

Both unknown-wiring output files close and are hashed before the program opens
the public spent truth. Separate one-true-wiring diagnostics and 31,200 local
true-key-neighbor score checks then test conditional search and score failures.
This is an audited file-read order, not an operating-system blind sandbox.

The normalized relation `G_delta=H^delta F`, with H a single 26-cycle, is
mathematically verified by the design. It removes an interface rotation gauge
but does not establish finite-text identifiability or add an unregistered solver.

One cumulative invocation covers imports, mathematical checks, both versions,
diagnostics and archival replay: **1,800 seconds wall and aggregate CPU,
2,048 MiB, one worker, zero retries**. Additional phase caps are 60, 300, 900
and 300 seconds. At most 1,008 newly computed states are retained, under the
QA ceiling of 1,100. The runner refuses an existing output directory and cannot
overwrite earlier failure evidence on a refused repeat.

All input texts are spent development data. Any success remains a development
observation; any failure leaves the cipher family open. Neither outcome
authorizes K4, a fresh gate, a false-positive estimate or an exclusion.
The sole command and output list are in `r94/EXECUTION_HANDOFF.md`.

## Publication blocker and required approval

Automatic approval review rejected the source upload twice as possible
sensitive egress, identifying synthetic plaintext/test-key data, historical
logs and derived audit results in the public payload. The second rejection
persisted after verification that the repository is public, PR #104 matches
the user's exact merged baseline, and both copied practice files are
byte-identical to existing public blobs. The provenance record is
`audit/reviews/PUBLICATION_PROVENANCE_R92_R94.md`.

No alternate publication route was used. Source publication is a required
prospective step for both new rounds, so their runs remain paused. The next
action needs explicit approval to publish this reviewed source/evidence bundle
and the specified registered experiment artifacts to the public
`tylerj-spec/kryptos-k4` repository. Once publication succeeds, execute the
recorded sequence, audit the actual results, run the required CI and merge with
the prospective commit/freeze history preserved. Nothing here claims that
those later stages have already happened.
